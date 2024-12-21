from flask import Blueprint, request, jsonify, current_app
from app import mongo
from bson import ObjectId
from datetime import datetime
from app.utils.auth_middleware import verify_token
import jwt

lost_found = Blueprint('lost_found', __name__)

@lost_found.route('', methods=['GET'])
def get_items():
    try:
        items = list(mongo.db.lost_found.find().sort('created_at', -1))
        for item in items:
            item['_id'] = str(item['_id'])
            item['user_id'] = str(item.get('user_id', ''))
            if hasattr(request, 'current_user'):
                item['is_owner'] = str(item.get('user_id', '')) == request.current_user.get('user_id', '')
            else:
                item['is_owner'] = False
            
            item.setdefault('title', 'Untitled')
            item.setdefault('description', 'No description')
            item.setdefault('type', 'lost')
            item.setdefault('contact', 'No contact info')
            item.setdefault('location', 'No location specified')
            item.setdefault('date', datetime.utcnow().isoformat())

        return jsonify({'items': items}), 200
    except Exception as e:
        print(f"Error fetching items: {str(e)}")
        return jsonify({'error': 'Failed to fetch items'}), 500

@lost_found.route('', methods=['POST'])
@verify_token
def create_item():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['title', 'description', 'type', 'contact', 'location', 'date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if data['type'] not in ['lost', 'found']:
            return jsonify({'error': 'Invalid type. Must be either "lost" or "found"'}), 400

        new_item = {
            'title': data['title'],
            'description': data['description'],
            'type': data['type'],
            'contact': data['contact'],
            'location': data['location'],
            'date': data['date'],
            'user_id': request.current_user['user_id'],
            'created_at': datetime.utcnow()
        }

        result = mongo.db.lost_found.insert_one(new_item)
        new_item['_id'] = str(result.inserted_id)

        return jsonify({
            'message': 'Item reported successfully',
            'item': new_item
        }), 201

    except Exception as e:
        print(f"Error creating item: {str(e)}")
        return jsonify({'error': 'Failed to create item'}), 500 

@lost_found.route('/<item_id>', methods=['DELETE'])
@verify_token
def delete_item(item_id):
    try:
        # Check if item exists and belongs to the user
        item = mongo.db.lost_found.find_one({
            '_id': ObjectId(item_id),
            'user_id': request.current_user['user_id']
        })
        
        if not item:
            return jsonify({'error': 'Item not found or unauthorized'}), 404

        # Delete the item
        result = mongo.db.lost_found.delete_one({
            '_id': ObjectId(item_id),
            'user_id': request.current_user['user_id']
        })

        if result.deleted_count:
            return jsonify({'message': 'Item deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete item'}), 400

    except Exception as e:
        print(f"Error deleting item: {str(e)}")
        return jsonify({'error': 'Failed to delete item'}), 500 