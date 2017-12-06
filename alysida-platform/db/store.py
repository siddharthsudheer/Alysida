#!/usr/bin/env python3
import io
import os
import re

class DBStore(object):

    _CHUNK_SIZE_BYTES = 4096

    def __init__(self, storage_path, fopen=io.open):
        self._storage_save_path = storage_path + '/downloads'
        self._my_storage_path = storage_path
        self._fopen = fopen

    def save(self, recv_db, filename):
        peer_name, db_stream = recv_db['Peer'], recv_db['Response']
        peer_name_stripped = re.sub('[^A-Za-z0-9]+', '', peer_name)
        name = '{filename}-{peer_name}{ext}'.format(filename=filename, peer_name=peer_name_stripped, ext='.db')
        db_path = os.path.join(self._storage_save_path, name)

        with self._fopen(db_path, 'wb') as db_file:
            while True:
                chunk = db_stream.raw.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                db_file.write(chunk)

        return {'peer_name': peer_name, 'db_file': name}

    def open(self, name):
        db_path = os.path.join(self._my_storage_path, name)
        stream = self._fopen(db_path, 'rb')
        stream_len = os.path.getsize(db_path)

        return stream, stream_len
