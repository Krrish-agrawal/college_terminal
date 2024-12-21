from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import mongo
from app.models.club import Club
from app.utils.auth_middleware import verify_token, check_role

clubs = Blueprint('clubs', __name__)

@clubs.route('', methods=['GET'])
@verify_token
def get_clubs():
    """Fetch all clubs"""
    try:
        # Get all clubs from database
        clubs_list = list(mongo.db.clubs.find())
        
        # Convert ObjectId to string for JSON serialization
        for club in clubs_list:
            club['_id'] = str(club['_id'])
            club['owner_id'] = str(club['owner_id'])
            club['members'] = [str(member_id) for member_id in club['members']]

        return jsonify(clubs_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clubs.route('', methods=['POST'])
@verify_token
@check_role(['clubowner'])
def create_club():
    """Create a new club"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get current user from token
        current_user = request.current_user

        # Create new club
        new_club = Club(
            name=data['name'],
            description=data['description'],
            owner_id=ObjectId(current_user['user_id']),
            social_links=data.get('socialLinks', {})
        )

        # Insert into database
        result = mongo.db.clubs.insert_one(new_club.to_dict())
        
        # Get the created club
        created_club = mongo.db.clubs.find_one({'_id': result.inserted_id})
        
        # Convert ObjectId to string for JSON serialization
        created_club['_id'] = str(created_club['_id'])
        created_club['owner_id'] = str(created_club['owner_id'])
        created_club['members'] = [str(member_id) for member_id in created_club['members']]

        return jsonify(created_club), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clubs.route('/join', methods=['POST'])
@verify_token
def join_club():
    """Join a club"""
    try:
        data = request.get_json()

        if 'clubId' not in data:
            return jsonify({'error': 'Club ID is required'}), 400

        # Get current user from token
        current_user = request.current_user
        user_id = ObjectId(current_user['user_id'])
        club_id = ObjectId(data['clubId'])

        # Check if club exists
        club = mongo.db.clubs.find_one({'_id': club_id})
        if not club:
            return jsonify({'error': 'Club not found'}), 404

        # Check if user is already a member
        if user_id in club['members']:
            return jsonify({'error': 'Already a member of this club'}), 400

        # Add user to club members
        mongo.db.clubs.update_one(
            {'_id': club_id},
            {'$push': {'members': user_id}}
        )

        # Add club to user's joined clubs
        mongo.db.users.update_one(
            {'_id': user_id},
            {'$push': {'joined_clubs': club_id}}
        )

        return jsonify({'message': 'Successfully joined the club'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Optional: Leave club endpoint
@clubs.route('/leave', methods=['POST'])
@verify_token
def leave_club():
    """Leave a club"""
    try:
        data = request.get_json()

        if 'clubId' not in data:
            return jsonify({'error': 'Club ID is required'}), 400

        current_user = request.current_user
        user_id = ObjectId(current_user['user_id'])
        club_id = ObjectId(data['clubId'])

        # Check if club exists
        club = mongo.db.clubs.find_one({'_id': club_id})
        if not club:
            return jsonify({'error': 'Club not found'}), 404

        # Can't leave if you're the owner
        if str(club['owner_id']) == current_user['user_id']:
            return jsonify({'error': 'Club owner cannot leave the club'}), 400

        # Remove user from club members
        mongo.db.clubs.update_one(
            {'_id': club_id},
            {'$pull': {'members': user_id}}
        )

        # Remove club from user's joined clubs
        mongo.db.users.update_one(
            {'_id': user_id},
            {'$pull': {'joined_clubs': club_id}}
        )

        return jsonify({'message': 'Successfully left the club'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500 