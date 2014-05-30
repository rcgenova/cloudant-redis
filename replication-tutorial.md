# Caching Tutorial with Multi-DC Replication (on EC2)

This tutorial demonstrates how to use the cloudant-redis sample app server ('app.py') within the context of a multi-region deployment with continuous, bi-directional replication. 'changes.py' will be used to clear the local cache for replication-derived changes (in real time). Filtering is used to prevent local changes from appearing in the changes feed.

The step-by-step walkthrough below requires you to create Cloudant accounts and launch EC2 instances in the east and west regions of the United States. You can then run sample read and write requests and observe the behavior of the system.

## Step 1: Cloudant configuration

* Create a Cloudant user account
  * Go to cloudant.com and click 'Sign Up'.
  * Fill out the form, selecting 'meritage' for data location.
  * Take note of your user name [USER1] and password [PASSWORD1]
* Create the 'product' database
  * 'curl -X PUT https://[USER1]:[PASSWORD1]@[USER1].cloudant.com/product'
* Create the '_replicator' database
  * 'curl -X PUT https://[USER1]:[PASSWORD1]@[USER1].cloudant.com/_replicator'
* Create an API key
  * 'curl -X POST https://[USER1]:[PASSWORD1]@cloudant.com/api/generate_api_key'
  * Take note of your key [KEY] and password [KEYPASS]
* Authorize the API key for the 'product' database
  * 'curl https://[USER1]:[PASSWORD1]@cloudant.com/api/set_permissions -d "database=[USER1]/product&username=[KEY]&roles=_reader&roles=_writer"'

* Create a second Cloudant user account
  * Go to cloudant.com and click 'Sign Up'.
  * Fill out the form, selecting 'moonshine' for data location.
  * Take note of your user name [USER2] and password [PASSWORD2]
* Create the 'product' database
  * 'curl -X PUT https://[USER2]:[PASSWORD2]@[USER2].cloudant.com/product'
* Create the '_replicator' database
  * 'curl -X PUT https://[USER2]:[PASSWORD2]@[USER2].cloudant.com/_replicator'
* Authorize the API key (created above) for the 'product' database
  * 'curl https://[USER2]:[PASSWORD2]@cloudant.com/api/set_permissions -d "database=[USER2]/product&username=[KEY]&roles=_reader&roles=_writer"'

## Step 2: Setup

Launch two EC2 instances running Redhat, one in us-east & one in us-west. Perform the following steps for each instance:

* Install gcc
  * sudo yum install gcc

* Install python-devel
  * sudo yum install python-devel

* Install curl-devel
  * sudo yum install curl-devel

* Install redis

  * 'wget http://download.redis.io/releases/redis-2.6.14.tar.gz'
  * 'tar xvzf redis-2.6.14.tar.gz'
  * 'cd redis-2.6.14'
  * 'make'
  * 'cd ..'

* Install git
  * 'sudo yum install git'
  * Optionally configure ~/.gitconfig

* Install PIP
  * 'wget https://bootstrap.pypa.io/get-pip.py'
  * 'sudo python get-pip.py'
* Install Python virtualenv
  * 'sudo pip install virtualenv'
* Clone the git repo
  * 'git clone https://github.com/rcgenova/cloudant-redis.git'
* Create a Python virtual environment within 'cloudant-redis'
  * 'cd ~'
  * 'virtualenv cloudant-redis'
* Activate cloudant-redis virtualenv
  * 'cd cloudant-redis'
  * 'source bin/activate'
* Install Python requests
  * 'pip install requests'
* Install Python flask
  * 'pip install flask'
* Install Python pycurl
  * 'export PYCURL_SSL_LIBRARY=nss'
  * 'pip install pycurl'
* Install Python redis
  * 'pip install redis'
* Install couchapp
  * 'pip install couchapp'

## Step 3: Application configuration

Open your terminal (hereafter referred to as TERMINAL1) and SSH in to the us-west EC2 instance. Then, take the following steps:

* Update app.py
  * 'vi ~/cloudant-redis/app.py'
  * Replace [KEY] & [KEYPASS] with [KEY] & [KEYPASS] generated above
  * Replace [USER] with [USER1] generated above
  * Set CLUSTER to 'meritage'
