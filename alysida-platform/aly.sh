#!/bin/bash

##########################################################
################## FUNCTION DEFINITIONS ##################
##########################################################

GREEN='\033[0;32m'
LIGHTGREEN='\033[1;32m'
BLUE='\033[0;34m'
LIGHTBLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
ULINE='\033[4m'
BOLD='\033[1m'


# Print the usage message
function printHelp () {
  echo 
  echo -e "${BLUE}##########################################################${NC}"
  echo -e "${BLUE}######\t\t       ${GREEN}Alysída Help \t\t    ${BLUE}######${NC}"
  echo -e "${BLUE}##########################################################${NC}"
  echo
  echo -e "${BLUE}${ULINE}Usage:${NC}"
  echo "  aly.sh -m up | down | restart"
  echo "  aly.sh -h|--help (print this message)"
  echo "    -m <mode> followed by one of the commands below:"
  echo "      -> 'generate'  -  generate config and required "
  echo "                        files for first time node."
  echo "      -> 'up'        -  bring up the network with"
  echo "                        docker-compose up."
  echo "      -> 'down'      -  clear the network with"
  echo "                        docker-compose down."
  echo "      -> 'restart'   -  restart the network."
  echo "      -> 'cleanup'   -  remove images and containers."
  echo
  echo -e "${BLUE}${ULINE}Commands:${NC}"
  echo -e "${GREEN}  aly.sh -m generate${NC}"
  echo -e "${GREEN}  aly.sh -m up${NC}"
  echo -e "${GREEN}  aly.sh -m down${NC}"
  echo -e "${GREEN}  aly.sh -m restart${NC}"
  echo -e "${GREEN}  aly.sh -m cleanup${NC}"
  echo -e "${GREEN}  aly.sh -h ${NC}"
  echo -e "\n${BLUE}##########################################################${NC}"
  echo 
}

# Ask user for confirmation to proceed
function askProceed () {
  read -p "Continue (y/n)? " ans
  case "$ans" in
    y|Y|"" )
      echo -e "${GREEN}proceeding...${NC}"
      echo
    ;;
    n|N )
      echo -e "${GREEN}exiting...${NC}"
      echo
      exit 1
    ;;
    * )
      echo -e "${RED}invalid response${NC}"
      echo
      askProceed
    ;;
  esac
}


# Delete any images that were generated as a part of this setup
# specifically the following images are often left behind:
# TODO list generated image naming patterns
function removeUnwantedImages() {
  DOCKER_IMAGE_IDS=$(docker images | grep "alysida\|none" | awk '{print $3}')
  if [ -z "$DOCKER_IMAGE_IDS" -o "$DOCKER_IMAGE_IDS" == " " ]; then
    echo -e "----\t   No images available for deletion \t----"
  else
    docker rmi -f $DOCKER_IMAGE_IDS
  fi
}

# Obtain CONTAINER_IDS and remove them
# TODO Might want to make this optional - could clear other containers
function clearContainers () {
  CONTAINER_IDS=$(docker ps -aq)
  if [ -z "$CONTAINER_IDS" -o "$CONTAINER_IDS" == " " ]; then
    echo -e "----\t No containers available for deletion \t----"
  else
    docker rm -f $CONTAINER_IDS
  fi
}

# Ask user which node should be "Core Peer"
# That is, the first node on the network
CORE_PEER_IP=""
declare -a nodes
nodes=([1]="mynode.alysida.com" [2]="peer1.alysida.com" [3]="peer2.alysida.com" [4]="peer3.alysida.com")
node_ips=([1]="10.0.0.104" [2]="10.0.0.101" [3]="10.0.0.102" [4]="10.0.0.103")
function askCorePeer () {
    echo
    echo -e "${BLUE}----------------------------------------------------------${NC}"
    echo -e "${GREEN}  Please select one of the following nodes${NC}"
    echo -e "${GREEN}  to be the core node of the network.${NC}"
    echo -e "${LIGHTGREEN}  [Enter Corresponding Number]${NC}"
    echo -e "${BLUE}----------------------------------------------------------${NC}"

    COUNTER=1
    for node in "${nodes[@]}"
    do
        echo -e "  ${YELLOW}${COUNTER})  $node${NC}";
        let COUNTER+=1
    done

    echo -e "${BLUE}----------------------------------------------------------${NC}"
    
    read -e -p "  =>  Core Peer Selection:  " ans
    CORE_PEER_IP=${node_ips[ans]}
    CORE_PEER=${nodes[ans]}
    # echo $CORE_PEER
    if [ "$CORE_PEER" != "" ]; then
      echo -e "${GREEN}  =>  Selected Core Peer :  ${CORE_PEER}${NC}"
      echo -e "${GREEN}                            (${CORE_PEER_IP})${NC}"
      echo -e "${BLUE}----------------------------------------------------------${NC}"
    else 
      echo -e "${RED}  =>  Invalid selection. Try again.${NC}"
      echo -e "${BLUE}----------------------------------------------------------${NC}"
      echo
      askCorePeer
    fi
}

