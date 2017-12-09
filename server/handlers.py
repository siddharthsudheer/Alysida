#!/usr/bin/env python3
import json
import falcon
import requests
import server.utils as utils
import db.service as DBService
from crypt.certs import Certs
from bloc.block import Block
from bloc.transaction import Transaction
from bloc.chain import Chain
import time

DB_TYPE = 'application/x-sqlite3'


# class Chain(object):
#     #<my_url>/chain/ask-peers
#     #<peer_url>/chain/request

#     def __init__(self, db_store):
#         self._db_store = db_store

#     def on_get(self, req, resp, action):
#         # Asking for their chain
#         if action == 'ask-peers':
#             peer_chains = utils.broadcast(
#                 payload=None, endpoint="chain/request", request='GET')
#             db_filenames = []
#             for chain in peer_chains:
#                 chain_obj = self._db_store.save(chain, "main_chain")
#                 db_filenames.append(chain_obj)
#             resp.status = falcon.HTTP_201
#             resp.body = json.dumps(db_filenames)
#         # Giving them my chain upon request
#         elif action == 'request':
#             resp.content_type = DB_TYPE
#             resp.stream, resp.stream_len = self._db_store.open('main_chain.db')
#             resp.status = falcon.HTTP_200
#         else:
#             raise falcon.HTTPError(falcon.HTTP_400, 'Incorrect Endpoint Used.')

class Consensus(object):
    """
        Endpoint client can call to get 
        the longest chain in the network.
    """    
    def on_get(self, req, resp):
        blockchain = Chain()     
        replaced = blockchain.resolve_conflicts()

        if replaced:
            final_title, final_msg = "Success", "Our chain was replaced"
        else:
            final_title, final_msg = "Success", "Our chain is authoritative"

        msg = {
            "title": final_title,
            "message": final_msg,
            "blockchain": blockchain.gen_dict()
        }

        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(msg)


class PeerBlockchain(object):
    """
        Endpoint for peer to ask another
        peer for their blockchain headers
        or their db file.
    """
    def __init__(self, db_store):
        self._db_store = db_store

    def on_get(self, req, resp, action):
        blockchain = Chain()     
        if action == 'give-headers':
            response = {'blockchain': blockchain.gen_dict(only_headers=True)}
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response)
        elif action == 'give-db':
            resp.content_type = DB_TYPE
            resp.stream, resp.stream_len = self._db_store.open('main_chain.db')
            resp.status = falcon.HTTP_200
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Incorrect Endpoint Used.')


class GetBlockchain(object):
    """
        Endpoint for user to see the
        whole blockchain
    """
    def on_get(self, req, resp):
        blockchain = Chain()
        response = {'blockchain': blockchain.gen_dict()}

        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


class MineBlock(object):
    def on_post(self, req, resp):
        """
            Endpoint that client can POST to,
            with transaction IDs, to mine their 
            new block
        """
        payload = utils.parse_post_req(req)['txn_hashes']
        blockchain = Chain()
        replaced = blockchain.resolve_conflicts()
        # if replaced, then check if selected txns
        # are still in unconfirmed pool or not.
        # if not, msg user telling them to re-select

        # if not replaced.. continue

        new_block = Block(txn_hashes=payload)
        new_block.get_txn_recs()
        new_block = blockchain.add_new_block(new_block)

        send_payload = {'new_block': new_block.gen_dict()}
        responses = utils.broadcast(payload=send_payload, endpoint="accept-new-block", request='POST')

        msg = {
            'Title': 'Success',
            'Message': 'Block has been added and broadcast.',
            'Block': send_payload,
            'peer_responses': responses
        }

        # msg = {
        #     'Title': 'Success',
        #     'Message': 'Block has been added and broadcast.',
        #     'Block': send_payload,
        #     'peer_responses': 'all good'
        # }

        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(msg)

