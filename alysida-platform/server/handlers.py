#!/usr/bin/env python3
import json
import falcon
import server.utils as utils
import db.service as DBService
from blockchain import TransactionRecord

DB_TYPE = 'application/x-sqlite3'


class Chain(object):
    #<my_url>/chain/ask-peers
    #<peer_url>/chain/request

    def __init__(self, db_store):
        self._db_store = db_store

    def on_get(self, req, resp, action):
        # Asking for their chain
        if action == 'ask-peers':
            peer_chains = utils.broadcast(
                payload=None, endpoint="chain/request", request='GET')
            db_filenames = []
            for chain in peer_chains:
                chain_obj = self._db_store.save(chain)
                db_filenames.append(chain_obj)
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(db_filenames)
        # Giving them my chain upon request
        elif action == 'request':
            resp.content_type = DB_TYPE
            resp.stream, resp.stream_len = self._db_store.open('main_chain.db')
            resp.status = falcon.HTTP_200
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Incorrect Endpoint Used.')



class AcceptNewTransaction(object):
    def on_post(self, req, resp):
        """
            Endpoint that accepts a new transaction
            made by peer on network
        """
        results = utils.parse_post_req(req)['new_txn']
        txn_record_vals = tuple([str(v) for k,v in results.items()])
        insert_sql = DBService.insert_into("unconfirmed_pool", txn_record_vals)
        db_resp = DBService.post("unconfirmed_pool", insert_sql)
        db_resp = True
        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
            resp.status = falcon.HTTP_400
        else:
            final_title = 'Success'
            final_msg = 'New transaction successfully added to DB.'
            resp.status = falcon.HTTP_201

        msg = {
            'Title': final_title,
            'Message': final_msg,
            'Txn_data': results
        }
        resp.content_type = 'application/json'
        resp.body = json.dumps(msg)



class AddNewTransaction(object):
    def on_post(self, req, resp):
        """
            Endpoint that client can POST to,
            to add their new transaction
        """
        payload = utils.parse_post_req(req)
        txn_rec = TransactionRecord(payload)
        txn_record_vals = txn_rec.generate()

        insert_sql = DBService.insert_into("unconfirmed_pool", txn_record_vals)
        db_resp = DBService.post("unconfirmed_pool", insert_sql)

        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
            resp.status = falcon.HTTP_400
        else:
            final_title = 'Success'
            final_msg = 'New transaction successfully added to DB.'
            resp.status = falcon.HTTP_201

        jsonified = {'new_txn': txn_rec.json_format()}
        responses = utils.broadcast(payload=jsonified, endpoint="accept-new-transaction", request='POST')

        msg = {
            'Title': final_title,
            'Message': final_msg,
            'Txn_data': jsonified,
            'peer_responses': responses
        }

        resp.content_type = 'application/json'
        resp.body = json.dumps(msg)



class GetUnconfirmedTransactions(object):
    """
        Endpoint for user to see what is 
        in the unconfirmed txns pool
    """
    def on_get(self, req, resp):
        sql_query = "SELECT * FROM unconfirmed_pool"
        result = DBService.query("unconfirmed_pool", sql_query)
        unconfirmed_txns = [ dict(zip( result['column_names'], txn )) for txn in result['rows'] ] if result else []
        response = {'unconfirmed_txns': unconfirmed_txns}
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)


class AddPeerAddresses(object):
    def on_post(self, req, resp):
        """
            Endpoint that client can POST to,
            to add peer addresses
        """
        peer_addrs = list(map(lambda x: (x,), utils.parse_post_req(req)['ips']))
        multi_insert = "INSERT INTO peer_addresses (IP) VALUES (?)"
        db_resp = DBService.post_many("peer_addresses", multi_insert, peer_addrs)
        
        if db_resp != True:
            if str(db_resp) == 'UNIQUE constraint failed: peer_addresses.IP':
                final_title = 'Duplicate Entry'
                final_msg = 'One or more provided peers already exists in DB.'
                resp.status = falcon.HTTP_201
            else:
                final_title = 'Error'
                final_msg = db_resp
                resp.status = falcon.HTTP_400

            msg = {
                'Title': final_title,
                'Message': final_msg
            }
        else:
            msg = {
                'Title': 'Success',
                'Message': 'Peer(s) successfully added.'
            }
            resp.status = falcon.HTTP_201

        resp.content_type = 'application/json'
        resp.body = json.dumps(msg)

class RegisterMe(object):
    """
        Endpoint that client will call
        to register themselves with the 
        other nodes
    """
    def on_get(self, req, resp):
        sql_query = "SELECT IP FROM node_prefs"
        my_ip = {'ips': DBService.query("node_prefs", sql_query)['rows']}
        responses = utils.broadcast(payload=my_ip, endpoint="add-peer-addresses", request='POST')
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(responses)


class GetPeerAddresses(object):
    """
        Endpoint for user to see who's on his list.
        #TODO: Nodes can ask for each other's peer_addresses.db
               (discovery of nodes in a way).
    """
    def on_get(self, req, resp):
        sql_query = "SELECT IP FROM peer_addresses"
        peer_ips = {'peers': DBService.query("peer_addresses", sql_query)['rows']}
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(dict(peer_ips))