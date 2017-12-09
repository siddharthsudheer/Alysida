#!/bin/bash

echo '{"sender": "admin", "receiver": "Sidd", "amount": "100"}' | http POST http://localhost:4201/add-new-transaction
# echo '{"sender": "Sidd", "receiver": "Isit", "amount": "50"}' | http POST http://localhost:4200/add-new-transaction
# echo '{"sender": "Isit", "receiver": "John", "amount": "25"}' | http POST http://localhost:4200/add-new-transaction
# echo '{"sender": "John", "receiver": "Atit", "amount": "5"}' | http POST http://localhost:4200/add-new-transaction
# echo '{"sender": "Philip", "receiver": "Sidd", "amount": "45"}' | http POST http://localhost:4200/add-new-transaction
# echo '{"sender": "Sidd", "receiver": "Mary", "amount": "60"}' | http POST http://localhost:4200/add-new-transaction
# echo '{"sender": "Mary", "receiver": "Atit", "amount": "89"}' | http POST http://localhost:4200/add-new-transaction
