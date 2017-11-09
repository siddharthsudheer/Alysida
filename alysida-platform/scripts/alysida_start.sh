#!/bin/bash

# MY_UUID="$(uuidgen)"

NODE_CONFIG="$(cat <<-EOF
{
  "UUID": "MY_UUID",
  "MY_PREFERENCES": "None Yet!",
  "CORE_PEER": "10.0.0.101",
  "PEER_ADDRESSES": []
}
EOF
)"

echo "$NODE_CONFIG" > './AlysidaFile'

gunicorn --config gunicorn.conf -b 0.0.0.0:4200 'app:start_alysida()'
