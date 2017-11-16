#!/usr/bin/env python3
import json
import falcon
import server.utils as utils
import db.service as DBService

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


class NewTransaction(object):
    #<my_url>/new-transaction/add
    #<peer_url>/new-transaction/accept
    def __init__(self, db_store):
        self._db_store = db_store

    def on_get(self, req, resp, action):
        if action == 'add':
            resp.status = falcon.HTTP_200
            resp.content_type = 'text/html'
            resp.body = "WOHOO"

    def on_post(self, req, resp, action):
        """Adding New Transaction to my DB
           Then, broadcasting it to all peers.
           (This POST method will be captured from
            some kind of a web form)"""

        result_json = utils.parse_post_req(req)

        if action == 'add':
            utils.broadcast(payload=result_json,
                            endpoint="new-transaction/accept", request='POST')
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(result_json)
        elif action == 'accept':
            print(result_json)
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(result_json)
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Incorrect Endpoint Used.')


class AddPeerAddresses(object):
    def on_post(self, req, resp):
        """
            Endpoint that client can POST to,
            to add peer addresses

            #TODO: Give correct message if a node that already exists
                   is trying to be added.
        """
        peer_addrs = list(map(lambda x: (x,), utils.parse_post_req(req)['ips']))
        if len(peer_addrs) > 0:
            multi_insert = "INSERT INTO peer_addresses (IP) VALUES (?)"
            db_resp = DBService.post_many("peer_addresses", multi_insert, peer_addrs)
        else:
            post_sql = DBService.insert_into("peer_addresses", peer_addrs[0])
            db_resp = DBService.post("peer_addresses", post_sql)
        
        if db_resp:
            msg = {
                'Title': 'Success',
                'Message': 'Peer(s) successfully added.'
            }
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(msg)
        else:
            msg = {
                'Title': 'Error',
                'Message': 'Sorry, something went wrong. Please try again.'
            }
            raise falcon.HTTPError(falcon.HTTP_400, msg)


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