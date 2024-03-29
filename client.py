import datetime
import json
import requests
from flask import render_template, redirect, request
from tools import get_ip

id_ip = {}

def register(ip):
        url = myAddress + "register_with"
        headers = {'Content-Type': "application/json"}
        # This is the bootstrap NODE.
        data = {"bootstrap_address":ip}    
        requests.post(url, data=json.dumps(data), headers=headers)

def update_ids():
        url = myAddress + "get_id_ip"
        response=requests.get(url)
        global id_ip
        id_ip.update(response.json()["id_ip"])


if __name__ == '__main__':
        from argparse import ArgumentParser
        import socket
        parser = ArgumentParser()
        parser.add_argument('-b', '--bootstrap', default=0, type=int, help="if this is bootstrap set b=1")
        parser.add_argument('-p', '--port', default=5000, type=int, help="port your api listens too")
        parser.add_argument('-ip', '--ip', default="10.0.2.4:5000", type=str, help="bootstrap ip")
        args = parser.parse_args()
        bts = args.bootstrap
        port = args.port
        ip = args.ip

        global myAddress
        myAddress = "http://"  + get_ip() + ":" + str(port) + "/"
        if not bts:
                register(ip) #register
        while(1):
                print("------ Give a command -----")
                command = input()
                print("Please wait")
                update_ids()
                if command == "bye":
                        print("Bye bye")
                        break
                if command == "view":
                        url = myAddress + "view_transactions"
                        transactions = requests.get(url).json().get("transactions")
                        for tx in transactions:
                                print("TXID: ", tx.get("transaction_id"))
                                print("From :", tx.get("sender_address"))
                                print("To :", tx.get("receiver_address"))
                                print("amount :", tx.get("amount"))
                if command == "balance":
                        url = myAddress + "wallet_balance"
                        response = requests.get(url)
                        balance = response.json()
                        print("Your balance is: ", balance.get("wallet_balance"))
                if command == "help":
                        print("A helpful message")
                command = command.split(" ")
                if command[0] == "t":
                        #check if balance is enough
                        url = myAddress + "wallet_balance"
                        response = requests.get(url)
                        balance = response.json()
                        if(balance.get("wallet_balance") < int(command[2])):
                                print("Not enough balance!!!")
                                continue
                        url = myAddress + "create_new_transaction"
                        headers = {'Content-Type': "application/json"}
                        data = {"sender_ip": myAddress, "receiver_ip": (id_ip.get(command[1])), "amount": (int(command[2]))}
                        response = requests.post(url, data=json.dumps(data), headers = headers)
                        print(response.text)
                
