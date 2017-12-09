#!/bin/bash


## CREATE NETWORK 
# docker network create --driver bridge --subnet 10.0.0.1/24 alysida-bridge




declare -a nodes=("1" "2" "3" "4")

## DELETES
for i in "${nodes[@]}"
do
    docker stop a$i
    docker network disconnect alysida-bridge a$i
    docker rm a$i
done
# docker network rm alysida-bridge





# ## BUILD 

# docker build -t alysida .




# # RUN
# for i in "${nodes[@]}"
# do
#     ip=$(($i+1))
#     if [ $i = 1 ]; then
#         docker run -idt -p 4200:4200 --name a$i --network alysida-bridge --ip 10.0.0.$ip alysida /bin/bash
#     else
#         docker run -idt --name a$i --network alysida-bridge --ip 10.0.0.$ip alysida /bin/bash
#     fi
# done

# for i in "${nodes[@]}"
# do
#     docker exec -d a$i /bin/bash -c "nohup gunicorn -c gunicorn.conf -b 0.0.0.0:4200 'app:start_alysida()'</dev/null >./output/alysida.out 2>&1 & tail -f alysida.out" sleep 1d
#     # YOu can now do "docker attach a1"
# done



## OTHER
# docker network inspect alysida-bridge
# docker exec -it a1 /bin/bash