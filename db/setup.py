#!/usr/bin/env python3
import os
import json
import socket
import db.service as DBService


DB_SCHEMA = {
    "node_addresses": {
        "schema": """
            CREATE TABLE IF NOT EXISTS node_addresses (
                NODENAME                VARCHAR(64),
                IP                      VARCHAR(15),
                TIME_STAMP              TIMESTAMP,
                PRIMARY KEY             (IP)
            );
        """
    },
    "main_chain": {
        "schema": """
            CREATE TABLE IF NOT EXISTS main_chain (
                BLOCK_ID                INTEGER,
                NONCE                   INTEGER,
                HASH                    VARCHAR(64),
                BLOCK_DATA              TEXT,
                TIME_STAMP              TIMESTAMP,
                PRIMARY KEY             (BLOCK_ID)
            );
        """
    },
    "unconfirmed_txns": {
        "schema": """
            CREATE TABLE IF NOT EXISTS unconfirmed_txns (
                HASH                    VARCHAR(64),
                TXN_DATA                TEXT,
                TIME_STAMP              TIMESTAMP,
                PRIMARY KEY             (HASH, TXN_DATA)
            );
        """
    },
    "my_node_info": {
        "schema": """
            CREATE TABLE IF NOT EXISTS my_node_info (
                IP                      VARCHAR(15),
                NODENAME                VARCHAR(64),
                PREFERENCES             TEXT,
                PRIMARY KEY             (IP)
            );
        """
    }
}

DB_PATH = "./db/myDbs/"
NODE_CONFIG = './node_config.json'


class SetupDB(object):
    def __init__(self, DBService):
        for dbfile, db_obj in DB_SCHEMA.items():
            db_path = DBService.DB_PATH + dbfile + '.db'
            if not os.path.isfile(db_path):
                open(db_path, 'w').close()
            DBService.post(dbfile, db_obj['schema'])

        with open(NODE_CONFIG) as data_file:
            self.config = json.load(data_file)
            data_file.close()

        self.populate_node_addresses()
        self.populate_my_node_info()

    def populate_node_addresses(self):
        """
            Populate the node_addresses db if empty
        """

        sql_query = "SELECT count(*) FROM node_addresses"
        res = DBService.query("node_addresses", sql_query)
        num_addrs = res['rows'][0]

        if not num_addrs > 0:
            for node in self.config['OTHER_NODE_ADDRESSES']:
                vals = (node['node_name'],
                        node['ip_address'],
                        DBService.get_timestamp())
                insert_sql = DBService.insert_into("node_addresses", vals)
                DBService.post("node_addresses", insert_sql)

    def populate_my_node_info(self):
        """
            Populate my_node_info db if its empty or the
            info in config file doesn't match the db data.
        """
        sql_query = "SELECT * FROM my_node_info"
        res = DBService.query("my_node_info", sql_query)
        try:
            my_ip = socket.gethostbyname(socket.gethostname())
        except:
            my_ip = socket.gethostname()
        vals = (my_ip,
                self.config['MY_NODE_NAME'],
                self.config['MY_PREFERENCES'])

        def _insert_config_info():
            insert_sql = DBService.insert_into("my_node_info", vals)
            DBService.post("my_node_info", insert_sql)

        if not res:
            # If no info in DB
            _insert_config_info()
        elif res['rows'][0] != vals:
            # If info doesnt match
            delete_sql = "DELETE FROM my_node_info WHERE IP='{}'".format(my_ip)
            DBService.post("my_node_info", delete_sql)
            _insert_config_info()
