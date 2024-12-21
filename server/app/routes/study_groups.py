from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import mongo
from app.models.study_group import StudyGroup
from app.utils.auth_middleware import verify_token
from datetime import datetime

study_groups = Blueprint('study_groups', __name__)

@study_groups.route('', methods=['GET'])
@verify_token
def get_groups():
    """Fetch all study groups"""
    try:
        # Get all groups, sorted by creation date
        groups = list(mongo.db.study_groups.find().sort('created_at', -1))
        formatted_groups = []

        for group in groups:
            try:
                formatted_group = {
                    '_id': str(group['_id']),
                    'name': group.get('name', 'Unnamed Group'),
                    'topic': group.get('topic', 'No topic'),
                    'description': group.get('description', 'No description'),
                    'meetingTime': group.get('meeting_time', ''),
                    'maxMembers': group.get('max_members', 10),
                    'members': [str(member_id) for member_id in group.get('members', [])],
                    'owner_id': str(group.get('owner_id', '')),
                    'created_at': group.get('created_at', datetime.utcnow()).isoformat()
                }
                formatted_groups.append(formatted_group)
            except Exception as e:
                print(f"Error formatting group {group.get('_id')}: {str(e)}")
                continue

        return jsonify({'groups': formatted_groups}), 200

    except Exception as e:
        print(f"Error fetching groups: {str(e)}")
        return jsonify({'error': 'Failed to fetch groups'}), 500

@study_groups.route('', methods=['POST'])
@verify_token
def create_group():
    """Create a new study group"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['name', 'topic', 'description']
        for field in required_fields:
            if not field in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create new group document
        new_group = {
            'name': data['name'],
            'topic': data['topic'],
            'description': data['description'],
            'meeting_time': data.get('meetingTime', ''),
            'max_members': int(data.get('maxMembers', 10)),
            'owner_id': ObjectId(request.current_user['user_id']),
            'members': [ObjectId(request.current_user['user_id'])],  # Owner is automatically a member
            'created_at': datetime.utcnow()
        }

        # Validate max_members
        if new_group['max_members'] < 2 or new_group['max_members'] > 50:
            return jsonify({'error': 'Max members must be between 2 and 50'}), 400

        # Insert into database
        result = mongo.db.study_groups.insert_one(new_group)
        
        # Format the response
        created_group = {
            '_id': str(result.inserted_id),
            'name': new_group['name'],
            'topic': new_group['topic'],
            'description': new_group['description'],
            'meetingTime': new_group['meeting_time'],
            'maxMembers': new_group['max_members'],
            'members': [str(m) for m in new_group['members']],
            'owner_id': str(new_group['owner_id']),
            'created_at': new_group['created_at'].isoformat()
        }

        return jsonify({'group': created_group}), 201

    except Exception as e:
        print(f"Error creating group: {str(e)}")
        return jsonify({'error': 'Failed to create study group'}), 500

@study_groups.route('/<group_id>/join', methods=['POST'])
@verify_token
def join_group(group_id):
    """Join a study group"""
    try:
        # Convert string ID to ObjectId
        group_oid = ObjectId(group_id)
        user_oid = ObjectId(request.current_user['user_id'])

        # Find the group
        group = mongo.db.study_groups.find_one({'_id': group_oid})
        if not group:
            return jsonify({'error': 'Group not found'}), 404

        # Check if user is already a member
        if user_oid in group.get('members', []):
            return jsonify({'error': 'Already a member of this group'}), 400

        # Check if group is full
        if len(group.get('members', [])) >= group.get('max_members', 10):
            return jsonify({'error': 'Group is full'}), 400

        # Add user to group
        result = mongo.db.study_groups.update_one(
            {'_id': group_oid},
            {'$addToSet': {'members': user_oid}}
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Failed to join group'}), 500

        return jsonify({'message': 'Successfully joined group'}), 200

    except Exception as e:
        print(f"Error joining group: {str(e)}")
        return jsonify({'error': 'Failed to join group'}), 500

@study_groups.route('/<group_id>/leave', methods=['POST'])
@verify_token
def leave_group(group_id):
    """Leave a study group"""
    try:
        current_user = request.current_user
        user_id = ObjectId(current_user['user_id'])
        group_id = ObjectId(group_id)

        # Check if group exists
        group = mongo.db.study_groups.find_one({'_id': group_id})
        if not group:
            return jsonify({'error': 'Study group not found'}), 404

        # Can't leave if you're the owner
        if str(group['owner_id']) == current_user['user_id']:
            return jsonify({'error': 'Group owner cannot leave the group'}), 400

        # Remove user from group members
        result = mongo.db.study_groups.update_one(
            {'_id': group_id},
            {'$pull': {'members': user_id}}
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Failed to leave group or not a member'}), 400

        return jsonify({'message': 'Successfully left the group'}), 200

    except Exception as e:
        print(f"Error leaving group: {str(e)}")
        return jsonify({'error': 'Failed to leave group'}), 500

@study_groups.route('/<group_id>', methods=['DELETE'])
@verify_token
def delete_group(group_id):
    """Delete a study group"""
    try:
        # Convert string ID to ObjectId
        group_oid = ObjectId(group_id)
        user_oid = ObjectId(request.current_user['user_id'])

        # Find the group and verify ownership
        group = mongo.db.study_groups.find_one({
            '_id': group_oid,
            'owner_id': user_oid
        })

        if not group:
            return jsonify({'error': 'Group not found or unauthorized'}), 404

        # Delete the group
        result = mongo.db.study_groups.delete_one({
            '_id': group_oid,
            'owner_id': user_oid
        })

        if result.deleted_count:
            # Remove group reference from all users who joined it
            mongo.db.users.update_many(
                {'joined_study_groups': group_oid},
                {'$pull': {'joined_study_groups': group_oid}}
            )
            return jsonify({'message': 'Study group deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete group'}), 400

    except Exception as e:
        print(f"Error deleting group: {str(e)}")
        return jsonify({'error': 'Failed to delete group'}), 500 