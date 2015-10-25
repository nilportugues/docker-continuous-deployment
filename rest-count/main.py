"""
Flask webapp, registered as a consul client
"""

from flask import Flask, jsonify, request
from json import loads
import logging
import os
from consulclient import register, deregister
import os
import redis

PORT=8000

API_V1 = '/api/v1/'

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, static_url_path='')

register(PORT,  os.environ['TAGS'].split(',') if os.environ.has_key('TAGS') else None)

r = redis.StrictRedis(host='redis', port=6379, db=0)

# REST endpoints
@app.route(API_V1 + "health", methods=['GET'])
def health():
    """
    healthcheck endpoint
    """
    return jsonify(health=True)

@app.route(API_V1 + "count")
def index():
    """
    RESTful web service
    """
    n = r.get('count')
    n = int(n)+1 if n else 1
    r.set('count', n)
    return jsonify(version='1.0', kind=os.environ['TAGS'], count=n)

@app.errorhandler(Exception)
def handle_generic_error(err):
    """
    default exception handler
    """
    return 'error: ' + str(err), 500

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', debug=True, threaded=True,port=PORT)
    finally:
        deregister()
        logging.warn('shutting down')
