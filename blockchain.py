import block
import json
import transaction
import _thread
from Crypto.Random import random
class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 2
        self.capacity = 1
        self.unconfirmed_transactions = [] 
        self.mining = False
        self.lock = _thread.allocate_lock()

    def create_genesis_block(self, initTransaction):
        genesis_block = block.Block(0, "1b", [initTransaction.to_dict()])
        genesis_block.hash = genesis_block.compute_hash()
        genesis_block.nonce = 0
        self.chain.append(genesis_block)

    def proof_of_work(self, block):
        block.nonce = random.getrandbits(64)
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):# and self.mining:
            block.nonce += 1
            computed_hash = block.compute_hash()
            if not self.mining:
                return False
                print("I successfully mined a block")
        return computed_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            print(proof)
            print(json.dump(block.__dict__))
            print("ER2")
            return False
        block.hash = proof
        self.mining = False
        self.chain.append(block)
        #for tx in block.transactions:
        #   for unconfirmed in self.unconfirmed_transactions:
        #   print(tx["transaction_id"], unconfirmed["transaction_id"])
        #       if tx["transaction_id"] == unconfirmed["transaction_id"]: self.unconfirmed_transactions.remove(unconfirmed)
        self.unconfirmed_transactions = []
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * self.difficulty) and block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.lock.acquire()
        if(len(self.unconfirmed_transactions)==self.capacity):
            self.lock.release()
            return False
        self.unconfirmed_transactions.append(transaction)
        self.lock.release()
        return True

    def mine(self):
        if len(self.unconfirmed_transactions) < self.capacity:
            return False
        last_block = self.last_block
        new_block = block.Block(index = last_block.index + 1,
        previous_hash = last_block.hash,
        transactions = self.unconfirmed_transactions)
        self.mining = True
        proof = self.proof_of_work(new_block)
        if not proof:
            return False
        new_block.hash = proof
        #self.add_block(new_block, proof)
        #self.unconfirmed_transactions = []
        return new_block

    def check_chain_validity(self):
        result = True
        previous_hash = self.chain[0].hash #genesis hash
        for block in self.chain[1:]: #skip genesis block
            block_hash = block.hash
            delattr(block, "hash")
            if not self.is_valid_proof( block, block_hash) or previous_hash != block.previous_hash:
                print("NOT VALID CHAIN")
                result = False
                break
            block.hash, previous_hash = block_hash, block_hash
        return result