* Update changes.py
  * 'vi ~/cloudant-redis/changes.py'
  * Replace [KEY] & [KEYPASS] with [KEY] & [KEYPASS] generated above
  * Replace [USER] with [USER1] generated above
* Update the 'changes' design doc
  * 'vi ~/design/changes/filters/last_update.js'
  * Replace [CLUSTER] with 'meritage'
* Push the 'changes' design doc to your Cloudant account
  * 'cd ~/cloudant-redis/design/changes'
  * 'couchapp push https://[USER1]:[PASSWORD1]@[USER1].cloudant.com/product'
* Set up replication to account2
  * curl -X PUT https://[USER1]:[PASSWORD1]@[USER1].cloudant.com/_replicator -d '{"source":"https://[KEY]:[KEYPASS]@[USER1].cloudant.com/product","target":"https://[KEY]:[KEYPASS]@[USER2].cloudant.com/product","continuous":true}'

* Start Redis server in a new tab (TAB2)
  * 'cd ~/redis-2.6.14/src'
  * './redis-server'
* Start the Redis CLI in a new tab (TAB3)
  * 'cd ~/redis-2.6.14/src'
  * './redis-cli'
* Start the app server in a new tab (TAB4)
  * 'cd ~/cloudant-redis'
  * 'source bin/activate'
  * 'python app.py'
* Start the changes listener in a new tab (TAB5)
  * 'cd ~/cloudant-redis'
  * 'source bin/activate'
  * 'python changes.py'

In a new terminal window (TERMINAL2), SSH in to the us-east EC2 instance and take the following steps:

* Update app.py
  * 'vi ~/cloudant-redis/app.py'
  * Replace [KEY] & [KEYPASS] with [KEY] & [KEYPASS] generated above
  * Replace [USER] with [USER2] generated above
  * Set CLUSTER to 'moonshine'
* Update changes.py
  * 'vi ~/cloudant-redis/changes.py'
  * Replace [KEY] & [PASSWORD] with [KEY] & [KEYPASS] generated above
  * Replace [USER] with [USER2] generated above
* Update the 'changes' design doc
  * 'vi ~/design/changes/filters/last_update.js'
  * Replace [CLUSTER] with 'moonshine'
* Push the 'changes' design doc to your Cloudant account
  * 'cd ~/cloudant-redis/design/changes'
  * 'couchapp push https://[USER2]:[PASSWORD2]@[USER2].cloudant.com/product'
* Set up replication to account1
  * curl -X PUT https://[USER2]:[PASSWORD2]@[USER2].cloudant.com/_replicator -d '{"source":"https://[KEY]:[KEYPASS]@[USER2].cloudant.com/product","target":"https://[KEY]:[KEYPASS]@[USER1].cloudant.com/product","continuous":true}'

* Start Redis server in a new tab (TAB2)
  * 'cd ~/redis-2.6.14/src'
  * './redis-server'
* Start the Redis CLI in a new tab (TAB3)
  * 'cd ~/redis-2.6.14/src'
  * './redis-cli'
* Start the app server in a new tab (TAB4)
  * 'cd ~/cloudant-redis'
  * 'source bin/activate'
  * 'python app.py'
* Start the changes listener in a new tab (TAB5)
  * 'cd ~/cloudant-redis'
  * 'source bin/activate'
  * 'python changes.py'

You should now have two terminal windows open, each with five tabs. We will use the first tab in each to execute API requests against the local app server. We can monitor the other tabs for appropriate activity.

## Step 4: Execute sample requests

Using TAB1 in either terminal window, execute a few sample requests. You will want to prefix your documents with the local cluster name/id to avoid conflicts. You can manipulate or view the cache directly from the Redis CLI (TAB3).

To create a product:

* curl -H "Content-Type: application/json" -X POST -d '{"_id":"moonshine-product1"}' http://localhost:5000/product

* curl -H "Content-Type: application/json" -X POST -d '{"_id":"moonshine-product2","key1":"value1"}' http://localhost:5000/product

To update an existing product:

* curl -H "Content-Type: application/json" -X POST -d '{"_id":"moonshine-product2","_rev":"[REV]","key1":"value1","key2":"value2"}' http://localhost:5000/product

To get an existing product:

* curl http://localhost:5000/product/moonshine-product1


