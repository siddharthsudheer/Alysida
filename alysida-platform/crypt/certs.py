#!/usr/bin/env python3
import os
from Crypto.PublicKey import RSA


class Certs(object):
    def __init__(self):
        self._certs_path = "./crypt/my_certs/"
        self.private_key, self.public_key = self._keys()

    def _keys(self):
        pvt_cert_path = os.path.join(self._certs_path, 'rsa_key')
        pub_cert_path = os.path.join(self._certs_path, 'rsa_key.pub')
        
        with open(pvt_cert_path, "rb") as private_f:
            private_key = private_f.read()
            private_f.close()

        with open(pub_cert_path, "rb") as public_f:
            public_key = public_f.read()
            private_f.close()
        
        return (str(private_key.decode('utf-8')), str(public_key.decode('utf-8')))
