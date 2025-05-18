from flask import Flask, request, jsonify
from data_access.db_functions import (
    get_collections     as db_get_collections,
    get_collection      as db_get_collection,
    get_pairs           as db_get_pairs,
    get_pair            as db_get_pair,
    get_all_history     as db_get_all_history,
    get_collection_history as db_get_collection_history,
    add_collection      as db_add_collection,
    add_pair            as db_add_pair,
    add_history         as db_add_history,
    delete_collection   as db_delete_collection,
    delete_pair         as db_delete_pair,
    change_collection   as db_change_collection,
    change_pair         as db_change_pair,
    update_pair         as db_update_pair,
    get_next_pair       as db_get_next_pair,
)

app = Flask(__name__)

@app.route('/get_collections', methods=['GET'])
def get_collections():
    return db_get_collections()

@app.route('/get_collection', methods=['GET'])
def get_collection():
    data = request.get_json()
    collection_id = data.collection_id
    return db_get_collection(collection_id)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
