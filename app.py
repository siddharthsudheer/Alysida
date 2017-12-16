#!/usr/bin/env python3
import os
import falcon
import server.handlers as server
from db.store import DBStore
# from bloc.block import Block
# from bloc.transaction import Transaction
from bloc.chain import Chain


def create_app(db_store):
    api = application = falcon.API()
    # api.add_route('/chain/{action}', server.Chain(db_store))  # GET


    # Client-Facing Routes
    api.add_route('/register-with-peer', server.RegisterWithPeer())  # POST
    api.add_route('/add-peer-addresses', server.AddPeerAddresses())  # POST
    api.add_route('/get-peer-addresses', server.GetPeerAddresses())  # GET
    api.add_route('/discover-peer-addresses', server.DiscoverPeerAddresses(db_store))  # GET
    api.add_route('/add-new-transaction', server.AddNewTransaction())  # POST
    api.add_route('/get-unconfirmed-transactions', server.GetUnconfirmedTransactions())  # GET
    api.add_route('/mine', server.MineBlock())  # POST
    api.add_route('/get-blockchain', server.GetBlockchain())  # GET
    api.add_route('/consensus', server.Consensus())  # GET
    api.add_route('/accept-new-registration', server.AcceptNewRegistration())  # POST
   
    # Internal Routes
    api.add_route('/request-registration-update', server.RequestRegistrationUpdate())  # POST
    api.add_route('/new-registration', server.AddNewRegistration())  # POST
    api.add_route('/update-registration-status', server.UpdateRegistrationStatus())  # POST
    api.add_route('/serve-peer-addresses', server.ServePeerAddresses(db_store))  # GET
    api.add_route('/accept-new-transaction', server.AcceptNewTransaction())  # POST
    api.add_route('/accept-new-block', server.AcceptNewBlock())  # POST
    api.add_route('/peer-blockchain/{action}', server.PeerBlockchain(db_store))  # GET


    return api


def start_alysida():
    storage_path = os.environ.get('DB_STORAGE_PATH', './db/my_dbs')
    db_store = DBStore(storage_path)
    return create_app(db_store)

# import json
# blockchain = Chain()
# x = blockchain.is_valid()
# print("Is Valid? ", x)
# # x = blockchain.gen_dict(only_headers=False)
# # print(json.dumps(x, indent=4))
