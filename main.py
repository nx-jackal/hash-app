#!/usr/bin/python2

from flask import Flask, jsonify, request
import random
import string
import hashlib
import os
import redis

app = Flask(__name__)

ENTROPY_CONFIG = string.ascii_uppercase + string.digits
HASH_ROUND = 10
REDIS_SERVER = '127.0.0.1'
REDIS_PORT = 6379
REDIS_ENABLED = False
REDIS_CONNECTOR = None
SERVICE_INET = '0.0.0.0'
SERVICE_PORT = 5000


def init():
    """Initiate Redis connection if needed"""
    global REDIS_SERVER
    global REDIS_PORT
    global REDIS_ENABLED
    global REDIS_CONNECTOR

    try:
        # Always strip() in case someone added whitespace unintentionally
        REDIS_SERVER = os.environ['REDIS_SERVER'].strip()
        REDIS_PORT = int(os.environ['REDIS_PORT'].strip())
        REDIS_ENABLED = os.environ['REDIS_ENABLED'].strip()

        REDIS_ENABLED = True if REDIS_ENABLED.lower() == 'true' else False
        REDIS_CONNECTOR = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT)
    except:
        REDIS_SERVER = ''
        REDIS_ENABLED = False


def slow_hasher(string_to_hash):
    """ Return a SHA512 hash of a given string"""
    # Just hash for 10 round is sufficient even if paranoid as current
    # computing power is very far from getting SHA-512 collision easily
    hashed_string = string_to_hash

    for cycle_count in range(HASH_ROUND):
        hashed_string = hashlib.sha512(hashed_string).hexdigest()
    return hashed_string


@app.route('/status')
def status():
    """Return a simple healthy status"""
    return "I'm Healthy!"


@app.route('/random_hash')
def random_hash():
    """Return a random hash."""
    random_float = random.random()

    # Just get the next random number if the number is too small
    while random_float < 0.001:
        random_float = random.random()

    random_int = int(random_float * 10)
    random_int = 1 if random_int < 1 else random_int

    random_string = ''.join(random.choice(ENTROPY_CONFIG) for _ in range(random_int))
    hashed_string = slow_hasher(random_string)

    return jsonify({ random_string: hashed_string })


@app.route('/hash', methods=['GET'])
def hash_string():
    """ Return a SHA512 hash of a given string, read from cache if available"""
    string_to_hash = request.args.get('string')

    if REDIS_ENABLED:
        log("Asking Redis about {}".format(string_to_hash))
        hashed_string = REDIS_CONNECTOR.get(string_to_hash)
        if hashed_string is None:
            log("String not found in redis, hashing..")
            hashed_string = slow_hasher(string_to_hash)
            REDIS_CONNECTOR.set(string_to_hash, hashed_string)
            log("String {} stored in redis".format(string_to_hash))
    else:
        hashed_string = slow_hasher(string_to_hash)

    return jsonify({ string_to_hash: hashed_string })


def log(message):
    """Central method for logging"""
    # Can be replaced with logging.{debug/info/warn/error}. Recommended to log
    # to local rsyslog daemon then rsyslog stream to a central log server
    print(message)

if __name__ == "__main__":
    init()
    app.run(host=SERVICE_INET, port=SERVICE_PORT, debug=True)
