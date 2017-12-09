#!/usr/bin/env python3
import os
import hashlib
import db.service as DBService
from bloc.block import Block
import json
import server.utils as utils
from itertools import groupby
from random import *
import requests
from db.store import DBStore
from urllib.parse import urlparse

class Chain(object):
    def __init__(self):
        self.chain = self._chain()
        self.length = len(self.chain)
        self.last_block = self.chain[-1] if self.length > 0 else None


    def _chain(self):
        sql_query = "SELECT * FROM main_chain"
        result = DBService.query("main_chain", sql_query)

        blocks = [dict(zip(result['column_names'], bloc))
                  for bloc in result['rows']] if result else []

        def _bloc(b):
            bloc = Block(
                block_num=b['BLOCK_NUM'],
                block_hash=b['BLOCK_HASH'],
                nonce=b['NONCE'],
                time_stamp=b['TIME_STAMP']
            )
            bloc.get_block_confirmed_txns()
            return bloc

        blocks = list(map(_bloc, blocks))
        return blocks
    

    def refresh_vals(self):
         self.chain = self._chain()
         self.length = len(self.chain)
         self.last_block = self.chain[-1] if self.length > 0 else None


    def add_new_block(self, block):
        block.block_num = self.last_block.block_num + 1 if self.last_block != None else 1
        last_block_hash = self.last_block.block_hash if self.last_block != None else '0'
        block.create(last_block_hash)
        block.add_to_chain()
        self.refresh_vals()
        return block


    def gen_dict(self, only_headers=False): 
        if only_headers: 
            final = [{b.block_num: str(b.block_hash)} for b in self.chain]
            x = "_headers"
        else: 
            final = [b.gen_dict() for b in self.chain]
            x = "s"
        
        chain_dict = {
            "chain_length": self.length,
            "db_checksum": str(self.get_db_checksum()),
            "block{}".format(x): final
        }
        return chain_dict


    def get_db_checksum(self):
        db = "./db/my_dbs/main_chain.db"
        hash_md5 = hashlib.md5()
        with open(db, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


    def is_valid(self):
        last_block = self.chain[0]
        current_index = 1

        while current_index < len(self.chain):
            block = self.chain[current_index]

            # Check that the hash of the block is correct
            block.get_prev_block_hash()
            if block.prev_block_hash != last_block.block_hash:
                return False

            if not block.is_valid():
                return False

            last_block = block
            current_index += 1

        return True
    
    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: <bool> True if our chain was replaced, False if not
        """
        new_chain = None
        peer_headers = utils.broadcast(payload=None, endpoint="peer-blockchain/give-headers", request='GET')
        # Find max length chain
        # Find all peers' checksum who have that max length
        # if there are peers having the max length but different 
        # checksums, we check to see which of those checksums
        # have the highest frequency on network, and choose
        # that one as our best bet.

        r,b,l,c = "Response", "blockchain", "chain_length", "db_checksum"

        get_len = lambda p: p[r][b][l]
        get_checksum = lambda p: p[r][b][c]

        max_len = max(list(map(get_len, peer_headers)))
        if max_len >= self.length:
            max_len_peers = list(filter(lambda p: p[r][b][l] == max_len, peer_headers))
            max_len_peers_chks = list(map(get_checksum, max_len_peers))
            max_len_peers_chks_freq = [{c: chk, 'freq': len(list(freq))} for chk, freq in groupby(max_len_peers_chks)]
            max_freq = max(list(map(lambda f: f['freq'], max_len_peers_chks_freq)))
            best_bet_chks = list(filter(lambda f: f['freq'] == max_freq, max_len_peers_chks_freq))
            # If the frequencies are the same, choose a random one
            rand = randint(0, len(best_bet_chks)-1) if len(best_bet_chks) > 1 else 0
            best_bet_chk = best_bet_chks[rand][c]
            peers_with_best_bet = list(filter(lambda p: p[r][b][c] == best_bet_chk, peer_headers))
            peer_addrs = list(map(lambda i: 'http://{}:4200/peer-blockchain/give-db'.format(i['Peer']), peers_with_best_bet))
            
            got_file=False
            unresponsive_peers=list()
            count=0
            for peer in peer_addrs:
                if not got_file:
                    peer_to_contact = peer_addrs[count]
                    response = requests.get(peer_to_contact, stream=True)

                    if response.status_code == 200:
                        peer_name = urlparse(peer).hostname
                        resp_obj = { 
                            'Peer': '{}'.format(peer_name),
                            'Response': response 
                        }
                        storage_path = os.environ.get('DB_STORAGE_PATH', './db/my_dbs')
                        db_store = DBStore(storage_path)
                        db_store._storage_save_path = storage_path
                        db_obj = db_store.save(resp_obj, "main_chain")
                        new_chain = db_obj
                        got_file = True
                    else:
                        print("--> Failed: ", peer_to_contact)
                        unresponsive_peers.append(peer_to_contact)
        
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            new_db_file = './db/my_dbs/{}'.format(new_chain['db_file'])
            os.rename('./db/my_dbs/main_chain.db', './db/my_dbs/main_chain_current.db')
            os.rename(new_db_file, './db/my_dbs/main_chain.db')
            self.chain = self._chain()
            self.length = len(self.chain)
            self.last_block = self.chain[-1] if self.length > 0 else None

            if self.is_valid():
                os.remove('./db/my_dbs/main_chain_current.db')
                return True

        return False
    