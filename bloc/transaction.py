#!/usr/bin/env python3
import hashlib
import falcon
import db.service as DBService


class Transaction(object):
    def __init__(self, sender=None, receiver=None, amount=None, txn_hash=None, time_stamp=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time_stamp = time_stamp
        self.txn_hash = txn_hash

    def create(self):
        self.time_stamp = DBService.get_timestamp()
        self.txn_hash = self.gen_txn_hash()
        return self.txn_hash

    def gen_txn_hash(self):
        txn_string = '{}{}{}{}'.format(
            self.sender, self.receiver, self.amount, self.time_stamp)
        encoded_txn_string = f'{txn_string}'.encode()
        return hashlib.sha256(encoded_txn_string).hexdigest()

    def gen_dict(self):
        if self.time_stamp and self.txn_hash:
            txn_dict = {
                "txn_hash": self.txn_hash,
                "txn_data": {
                    "sender": self.sender,
                    "receiver": self.receiver,
                    "amount": self.amount
                },
                "txn_time_stamp": '{}'.format(self.time_stamp)
            }
            return txn_dict
        else:
            print("Hash and Timestamp not provided.")
            return False

    def gen_tuple(self):
        if self.time_stamp and self.txn_hash:
            return (self.txn_hash, self.sender, self.receiver, self.amount, self.time_stamp)
        else:
            print("Hash and Timestamp not provided.")
            return False

    def is_valid(self):
        if self.time_stamp and self.txn_hash:
            return self.gen_txn_hash() == self.txn_hash
        else:
            print("Hash and Timestamp not provided.")
            return False

    def add_to_unconfirmed_pool(self):
        insert_sql = "INSERT INTO unconfirmed_pool (TXN_HASH, TXN_TIME_STAMP, sender, receiver, amount) VALUES {};".format(
            (self.txn_hash, self.time_stamp, self.sender, self.receiver, self.amount)
        )

        db_resp = DBService.post("unconfirmed_pool", insert_sql)

        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
            resp_status = falcon.HTTP_400
        else:
            final_title = 'Success'
            final_msg = 'New transaction successfully added to DB.'
            resp_status = falcon.HTTP_201

        return (final_title, final_msg, resp_status)

    def confirmed_txns_insert_sql(self, block_hash):
        vals = (block_hash, self.txn_hash, self.sender, self.receiver, self.amount, self.time_stamp)
        insert_sql = """
            INSERT INTO confirmed_txns (BLOCK_HASH, TXN_HASH, sender, receiver, amount, TXN_TIME_STAMP) 
            VALUES {};
        """.format(vals)
        return insert_sql

    def to_obj(self, data):
        self.sender = data['txn_data']['sender']
        self.receiver = data['txn_data']['receiver']
        self.amount = data['txn_data']['amount']
        self.time_stamp = data['txn_time_stamp']
        self.txn_hash = data['txn_hash']
