#!/usr/bin/env python3
import os
import falcon
import server.api as server
from db.store import DBStore
from db.setup import SetupDB
import db.service as DBService

SetupDB(DBService)

# i = '1.1.1.1.1'
# postSQL = DBService.insert_into("peer_addresses", i)
# DBService.post("peer_addresses", postSQL)

# sql_query = "SELECT IP FROM peer_addresses"
# res = DBService.query("peer_addresses", sql_query)

# print(res)

# INSERTS = [
#     (13, 'SOMEHASH13', 'SOME BLOCK DATATATATA 13', DBService.get_timestamp()),
#     (17, 'SOMEHASH17', 'SOME BLOCK DATATATATA 17', DBService.get_timestamp())
# ]


# for i in INSERTS:
#     postSQL = DBService.insert_into("main_chain", i)
#     DBService.post("main_chain", postSQL)

# postSQL = DBService.insert_into("node_addresses", pop)
# DBService.post("node_addresses", postSQL)
# x = DBService.query("my_node_info", "SELECT * FROM my_node_info;")
# print(x)
# print(DBService.compare_dbs("node_addresses", "1_node_addresses"))


def create_app(db_store):
    api = application = falcon.API()
    api.add_route('/chain/{action}', server.Chain(db_store))  # GET
    api.add_route('/new-transaction/{action}', server.NewTransaction(db_store))  # POST

    api.add_route('/add-peer-addresses', server.AddPeerAddresses())  # POST
    api.add_route('/register-me', server.RegisterMe())  # GET
    api.add_route('/get-peer-addresses', server.GetPeerAddresses())  # GET
    return api


def start_alysida():
    storage_path = os.environ.get('DB_STORAGE_PATH', './db/my_dbs')
    db_store = DBStore(storage_path)
    return create_app(db_store)
