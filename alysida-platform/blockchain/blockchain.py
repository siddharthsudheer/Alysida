#!/usr/bin/env python3
import json
import hashlib
from urllib.parse import urlparse
import db.service as DBService

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.nodes = set()

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


class TransactionRecord(object):
    def __init__(self, txn_data):
        self.txn_data = txn_data
        self.timestamp = DBService.get_timestamp()
        self.hash = '{}'.format(self.get_hash())

    def generate(self):
        jsonified = dict({'data': dict(self.txn_data)})
        final_txn_data = '{}'.format(jsonified['data'])
        return (self.hash, final_txn_data, self.timestamp)

    def get_hash(self):
        data = {
            'txn_data': '{}'.format(self.txn_data),
            'time_stamp': '{}'.format(self.timestamp)
        }

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        data_string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(data_string).hexdigest()
    
    def json_format(self):
        data = {
            'hash': self.hash,
            'txn_data': self.txn_data,
            'time_stamp': '{}'.format(self.timestamp)
        }

        return data