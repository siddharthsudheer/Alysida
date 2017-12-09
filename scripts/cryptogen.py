#!/usr/bin/env python3
import os
import json
from Crypto.PublicKey import RSA

def get_uuid():
    NODE_CONFIG = './AlysidaFile'
    with open(NODE_CONFIG) as data_file:
        config = json.load(data_file)
        data_file.close()
    return config['UUID']

def main():
    certs_path = "./crypt/my_certs/"
    pvt_cert_path = os.path.join(certs_path, 'rsa_key')
    pub_cert_path = os.path.join(certs_path, 'rsa_key.pub')

    if not os.path.exists(certs_path):
        os.makedirs(certs_path)
  
    secret_code = get_uuid()
    key = RSA.generate(2048)

    private_key = key.exportKey(passphrase=secret_code, pkcs=8)
    with open(pvt_cert_path, "wb") as private_f:
        private_f.write(private_key)
        private_f.close()

    public_key = key.publickey().exportKey()
    with open(pub_cert_path, "wb") as public_f:
        public_f.write(public_key)
        public_f.close()


if __name__ == "__main__":
    main()

