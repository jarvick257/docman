#!/bin/bash

if [[ -z $DOCMAN_NO_DB ]]; then
    docker-entrypoint.sh mongod > /dev/null & disown
    echo $! > /usr/src/app/mongo.pid
fi

python3 main.py
kill $(cat /usr/src/app/mongo.pid) || true