function createConfig () {
  NODE_CONFIG="$(cat <<-EOF
  {
    "UUID": "MY_UUID",
    "MY_PREFERENCES": "None Yet!",
    "CORE_PEER": "$CORE_PEER_IP",
    "PEER_ADDRESSES": []
  }
EOF
)"
  echo "$NODE_CONFIG" > './AlysidaFile'
}

function generator () {
  askCorePeer
  createConfig
  echo
}

# Removing containers, images, etc
function cleanUp () {
    #Cleanup the chaincode containers
    clearContainers
    #Cleanup images
    removeUnwantedImages
    echo 
}
function printAccessUrls () {
    echo -e "${BLUE}----------------------------------------------------------${NC}"
    echo -e "${GREEN}  ${BOLD}Access URLs:${NC}"
    echo -e "${BLUE}----------------------------------------------------------${NC}"
    COUNTER=1
    for node in "${nodes[@]}"
    do
        portNum=$((4200+$COUNTER-1))
        echo -e "  ${YELLOW}${COUNTER}) $node\t=>   ${GREEN}http://localhost:$portNum/ ${NC}";
        let COUNTER+=1
    done
    echo -e "${BLUE}----------------------------------------------------------${NC}\n"
}

# Start the network.
function networkUp () {
  # Run Generator if artifacts are missing
  if [ ! -f ./AlysidaFile ]; then
    generator
  fi

  docker-compose -f $COMPOSE_FILE up -d
  if [ $? -ne 0 ]; then
    echo -e "${RED}!!!!\t ERROR: Unable to start network     !!!!${NC}"
    docker logs -f mynode.alysida.com
    exit 1
  fi

  printAccessUrls

  # To see what's running on cli
  docker logs -f mynode.alysida.com
}

# Tear down running network
function networkDown () {
  docker-compose -f $COMPOSE_FILE stop
  docker-compose -f $COMPOSE_FILE kill && docker-compose -f $COMPOSE_FILE down
}


##########################################################
############### BEGIN EXECUTION OF PROGRAM ###############
##########################################################
clear
COMPOSE_FILE=docker-compose.yml
printf "\e]0;Alysída\007" # Set Session Name

# Parse commandline args
while getopts "h?m:" opt; do
  case "$opt" in
    h|\?)
      printHelp
      exit 0
    ;;
    m)  MODE=$OPTARG
    ;;
  esac
done

# Determine whether starting, stopping, restarting or generating for announce
if [ "$MODE" == "generate" ]; then
  EXPMODE=" Welcome to"
elif [ "$MODE" == "up" ]; then
  EXPMODE="   Starting"
elif [ "$MODE" == "down" ]; then
  EXPMODE="   Stopping"
elif [ "$MODE" == "restart" ]; then
  EXPMODE=" Restarting"
elif [ "$MODE" == "cleanup" ]; then
  EXPMODE="   Cleaning"
else
  printHelp
  exit 1
fi

# Announce what was requested
echo 
echo -e "${BLUE}##########################################################${NC}"
echo -e "${BLUE}####\t\t  ${GREEN}${EXPMODE} Alysída   \t     ${BLUE}#####${NC}"
echo -e "${BLUE}##########################################################${NC}"
echo

# ask for confirmation to proceed
if [ "${MODE}" != "generate" ]; then
  askProceed
fi

#Create the network using docker compose
if [ "${MODE}" == "generate" ]; then
  generator
elif [ "${MODE}" == "up" ]; then
  networkUp
elif [ "${MODE}" == "down" ]; then ## Clear the network
  networkDown
elif [ "${MODE}" == "restart" ]; then ## Restart the network
  networkDown
  cleanUp
  networkUp
elif [ "${MODE}" == "cleanup" ]; then ## Restart the network
  cleanUp
else
  printHelp
  exit 1
fi

