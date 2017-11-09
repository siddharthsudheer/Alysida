#!/usr/bin/env python3
from urllib.parse import urlparse


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

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        new_txn = {
            'Sender': 'Person1',
            'Receiver': 'Person2',
            'Amount': 50
        }

        return new_txn
