#!/bin/bash

echo '{"sender": "admin", "receiver": "Sidd", "amount": "100"}' | http POST http://localhost:4200/add-new-transaction
echo '{"sender": "Sidd", "receiver": "Isit", "amount": "50"}' | http POST http://localhost:4200/add-new-transaction

http http://localhost:4200/get-unconfirmed-transactions

