A simple flask app that returns the SHA512 hash for any given string (or a random string).
Install required dependencies using:

    `pip2 install -r requirements.txt`
    
Run with:

    `python2 main.py`
    
Sample Requests:

    `curl -X GET http://localhost:5000/hash\?string\=hello`
    
    `curl -X GET http://localhost:5000/random_hash`


App can make use of a redis server if present. Set the following environment variables to enable it:
    `REDIS_ENABLED=True`
    `REDIS_SERVER=host/ip`
    `REDIS_PORT=port`
