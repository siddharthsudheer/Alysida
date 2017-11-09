#!/bin/bash

##########################################################
################## FUNCTION DEFINITIONS ##################
##########################################################

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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
  echo "      -> 'up'      -  bring up the network with"
  echo "                      docker-compose up."
  echo "      -> 'down'    -  clear the network with"
  echo "                      docker-compose down."
  echo "      -> 'restart' -  restart the network."
  echo "      -> 'cleanup' -  remove images and containers."
  echo
  echo -e "${BLUE}${ULINE}Commands:${NC}"
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

# Removing containers, images, etc
function cleanUp () {
    #Cleanup the chaincode containers
    clearContainers
    #Cleanup images
    removeUnwantedImages
    echo 
}

# Start the network.
function networkUp () {
  docker-compose -f $COMPOSE_FILE up -d
  if [ $? -ne 0 ]; then
    echo -e "${RED}!!!!\t ERROR: Unable to start network     !!!!${NC}"
    docker logs -f cli
    exit 1
  fi
  # To see what's running on cli
  docker logs -f cli
}

# Tear down running network
function networkDown () {
  docker-compose -f $COMPOSE_FILE stop
  docker-compose -f $COMPOSE_FILE kill && docker-compose -f $COMPOSE_FILE down
}


##########################################################
############### BEGIN EXECUTION OF PROGRAM ###############
##########################################################

COMPOSE_FILE=docker-compose.yml

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
if [ "$MODE" == "up" ]; then
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
askProceed

#Create the network using docker compose
if [ "${MODE}" == "up" ]; then
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

