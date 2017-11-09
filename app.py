#!/usr/bin/env python3
import os
import falcon
import server.api as server
from db.store import DBStore
from db.setup import SetupDB
import db.service as DBService

SetupDB(DBService)

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


# def create_app(db_store):
#     api = application = falcon.API()
#     api.add_route('/chain/{action}', server.Chain(db_store))  # GET
#     api.add_route('/new-transaction/{action}',
#                   server.NewTransaction(db_store))  # POST
#     api.add_route('/register/{action}', server.RegisterNode(db_store))  # POST
#     return api


# def start_alysida():
#     storage_path = os.environ.get('DB_STORAGE_PATH', './db/myDbs')
#     db_store = DBStore(storage_path)
#     return create_app(db_store)
