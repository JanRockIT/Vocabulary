from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import traceback
from typing import Dict, Any, Optional

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
app.config['JSON_SORT_KEYS'] = False

def handle_errors(f):
    """Decorator für zentrale Fehlerbehandlung"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in {f.__name__}: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': str(e),
                'type': type(e).__name__
            }), 500
    return wrapper

@app.route('/collections', methods=['GET'])
@handle_errors
def collections():
    """Holt alle Vokabelsammlungen"""
    collections = db_get_collections()
    return jsonify({
        'status': 'success',
        'data': collections,
        'count': len(collections)
    })

@app.route('/collection', methods=['GET'])
@handle_errors
def collection():
    """Holt eine bestimmte Vokabelsammlung"""
    cid = request.args.get('collection_id', type=int)
    if not cid:
        return jsonify({'status': 'error', 'message': 'collection_id is required'}), 400
        
    collection = db_get_collection(cid)
    if not collection:
        return jsonify({'status': 'error', 'message': 'Collection not found'}), 404
        
    return jsonify({
        'status': 'success',
        'data': collection
    })

@app.route('/collection/<int:collection_id>/pairs', methods=['GET'])
@handle_errors
def pairs_by_collection(collection_id):
    """Holt alle Vokabelpaare einer Sammlung"""
    pairs = db_get_pairs(collection_id)
    return jsonify({
        'status': 'success',
        'data': pairs,
        'count': len(pairs)
    })

@app.route('/pair', methods=['GET'])
@handle_errors
def pair():
    """Holt ein bestimmtes Vokabelpaar"""
    cid = request.args.get('collection_id', type=int)
    pid = request.args.get('pair_id', type=int)
    
    if not all([cid, pid]):
        return jsonify({
            'status': 'error',
            'message': 'Both collection_id and pair_id are required'
        }), 400
        
    pair_data = db_get_pair(cid, pid)
    if not pair_data:
        return jsonify({
            'status': 'error',
            'message': 'Pair not found'
        }), 404
        
    return jsonify({
        'status': 'success',
        'data': pair_data
    })

@app.route('/history', methods=['GET'])
@handle_errors
def history_all():
    """Holt den gesamten Lernverlauf"""
    history = db_get_all_history()
    return jsonify({
        'status': 'success',
        'data': history,
        'count': len(history)
    })

@app.route('/history/collection', methods=['GET'])
@handle_errors
def history_by_collection():
    """Holt den Lernverlauf einer bestimmten Sammlung"""
    cid = request.args.get('collection_id', type=int)
    if not cid:
        return jsonify({
            'status': 'error',
            'message': 'collection_id is required'
        }), 400
        
    history = db_get_collection_history(cid)
    return jsonify({
        'status': 'success',
        'data': history,
        'count': len(history)
    })

@app.route('/pair/next', methods=['GET'])
@handle_errors
def next_pair():
    """Holt das nächste zu lernende Vokabelpaar"""
    cid = request.args.get('collection_id', type=int)
    if not cid:
        return jsonify({
            'status': 'error',
            'message': 'collection_id is required'
        }), 400
        
    next_pair_data = db_get_next_pair(cid)
    if not next_pair_data:
        return jsonify({
            'status': 'error',
            'message': 'No more pairs to learn'
        }), 404
        
    return jsonify({
        'status': 'success',
        'data': next_pair_data
    })

@app.route('/collection', methods=['POST'])
@handle_errors
def create_collection():
    """Erstellt eine neue Vokabelsammlung"""
    data = request.get_json()
    
    required_fields = ['collection_name', 'source_language', 'target_language']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    cid = db_add_collection(
        data['collection_name'],
        data['source_language'],
        data['target_language']
    )
    
    if not cid:
        return jsonify({
            'status': 'error',
            'message': 'Failed to create collection'
        }), 500
    
    return jsonify({
        'status': 'success',
        'data': {
            'collection_id': cid
        }
    }), 201

@app.route('/pair', methods=['POST'])
@handle_errors
def create_pair():
    """Fügt ein neues Vokabelpaar hinzu"""
    data = request.get_json()
    
    required_fields = ['collection_id', 'source_word', 'target_word']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    pair_id = db_add_pair(
        data['collection_id'],
        data['source_word'],
        data['target_word']
    )
    
    if not pair_id:
        return jsonify({
            'status': 'error',
            'message': 'Failed to add pair. Collection might not exist.'
        }), 400
    
    return jsonify({
        'status': 'success',
        'data': {
            'pair_id': pair_id
        }
    }), 201

@app.route('/history', methods=['POST'])
@handle_errors
def create_history():
    """Fügt einen neuen Eintrag zum Lernverlauf hinzu"""
    data = request.get_json()
    
    required_fields = ['collection_id', 'pair_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    db_add_history(
        data['collection_id'],
        data['pair_id']
    )
    
    return jsonify({
        'status': 'success',
        'message': 'History entry added successfully'
    }), 201

@app.route('/collection/delete', methods=['POST'])
@handle_errors
def remove_collection():
    """Löscht eine Vokabelsammlung (soft delete)"""
    data = request.get_json()
    
    if 'collection_id' not in data:
        return jsonify({
            'status': 'error',
            'message': 'collection_id is required'
        }), 400
    
    db_delete_collection(data['collection_id'])
    
    return jsonify({
        'status': 'success',
        'message': 'Collection marked as deleted'
    })

@app.route('/pair/delete', methods=['POST'])
@handle_errors
def remove_pair():
    """Löscht ein Vokabelpaar (soft delete)"""
    data = request.get_json()
    
    required_fields = ['collection_id', 'pair_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    db_delete_pair(data['collection_id'], data['pair_id'])
    
    return jsonify({
        'status': 'success',
        'message': 'Pair marked as deleted'
    })

@app.route('/collection/change', methods=['POST'])
@handle_errors
def edit_collection():
    """Aktualisiert eine Vokabelsammlung"""
    data = request.get_json()
    
    required_fields = ['collection_id', 'columns', 'values']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    if len(data['columns']) != len(data['values']):
        return jsonify({
            'status': 'error',
            'message': 'Number of columns and values must match'
        }), 400
    
    db_change_collection(
        data['collection_id'],
        data['columns'],
        data['values']
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Collection updated successfully'
    })

@app.route('/pair/change', methods=['POST'])
@handle_errors
def edit_pair():
    """Aktualisiert ein Vokabelpaar"""
    data = request.get_json()
    
    required_fields = ['collection_id', 'pair_id', 'columns', 'values']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    if len(data['columns']) != len(data['values']):
        return jsonify({
            'status': 'error',
            'message': 'Number of columns and values must match'
        }), 400
    
    db_change_pair(
        data['collection_id'],
        data['pair_id'],
        data['columns'],
        data['values']
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Pair updated successfully'
    })

@app.route('/pair/update', methods=['POST'])
@handle_errors
def learn_pair():
    """Aktualisiert den Lernstatus eines Vokabelpaares"""
    data = request.get_json()
    
    required_fields = ['collection_id', 'pair_id', 'known']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields. Required: {required_fields}'
        }), 400
    
    db_update_pair(
        data['collection_id'],
        data['pair_id'],
        data['known']
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Pair learning status updated'
    })

@app.route('/collection/learn', methods=['POST'])
@handle_errors
def learn_collection():
    """Startet eine Lernsession für eine Vokabelsammlung"""
    data = request.get_json()
    
    if 'collection_id' not in data:
        return jsonify({
            'status': 'error',
            'message': 'collection_id is required'
        }), 400
    
    db_start_learning(data['collection_id'])
    
    return jsonify({
        'status': 'success',
        'message': 'Learning session started'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
