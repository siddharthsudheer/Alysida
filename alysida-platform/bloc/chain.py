#!/usr/bin/env python3
import hashlib
import falcon
import db.service as DBService
from bloc.block import Block

class Chain(object):
    def __init__(self):
        self.chain = self._chain()
        self.length = len(self.chain)
        self.last_block = self.chain[-1] if self.length > 0 else None

    def _chain(self):
        sql_query = "SELECT * FROM main_chain"
        result = DBService.query("main_chain", sql_query)
        blocks = [ dict(zip( result['column_names'], bloc )) for bloc in result['rows'] ] if result else []
        bloc = lambda t: Block(
            block_num=t['BLOCK_NUM'],
            block_hash=t['BLOCK_HASH'],
            nonce=t['NONCE'],
            time_stamp=t['TIME_STAMP']
        )
        blocks = list(map(bloc, blocks))
        return blocks
    
    def add_new_block(self, block):
        if self.length > 0 and self.last_block != None:
            block.prev_block_hash = self.last_block.block_hash
            block.block_num = self.last_block.block_num + 1
        block.create()
        block.add_to_chain()
        self.chain = self._chain()
        return block

    # def gen_dict(self):
    #     if self.time_stamp and self.txn_hash:
    #         txn_dict = {
    #             "txn_hash": self.txn_hash,
    #             "txn_data": {
    #                 "sender": self.sender,
    #                 "receiver": self.receiver,
    #                 "amount": self.amount
    #             },
    #             "time_stamp": '{}'.format(self.time_stamp)
    #         }
    #         return txn_dict
    #     else:
    #         print("Hash and Timestamp not provided.")
    #         return False

    # def is_valid(self):
    #     if self.time_stamp and self.txn_hash:
    #         return self.gen_txn_hash() == self.txn_hash
    #     else:
    #         print("Hash and Timestamp not provided.")
    #         return False


