import socket
import blockchain as blockchainModule
import block
 
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def create_chain_from_dump(chain_dump):
    newblockchain = blockchainModule.Blockchain()
    for idx, block_data in enumerate(chain_dump):
        newblock = block.Block(block_data["index"],
                               block_data["previous_hash"],
                               block_data["transactions"])
        newblock.timestamp = block_data["timestamp"]
        proof = block_data['hash']
        if idx > 0:
            newblock.nonce = block_data["nonce"]
            added = newblockchain.add_block(newblock, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # else the block is a genesis block, no verification needed
            newblock.hash = proof
            newblockchain.chain.append(newblock)
    return newblockchain
