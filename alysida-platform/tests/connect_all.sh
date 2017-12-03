#!/bin/bash

http http://localhost:4200/register-me
http http://localhost:4202/register-me
http http://localhost:4203/register-me

# 4201 Accepts all the other 3
echo '{"ips": ["10.0.0.102","10.0.0.103","10.0.0.104"]}' | http POST http://localhost:4201/accept-new-registration

http http://localhost:4200/register-me
echo '{"ips": ["10.0.0.102","10.0.0.103","10.0.0.104"]}' | http POST http://localhost:4201/accept-new-registration