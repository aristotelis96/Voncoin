
#import blockchain
import time
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
import json

class Block:
	def __init__(self, index, previous_hash, transactions):
		self.index = index
		self.transactions =  transactions
		self.timestamp = time.time()
		self.previous_hash = previous_hash

	def compute_hash(self):
		serialized = json.dumps(self.__dict__, sort_keys=True).encode('utf-8')
		return SHA.new(serialized).hexdigest()
		
	def add_transaction(self, transaction, blockchain):
		self.transactions.append(transaction)
