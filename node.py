import block
import blockchain
import wallet
import tools
import transaction
import requests
import json
import threading

class node:
    def __init__(self, address):
        ##set
        self.chain = blockchain.Blockchain()
        self.current_id_count = 1
        self.address = address
        self.wallet = wallet.wallet(address)
        # here we store information for every node, as its id, its address (ip:port) its public key and its balance
        self.peers = ({address: str(self.wallet.publickey.decode('utf-8'))})
        self.id_ip = {"id0": address}
        self.wallets = {}
        
    #def create_new_block():
        #previousHash = blockchain.chain[-1].current_hash
        #self.myBlock = block.Block(previousHash, [])

    #def create_wallet():
        #create a wallet for this node, with a public key and a private key

    #Bootstrap Method to register a node
    def register_node(self, request):
        node_address = request.get_json()["node_address"]
        key = request.get_json()["public_key"]
        if not node_address:
                return "invalid data", 400
        self.peers.update({node_address: key})        
        self.id_ip.update({("id"+str(self.current_id_count)): node_address})
        self.current_id_count += 1
        #Notify everyone about newly entered peer
        for(peer,_) in self.peers.items():
            url = "{}add_peers".format(peer)
            headers = {'Content-Type': "application/json"}
            requests.post(url, data=json.dumps({"peers": (self.peers), "id_ip": self.id_ip}), headers=headers)
        # Create transaction for new node. 100 NBC from bootstrap
        inputs = [{"transaction_id": self.wallets.get(self.wallet.address)[0].get("transaction_id"), "id": self.wallets.get(self.wallet.address)[0].get("id")}]
        newNodeTx = transaction.Transaction(self.wallet.publickey.decode('utf-8'), key, 100, inputs)
        newNodeTx.sign_transaction(self.wallet.privatekey)
        # we need to broadcast transactiont to everyone and then add to our block (except myself and registering node *register node can't verify it for now*)
        for peer in [p for (p,_) in self.peers.items() if p != self.wallet.address and p != node_address]:
            self.send_transaction(newNodeTx, peer)
        #we didnt broadcast to self, no need to validate, just create outputs
        #remove from utxo, while registering only 1 UTXO in list
        UTXO = self.wallets.pop(self.wallet.address)[0]
        output0 = {"id": 0, "transaction_id": newNodeTx.transaction_id,
                   "ammount": newNodeTx.ammount, "recipient_address": key}
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

    def create_initial_transaction(self, bootstrap, ammount):
        firstInput = {"previousOutputId": 0, "ammount": ammount}
        initTransaction = transaction.Transaction("0", self.wallet.publickey.decode('utf-8'), ammount, firstInput)
        initTransaction.sign_transaction(self.wallet.privatekey)
        output = {"id": 0, "transaction_id": initTransaction.transaction_id, "recipient_address": self.wallet.publickey.decode('utf-8'), "ammount": initTransaction.ammount}
        initTransaction.transaction_outputs.append(output)
        self.wallets.update({self.address: [output]})
        self.chain.create_genesis_block(initTransaction)
        return

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


    def add_transaction_to_block(self, newTx):
        #if enough transactions  mine
        while not (self.chain.add_new_transaction(newTx.to_dict())):
            self.mine_unconfirmed_transactions()

    def mine_unconfirmed_transactions(self):
        result = self.chain.mine()
        if not result:
            return -1
        self.broadcast_block(result)
        proof = result.hash
        delattr(result, "hash")
        self.chain.add_block(result, proof)
        return result.index


    def broadcast_block(self, block):
        #TODO
        return


        

    #def valid_proof(.., difficulty=MINING_DIFFICULTY):




    #concencus functions

    def valid_chain(self):
        #check for the longer chain accroose all nodes
        longest_chain = None
        current_len = len(self.chain.chain)
        for (node, _) in self.peers.items():
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


    # def resolve_conflicts(self):
    # 	global blockchain
    # 	longest_chain = None
    # 	current_len = len (blockchain.chain)
        
    # 	for node in peers:
    # 		response = requests.get('http://{}/chain'.format(node))
    # 		length = response.json()['length']
    # 		chain = response.json()['chain']
    # 		if length > current_len and blockchain.check_chain_validity(chain):
    # 			current_len = length
    # 			longest_chain = chain
    # 	if longest_chain:
    # 		blockchain = longest_chain
    # 		return True
    # 	return False



