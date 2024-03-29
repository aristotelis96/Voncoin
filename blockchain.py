import block
import json
import transaction
import threading
from Crypto.Random import random

class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 4
        self.capacity = 1
        self.unconfirmed_transactions = [] 
        self.mining = False
        self.lock = threading.Lock()

    def create_genesis_block(self, initTransaction):
        genesis_block = block.Block(0, "1b", [initTransaction.to_dict()])
        genesis_block.hash = genesis_block.compute_hash()
        genesis_block.nonce = 0
        self.chain.append(genesis_block)

    def proof_of_work(self, block):
        block.nonce = random.getrandbits(64)
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
            if not self.mining:
                print("I failed to mine a block")
                return False
        print("I successfully mined a block")
        return computed_hash

    @property
    def last_block(self):
        return self.chain[-1]



    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * self.difficulty) and block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.lock.acquire()
        self.unconfirmed_transactions.append(transaction)
        if(len(self.unconfirmed_transactions)==self.capacity):
            self.lock.release()
            return False
        self.lock.release()
        return True

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            print(proof)
            print("ER2")
            return False
        block.hash = proof  
        self.lock.acquire()
        # STOP mining
        self.mining = False
        self.chain.append(block)
        # Remove new Block transactions from unconfirmed transactions list
        self.unconfirmed_transactions = [tx for tx in self.unconfirmed_transactions if tx not in block.transactions] 
        self.lock.release()
        return True

    def create_block(self,transactions = None):
        last_block = self.last_block
        if not transactions:
            if self.capacity > len(self.unconfirmed_transactions):
                return False
            transactions = self.unconfirmed_transactions[:self.capacity]
        newBlock = block.Block(self.last_block.index + 1, last_block.hash, transactions)
        return newBlock

    def mine(self, newBlock = None):
        if not newBlock:
            newBlock = self.create_block()
            if not newBlock:
                return
        self.mining = True
        proof = self.proof_of_work(newBlock)
        if not proof:
            return newBlock, False
        return newBlock, proof

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