class AcceptNewBlock(object):
    def on_post(self, req, resp):
        """
            Endpoint that accepts a new block
            mined by peer on network
        """
        res = utils.parse_post_req(req)['new_block']

        blockchain = Chain()
        new_block = Block(prev_block_hash=blockchain.last_block.block_hash)
        new_block.to_obj(res)

        if blockchain.length >= new_block.block_num:
            block_exists = True if blockchain.last_block.block_hash == new_block.block_hash else False
            if block_exists:
                msg = {
                    'title': "Block exists",
                    'message': "Block already in Blockchain."
                }
            else:
                msg = {
                    'title': "Stale Block",
                    'message': "My blockchain is longer that yours."
                }
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(msg)
        
        if blockchain.length < new_block.block_num:
            is_next_block_num = True if (blockchain.length + 1) == new_block.block_num else False
            
            if is_next_block_num and new_block.is_valid():
                blockchain.add_new_block(new_block)
                msg = {
                    'title': "Success",
                    'message': "New Block Added",
                    'block_data': res
                }
                utils.notifier("accepted_new_block", msg)
                resp.content_type = 'application/json'
                resp.status = falcon.HTTP_201
                resp.body = json.dumps(msg)

            else:
                time.sleep(2)
                replaced = blockchain.resolve_conflicts()
                new_block.prev_block_hash = blockchain.last_block.block_hash
                block_added = True if blockchain.last_block.block_hash == new_block.block_hash else False
                if replaced and block_added:
                    msg = {
                        'title': "Success",
                        'message': "New Block Added",
                        'block_data': res
                    }
                    utils.notifier("accepted_new_block", msg)
                    resp.content_type = 'application/json'
                    resp.status = falcon.HTTP_201
                    resp.body = json.dumps(msg)
                else:
                    msg = {
                        'title': "Failed",
                        'message': "Unable to accept block into chain.",
                        'block_data': res
                    }
                    resp.content_type = 'application/json'
                    resp.status = falcon.HTTP_200
                    resp.body = json.dumps(msg)


class AcceptNewTransaction(object):
    def on_post(self, req, resp):
        """
            Endpoint that accepts a new transaction
            made by peer on network
        """
        results = utils.parse_post_req(req)['new_txn']
        txn_rec = Transaction()
        txn_rec.to_obj(results)

        if txn_rec.is_valid():
            final_title, final_msg, resp_status = txn_rec.add_to_unconfirmed_pool()
        else:
            final_title, final_msg, resp_status = "Invalid", "Transaction hash not valid", falcon.HTTP_400
        
        msg = {
            'Title': final_title,
            'Message': final_msg,
            'Txn_data': results
        }

        utils.notifier("accepted_new_txn", results)

        resp.content_type = 'application/json'
        resp.status = resp_status
        resp.body = json.dumps(msg)


class AddNewTransaction(object):
    def on_post(self, req, resp):
        """
            Endpoint that client can POST to,
            to add their new transaction
        """
        payload = utils.parse_post_req(req)
        txn_rec = Transaction(sender=payload['sender'], receiver=payload['receiver'], amount=payload['amount'])
        txn_rec.create()
        final_title, final_msg, resp_status = txn_rec.add_to_unconfirmed_pool()

        send_payload = {'new_txn': txn_rec.gen_dict()}
        responses = utils.broadcast(payload=send_payload, endpoint="accept-new-transaction", request='POST')

        msg = {
            'Title': final_title,
            'Message': final_msg,
            'Txn_data': send_payload,
            'peer_responses': responses
        }

        # msg = {
        #     'Title': final_title,
        #     'Message': final_msg,
        #     'Txn_data': send_payload,
        #     'peer_responses': "all good"
        # }

        resp.content_type = 'application/json'
        resp.status = resp_status
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
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


class RegisterMe(object):
    """
        Endpoint that client will call
        to register themselves with the 
        other nodes
    """
    def on_get(self, req, resp):
        sql_query = "SELECT IP FROM node_prefs"
        my_ip = str(DBService.query("node_prefs", sql_query)['rows'][0])
        my_pub_key = str(Certs().public_key)
        payload_to_send_peers = dict({'ips': [[my_ip, my_pub_key]]})

        sql_query = "SELECT IP FROM peer_addresses WHERE IP!='{}' AND (REGISTRATION_STATUS=='unregistered' OR REGISTRATION_STATUS=='registration-pending')".format(my_ip)
        query_result = DBService.query("peer_addresses", sql_query)

        if not query_result: # if 0 results for unregistered peers addrs returned
            final_title = 'Success'
            final_msg = 'No unregistered peers. You are already registered with all known peers.'
            final_status = falcon.HTTP_200
        else:
            peer_ips = query_result['rows']
            failed_responses = list()
            success_response_ips = list()

            for peer in peer_ips:
                url = 'http://{}:4200/new-registration'.format(peer)
                json_resp = dict()

                try:
                    peer_resp = requests.post(url, data=json.dumps(payload_to_send_peers))
                    json_resp = peer_resp.json()
                except requests.exceptions.RequestException as e:
                    json_resp['title'] = 'Peer not reachable'
                    print( '**{}\n**{}\n**{}'.format(json_resp['title'], peer, e) )

                if json_resp['title'] == "Success: Successfully Added":
                    success_response_ips.append('{}'.format(peer))
                    update_query = "UPDATE peer_addresses SET PUBLIC_KEY = 'unreceived', REGISTRATION_STATUS = 'registration-pending' WHERE IP = '{}'".format(peer)
                    DBService.post("peer_addresses", update_query)
                elif json_resp['title'] == "Success: Successfully Registered":
                    update_url = 'http://{}:4200/request-registration-update'.format(peer)
                    update_resp = dict()
                    my_ip_payload = dict({'ip': my_ip})

                    try:
                        peer_update_resp = requests.post(update_url, data=json.dumps(my_ip_payload))
                        update_resp = peer_update_resp.json()
                    except requests.exceptions.RequestException as e:
                        update_resp['title'] = 'Peer not reachable'
                        print( '**{}\n**{}\n**{}'.format(update_resp['title'], peer, e) )
                    
                    if update_resp['title'] == "Success":
                        success_response_ips.append('{}'.format(peer))
                    else:
                        failed_responses.append({ 'Peer': '{}'.format(peer), 'Response': update_resp })
                else:
                    failed_responses.append({ 'Peer': '{}'.format(peer), 'Response': json_resp })


            if not failed_responses:
                final_title = 'Success'
                final_msg = 'You have been registered with: {}'.format(','.join(map(str, success_response_ips)) )
                final_status = falcon.HTTP_201
            else:
                final_title = 'Error: Unable to register with following peers.'
                final_msg = {
                    'failed_peers': failed_responses,
                    'success_peers': success_response_ips
                }
                final_status = falcon.HTTP_500
        
        msg = {
            'Title': final_title,
            'Message': final_msg
        }

        utils.notifier("new_peer", msg)
        resp.content_type = 'application/json'
        resp.status = final_status
        resp.body = json.dumps(msg)

