from flask import Blueprint, request, jsonify
from app import mongo
from bson import ObjectId
from datetime import datetime
from app.utils.auth_middleware import verify_token

smart_sell = Blueprint('smart_sell', __name__)

@smart_sell.route('', methods=['GET'])
def get_items():
    """Get all items listed for sale"""
    try:
        items = list(mongo.db.smart_sell.find().sort('created_at', -1))
        for item in items:
            item['_id'] = str(item['_id'])
            # Add user_id to the response
            item['user_id'] = str(item.get('user_id', ''))
            # Add is_owner flag if user is authenticated
            if hasattr(request, 'current_user'):
                item['is_owner'] = str(item.get('user_id', '')) == request.current_user.get('user_id', '')
            else:
                item['is_owner'] = False
            
            # Ensure all required fields exist
            item.setdefault('title', 'Untitled')
            item.setdefault('description', 'No description')
            item.setdefault('price', 0)
            item.setdefault('condition', 'Not specified')
            item.setdefault('category', 'Other')
            item.setdefault('contact', 'No contact info')
            item.setdefault('created_at', datetime.utcnow().isoformat())

        return jsonify({'items': items}), 200
    except Exception as e:
        print(f"Error fetching items: {str(e)}")
        return jsonify({'error': 'Failed to fetch items'}), 500

@smart_sell.route('', methods=['POST'])
@verify_token
def create_item():
    """Create a new item listing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['title', 'description', 'price', 'condition', 'category', 'contact']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create new item
        new_item = {
            'title': data['title'],
            'description': data['description'],
            'price': float(data['price']),
            'condition': data['condition'],
            'category': data['category'],
            'contact': data['contact'],
            'user_id': request.current_user['user_id'],
            'created_at': datetime.utcnow()
        }

        # Insert into database
        result = mongo.db.smart_sell.insert_one(new_item)
        new_item['_id'] = str(result.inserted_id)
        new_item['is_owner'] = True

        return jsonify({
            'message': 'Item listed successfully',
            'item': new_item
        }), 201

    except Exception as e:
        print(f"Error creating item: {str(e)}")
        return jsonify({'error': 'Failed to create listing'}), 500

@smart_sell.route('/<item_id>', methods=['DELETE'])
@verify_token
def delete_item(item_id):
    """Delete an item listing"""
    try:
        # Check if item exists and belongs to the user
        item = mongo.db.smart_sell.find_one({
            '_id': ObjectId(item_id),
            'user_id': request.current_user['user_id']
        })
        
        if not item:
            return jsonify({'error': 'Item not found or unauthorized'}), 404

        # Delete the item
        result = mongo.db.smart_sell.delete_one({
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

@smart_sell.route('/<item_id>', methods=['PUT'])
@verify_token
def update_item(item_id):
    """Update an item listing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Check if item exists and belongs to the user
        item = mongo.db.smart_sell.find_one({
            '_id': ObjectId(item_id),
            'user_id': request.current_user['user_id']
        })
        
        if not item:
            return jsonify({'error': 'Item not found or unauthorized'}), 404

        # Update fields
        update_data = {
            'title': data.get('title', item['title']),
            'description': data.get('description', item['description']),
            'price': float(data.get('price', item['price'])),
            'condition': data.get('condition', item['condition']),
            'category': data.get('category', item['category']),
            'contact': data.get('contact', item['contact'])
        }

        result = mongo.db.smart_sell.update_one(
            {'_id': ObjectId(item_id), 'user_id': request.current_user['user_id']},
            {'$set': update_data}
        )

        if result.modified_count:
            updated_item = mongo.db.smart_sell.find_one({'_id': ObjectId(item_id)})
            updated_item['_id'] = str(updated_item['_id'])
            updated_item['is_owner'] = True
            return jsonify({
                'message': 'Item updated successfully',
                'item': updated_item
            }), 200
        else:
            return jsonify({'error': 'No changes made to the item'}), 400

    except Exception as e:
        print(f"Error updating item: {str(e)}")
        return jsonify({'error': 'Failed to update item'}), 500 