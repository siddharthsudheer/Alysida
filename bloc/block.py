#!/usr/bin/env python3
import hashlib
import falcon
import json
import db.service as DBService
from bloc.transaction import Transaction

DIFFICULTY_TARGET = "000"


class Block(object):
    def __init__(
            self,
            block_num=None,
            block_hash=None,
            prev_block_hash=None,
            time_stamp=None,
            nonce=None,
            txn_hashes=None,
            txn_recs=None):

        self.block_num = block_num
        self.block_hash = block_hash
        self.prev_block_hash = prev_block_hash
        self.time_stamp = time_stamp
        self.nonce = nonce
        self.txn_hashes = txn_hashes
        self.txn_recs = txn_recs

    def create(self, last_block_hash):
        if self.get_txn_recs():
            self.time_stamp = DBService.get_timestamp()
            self.prev_block_hash = last_block_hash
            self.nonce = self.proof_of_work(self.time_stamp, self.txn_hashes_string(), self.prev_block_hash)
            self.block_hash = self.gen_block_hash()
            return self.block_hash
        else:
            print("Something wrong with transactions chosen.")

    def proof_of_work(self, time_stamp, txn_hashes, prev_block_hash):
        nonce = 0

        def _is_valid_block(nonce, prev_block_hash, time_stamp, txn_hashes):
            if nonce not in self.used_nonces():
                guess = self.gen_block_string(nonce, prev_block_hash, time_stamp, txn_hashes)
                guess_hash = hashlib.sha256(guess).hexdigest()
                print('~~~> Hash: {}'.format(guess_hash), end="\r")
                return guess_hash[:len(DIFFICULTY_TARGET)] == DIFFICULTY_TARGET
            else:
                return False
        
        print(" ")
        while _is_valid_block(nonce, prev_block_hash, time_stamp, txn_hashes) is False:
            nonce += 1
        print(" ")
        return nonce
    
    def convert_to_txns_obj(self, res):
        txn_recs = [dict(zip(res['column_names'], c))
                    for c in res['rows']] if res else []

        txo = lambda t: Transaction(
            sender=t['sender'],
            receiver=t['receiver'],
            amount=t['amount'],
            txn_hash=t['TXN_HASH'],
            time_stamp=t['TXN_TIME_STAMP']
        )
        return list(map(txo, txn_recs))

    def get_txn_recs(self):
        if self.txn_recs is None:
            hashes = str(tuple(self.txn_hashes)).replace(",)",")")
            sql_query = """
                SELECT TXN_HASH, TXN_TIME_STAMP, sender, receiver, amount 
                FROM unconfirmed_pool 
                WHERE TXN_HASH IN {}
            """.format(hashes)
            res = DBService.query("unconfirmed_pool", sql_query)
            if res:
                txn_recs = self.convert_to_txns_obj(res)
                if len(txn_recs) != len(self.txn_hashes):
                    return False
                else:
                    self.txn_recs = self.convert_to_txns_obj(res)
                    return self.txn_recs
            else:
                return False
        else:
            if len(self.txn_recs) != len(self.txn_hashes):
                return False
            return self.txn_recs
    
    def get_block_confirmed_txns(self):
            sql_query = """
                SELECT TXN_HASH, TXN_TIME_STAMP, sender, receiver, amount 
                FROM confirmed_txns 
                WHERE BLOCK_HASH = '{}'
            """.format(self.block_hash)
            res = DBService.query("main_chain", sql_query)
            if res:    
                self.txn_recs = self.convert_to_txns_obj(res)
                self.txn_hashes = self.gen_txn_hashes()
                return self.txn_recs
            else:
                return False

    def gen_block_hash(self):
        block_string = self.gen_block_string(self.nonce, self.prev_block_hash, self.time_stamp, self.txn_hashes_string())
        return hashlib.sha256(block_string).hexdigest()

    def is_valid(self):
        if self.time_stamp and self.block_hash and self.nonce:
            return self.gen_block_hash() == self.block_hash
        else:
            print("Hash, Nonce, and/or Timestamp not provided.")
            return False

    def add_to_chain(self):
        main_chain = """
            INSERT INTO main_chain (BLOCK_NUM, BLOCK_HASH, NONCE, TIME_STAMP) 
            VALUES (NULL,'{}',{},'{}');
        """.format(self.block_hash, self.nonce, self.time_stamp)
        self.txn_recs = self.get_txn_recs()
        print(self.txn_recs)
        txn_inserts = [txn.confirmed_txns_insert_sql(self.block_hash) for txn in self.txn_recs]
        confirmed_txns = '{}'.format(''.join(map(str, txn_inserts)))
        final = main_chain + "\n" + confirmed_txns

        db_resp = DBService.post_many("main_chain", final)

        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
            resp_status = falcon.HTTP_400
        else:
            final_title = 'Success'
            final_msg = 'New transaction successfully added to DB.'
            resp_status = falcon.HTTP_201
            self.get_block_num()
            self.clean_unconfirmed_pool()

        return (final_title, final_msg, resp_status)


    def clean_unconfirmed_pool(self):
        hashes = str(tuple(self.txn_hashes)).replace(",)",")")
        delete_sql = """
            DELETE FROM unconfirmed_pool WHERE TXN_HASH in {};
        """.format(hashes)
        db_resp = DBService.post("unconfirmed_pool", delete_sql)


    def gen_dict(self):
        if self.txn_recs is None:
            self.get_txn_recs()

        txn_recs_dict = [t.gen_dict() for t in self.txn_recs]
        block_dict = {
            "block_num": self.block_num,
            "block_hash": self.block_hash,
            "time_stamp": self.time_stamp,
            "nonce": self.nonce,
            "txns": txn_recs_dict
        }

        return block_dict

    def to_obj(self, data):
        self.block_num = data['block_num']
        self.block_hash = data['block_hash']
        self.time_stamp = data['time_stamp']
        self.nonce = data['nonce']

        def _txo(t):
            new_t = Transaction()
            new_t.to_obj(t)
            return new_t

        self.txn_recs = list(map(_txo, data['txns']))
        self.txn_hashes = [t.txn_hash for t in self.txn_recs]
        # self.prev_block_hash = self.get_prev_block_hash()

    def get_block_num(self):
        sql_query = "SELECT BLOCK_NUM FROM main_chain WHERE BLOCK_HASH='{}'".format(self.block_hash)
        res = DBService.query("main_chain", sql_query)
        self.block_num = None if not res else res['rows'][0]
        return self.block_num
    
    #####################################################################################
    #   Helper Functions
    #####################################################################################
    def used_nonces(self):
        sql_query = "SELECT NONCE FROM main_chain"
        result = DBService.query("main_chain", sql_query)
        nonces = result['rows'] if result else []
        return nonces
    
    def gen_txn_hashes(self):
        return [t.txn_hash for t in self.txn_recs]

    def txn_hashes_string(self):
        x = '{}'.format(','.join(map(str, sorted(self.txn_hashes))))
        return x

    def gen_block_string(self, nonce, prev_block_hash, time_stamp, txn_hashes):
        block_string = '{}{}{}{}'.format(
            str(nonce), prev_block_hash, time_stamp, txn_hashes
        )
        final = f'{block_string}'.encode()
        return final

    def get_prev_block_hash(self):
        if self.prev_block_hash != None:
            return self.prev_block_hash

        def _using_block_num():
            if self.block_num != None:
                if self.block_num - 1 < 1:
                    return '0'
                else:
                    prev_block_num = self.block_num - 1
                    sql_query = "SELECT BLOCK_HASH FROM main_chain WHERE BLOCK_NUM = {}".format(prev_block_num)
                    res = DBService.query("main_chain", sql_query)
                    prev_hash = False if not res else '{}'.format(res['rows'][0])
                    return prev_hash
            else:
                return False

        prev_hash = _using_block_num()
        if prev_hash != True:
            if self.block_hash != None:
                sql_query = "SELECT BLOCK_NUM FROM main_chain WHERE BLOCK_HASH = '{}'".format(self.block_hash)
                res = DBService.query("main_chain", sql_query)
                self.block_num = None if not res else res['rows'][0]
                prev_hash = _using_block_num()
        
        self.prev_block_hash = prev_hash if prev_hash else None
        return self.prev_block_hash