class AddNewRegistration(object):
    def on_post(self, req, resp):
        """
            Endpoint that other peers POST to,
            to register themselves
        """
        parsed = utils.parse_post_req(req)
        resp.content_type = 'application/json'
        msg, resp.status = DBService.add_new_peer_address(parsed, 'acceptance-pending')
        utils.notifier("new_peer", parsed)
        resp.body = json.dumps(msg)


class AddPeerAddresses(object):
    def on_post(self, req, resp):
        """
            Endpoint that client can POST to,
            to add peer addresses
        """
        parsed = utils.parse_post_req(req)
        resp.content_type = 'application/json'
        msg, resp.status = DBService.add_new_peer_address(parsed, 'unregistered')
        utils.notifier("new_peer", parsed)
        resp.body = json.dumps(msg)


class AcceptNewRegistration(object):
    def on_post(self, req, resp):
        """
            Endpoint that client POSTs to,
            to accept peers that have registered with client
            but haven't accepted yet (peers with status: 'acceptance-pending')
        """
        peer_addrs = str(tuple(utils.parse_post_req(req)['ips'])).replace(",)",")")
        update_query = "UPDATE peer_addresses SET REGISTRATION_STATUS = 'registered' WHERE REGISTRATION_STATUS = 'acceptance-pending' AND IP IN {}".format(peer_addrs)
        db_resp = DBService.post("peer_addresses", update_query)

        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
            resp.status = falcon.HTTP_500
        else:
            sql_query = "SELECT IP FROM peer_addresses WHERE REGISTRATION_STATUS = 'registered' AND IP IN {}".format(peer_addrs)
            res = DBService.query("peer_addresses", sql_query)
            if res:
                accepted_peers = res['rows']
                ip_query = "SELECT IP FROM node_prefs"
                my_ip = DBService.query("node_prefs", ip_query)['rows'][0]
                my_pub_key = Certs().public_key
                acceptance_msg = {
                    'registrar_ip': '{}'.format(my_ip), 
                    'registration_status': 'Success',
                    'public_key': my_pub_key
                    }
                for peer in accepted_peers:
                    url = 'http://{}:4200/update-registration-status'.format(peer)
                    try:
                        peer_resp = requests.post(url, data=json.dumps(acceptance_msg))
                    except requests.exceptions.RequestException as e:
                        err_msg = 'Peer not reachable'
                        print( '**{}\n**{}\n**{}'.format(err_msg, peer, e) )

                final_title = 'Success'
                final_msg = 'Accepted Peer(s): {}'.format(accepted_peers)
                resp.status = falcon.HTTP_201
            else:
                final_title = 'Error'
                final_msg = "Can only accept peers that exist in DB with status: 'acceptance-pending'."
                resp.status = falcon.HTTP_400

        msg = {
            'Title': final_title,
            'Message': final_msg
        }

        utils.notifier("new_peer", msg)
        resp.content_type = 'application/json'
        resp.body = json.dumps(msg)


