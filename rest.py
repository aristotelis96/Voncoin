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

### JUST A BASIC EXAMPLE OF A REST API WITH FLASK

""" 
Ksekinas to programma me ~python3 rest.py (PANTA ston 10.0.0.1 (bootstrap)
oi alloi sundeoontai me tin entoli:

curl --header "Content-Type: application/json" --request POST --data '{"node_address": "10.0.0.1:5000"}' MY_IP:5000/register_with

oustiastika post request me dedomena node_address=bootstrap_ip:bootstrap_port sto endpoint /register_with (o kathe komvos sto diko tou api)
otan kapoios kanei register_with stelnei ston bootstrap tin IP kai PORT tou wste na ksereis o bootstrap poios einai (pros to parwn den enimeronei tous allous oti mpike kapoios). O bootstrap epeita epistrefei se auton pou mpike ti lista me tous allous komvous kathws kai to megisto chain ekeini ti stigmi.
----
meta o mporoume na valoume ena transaction (leipei oli i class transaction, pros to parwn apla einai random json data)

kanoume mine ws eksis : o kathenas kanei request GET sto api tou sto endpoing /mine opote thelei na kanei mining. otan teleiosei frontizei na enimerosei
olous tous komvous tou diktuou gia to block pou vrike kai oli to prosthetoun sto blockchain tous. opote oloi enimeronontai. Tha thelame na prosthesoume:
        -- epeidi ta transactions ginontai broadcasted kai epeidi profanws dn exoume apolies, oloi lamvanoun tautoxrona ta transactions
        -- ara logika tha ksekinisoun oloi tautoxrona to mining, tha to kanoun oloi broadcast to block otan to vroun ara den exei poly noima to olo thema..
        -- OPOTE: isws valoume thread na kanei mine, kai ena allo thread na koitaei an kapoios vrike kapoio block (???)

uparxei diafora sto endpoint /chain me /currentchain. H /currentchain epistrefei to chain pou exei o node. H /chain elegxei prota me consensus oti exei 
ti megaliteri chain kai meta tin epistrefei


"""

app = Flask(__name__)
CORS(app)
#Initialize global node object

blockchain = blockchainModule.Blockchain()
#lock to handle each request seperately
glock = _thread.allocate_lock()
#transaction lock
txLock = _thread.allocate_lock()
# Nodes address
# myAddress = ""
#global variable wallet
# myWallet = 0

#Dictionary for peers (Routing Table)
# peers = {}
#peers.update({"http://10.0.0.1:5000/": ""})

# UTXOs for each wallet (Locally)
# wallets = {}

#Ids counter
idCounter = 0
# id_ip = {}

#Create new blockchain from dump data (json data)

@app.route('/test', methods=['GET'])
def test():
        global node
        return json.dumps(node.nodeTransactions)
# def create_chain_from_dump(chain_dump):
#     global blockchain
#     newblockchain = blockchainModule.Blockchain()
#     for idx, block_data in enumerate(chain_dump):
#         newblock = block.Block(block_data["index"],
#                                block_data["previous_hash"],
#                                block_data["transactions"])
#         newblock.timestamp = block_data["timestamp"]
#         proof = block_data['hash']
#         if idx > 0:
#             newblock.nonce = block_data["nonce"]
#             added = newblockchain.add_block(newblock, proof)
#             if not added:
#                 raise Exception("The chain dump is tampered!!")
#         else:  # else the block is a genesis block, no verification needed
#             newblock.hash = proof
#             newblockchain.chain.append(newblock)
#     newblockchain.unconfirmed_transactions = blockchain.unconfirmed_transactions
#     return newblockchain

# Broadcast transaction Function


# class broadcast_transaction (threading.Thread):
#     def __init__(self, tx, peer):
#         threading.Thread.__init__(self)
#         self.tx = tx
#         self.peer = peer

#     def run(self):
#         url = self.peer + "new_transaction"
#         headers = {'Content-Type': "application/json"}
#         data = json.dumps(self.tx.to_dict())
#         requests.post(url, data=data, headers=headers)

#.......................................................................................

