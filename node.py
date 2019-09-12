import block
import blockchain
#import wallet

class node:
	def __init__(self):
		self.NBC=100;
		##set
		#self.chain = blockchain.Blockchain()
		#self.current_id_count 
		#self.NBCs
		#self.wallet

		#slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 




	#def create_new_block():
		#previousHash = blockchain.chain[-1].current_hash
		#self.myBlock = block.Block(previousHash, [])

	#def create_wallet():
		#create a wallet for this node, with a public key and a private key

	#def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs


	#def create_transaction(sender, receiver, signature):
		#remember to broadcast it


	#def broadcast_transaction():





	#def validdate_transaction():
		#use of signature and NBCs balance


	#def add_transaction_to_block():
		#if enough transactions  mine



	#def broadcast_block():


		

	#def valid_proof(.., difficulty=MINING_DIFFICULTY):




	#concencus functions

	#def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		global blockchain
		longest_chain = None
		current_len = len (blockchain.chain)
		
		for node in peers:
			response = requests.get('http://{}/chain'.format(node))
			length = response.json()['length']
			chain = response.json()['chain']
			if length > current_len and blockchain.check_chain_validity(chain):
				current_len = length
				longest_chain = chain
		if longest_chain:
			blockchain = longest_chain
			return True
		return False



