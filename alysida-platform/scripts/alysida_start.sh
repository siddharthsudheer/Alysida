#!/bin/bash

MY_UUID="$(./scripts/uuidgen.py)"

if [ ! $MY_UUID == "" ]; then
    NODE_CONFIG=$(cat ./AlysidaFile | sed -e s/MY_UUID/$MY_UUID/g)
    echo "$NODE_CONFIG" > './AlysidaFile'
fi


./scripts/cryptogen.py
gunicorn --config gunicorn.conf -b 0.0.0.0:4200 'app:start_alysida()' 
