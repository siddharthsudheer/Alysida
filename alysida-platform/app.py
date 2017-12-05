#!/usr/bin/env python3
import os
import falcon
import server.handlers as server
from db.store import DBStore
from db.setup import SetupDB
import db.service as DBService
from bloc.block import Block
from bloc.transaction import Transaction
from bloc.chain import Chain


import json

SetupDB(DBService)

# def create_app(db_store):
#     api = application = falcon.API()
#     api.add_route('/chain/{action}', server.Chain(db_store))  # GET


#     # Client-Facing Routes
#     api.add_route('/add-peer-addresses', server.AddPeerAddresses())  # POST
#     api.add_route('/register-me', server.RegisterMe())  # GET
#     api.add_route('/get-peer-addresses', server.GetPeerAddresses())  # GET
#     api.add_route('/discover-peer-addresses', server.DiscoverPeerAddresses(db_store))  # GET
#     api.add_route('/add-new-transaction', server.AddNewTransaction())  # POST
#     api.add_route('/get-unconfirmed-transactions', server.GetUnconfirmedTransactions())  # GET

#     # Internal Routes
#     api.add_route('/new-registration', server.AddNewRegistration())  # POST
#     api.add_route('/accept-new-registration', server.AcceptNewRegistration())  # POST
#     api.add_route('/update-registration-status', server.UpdateRegistrationStatus())  # POST
#     api.add_route('/request-registration-update', server.RequestRegistrationUpdate())  # POST
#     api.add_route('/serve-peer-addresses', server.ServePeerAddresses(db_store))  # GET
#     api.add_route('/accept-new-transaction', server.AcceptNewTransaction())  # POST
    

#     return api


# def start_alysida():
#     storage_path = os.environ.get('DB_STORAGE_PATH', './db/my_dbs')
#     db_store = DBStore(storage_path)
#     return create_app(db_store)

# from time import sleep
# peeps = [
#     {'sender':'admin', 'receiver':'sidd', 'amount':'50'},
#     {'sender':'sidd', 'receiver':'isit', 'amount':'20'},
#     {'sender':'isit', 'receiver':'atit', 'amount':'10'},
#     {'sender':'admin', 'receiver':'sidd', 'amount':'50'},
#     {'sender':'sidd', 'receiver':'isit', 'amount':'20'},
#     {'sender':'isit', 'receiver':'atit', 'amount':'10'},
# ]

# txn_hashes = list()

# for i in peeps:
#     o = Transaction(sender=i['sender'], receiver=i['receiver'], amount=i['amount'])
#     txn_hashes.append(o.create())
#     o.add_to_unconfirmed_pool()
#     sleep(1)

# txns = txn_hashes[0:4]
# txns = ['809dde25fe6f4aa77bd3b18fae147acd5831490623b25f1098912c8bc5e1c514', '7d5a6d9f3cb78733085332ac27674bbaa5484d518de9705b13231fa9e8ccb752']
# blockchain = Chain()
# new_block = Block(txn_hashes=txns)
# new_block = blockchain.add_new_block(new_block)
# x = new_block.gen_dict()
# print(new_block.is_valid())
# print(json.dumps(x, indent=4, sort_keys=True))