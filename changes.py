import requests
import json
import redis
import pycurl
import urllib

BASE_URL = 'https://mpiederrioneoperabiromma:OQwSxvYeY5tnSbIcET4fLn7D@genova-oculus.cloudant.com/product'
CHANGES_URL = BASE_URL + '/_changes?feed=continuous&filter=changes/last_update&since='

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def stream(callback):

    while 1:

        # get last_seq stored in redis
        if r.get('changes_last_seq'):
            since = r.get('changes_last_seq')
        else:
            since = '0'

        # get last_seq stored in file
        # file = open("changes.txt", "r")
        # since = file.read()
        # file.close()

        url = CHANGES_URL + since
 
        conn = pycurl.Curl()
        conn.setopt(pycurl.URL, url)
        conn.setopt(pycurl.WRITEFUNCTION, callback)

        # print conn.getinfo(pycurl.EFFECTIVE_URL)
     
        conn.perform()
 
def process_item(data):

    if data.strip():
        dict = json.loads(data)

        if 'seq' in dict:

            # store  'last_seq' in redis
            r.set('changes_last_seq', dict['seq'])

            # store 'last_seq' in file
            # file = open("changes.txt", "w")
            # file.write(dict['seq'])
            # file.close()

            # pull doc and store in redis
            response = requests.get(BASE_URL + '/' + dict['id'])
            if response.status_code == 200:
                if 'doc_type' in response.json():
                    if response.json()['doc_type'] == 'product':
                        cluster = response.json()["last_update"]
                        r.set(dict['id'], json.dumps(response.json()))
                        print "Product " + dict['id'] + " from cluster '" + cluster + "' cached."

if __name__ == "__main__":
 
    stream(process_item)


