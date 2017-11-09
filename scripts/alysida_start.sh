#!/bin/bash

cd /alysida
gunicorn --config gunicorn.conf -b 0.0.0.0:4200 'app:start_alysida()'
