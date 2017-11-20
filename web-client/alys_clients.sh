#!/bin/bash

##########################################################
################## FUNCTION DEFINITIONS ##################
##########################################################

BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PINK='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'

NC='\033[0m' # No Color
ULINE='\033[4m'
BOLD='\033[1m'

function colorHelp () {
  echo -e "\n\n${ULINE}Text Colors and Variants:${NC}\n"
  color_start=30;
  while [ $color_start -le 37 ]; do
      variant=0;
      final=""
      while [ $variant -le 4 ]; do
        color="\033[${variant};${color_start}m"
        color_var="$variant;$color_start | ${color}hello world${NC}\t"
        final+="$color_var"
        ((variant++));
      done
      echo -e "$final"
      ((color_start++));
  done

  echo -e "\n\n${ULINE}Background Colors (works with 1-4 variants as above):${NC}\n"
  bg_color_start=40;
  while [ $bg_color_start -le 47 ]; do
      color="\033[0;${bg_color_start}m"
      echo -e "0;$bg_color_start | ${color}hello world${NC}\t"
      ((bg_color_start++));
  done
  echo
}

# Print the usage message
function printHelp () {
  echo 
  echo -e "${BLUE}#####################################################################${NC}"
  echo -e "${BLUE}#########\t\t${GREEN}Alysída Web-Client Help \t    ${BLUE}#########${NC}"
  echo -e "${BLUE}#####################################################################${NC}"
  echo
  echo -e "${BLUE}${ULINE}Usage:${NC}"
  echo "  aly_clients.sh -m up | down | restart"
  echo "  aly_clients.sh -h|--help (print this message)"
  echo "    -m <mode> followed by one of the commands below:"
  echo "      -> 'up'        -  start all the web-clients for"
  echo "                        for Alysída test network"
  echo "      -> 'down'      -  stop all the web-clients for"
  echo "                        the Alysída test network"
  echo "      -> 'restart'   -  restart all the web-clients."
  echo
  echo -e "${BLUE}${ULINE}Commands:${NC}"
  echo -e "${GREEN}  aly_clients.sh -m up${NC}"
  echo -e "${GREEN}  aly_clients.sh -m down${NC}"
  echo -e "${GREEN}  aly_clients.sh -m restart${NC}"
  echo -e "${GREEN}  aly_clients.sh -h ${NC}"
  echo -e "${BLUE}#####################################################################${NC}"
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

# Node Address Definitions
declare -a nodes
nodes=([1]="mynode;10.0.0.104;4200" [2]="peer1;10.0.0.101;4201" [3]="peer2;10.0.0.102;4202" [4]="peer3;10.0.0.103;4203")

ARCH=`uname -s | grep Darwin`
if [ "$ARCH" == "Darwin" ]; then
  SED_OPTS='-E'
else 
  SED_OPTS='-r'
fi;

function printAccessUrls () {
    echo -e "${BLUE}=====================================================================${NC}"
    echo -e "${GREEN}  ${BOLD}Web-Client Access URLs:${NC}"
    echo -e "${BLUE}=====================================================================${NC}\n"
    echo -e " \t ${LIGHTBLUE}Alysída${LIGHTBLUE}\t\t\t Web-Client${NC}";

    for node in "${nodes[@]}"
    do
        arr=(${node//;/ })
        peer_name="${arr[0]}.alysida.com"
        peer_ip="${arr[1]}"
        peer_access_url="http://localhost:${arr[2]}/"
        web_client_url=( $(echo $peer_access_url | sed $SED_OPTS 's|420|520|'	) )
        echo -e " ${GREEN}+------------------------+${NC}";
        echo -e " ${GREEN}|${BLUE} $peer_access_url ${GREEN}|${NC}       ${YELLOW}+------------------------+${NC}";
        echo -e " ${GREEN}|${BLUE} $peer_name  \t  ${GREEN}|  ${YELLOW}<==  | $web_client_url |${NC}";
        echo -e " ${GREEN}|${BLUE} ($peer_ip)           ${GREEN}|       ${YELLOW}+------------------------+${NC}";
        echo -e " ${GREEN}+------------------------+${NC}";
    done
    echo
    echo -e "${BLUE}=====================================================================${NC}\n"
}

function checkPortAvailability() {
    BASIC_LSOF=( $(lsof -i -P -n | grep ':520[0-3]' | grep -v grep | awk '{print $1}') )
    if [ ${#BASIC_LSOF[@]} -gt 0 ]; then
      echo -e "${RED}UNAVAILABLE.${NC}"
      echo -e "  Unable to start Web-Clients because of unavailable port(s)."
      echo -e "  [Required ports: 5200, 5201, 5202, 5203]\n"
      exit 1
    else
      echo -e "${GREEN}AVAILABLE.${NC}"
    fi
}

function checkAlysidaNetwork () {
  DOCKER_PORTS="$(docker ps | grep "alysida" | sed 's/.*0.0.0.0://g'| sed 's/->.*//g' | sort)"
  PORTS="$(echo ${nodes[@]} | tr ' ' '\n' | sed 's/^.*;//g' | sort )"
  
  if [ "$PORTS" != "$DOCKER_PORTS" ]; then
      echo -e "${RED}INACTIVE.${NC}"
      echo -e "  Please make sure you are running the Alysída test network."
      exit 1
  else
    echo -e "${GREEN}ACTIVE.${NC}"
  fi
}

# Start all clients.
function clientsUp () {
    echo -ne "${YELLOW}Building alysidaClient${NC}\t\t"
    go build -o alysidaClient .
    echo -e "${GREEN}DONE.${NC}"

    echo -ne "${YELLOW}Checking Alysída Test Network${NC}\t" 
    checkAlysidaNetwork

    echo -ne "${YELLOW}Web-Client Ports Required${NC}\t" 
    checkPortAvailability

    mkdir tmp-logs

    echo -e "\n${BLUE}---------------------------------------------------------------------${NC}"
    for node in "${nodes[@]}"
    do
        arr=(${node//;/ })
        alysida_port=${arr[2]}
        client_port=( $(echo $alysida_port | sed $SED_OPTS 's|420|520|'	) )
        logfile_name="${arr[0]}-localhost-${client_port}.log"

        client_cmd="./alysidaClient --alysida-port=${alysida_port} --client-port=${client_port}"

        nohup $client_cmd > "./tmp-logs/${logfile_name}" 2>&1 < /dev/null &
        sleep 0.5
        CHECKER="$(lsof -i -P -n | grep ":${client_port}" | grep -v grep | awk '{print $1}')"
        if [ "$CHECKER" == "alysidaCl" ]; then
          STATUS_COLOR1=${CYAN}
          STATUS_COLOR2=${GREEN}
          STATUS="Started"
        else
          STATUS_COLOR1=${PINK}
          STATUS_COLOR2=${RED}
          STATUS="Failed "
        fi

        client_cmd_print="${STATUS_COLOR1}./alysidaClient --alysida-port=${YELLOW}${alysida_port} ${STATUS_COLOR1}--client-port=${YELLOW}${client_port}${NC}"
        echo -e "${YELLOW}=> ${STATUS_COLOR2}${STATUS}: ${client_cmd_print}\n   ${STATUS_COLOR2}Logfile: ${STATUS_COLOR1}${logfile_name}${NC}"
    done
    echo -e "${BLUE}---------------------------------------------------------------------${NC}\n"
}

# Stop all clients.
function clientsDown () {
    echo -ne "${YELLOW}Stopping all processes${NC}\t\t"
    ps -ef | grep "alysidaClient" | grep -v grep | awk '{print $2}' | xargs kill
    echo -e "${GREEN}SUCCESS.${NC}"

    echo -ne "${YELLOW}Deleting log files${NC}\t\t"
    rm -rf tmp-logs
    echo -e "${GREEN}SUCCESS.${NC}"
    echo
}

##########################################################
############### BEGIN EXECUTION OF PROGRAM ###############
##########################################################
printf "\e]0;Alysída: Web-Clients\007" # Set Session Name
clear

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
else
  printHelp
  exit 1
fi

# Announce what was requested
echo 
echo -e "${BLUE}#####################################################################${NC}"
echo -e "${BLUE}#########\t ${GREEN}${EXPMODE} Alysída Web Clients  \t    ${BLUE}#########${NC}"
echo -e "${BLUE}#####################################################################${NC}"
echo

# ask for confirmation to proceed
if [ "${MODE}" != "generate" ]; then
  askProceed
fi

#Create the network's web clients
if [ "${MODE}" == "up" ]; then
  clientsUp
  printAccessUrls
elif [ "${MODE}" == "down" ]; then ## Clear the network
  clientsDown
elif [ "${MODE}" == "restart" ]; then ## Restart the network
  clientsDown
  clientsUp
  printAccessUrls
else
  printHelp
  exit 1
fi