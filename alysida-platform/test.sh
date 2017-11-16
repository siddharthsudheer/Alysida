#!/bin/bash
MY_UUID="$(uuidgen)"

if [ ! $MY_UUID == "" ]; then
    NODE_CONFIG=$(cat ./AlysidaFile | sed -e s/MY_UUID/$MY_UUID/g)
    echo "$NODE_CONFIG" > './AlysidaFile'
fi