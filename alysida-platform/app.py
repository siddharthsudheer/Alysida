#!/usr/bin/env python3
import os
import falcon
import server.handlers as server
from db.store import DBStore
from db.setup import SetupDB
import db.service as DBService
from crypt.certs import Certs
# from blockchain import Blockchain

SetupDB(DBService)

def create_app(db_store):
    api = application = falcon.API()
    api.add_route('/chain/{action}', server.Chain(db_store))  # GET


    # Client-Facing Routes
    api.add_route('/add-peer-addresses', server.AddPeerAddresses())  # POST
    api.add_route('/register-me', server.RegisterMe())  # GET
    api.add_route('/get-peer-addresses', server.GetPeerAddresses())  # GET
    api.add_route('/discover-peer-addresses', server.DiscoverPeerAddresses(db_store))  # GET
    api.add_route('/add-new-transaction', server.AddNewTransaction())  # POST
    api.add_route('/get-unconfirmed-transactions', server.GetUnconfirmedTransactions())  # GET

    # Internal Routes
    api.add_route('/new-registration', server.AddNewRegistration())  # POST
    api.add_route('/accept-new-registration', server.AcceptNewRegistration())  # POST
    api.add_route('/update-registration-status', server.UpdateRegistrationStatus())  # POST
    api.add_route('/request-registration-update', server.RequestRegistrationUpdate())  # POST
    api.add_route('/serve-peer-addresses', server.ServePeerAddresses(db_store))  # GET
    api.add_route('/accept-new-transaction', server.AcceptNewTransaction())  # POST
    

    return api


def start_alysida():
    storage_path = os.environ.get('DB_STORAGE_PATH', './db/my_dbs')
    db_store = DBStore(storage_path)
    return create_app(db_store)

# blockchain = Blockchain()
# # txns = ['e8de0abe96f20c20a531489c77f7692b68e83af3a55dd51a5ace121c5dac9bef', '295e6a00e15a16428392015954c9166274cf2544bec2135fcdc7194d1f884a17', '3a95ea8c7ad05d21db0e0e90b693dbded399f27639951bb2a8587a9f404491c1']
# # blockchain.new_block(txns)
# x = blockchain.check_block_validity('00ad35f33dc2bc4f98a1f149ea5b112745d0f19c066be1320a7e8c3d87a61e27')
# print(x)