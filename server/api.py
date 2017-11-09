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


class RegisterNode(object):
    #<my_url>/register/me
    #<peer_url>/register/new
    def __init__(self, db_store):
        self._db_store = db_store

    def on_post(self, req, resp, action):
        """Broadcasting my IP to all peers
           to register. And each node accepting it."""

        result_json = utils.parse_post_req(req)

        if action == 'me':
            utils.broadcast(payload=result_json,
                            endpoint="register/new", request='POST')
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(result_json)
        elif action == 'new':
            print(result_json)
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(result_json)
            vals = (result_json['uuid'], result_json['ip'], DBService.get_timestamp())
            post_sql = DBService.insert_into("peer_addresses", vals)
            DBService.post("peer_addresses", post_sql)
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Incorrect Endpoint Used.')
