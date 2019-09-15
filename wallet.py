import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

        def __init__(self, myAddress):
                key = RSA.generate(1024)
                self.public_key = key.publickey()
                self.private_key = key
                self.address = myAddress
                #self.transactions

        @property
        def publickey(self):
                return self.public_key.exportKey()

        @property
        def privatekey(self):
                return self.private_key.exportKey()
        
        @property
        def myAddress(self):
                return self.address
        #def balance():

