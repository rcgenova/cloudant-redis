import requests
import json
import redis
import pycurl
import urllib

BASE_URL = 'https://[KEY]:[KEYPASS]@[USER].cloudant.com/product'
CHANGES_URL = BASE_URL + '/_changes?feed=continuous&filter=changes/last_update&since='

# Connect to Redis; requires Redis to be running
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def stream(callback):

    # Poll _changes for the local 'product' database.
    # The filter function filters out local changes, leaving only replication-derived changes.
    # The 'since' parameter allows us to resume after a reconnect.

    while 1:    # Automatically re-establish connection if it drops

        # get last_seq stored in redis
        if not (r.get('changes_last_seq') is None):
            since = r.get('changes_last_seq')
        else:
            since = '0'

        url = CHANGES_URL + since
 
        conn = pycurl.Curl()
        conn.setopt(pycurl.URL, url)
        conn.setopt(pycurl.WRITEFUNCTION, callback)

        # print conn.getinfo(pycurl.EFFECTIVE_URL)
     
        conn.perform()
 
def process_item(data):

    # Process an individual change and clear the cache

    if data.strip():
        dict = json.loads(data)

        if 'seq' in dict:

            # Store 'last_seq' in redis
            if not(r.set('changes_last_seq', dict['seq'])):
                print "Last sequence " + dict['seq'] + " not stored."

            # Delete the cache entry
            if r.delete(dict['id']):
                print "Product " + dict['id'] + " from cluster '" + cluster + "' cache entry deleted."
            else:
                print "Product " + dict['id'] + " from cluster '" + cluster + "' cache entry deletion failed."                

            # Pull doc from Cloudant and cache in Redis
            # response = requests.get(BASE_URL + '/' + dict['id'])
            # if response.status_code == 200:
            #     if 'doc_type' in response.json():
            #         if response.json()['doc_type'] == 'product':

            #             cluster = response.json()['last_update']

            #             # Cache it
            #             # r.set(dict['id'], json.dumps(response.json()))

            #             print "Product " + dict['id'] + " from cluster '" + cluster + "' cached."

if __name__ == '__main__':
 
    stream(process_item)


