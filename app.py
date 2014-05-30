#!bin/python

import requests
import json
import redis
from flask import Flask
from flask import request

BASE_URL = 'https://[KEY]:[KEYPASS]@[USER].cloudant.com/product'
CLUSTER = 'meritage'
# CLUSTER = 'moonshine'

# Connect to Redis; requires Redis to be running
r = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)

@app.route('/')
def index():
    return "Cloudant/Redis caching example."

# Get Product by Id
@app.route('/product/<product_id>', methods = ['GET'])
def get_product(product_id):

	# Check cache
	if (r.get(str(product_id))):
		return "Cache hit: " + r.get(str(product_id)) + "\n"
	else:	# Not in cache
		response = requests.get(BASE_URL + '/' + str(product_id))
		if response.status_code == 200:
			# Cache it
			r.set(str(product_id), json.dumps(response.json()))
			return "DB hit: " + json.dumps(response.json()) + "\n"
		else:
			return str(response.status_code) + "\n"

# Insert/Update Product
@app.route('/product', methods = ['POST'])
def update_product():

	# Clear the cache
	r.delete(request.json["_id"])
	
	request.json['last_update'] = CLUSTER
	request.json['doc_type'] = 'product'

	data = json.dumps(request.json)
 
	headers = {'Content-type': 'application/json'}
	response = requests.post(BASE_URL, data=data, headers=headers)

	if response.status_code == 201:
		# Cache it
		r.set(request.json["_id"], data)
		return str(response.status_code) + ": " + response.json()["rev"] + "\n"
	else:
		return str(response.status_code) + "\n"

if __name__ == '__main__':
    app.run(debug = True)
