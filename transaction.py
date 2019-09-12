from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as SIGN

import requests
from flask import Flask, jsonify, request, render_template
import json
import base64

def verify_signature(tx):
	toTest = Transaction(tx.get("sender_address"), tx.get("receiver_address"), tx.get("ammount"), tx.get("txInput"))
	pubKey = RSA.importKey(tx.get("sender_address"))
	verifier = SIGN.new(pubKey)
	return (verifier.verify(toTest.transaction_id_Obj, tx.get("signature").encode('cp437')))

class Transaction:

	def __init__(self, sender_address, recipient_address, value, inputs):
		##set
		#self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
		self.sender_address = sender_address
		#self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
		self.receiver_address = recipient_address
		#self.amount: το ποσό που θα μεταφερθεί
		self.ammount = value
		#self.transaction_inputs: λίστα από Transaction Input 
		self.transaction_inputs = inputs
		#self.transaction_id: το hash του transaction
		serialized = json.dumps(self.__dict__, sort_keys=True).encode('utf-8')
		self.transaction_id_Obj = SHA.new(serialized)
		self.transaction_id = self.transaction_id_Obj.hexdigest()
		#self.transaction_outputs: λίστα από Transaction Output
		self.transaction_outputs = []
		#self Signature
		#privKey = RSA.importKey(sender_private_key)
		#signer = SIGN.new(privKey)
		#self.signature = signer.sign(self.transaction_id)

	def to_dict(self):
		tmp = {"sender_address": self.sender_address, "receiver_address": self.receiver_address, "ammount": self.ammount, "transaction_id": self.transaction_id, "txInput": self.transaction_inputs, "txOutput": self.transaction_outputs, "signature": self.signature.decode('cp437')}
		return tmp

	def sign_transaction(self, key):
		"""
		Sign transaction with private key
		"""
		privKey = RSA.importKey(key)
		signer = SIGN.new(privKey)
		self.signature = signer.sign(self.transaction_id_Obj)
	   
