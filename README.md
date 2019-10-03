# Voncoin
Voncoin is a simple blockchain system, written in Python. Voncoin is the name of the coin used in this system.

## Getting started
### Prerequisites
In order to install Voncoin you will need [Python3.6](https://www.python.org/downloads/) and the following packages installed with pip3
```
pip3 install flask flask-cors requests pycrypto 
```


### Installation
First you have to run the backend server on each node (or on the same node using different ports)
```
python3 rest.py -p=PORT -n=NODES
```
* PORT is port number for api to listen to (default 5000)
* NODES is the number of nodes that will be used in the network (default 5)
After all backend services are up and running you will need to start a simple cli program that will be used to control the backend RESTful API
```
python3 client.py -p=PORT -ip=IP -b=1
```
* PORT is the port number of each node's **own** API
* IP is the IP of the bootstrap node (default 10.0.2.4:5000)
* -b=1 is a flag indicating a node as bootstrap (default value 0). NOTE: Only **one** node can be set as bootstrap in a network at a time

Bootstrap node starts with 500 coins (genesis block) and each time a new node enters the network it recieves 100 coins. 
Also each node is assinged an id (bootstrap has id=0, first node to connect has id=1 etc.)

*This is hardcoded for now meaning maximum number of nodes can be 5. To be updated*

## Testing the blockchain
##### Important note: Before making any transactions all nodes must be connected to the network
Each node is controlled via the cli program client.py. There are 3 available commands for now
* **t id[#id] [amount]** Send [amount] of coins to node number [#id] Ex: ``` t id0 10 ```
* **balance** Show node's balance
* **view** Show transactions in the last block of the blockchain