#endpoint to return wallet balance
@app.route('/wallet_balance', methods=['GET'])
def wallet_balance():
        global node
        ammount = node.wallet_balance
        return json.dumps({"wallet_balance": ammount}), 200

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
        required_fields = ["sender_ip", "receiver_ip", "ammount"]
        for field in required_fields:              
                if not tx_data.get(field):
                        return "Invalid transaction data", 403
        global node
        node.create_transaction(tx_data["sender_ip"], tx_data["receiver_ip"], tx_data["ammount"])
        # if(tx_data["sender_ip"] != myWallet.myAddress):
        #         return "Wrong sender IP", 405
        # #get inputs from UTXO pool until ammount is reached
        # NBCtotal = 0
        # UTXOs = wallets.get(tx_data.get("sender_ip"))
        # NewUTXOs = UTXOs
        # inputs = []
        # while NBCtotal < tx_data.get("ammount"):
        #         for txInput in UTXOs:
        #                 NBCtotal += txInput.get("ammount")
        #                 inputs.append(txInput)
        #                 NewUTXOs.remove(txInput)
        # #find key of recipient
        # recipient_key = ""
        # for (key, ip) in peers.items():
        #         if ip == tx_data.get("receiver_ip"):
        #                 recipient_key = key
        #                 break
        # newTx = transaction.Transaction(myWallet.publickey.decode(
        #     'utf-8'), recipient_key, tx_data.get("ammount"), inputs)
        # newTx.sign_transaction(myWallet.privatekey)
        # #broadcast TX
        # for peer in [p for (_, p) in peers.items() if p != myWallet.myAddress]:
        #     thread = broadcast_transaction(newTx, peer)
        #     thread.start()
        # output = []
        # output.append({"id": 0, "transaction_id": newTx.transaction_id, "ammount": tx_data.get(
        #     "ammount"), "recipient_address": recipient_key})
        # wallets[tx_data.get("receiver_ip")].append(output[0])
        # change = NBCtotal - tx_data.get("ammount")
        # if(change > 0):
        #         output.append({"id": 1, "transaction_id": newTx.transaction_id, "ammount": NBCtotal -
        #                        tx_data.get("ammount"), "recipient_address": myWallet.publickey.decode('utf-8')})
        #         wallets[tx_data.get("sender_ip")].append(output[1])
        # newTx.transaction_outputs = output
        # while not blockchain.add_new_transaction(newTx.to_dict()):
        #         mine_unconfirmed_transactions()
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
                           "ammount", "transaction_id", "txInput", "signature"]
        for field in required_fields:
                if not tx_data.get(field):
                        print(field)
                        return "Invalid transaction data", 403

        if not node.receive_transaction(tx_data):
                return "Invalid transaction", 400
        txLock.release()
        return "Success", 201
        # tx_data = request.get_json()
        # required_fields = ["sender_address", "receiver_address",
        #                    "ammount", "transaction_id", "txInput", "signature"]
        # for field in required_fields:
        #         if not tx_data.get(field):
        #                 print(field)
        #                 return "Invalid transaction data", 403
        # #verify signature
        # if not transaction.verify_signature(tx_data):
        #         print("failed to verify signature in /new_transaction")
        #         txLock.release()
        #         return "Invalid signature", 403
        # # validate Inputs are UTXOs
        # inputs = tx_data.get("txInput")
        # # get ip for sender_address
        # ip = peers.get(tx_data.get("sender_address"))
        # #get UTXOs for this ip
        # UTXOs = wallets.get(ip)
        # for txInput in inputs:
        #         if not any(inp["transaction_id"] == txInput["transaction_id"] for inp in UTXOs):
        #                 print("Invalid inputs in /new_transaction")
        #                 return "Invalid transaction, invalid input", 403
        # #remove these inputs and find total NBC ammount used
        # NBCused = 0
        # for txInput in inputs:
        #         tbremoved = (
        #             next(inp for inp in UTXOs if inp["transaction_id"] == txInput["transaction_id"]))
        #         #check if sender is authorized for this transaction
        #         if not tbremoved["recipient_address"] == tx_data["sender_address"]:
        #                 print("Transaction is using wrong inputs, discarding")
        #                 return "Invalid Transaction, wrong inputs", 405
        #         NBCused += tbremoved.get("ammount")
        #         wallets.get(ip).remove(tbremoved)
        # output = []
        # output.append({"id": 0, "transaction_id": tx_data.get("transaction_id"), "ammount": tx_data.get(
        #     "ammount"), "recipient_address": tx_data.get("receiver_address")})
        # recv_ip = peers.get(tx_data.get("receiver_address"))
        # if not wallets.get(recv_ip):
        #         wallets[recv_ip] = []
        # wallets[recv_ip].append(output[0])
        # change = NBCused - tx_data.get("ammount")
        # if(change > 0):
        #         output.append({"id": 1, "transaction_id": tx_data.get("transaction_id"), "ammount": NBCused -
        #                        tx_data.get("ammount"), "recipient_address": tx_data.get("sender_address")})
        #         wallets[ip].append(output[1])
        # tx_data["txOutput"] = output
        # print("/new_transaction adding ammount: ",
        #       tx_data.get('ammount'), " from ", ip, " to: ", recv_ip)
        # while not blockchain.add_new_transaction(tx_data):
        #         mine_unconfirmed_transactions()


