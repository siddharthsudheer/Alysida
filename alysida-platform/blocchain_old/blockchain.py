#!/usr/bin/env python3
import falcon
import json
import hashlib
from urllib.parse import urlparse
import db.service as DBService

DIFFICULTY_TARGET = "00"

class Blockchain(object):
    def __init__(self):
        self.chain = self._chain()
        self.length = len(self.chain)
        self.last_block = self.chain[-1] if self.length > 0 else None


    def _chain(self):
        sql_query = "SELECT * FROM main_chain"
        result = DBService.query("main_chain", sql_query)
        blocks = [ dict(zip( result['column_names'], bloc )) for bloc in result['rows'] ] if result else []
        return blocks


    def taken_nonces(self):
        sql_query = "SELECT NONCE FROM main_chain"
        result = DBService.query("main_chain", sql_query)
        nonces = result['rows'] if result else []
        return nonces


    def check_block_validity(self, block_hash):
        main_chain_query = "SELECT * FROM main_chain WHERE BLOCK_HASH = '{}'".format(block_hash)
        get_txns_query = "SELECT * FROM confirmed_txns WHERE BLOCK_HASH = '{}'".format(block_hash)

        main_res = DBService.query("main_chain", main_chain_query)
        txn_res = DBService.query("main_chain", get_txns_query)

        block_rec = [ dict(zip( main_res['column_names'], c )) for c in main_res['rows'] ][0] if main_res else []
        txn_recs = [ dict(zip( txn_res['column_names'], c )) for c in txn_res['rows'] ] if txn_res else []
        txn_hashes = [ txn['TXN_HASH'] for txn in txn_recs ]
        txn_data = '{}'.format(','.join(map(str, txn_hashes))) 
        prev_block_hash = self.get_prev_block_hash(block_rec['BLOCK_NUM'])
        block_hash = self.block_hash(block_rec['NONCE'], txn_data, block_rec['TIME_STAMP'], prev_block_hash)
        return block_hash == block_rec['BLOCK_HASH'] 


    def get_prev_block_hash(self, block_num):
        if block_num - 1 < 1:
            return  '0'
        else: 
            prev_block_num = block_num - 1
            sql_query = "SELECT BLOCK_HASH FROM main_chain WHERE BLOCK_NUM = {}".format(prev_block_num)
            res = DBService.query("main_chain", sql_query)
            prev_hash = False if not res else '{}'.format(res['rows'][0])
            return prev_hash
    
    def print_and_add_block_to_db(self, vals):
        self.print_block(vals)
        insert_sql = str(DBService.insert_into("main_chain", vals))
        db_resp = DBService.post_many("main_chain", insert_sql)

        if db_resp != True:
            final_title = 'Error'
            final_msg = db_resp
        else:
            final_title = 'Success'
            final_msg = 'Block successfully added to DB.'
        print("\n  Title: {}\n  Message: {}\n".format(final_title, final_msg))

    
    def new_block(self, txn_ids):
        txns_query = "SELECT HASH, TIME_STAMP, sender, receiver, amount FROM unconfirmed_pool NATURAL JOIN transaction_recs WHERE HASH IN {}".format(tuple(txn_ids))
        txn_res = DBService.query("unconfirmed_pool", txns_query)
        if txn_res:
            txn_recs = [ dict(zip( txn_res['column_names'], c )) for c in txn_res['rows'] ] if txn_res else []
            txn_recs = list(map(lambda x: TxnModel(x).gen(), txn_recs))
            txn_hashes = [ txn['hash'] for txn in txn_recs ]
            prev_block_hash = self.last_block['BLOCK_HASH']
            new_block = self.mine_block(prev_block_hash, txn_hashes)
            vals = (new_block["block_hash"], new_block["nonce"], new_block["time_stamp"], txn_recs)
            self.print_and_add_block_to_db(vals)


    def generate_genesis_block(self):
        txn_data = {
            "sender":"genesis",
            "receiver":"genesis",
            "amount":0
        }
        txn = TransactionRecord(txn_data)
        txn_json = txn.json_format()
        genesis_block = self.mine_block('0', [txn_json["hash"]])
        main_chain_vals = (genesis_block["block_hash"], genesis_block["nonce"], genesis_block["time_stamp"], [txn_json])
        self.print_and_add_block_to_db(main_chain_vals)
        

    def block_hash(self, nonce, txn_data, time_stamp, prev_block_hash):
        block_string = '{}{}{}{}'.format(str(nonce), txn_data, time_stamp, prev_block_hash)
        encoded_block_string = f'{block_string}'.encode()
        return hashlib.sha256(encoded_block_string).hexdigest()


    def mine_block(self, prev_block_hash, txn_recs_list):
        txn_data = '{}'.format(','.join(map(str, txn_recs_list))) 
        time_stamp = '{}'.format(DBService.get_timestamp())
        block_nonce = self.proof_of_work(txn_data, time_stamp, prev_block_hash)
        block_hash = self.block_hash(block_nonce, txn_data, time_stamp, prev_block_hash)
        block = {
            "block_hash": block_hash,
            "nonce": block_nonce,
            "time_stamp": time_stamp,
        }
        return block


    def proof_of_work(self, txn_data, time_stamp, prev_block_hash):
        nonce = 0
        print(" ")
        while self.is_valid_block(nonce, txn_data, time_stamp, prev_block_hash) is False:
            nonce += 1
        return nonce


    def is_valid_block(self, nonce, txn_data, time_stamp, prev_block_hash):
        if nonce not in self.taken_nonces():
            block_string = '{}{}{}{}'.format(str(nonce), txn_data, time_stamp, prev_block_hash)
            guess = f'{block_string}'.encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            print('~~~> Hash: {}'.format(guess_hash), end="\r")
            return guess_hash[:len(DIFFICULTY_TARGET)] == DIFFICULTY_TARGET
        else:
            return False


    def print_block(self, vals):
        block_hash, nonce, time_stamp, txns = vals
        print("\n\n========================================== GENESIS BLOCK ==========================================\n")
        print("  Block Hash: ",block_hash)
        print("  Nonce: ",nonce)
        print("  Time Stamp: ",time_stamp)
        print("\n  Transactions:")
        print("---------------------------------------------------------------------------------------\n")
        for txn in txns:
            for k,v in txn.items():
                print("    {}: {}".format(k,v))
            print(" ")
        print("---------------------------------------------------------------------------------------\n")
        print("===================================================================================================\n")


class TransactionRecord(object):
    def __init__(self, txn_data):
        self.txn_data = txn_data
        self.timestamp = DBService.get_timestamp()
        self.hash = '{}'.format(self.get_hash())

    def generate_vals(self):
        vals = (self.hash, self.txn_data['sender'], self.txn_data['receiver'], self.txn_data['amount'], self.timestamp)
        return vals

    def get_hash(self):
        """
        Creates a SHA-256 hash of a Transaction
        """
        data = {
            'txn_data': '{}'.format(self.txn_data),
            'time_stamp': '{}'.format(self.timestamp)
        }

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        data_string = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(data_string).hexdigest()
    
    def json_format(self):
        data = {
            "hash": self.hash,
            "txn_data": self.txn_data,
            "time_stamp": '{}'.format(self.timestamp)
        }

        return data