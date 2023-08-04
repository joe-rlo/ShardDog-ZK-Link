from http.server import BaseHTTPRequestHandler
from py_ecc import bn128
from py_ecc.bn128 import G1
import requests
import asyncio
import time
import logging
import json
import hashlib

logging.basicConfig(level=logging.INFO)

# Fetch reputation data for an account
def get_reputation(wallet):
	response = requests.get(f"https://auth.shard.dog/wallet/{wallet}")
	if response.status_code == 200:
		return response.json()
	else:
		return None

def send_nft(metadata):
	responseNFT = requests.post('https://api.shard.dog/zklinkNFT', json=metadata)
	if responseNFT.status_code == 200:
		return responseNFT.json()
	else:
		return None

def account_to_int(account):
		# Get bytes of the account name
		account_bytes = account.encode()

		# Hash the account name using SHA-256
		hash_bytes = hashlib.sha256(account_bytes).digest()

		# Convert the hash bytes to an integer
		account_int = int.from_bytes(hash_bytes, byteorder='big')

		return account_int


class handler(BaseHTTPRequestHandler):
	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		data = json.loads(post_data)

		# Get the account IDs from the request data
		account_1 = data.get('accountId1')
		account_2 = data.get('accountId2')

		# Fetch reputation data for both accounts
		#reputation_data_1 = get_reputation(account_1)
		reputation_data_2 = get_reputation(account_2)

		#account_1_int = account_to_int(account_1)
		account_2_int = account_to_int(account_2)

		# Generate a ECC output for the second account
		output = bn128.multiply(G1, account_2_int)

		description = ".".join(str(x) for x in output)

		# Prepare the token's metadata
		timestamp = int(time.time())
		metadata = {
			'token_id': 'token-' + str(timestamp),
			'metadata': {
				'title': 'ShardDog Account Zk Link',
				'description':description,
				'media': 'https://nftstorage.link/ipfs/bafybeidmtqiei2upy2f3dynjaeecyoj6e7outsd2ioyco2et7vbkyuh3ay',
				'extra' : json.dumps(reputation_data_2)
			},
			'receiver_id': account_1
		}

		send_nft(metadata)

		logging.info(metadata)

		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(json.dumps(metadata).encode())
		return



