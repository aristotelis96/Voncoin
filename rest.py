import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import _thread
import threading

import time
import block
import blockchain as blockchainModule
import wallet
import transaction
import tools
import node as NodeModule


app = Flask(__name__)
CORS(app)
#Initialize global node object

blockchain = blockchainModule.Blockchain()
#lock to handle each request seperately
glock = _thread.allocate_lock()
#transaction lock
txLock = _thread.allocate_lock()

# Testing endpoint
@app.route('/test', methods=['GET'])
def test():
        global node
        return json.dumps(node.nodeTransactions)

#endpoint to return wallet balance
@app.route('/wallet_balance', methods=['GET'])
def wallet_balance():
        global node
        amount = node.wallet_balance
        return json.dumps({"wallet_balance": amount}), 200

#endpoint to return current chain without consensus
@app.route('/currentchain', methods=['GET'])
def currentchain():        
        global node
        chain_data = [blk.__dict__ for blk in node.chain.chain]
        return json.dumps({"length": len(chain_data), "chain": chain_data, "_datapeers": (node.peers)})

#endpoint to create a new transaction
@app.route('/create_new_transaction', methods=['POST'])
def create_new_transaction():
    try:
        txLock.acquire()
        tx_data = request.get_json()
        required_fields = ["sender_ip", "receiver_ip", "amount"]
        for field in required_fields:              
                if not tx_data.get(field):
                        return "Invalid transaction data", 403
        global node
        node.create_transaction(tx_data["sender_ip"], tx_data["receiver_ip"], tx_data["amount"])        
    finally:
        txLock.release()
    return "Success", 201

#endpoint to add a transaction someone else created
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
        global txLock, node
        txLock.acquire()
        tx_data = request.get_json()
        required_fields = ["sender_address", "receiver_address",
                           "amount", "transaction_id", "txInput", "signature"]
        for field in required_fields:
                if not tx_data.get(field):
                        print(field)
                        return "Invalid transaction data", 403

        if not node.receive_transaction(tx_data):
                return "Invalid transaction", 400
        txLock.release()
        return "Success", 201

# Return blockchain after consensus
@app.route('/chain', methods=['GET'])
def get_chain():        
        global node                
        node.valid_chain()                
        chain_data = [blk.__dict__ for blk in node.chain.chain]        
        return json.dumps({"length": len(chain_data), "chain": chain_data, "wallets": node.wallets})

# Get unmined transcation
@app.route('/pending_tx')
def pending_tx():
        global node
        return json.dumps(node.chain.unconfirmed_transactions)

#this is called only from bootstrap. registers new node and broadcasts to everyone
@app.route('/register_node', methods=['POST'])
def register_new_peers():
        node_address = request.get_json()["node_address"]
        key = request.get_json()["public_key"]
        global node
        node.register_node(node_address, key)
        return get_chain()

#endPoint to register this node with someone else (e.x. bootstrap)
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
        bootstrap_address = request.get_json()["bootstrap_address"]
        global node
        return node.register_to_ring(bootstrap_address)  

# Endpoint to add peers
@app.route('/add_peers', methods=['POST'])
def add_peers():
        try:
                glock.acquire()
                global node
                node.peers.update(request.get_json()["peers"])
                node.id_ip.update(request.get_json()["id_ip"])
                return "Updated peers", 200
        finally:
                glock.release()

#endPoint to get ids
@app.route('/get_id_ip', methods=['GET'])
def get_id_ip():
        global node
        return jsonify({"id_ip": node.id_ip}), 200

#Route to add a block someone else mined
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():    
    global node
    data = request.get_json()
    block_data = data["block"]
    proof = data["proof"]
    index = block_data["index"]
    previous_hash = block_data["previous_hash"]
    transactions = block_data["transactions"]
    timestamp = block_data["timestamp"]
    nonce = block_data["nonce"]    
    node.add_block(index, previous_hash, transactions, timestamp, nonce, proof)
    return "block added to chain", 200


# Route to mine a block that someone else needs
@app.route('/mine_a_block', methods=['POST'])
def mine_a_block():
        newBlock = request.get_json()
        # Start a thread to help mining and return api call
        global node
        thread = threading.Thread(target=node.validate_and_mine, args=(newBlock,))
        thread.start()
        return "Success", 200

# get last block transactions from the blockchain
@app.route('/view_transactions', methods=['GET'])
def get_transactions():
        global node
        lastBlock = node.chain.last_block
        response = {'transactions': lastBlock.transactions}
        return jsonify(response), 200


# run it once fore every node
if __name__ == '__main__':
    from argparse import ArgumentParser
    import socket
    #Initialize Node object
    parser = ArgumentParser()
    # Get Port to listen to
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    #Get own address
    myAddress = "http://" + tools.get_ip() + ":" + str(port) + "/"
    global node
    node = NodeModule.node(myAddress)            
    node.create_initial_transaction(node.address, 500)    
    app.run(host='0.0.0.0', port=port)
