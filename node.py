import block
import blockchain
import wallet
import tools
import transaction
import requests
import json
import threading

#This class tries to mine a block and then broadcasts it.
class miner (threading.Thread):
    def __init__(self, chain, transactions, peers, lock):
        threading.Thread.__init__(self)
        self.transactions = transactions
        self.chain = chain
        self.peers = peers
        self.lock = lock

    def run(self):
        # Make sure only one thread is mining at a time
        self.lock.acquire()
        # Mine block
        if not self.mine_transactions():
            return # If mine fails do not broadcast
        self.broadcast_last_block()
        self.lock.release()
        return

    def broadcast_last_block(self):
        for (_, peer) in self.peers:
            url = peer + "add_block"
            headers = {'Content-Type': "application/json"}            
            requests.post(url, data=json.dumps(self.chain.last_block.__dict__, sort_keys=True), headers=headers)

    #mine a block
    def mine_transactions(self):
        result = self.chain.mine(self.transactions)
        if not result:
            return False # If mine fails, return
        proof = result.hash
        delattr(result, "hash")
        self.chain.add_block(result, proof)

        # if not result:
        #     return -1
        # self.broadcast_block(result)
        # proof = result.hash
        # delattr(result, "hash")
        # self.chain.add_block(result, proof)
        # return result.index

 

    
