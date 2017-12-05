#!/bin/bash

echo '{"sender": "admin", "receiver": "Sidd", "amount": "100"}' | http POST http://localhost:4200/add-new-transaction
echo '{"sender": "Sidd", "receiver": "Isit", "amount": "50"}' | http POST http://localhost:4200/add-new-transaction
echo '{"sender": "Isit", "receiver": "Atit", "amount": "25"}' | http POST http://localhost:4200/add-new-transaction

# http http://localhost:4200/get-unconfirmed-transactions

# INSERT INTO main_chain (BLOCK_NUM, BLOCK_HASH, NONCE, TIME_STAMP) VALUES (NULL, '8948a85b150df79fc981a3aa653ce1c7ad25a006043295413eda21006cd8d56e', 2, '2017-12-05 04:13:25');
# INSERT INTO main_chain (BLOCK_NUM, BLOCK_HASH, NONCE, TIME_STAMP) VALUES (NULL, 'Z948a85b150df7ddfc981a3aa653ce1c7ad25a006043295413eda21006cd8d56Z', 2, '2017-13-05 10:40:25');
# INSERT INTO confirmed_txns (BLOCK_HASH, TXN_HASH, sender, receiver, amount, TXN_TIME_STAMP) VALUES ('8948a85b150df79fc981a3aa653ce1c7ad25a006043295413eda21006cd8d56e', 'Za5ef2b9c98ee2daba62eda035d22c75000135e10f024bf89f8e314721ec37cZ', 'Isit', 'Atit', 25, '2017-12-05 06:30:25');