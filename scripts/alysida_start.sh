#!/bin/bash

alysida_mynohup() {
    [[ "$1" = "" ]] && echo "usage: mynohup script_file" && return 0
    nohup "$1.py" >"$1.out" 2>&1 < /dev/null &
    echo $'\n======================================='
    echo $'  Process '$1' has started.'
    echo $'=======================================\n'
}

alysida_mykill() {
    ps -ef | grep "$1" | grep -v grep | awk '{print $2}' | xargs kill
    echo $'\n======================================='
    echo $'  Process '$1' has been killed.'
    echo $'=======================================\n'
}



start() {
    alysida_mynohup ./webapp2/run.py
}

stop() {
    alysida_mykill ./webapp2/run.py
    PIDS=( $(lsof -i -P -n | grep ':5200' | grep -v grep | awk '{print $2}') )
    echo ${PIDS}
    if [ ${#PIDS[@]} -gt 0 ]; then
        for pid in "${PIDS[@]}"
        do 
            kill -9 $pid
        done
    fi
}

prod() {
    alysida_mynohup ./webapp/run
}

${1}


MY_UUID="$(./scripts/uuidgen.py)"

if [ ! $MY_UUID == "" ]; then
    NODE_CONFIG=$(cat ./AlysidaFile | sed -e s/MY_UUID/$MY_UUID/g)
    echo "$NODE_CONFIG" > './AlysidaFile'
fi


./scripts/cryptogen.py
./scripts/db_setup.py
gunicorn --config gunicorn.conf -b 0.0.0.0:4200 'app:start_alysida()' 
