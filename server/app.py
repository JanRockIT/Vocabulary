from flask import Flask, request, jsonify
from flask_cors import CORS
from data_access.db_functions import (
    get_collections        as db_get_collections,
    get_collection        as db_get_collection,
    get_pairs             as db_get_pairs,
    get_pair              as db_get_pair,
    get_all_history       as db_get_all_history,
    get_collection_history as db_get_collection_history,
    add_collection        as db_add_collection,
    add_pair              as db_add_pair,
    add_history           as db_add_history,
    delete_collection     as db_delete_collection,
    delete_pair           as db_delete_pair,
    change_collection     as db_change_collection,
    change_pair           as db_change_pair,
    update_pair           as db_update_pair,
    get_next_pair         as db_get_next_pair,
    start_learning        as db_start_learning
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/collections', methods=['GET'])
def collections():
    return jsonify(db_get_collections())

@app.route('/collection', methods=['GET'])
def collection():
    cid = request.args.get('collection_id', type=int)
    return jsonify(db_get_collection(cid))

@app.route('/collection/<int:collection_id>/pairs', methods=['GET'])
def pairs_by_collection(collection_id):
    return jsonify(db_get_pairs(collection_id))

@app.route('/pair', methods=['GET'])
def pair():
    cid = request.args.get('collection_id', type=int)
    pid = request.args.get('pair_id',       type=int)
    return jsonify(db_get_pair(cid, pid))

@app.route('/history', methods=['GET'])
def history_all():
    return jsonify(db_get_all_history())

@app.route('/history/collection', methods=['GET'])
def history_by_collection():
    cid = request.args.get('collection_id', type=int)
    return jsonify(db_get_collection_history(cid))

@app.route('/pair/next', methods=['GET'])
def next_pair():
    cid = request.args.get('collection_id', type=int)
    return jsonify(db_get_next_pair(cid))

@app.route('/collection', methods=['POST'])
def create_collection():
    data = request.get_json()
    cid = db_add_collection(
        data['collection_name'],
        data['source_language'],
        data['target_language']
    )
    return jsonify({'collection_id': cid})

@app.route('/pair', methods=['POST'])
def create_pair():
    data = request.get_json()
    db_add_pair(
        data['collection_id'],
        data['source_word'],
        data['target_word']
    )
    return jsonify({'status': 'ok'})

@app.route('/history', methods=['POST'])
def create_history():
    data = request.get_json()
    db_add_history(
        data['collection_id'],
        data['pair_id']
    )
    return jsonify({'status': 'ok'})

@app.route('/collection/delete', methods=['POST'])
def remove_collection():
    data = request.get_json()
    db_delete_collection(data['collection_id'])
    return jsonify({'status': 'ok'})

@app.route('/pair/delete', methods=['POST'])
def remove_pair():
    data = request.get_json()
    db_delete_pair(data['collection_id'], data['pair_id'])
    return jsonify({'status': 'ok'})

@app.route('/collection/change', methods=['POST'])
def edit_collection():
    data = request.get_json()
    db_change_collection(
        data['collection_id'],
        data['columns'],
        data['values']
    )
    return jsonify({'status': 'ok'})

@app.route('/pair/change', methods=['POST'])
def edit_pair():
    data = request.get_json()
    db_change_pair(
        data['collection_id'],
        data['pair_id'],
        data['columns'],
        data['values']
    )
    return jsonify({'status': 'ok'})

@app.route('/pair/update', methods=['POST'])
def lern_pair():
    data = request.get_json()
    db_update_pair(
        data['collection_id'],
        data['pair_id'],
        data['known']
    )
    return jsonify({'status': 'ok'})

@app.route('/collection/learn', methods=['POST'])
def learn_collection():
    data = request.get_json()
    db_start_learning(data['collection_id'])
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