class RequestRegistrationUpdate(object):
    """
        Endpoint for one node to ask the other node
        to send it back a public key, if it has been
        accepted.
    """
    def on_post(self, req, resp):
        peer_addr = str(utils.parse_post_req(req)['ip'])
        sql_query = "SELECT REGISTRATION_STATUS FROM peer_addresses WHERE IP = '{}'".format(peer_addr)
        res = DBService.query("peer_addresses", sql_query)
        print(res)
        if res:
            peer_status = str(res['rows'][0])
            print(peer_status)
            if peer_status == "registered":
                final_title = 'Success'
                final_msg = 'Okay. Attempting to send you my Info.'
                resp.status = falcon.HTTP_200

                ip_query = "SELECT IP FROM node_prefs"
                my_ip = DBService.query("node_prefs", ip_query)['rows'][0]
                my_pub_key = Certs().public_key
                acceptance_msg = {
                    'registrar_ip': '{}'.format(my_ip), 
                    'registration_status': 'Success',
                    'public_key': my_pub_key
                    }
                url = 'http://{}:4200/update-registration-status'.format(peer_addr)

                try:
                    peer_resp = requests.post(url, data=json.dumps(acceptance_msg))
                except requests.exceptions.RequestException as e:
                    err_msg = 'Peer not reachable'
                    print( '**{}\n**{}\n**{}'.format(err_msg, peer, e) )

            elif peer_status == "acceptance-pending":
                final_title = 'In Progress'
                final_msg = 'You are yet to be accepted.'
                resp.status = falcon.HTTP_202
            else:
                final_title = 'Error'
                final_msg = 'Something is not right!'
                resp.status = falcon.HTTP_500
        else:
            final_title = 'Error'
            final_msg = 'Unauthorized. You seem like a fishy person!'
            resp.status = falcon.HTTP_401
        
        msg = {
            'title': str(final_title),
            'message': str(final_msg)
        }
        utils.notifier("new_peer", msg)
        resp.content_type = 'application/json'
        resp.body = json.dumps(dict(msg))


class UpdateRegistrationStatus(object):
    def on_post(self, req, resp):
        """
            Endpoint that the peers use to 
            respond to client's registration
        """
        recv_payload = utils.parse_post_req(req)

        if recv_payload['registration_status'] == 'Success':
            update_query = "UPDATE peer_addresses SET PUBLIC_KEY = '{}', REGISTRATION_STATUS = 'registered' WHERE IP = '{}'".format(recv_payload['public_key'], recv_payload['registrar_ip'])
            db_resp = DBService.post("peer_addresses", update_query)

            msg = {
                'Title': 'Success',
                'Message': 'Thank you for accepting moi.'
            }

            utils.notifier("new_peer", msg)
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(msg)


class DiscoverPeerAddresses(object):
    """
        Endpoint that client will call
        to discover new peer addresses
        by asking other peers in network
    """
    def __init__(self, db_store):
        self._db_store = db_store
    
    def on_get(self, req, resp):
        peer_dbs = utils.broadcast(payload=None, endpoint="serve-peer-addresses", request='GET', isFile=True)
        db_filenames = []
        for peer_db in peer_dbs:
            db_obj = self._db_store.save(peer_db, "peer_addresses")
            db_filenames.append(db_obj)
        
        for i in db_filenames:
            diff = DBService.ip_db_diff("peer_addresses", i['db_file'])
            if diff:
                ips = [ i[0] for i in diff['rows'] ]
                i['difference'] = {
                    'column': diff['column_names'][0],
                    'values': ips
                }
                peer_addrs = list(map(lambda x: (x,), ips))
                multi_insert = "INSERT INTO peer_addresses (IP, PUBLIC_KEY, REGISTRATION_STATUS) VALUES (?, 'unregistered', 'unregistered')"

                db_resp = DBService.post_many("peer_addresses", multi_insert, peer_addrs)
                if db_resp != True:
                    i['post_status'] = db_resp
                else:
                    i['post_status'] = "The difference was inserted into DB."
            else:
                i['difference'] = "No Difference."
                i['post_status'] = "Nothing was inserted into DB."
        
        utils.notifier("peer_discovery_result", db_filenames)
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(db_filenames)


class ServePeerAddresses(object):
    """
        Endpoint that gives my peer_addresses.db
        to another peer in network upon request
    """
    def __init__(self, db_store):
        self._db_store = db_store
    
    def on_get(self, req, resp):
        resp.content_type = DB_TYPE
        resp.stream, resp.stream_len = self._db_store.open('peer_addresses.db')
        resp.status = falcon.HTTP_200


class GetPeerAddresses(object):
    """
        Endpoint for user to see who's on his list.
        #TODO: Nodes can ask for each other's peer_addresses.db
               (discovery of nodes in a way).
    """
    def on_get(self, req, resp):
        sql_query = "SELECT * FROM peer_addresses"
        results = DBService.query("peer_addresses", sql_query)

        if results:
            res_formatted = list(map(lambda i: {'peer_ip': i[0], 'pub_key': i[1], 'status': i[2]}, results['rows']))
            final_msg = {'peers': res_formatted}
        else:
            final_msg = {'Message':'Zero peers found.','peers': []}
        
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(dict(final_msg))