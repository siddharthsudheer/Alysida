#!/usr/bin/env python3

class Transaction(object):
     def __init__(self, sender, receiver, amount, txn_hash=None, timestamp=None):
         self.sender = sender
         self.receiver = receiver
         self.amount = amount
         self.time_stamp = time_stamp
         self.txn_hash = txn_hash
    
    def create(self):
        self.time_stamp = DBService.get_timestamp()
        self.txn_hash = self.gen_txn_hash()

    def gen_txn_hash(self):
        txn_string = '{}{}{}{}'.format(self.sender, self.receiver, self.amount, self.time_stamp)
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
                "time_stamp": '{}'.format(self.time_stamp)
            }
            return txn_dict
        else:
            print("Hash and Timestamp not provided.")
            return False
    
    def gen_tuple(self):
        if self.time_stamp and self.txn_hash:
            return (self.hash, self.sender, self.receiver, self.amount, self.time_stamp)
        else:
            print("Hash and Timestamp not provided.")
            return False

    def is_valid(self):
        if self.time_stamp and self.txn_hash:
            return gen_txn_hash() == self.txn_hash
        else:
            print("Hash and Timestamp not provided.")
            return False