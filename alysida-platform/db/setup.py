#!/usr/bin/env python3
import os
import json
import socket
import db.service as DBService
from bloc.block import Block
from bloc.transaction import Transaction
from bloc.chain import Chain

DB_SCHEMA = {
    "peer_addresses": {
        "schema": """
            CREATE TABLE IF NOT EXISTS peer_addresses (
                IP                      VARCHAR(15) PRIMARY KEY ON CONFLICT IGNORE,
                PUBLIC_KEY              TEXT NOT NULL,
                REGISTRATION_STATUS     TEXT NOT NULL
            );
        """
    },
    "main_chain": {
        "schema": """
            CREATE TABLE IF NOT EXISTS main_chain (
                BLOCK_NUM               INTEGER PRIMARY KEY AUTOINCREMENT,
                BLOCK_HASH              VARCHAR(66),
                NONCE                   INTEGER,
                TIME_STAMP              TIMESTAMP,
                UNIQUE                  (BLOCK_HASH),
                UNIQUE                  (NONCE)
            );
        """,
        "schema2": """
            CREATE TABLE IF NOT EXISTS confirmed_txns (
                BLOCK_HASH              VARCHAR(66),
                TXN_HASH                VARCHAR(66),
                sender                  TEXT,
                receiver                TEXT,
                amount                  REAL,
                TXN_TIME_STAMP          TIMESTAMP,
                PRIMARY KEY             (TXN_HASH)
                FOREIGN KEY (BLOCK_HASH) REFERENCES main_chain(BLOCK_HASH)
            );
        """
    },
    "unconfirmed_pool": {
        "schema": """
            CREATE TABLE IF NOT EXISTS unconfirmed_pool (
                TXN_HASH                VARCHAR(66),
                TXN_TIME_STAMP          TIMESTAMP,
                sender                  TEXT,
                receiver                TEXT,
                amount                  REAL,
                PRIMARY KEY             (TXN_HASH)
            );
        """
    },
    "node_prefs": {
        "schema": """
            CREATE TABLE IF NOT EXISTS node_prefs (
                UUID                    VARCHAR(40),
                IP                      VARCHAR(15),
                PREFERENCES             TEXT,
                PRIMARY KEY             (UUID, IP)
            );
        """
    }
}

DB_PATH = "./db/my_dbs/"
DB_DOWNLOADS_PATH = DB_PATH + 'downloads/'
NODE_CONFIG = './AlysidaFile'


class SetupDB(object):
    def __init__(self, DBService):
        for f in [DB_PATH, DB_DOWNLOADS_PATH]:
            if not os.path.exists(f):
                os.makedirs(f)

        for dbfile, db_obj in DB_SCHEMA.items():
            db_path = DBService.DB_PATH + dbfile + '.db'
            if not os.path.isfile(db_path):
                open(db_path, 'w').close()
            DBService.post(dbfile, db_obj['schema'])
            if 'schema2' in db_obj:
                DBService.post(dbfile, db_obj['schema2'])

        with open(NODE_CONFIG) as data_file:
            self.config = json.load(data_file)
            data_file.close()

        self.populate_my_prefs()
        self.populate_peer_addresses()
        self.add_genesis_block()
        

    def populate_peer_addresses(self):
        """
            Populate the peer_addresses db if empty
        """

        sql_query = "SELECT count(*) FROM peer_addresses"
        res = DBService.query("peer_addresses", sql_query)
        num_addrs = res['rows'][0]
        my_ip = str(DBService.query("node_prefs", "SELECT IP FROM node_prefs")['rows'][0])
        core_peer_ip = str(self.config['CORE_PEER']['IP'])
        if not num_addrs > 0 and core_peer_ip != my_ip:
            vals = (core_peer_ip, 'unregistered', 'unregistered')
            core_peer_insert_sql = DBService.insert_into("peer_addresses", vals)
            post_res = DBService.post("peer_addresses", core_peer_insert_sql)


    def populate_my_prefs(self):
        """
            Populate my_prefs db if its empty or the
            info in config file doesn't match the db data.
        """
        sql_query = "SELECT * FROM node_prefs"
        res = DBService.query("node_prefs", sql_query)

        try:
            my_ip = socket.gethostbyname(socket.gethostname())
        except:
            my_ip = socket.gethostname()

        vals = (self.config['UUID'], my_ip, self.config['MY_PREFERENCES'])

        def _insert_config_info():
            insert_sql = DBService.insert_into("node_prefs", vals)
            DBService.post("node_prefs", insert_sql)

        if not res:
            # If no info in DB
            _insert_config_info()
        elif tuple(res['rows'][0]) != vals:
            # If info doesnt match
            delete_sql = "DELETE FROM node_prefs WHERE IP='{}'".format(my_ip)
            DBService.post("node_prefs", delete_sql)
            _insert_config_info()


    def add_genesis_block(self):
        """
            If main_chain db is empty generate 
            and add genesis block.
        """
        blockchain = Chain()
        if not blockchain.length > 0:
            print("\nNothing in Chain. Generating genesis block.")
            genesis_txn = Transaction(sender='genesis', receiver='genesis', amount=0)
            genesis_txn.create()
            genesis_hash = genesis_txn.gen_dict()['txn_hash']

            genesis_block = Block(txn_hashes=[genesis_hash], txn_recs=[genesis_txn], prev_block_hash='0')
            genesis_block = blockchain.add_new_block(genesis_block)
            print("\nGenesis Block Validity: ", genesis_block.is_valid())
            g = genesis_block.gen_dict()
            print("\n{}\n".format(json.dumps(g, indent=4, sort_keys=True)))