@app.route('/chain', methods=['GET'])
def get_chain():
        #glock.acquire()
        global node                
        node.valid_chain()                
        chain_data = [blk.__dict__ for blk in node.chain.chain]
        #glock.release()
        return json.dumps({"length": len(chain_data), "chain": chain_data, "wallets": node.wallets})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
        glock.acquire()
        global node
        resultIndex = node.mine_unconfirmed_transactions()
        if resultIndex == -1:
                glock.release()
                return "No capacity reached"
        # result = blockchain.mine()  # melontika: Edw tha anoigei thread gia mine. An kapoios anakoinosei nwritera oti vrike block, stamatame to mining kai prosthetoume to block tou allou me xrisi tis /add_block
        # if not result:
        #         glock.release()
        #         return "No capacity reached"
        # # i announce frontizei na ginei to add block gia olous tous peers (ektos gia ton eauto tou)
        # announce_new_block(result)
        # proof = result.hash
        # delattr(result, "hash")
        # blockchain.add_block(result, proof)
        glock.release()
        return "Block #{} is mined.".format(resultIndex)


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
        # node_address = request.get_json()["node_address"]
        # key = request.get_json()["public_key"]
        # if not node_address:
        #         return "invalid data", 400
        # peers.update({key: node_address})
        # global idCounter
        # idCounter += 1
        # id_ip.update({("id"+str(idCounter)): node_address})
        # for (_, peer) in peers.items():
        #         url = "{}add_peers".format(peer)
        #         headers = {'Content-Type': "application/json"}
        #         requests.post(url, data=json.dumps(
        #             {"peers": (peers), "id_ip": id_ip}), headers=headers)
        # # Create transaction for new node
        # inputs = [{"transaction_id": wallets.get(myWallet.myAddress)[0].get(
        #     "transaction_id"), "id": wallets.get(myWallet.myAddress)[0].get("id")}]
        # newNodeTx = transaction.Transaction(
        #     myWallet.publickey.decode('utf-8'), key, 100, inputs)
        # newNodeTx.sign_transaction(myWallet.privatekey)
        # # we need to broadcast transactiont to everyone and then add to our block (except myself and registering node *register node can't verify it for now*)
        # for peer in [p for (_, p) in peers.items() if p != myWallet.myAddress and p != node_address]:
        #         # maybe _thread in future
        #         thread = broadcast_transaction(
        #             newNodeTx, peer)  # function at 101
        #         thread.start()
        # #we didnt broadcast to self, no need to validate, just create outputs
        # #remove from utxo, while registering only 1 UTXO in list
        # UTXO = wallets.pop(myWallet.myAddress)[0]
        # output0 = {"id": 0, "transaction_id": newNodeTx.transaction_id,
        #            "ammount": newNodeTx.ammount, "recipient_address": key}
        # output1 = {"id": 1, "transaction_id": newNodeTx.transaction_id, "ammount": UTXO.get(
        #     "ammount") - newNodeTx.ammount, "recipient_address": myWallet.publickey.decode('utf-8')}
        # output = [output0, output1]
        # newNodeTx.transaction_outputs = output
        # #add to blockchain
        # while not (blockchain.add_new_transaction(newNodeTx.to_dict())):
        #         mine_unconfirmed_transactions()
        # # Update wallets with UTXOs
        # wallets[node_address] = [output0]
        # wallets[myWallet.myAddress] = [output1]
        return get_chain()

