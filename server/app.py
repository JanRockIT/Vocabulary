from flask import Flask, request, jsonify
from server.data_access.db_functions import *

app = Flask(__name__)

@app.route('/collections', methods=['GET'])
def collections():
    return get_collections()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
