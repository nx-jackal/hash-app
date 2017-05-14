#!/usr/bin/python2

from flask import Flask, jsonify, request
import random
import string
import hashlib
import os
import redis


app = Flask(__name__)
REDIS_SERVER = ''
REDIS_ENABLED = False
REDIS_CONNECTOR = None


def init():
    """Initiate Redis connection if needed"""
    global REDIS_SERVER
    global REDIS_ENABLED
    global REDIS_CONNECTOR
    try:
        REDIS_SERVER = os.environ['REDIS_SERVER']
        REDIS_ENABLED = os.environ['REDIS_ENABLED']
        if REDIS_ENABLED.lower() == 'true':
            REDIS_ENABLED = True
        REDIS_CONNECTOR = redis.StrictRedis(host=REDIS_SERVER, port=6379)
    except:
        REDIS_SERVER = ''
        REDIS_ENABLED = False


def slow_hasher(string_to_hash):
    for i in range(100000):
        # Intentional loop to slow down
        hashed_string = hashlib.sha512(string_to_hash).hexdigest()
    return hashed_string


@app.route('/status')
def status():
    """Return a simple healthy status"""
    return "I'm Healthy!"


@app.route('/random_hash')
def random_hash():
    """Return a random hash. Has a 1 in 1000 chance of dying"""
    random_float = random.random()
    if random_float < 0.001:
        # noinspection PyProtectedMember
        os._exit(1)
    random_int = int(random_float*10)
    if random_int < 1:
        random_int = 1
    random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random_int))
    hashed_string = slow_hasher(random_string)
    result = {
        random_string: hashed_string
    }
    return jsonify(result)


@app.route('/hash', methods=['GET'])
def hash_string():
    """Returns SHA512 hash for the requested string. Has 1 in 100 chance of dying"""
    random_float = random.random()
    if random_float < 0.01:
            # noinspection PyProtectedMember
            os._exit(1)
    string_to_hash = request.args.get('string')
    if REDIS_ENABLED:
        print("Asking Redis about {}".format(string_to_hash))
        hashed_string = REDIS_CONNECTOR.get(string_to_hash)
        if hashed_string is None:
            print("String not found in redis, hashing..")
            hashed_string = slow_hasher(string_to_hash)
            REDIS_CONNECTOR.set(string_to_hash, hashed_string)
            print("String {} stored in redis".format(string_to_hash))
    else:
        hashed_string = slow_hasher(string_to_hash)
    result = {
        string_to_hash: hashed_string
    }
    return jsonify(result)


if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', debug=True)