class node:
    def __init__(self, address):
        ##set
        self.chain = blockchain.Blockchain()
        self.current_id_count = 1
        self.address = address
        self.wallet = wallet.wallet(address)
        # here we store information for every node, as its id, its address (ip:port) its public key and its balance
        self.peers = ({str(self.wallet.publickey.decode('utf-8')):address})
        self.id_ip = {"id0": address}
        self.wallets = {}
        self.miner = miner
        self.lock = threading.Lock()

    @property
    def wallet_balance(self):
        ammount = sum(UTXO.get("ammount") for UTXO in self.wallets[self.wallet.address])
        return ammount

    #Bootstrap Method to register a node
    def register_node(self, node_address, node_key):    
        if not node_address:
                return "invalid data", 400
        self.peers.update({node_key: node_address})        
        self.id_ip.update({("id"+str(self.current_id_count)): node_address})
        self.current_id_count += 1
        #Notify everyone about newly entered peer
        for(_,peer) in self.peers.items():
            url = "{}add_peers".format(peer)
            headers = {'Content-Type': "application/json"}
            requests.post(url, data=json.dumps({"peers": (self.peers), "id_ip": self.id_ip}), headers=headers)
        # Create transaction for new node. 100 NBC from bootstrap
        inputs = [{"transaction_id": self.wallets.get(self.wallet.address)[0].get("transaction_id"), "id": self.wallets.get(self.wallet.address)[0].get("id")}]
        newNodeTx = transaction.Transaction(self.wallet.publickey.decode('utf-8'), node_key, 100, inputs)
        newNodeTx.sign_transaction(self.wallet.privatekey)
        # we need to broadcast transactiont to everyone and then add to our block (except myself and registering node *register node can't verify it for now*)
        for peer in [p for (_,p) in self.peers.items() if p != self.wallet.address and p != node_address]:
            self.send_transaction(newNodeTx, peer)
        #we didnt broadcast to self, no need to validate, just create outputs
        #remove from utxo, while registering only 1 UTXO in list
        UTXO = self.wallets.pop(self.wallet.address)[0]
        output0 = {"id": 0, "transaction_id": newNodeTx.transaction_id,
                   "ammount": newNodeTx.ammount, "recipient_address": node_key}
        output1 = {"id": 1, "transaction_id": newNodeTx.transaction_id, "ammount": UTXO.get(
            "ammount") - newNodeTx.ammount, "recipient_address": self.wallet.publickey.decode('utf-8')}
        output = [output0, output1]
        newNodeTx.transaction_outputs = output
        self.add_transaction_to_block(newNodeTx)
        self.wallets[node_address] = [output0]
        self.wallets[self.wallet.address] = [output1]
        return

    #Register this node to ring
    def register_to_ring(self, bootstrap_address):
        #First delete wallets (bootstrap will send you the correct ones, or find them searching chain)
        self.wallets = {}
        data = {"node_address": self.address, "public_key": str(self.wallet.publickey.decode('utf-8'))}
        headers = {'Content-Type': "application/json"}
        response = requests.post("http://" + bootstrap_address + "/register_node", data=json.dumps(data), headers=headers)
        if response.status_code == 200:
                chain_dump = response.json()["chain"]
                newChain = tools.create_chain_from_dump(chain_dump)
                newChain.unconfirmed_transactions = self.chain.unconfirmed_transactions
                self.chain = newChain
                self.wallets = response.json()["wallets"]
                return "Registration Successful", 200
        else:
                return "Registration failed", 500
    #add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    #bottstrap node informs all other nodes and gives the request node an id and 100 NBCs

    # Create initial transaction (100 NBC to a peer from bootstrap)
    def create_initial_transaction(self, bootstrap, ammount):
        firstInput = {"previousOutputId": 0, "ammount": ammount}
        initTransaction = transaction.Transaction("0", self.wallet.publickey.decode('utf-8'), ammount, firstInput)
        initTransaction.sign_transaction(self.wallet.privatekey)
        output = {"id": 0, "transaction_id": initTransaction.transaction_id, "recipient_address": self.wallet.publickey.decode('utf-8'), "ammount": initTransaction.ammount}
        initTransaction.transaction_outputs.append(output)        
        self.wallets.update({self.address: [output]})
        self.chain.create_genesis_block(initTransaction)
        return

    def create_transaction(self, sender, receiver, ammount):
        if (sender != self.wallet.address):
            return "Wrong sender IP"
        UTXOs = self.wallets.get(sender)
        total = 0
        inputs = []
        newUTXOs = UTXOs
        # Use UTXOs from node's wallet
        for txInput in UTXOs:
            if total > ammount:
                break
            total += txInput["ammount"]
            inputs.append(txInput)
            newUTXOs.remove(txInput)
        #Find key from ip
        recipient_key = [key for (key, ip) in self.peers.items() if ip == receiver][0]
        newTx = transaction.Transaction(self.wallet.publickey.decode('utf-8'), recipient_key, ammount, inputs)
        newTx.sign_transaction(self.wallet.privatekey)
        #Broadcast TX
        for peer in [p for (_,p) in self.peers.items() if p!=self.wallet.address]:
            self.send_transaction(newTx, peer)
        output = []
        output.append({"id": 0, "transaction_id": newTx.transaction_id, "ammount": ammount, "recipient_address": recipient_key})
        self.wallets[receiver].append(output[0])
        change = total - ammount
        if change > 0:
            output.append({"id": 1, "transaction_id": newTx.transaction_id, "ammount": total - ammount, "recipient_address": self.wallet.publickey.decode('utf-8')})
            self.wallets[sender].append(output[1])
        newTx.transaction_outputs = output
        self.add_transaction_to_block(newTx)
        return
    
    def receive_transaction(self, tx):
        if not transaction.verify_signature(tx):
            print("failed to verify signature in /new_transaction")
            return "Error"
        #Validate inputs are indeed UTXOs
        ip = self.peers.get(tx["sender_address"])
        UXTOs = self.wallets[ip]        
        for txInput in tx["txInput"]:
            if not any(inp["transaction_id"] == txInput["transaction_id"] for inp in UXTOs):
                print("Invalid inputs")
                return False
        # Remove inputs from wallet and find total coins used
        #TODO
        return True
    # Send a transaction to a peer
    def send_transaction(self, transaction, peer):
        class send_transaction (threading.Thread):
            def __init__(self, tx, peer):
                threading.Thread.__init__(self)
                self.tx = tx
                self.peer = peer

            def run(self):
                url = self.peer + "new_transaction"
                headers = {'Content-Type': "application/json"}
                data = json.dumps(self.tx.to_dict())
                requests.post(url, data=data, headers=headers)
        thread = send_transaction(transaction, peer)
        thread.start()
        return

    #def validdate_transaction():
        #use of signature and NBCs balance

    # Add a transaction to current block
    def add_transaction_to_block(self, newTx):
        #if enough transactions  mine
        while not (self.chain.add_new_transaction(newTx.to_dict())):        
            self.mine(self.chain.unconfirmed_transactions)
            self.chain.unconfirmed_transactions = []
    
    #Function to mine validated transactions
    def mine(self, transactions):
        #broadcast to everyone the block to be mined        
        for (_, peer) in self.peers:
            url = peer + "mine_a_block"
            headers = {'Content-Type': "application/json"}
            data = json.dumps(transactions.__dict__)
            requests.post(url, data=data, headers=headers)

        #start miner thread
        self.miner(self.chain, transactions, self.peers, self.lock).start()

    #Function to mine not validated transactions (TXs from other peers)
    def validate_and_mine(self, transactions):
        for tx in transactions:
            if not (transaction.verify_signature(tx)):
                return False
        # No need to broadcast now just mine the block
        self.miner(self.chain, transactions, self.peers, self.lock).start()
        return True

   # Add a block
    def add_block(self, index, previous_hash, transactions, timestamp, nonce, proof):
        #create new block
        newBlk = block.Block(index, previous_hash, transactions)
        newBlk.timestamp = timestamp
        newBlk.nonce = nonce

        added = self.chain.add_block(newBlk, proof)
        if not added:
            print("Block discarded")
            self.valid_chain()
            #self.setWallets()
            return
        # If added correctly fix wallets
        for tx in transactions:
            for (_, UTXOs) in self.wallets.items():
                if tx["transaction_id"] in UTXOs:
                    UTXOs.remove(tx["transaction_id"])
        return

        

    #def valid_proof(.., difficulty=MINING_DIFFICULTY):

    #concencus functions

    def valid_chain(self):
        #check for the longer chain accroose all nodes
        longest_chain = None
        current_len = len(self.chain.chain)
        for (_, node) in self.peers.items():
            url = ('{}currentchain'.format(node))
            response = requests.get(url)
            length = response.json()['length']
            # create chain and check if is valid and bigger
            chain = tools.create_chain_from_dump(response.json()['chain'])
            if length > current_len and chain.check_chain_validity():
                current_len = length
                longest_chain = chain
        if longest_chain:
            longest_chain.unconfirmed_transactions = self.chain.unconfirmed_transactions
            self.chain = longest_chain
            return True
        return False
