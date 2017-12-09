#!/bin/bash

http http://localhost:4200/register-me
http http://localhost:4202/register-me
http http://localhost:4203/register-me

echo '{"ips": ["10.0.0.102","10.0.0.103","10.0.0.104"]}' | http POST http://localhost:4201/accept-new-registration


http http://localhost:4201/get-peer-addresses
http http://localhost:4200/get-peer-addresses

http http://localhost:4200/discover-peer-addresses
http http://localhost:4200/get-peer-addresses

