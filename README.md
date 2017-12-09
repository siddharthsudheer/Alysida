Alysída
=========================== 

A blockchain starter-kit for application developers

## About
Author: Siddharth Sudheer

Email: siddharthsudheer@gmail.com

Alysída is the Greek word for Chain.

It is pronounced: *elli-see-da*

## Running the App

Pre-requisite: 
* Docker Daemon Running
* Ports `4200, 4201, 4202, 4203, 5200, 5201, 5202, 5203` available.

To start network up: `./alys -m up`

Then, you can visit the UI's each of the nodes at:

`http://localhost:5200/`
`http://localhost:5201/`
`http://localhost:5202/`
`http://localhost:5203/`

The Alysída endpoints that each of the above nodes access are:

`http://localhost:4200/`
`http://localhost:4201/`
`http://localhost:4202/`
`http://localhost:4203/`

To stop the network: `./alys -m down`
To cleanup the docker containers on network: `./alys -m cleanup`