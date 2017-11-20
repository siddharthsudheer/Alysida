#!/usr/bin/env python3
import os
import falcon
import server.handlers as server
from db.store import DBStore
from db.setup import SetupDB
import db.service as DBService

SetupDB(DBService)

def create_app(db_store):
    api = application = falcon.API()
    api.add_route('/chain/{action}', server.Chain(db_store))  # GET
    

    api.add_route('/add-peer-addresses', server.AddPeerAddresses())  # POST
    api.add_route('/register-me', server.RegisterMe())  # GET
    api.add_route('/get-peer-addresses', server.GetPeerAddresses())  # GET

    api.add_route('/discover-peer-addresses', server.DiscoverPeerAddresses(db_store))  # GET
    api.add_route('/serve-peer-addresses', server.ServePeerAddresses(db_store))  # GET

    api.add_route('/add-new-transaction', server.AddNewTransaction())  # POST
    api.add_route('/accept-new-transaction', server.AcceptNewTransaction())  # POST
    api.add_route('/get-unconfirmed-transactions', server.GetUnconfirmedTransactions())  # GET
    # api.add_route('/get-txn-info/{txn_id}', server.GetTxnInfo())  # GET

    
    return api


def start_alysida():
    storage_path = os.environ.get('DB_STORAGE_PATH', './db/my_dbs')
    db_store = DBStore(storage_path)
    return create_app(db_store)