#endPoint to register this node with someone else (e.x. bootstrap)
# Make post request with data = { node_address: #address_to_connect(bootstrap) }
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
    # glock.acquire()
    global node
    block_data = request.get_json()
    index = block_data["index"]
    previous_hash = block_data["previous_hash"]
    transactions = block_data["transactions"]
    timestamp = block_data["timestamp"]
    nonce = block_data["nonce"]
    proof = block_data['hash']
    node.add_block(index, previous_hash, transactions, timestamp, nonce, proof)
    return "block added to chain", 200

#         global blockchain
#         block_data = request.get_json()
#         newblock = block.Block(
#             block_data["index"], block_data["previous_hash"], block_data["transactions"])
#         newblock.timestamp = block_data["timestamp"]
#         newblock.nonce = block_data["nonce"]
#         proof = block_data['hash']
#         added = blockchain.add_block(newblock, proof)
#         if not added:
#                 print("block discarded")
#                 global wallets
#                 data = get_chain()
#                 chain_dump = json.loads(data)["chain"]
#                 blockchain = create_chain_from_dump(chain_dump)
#                 wallets = json.loads(data)["wallets"]
# #               glock.release()
#                 return "block was discarded", 400
#         ## update wallets
#         for tx in block_data["transactions"]:
#                 for (_, UTXOs) in wallets.items():
#                         if tx["transaction_id"] in UTXOs:
#                             UTXOs.remove(tx["transaction_id"])
# #       glock.release()
#      return "Block added to chain", 201

# Route to mine a block that someone else needs
@app.route('/mine_a_block', methods=['POST'])
def mine_a_block():
        transactions = request.get_json()
        # Validate that transactions are good and mine a block
        if not node.validate_and_mine(transactions):
                return "Invalidation failed", 400
        else:
                return "Success", 200


# def announce_new_block(newblock):
#         #for (_,peer) in peers.items():
#         def threadFunc(peer, newblock):
#                 url = "{}add_block".format(peer)
#                 headers = {'Content-Type': "application/json"}
#                 print("announce is hitting : ", url)
#                 requests.post(url, data=json.dumps(
#                     newblock.__dict__, sort_keys=True), headers=headers)
#         for peer in [p for (_, p) in peers.items() if p != myWallet.myAddress]:
#                 _thread.start_new_thread(threadFunc, (peer, newblock))


# get last block transactions from the blockchain

@app.route('/view_transactions', methods=['GET'])
def get_transactions():
    lastBlock = blockchain.chain[-1]
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
#     #Initialize wallet
#     myWallet = wallet.wallet(myAddress)
#     peers.update({str(myWallet.publickey.decode('utf-8')): myAddress})
#     #This probably needs to be updated
#     id_ip.update({"id0": myAddress})
#     idCounter += 1
#     #create First Transaction, 500*N NBC to my self # Everyone assumes self as bootstrap until registered
#     firstInput = {"previousOutputId": 0, "ammount": 500}
#     initTransaction = transaction.Transaction(
#         "0", myWallet.publickey.decode('utf-8'), 500, firstInput)
#     initTransaction.sign_transaction(myWallet.privatekey)
#     #we dont validate this transaction, just create UTXOs
#     output = {"id": 0, "transaction_id": initTransaction.transaction_id,
#               "recipient_address": myWallet.publickey.decode('utf-8'), "ammount": initTransaction.ammount}
#     initTransaction.transaction_outputs.append(output)
#     # save to wallets
#     wallets.update({myAddress: [output]})
#     #create genesis block, assign to self 500*n NBC
#     blockchain.create_genesis_block(initTransaction)
    app.run(host='0.0.0.0', port=port)
