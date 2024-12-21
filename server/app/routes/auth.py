from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from app import mongo
from bson.objectid import ObjectId
import traceback
from app.utils.auth_middleware import verify_token

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if email already exists
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 400

        # Validate role
        valid_roles = ['student', 'clubowner']
        if data['role'] not in valid_roles:
            return jsonify({'error': 'Invalid role'}), 400

        # Create new user
        new_user = {
            'name': data['name'],
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'roles': [data['role']],
            'joined_clubs': [],
            'joined_study_groups': [],
            'created_at': datetime.utcnow()
        }

        # Insert into database
        result = mongo.db.users.insert_one(new_user)

        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': str(result.inserted_id),
                'name': new_user['name'],
                'email': new_user['email'],
                'roles': new_user['roles']
            }
        }), 201

    except Exception as e:
        print(f"Signup Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Internal server error during signup'}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400

        user = mongo.db.users.find_one({'email': email})
        
        if not user or not check_password_hash(user.get('password_hash', ''), password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'email': user['email'],
            'roles': user.get('roles', ['student']),
            'exp': datetime.utcnow() + timedelta(days=1)
        }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

        response = jsonify({
            'token': token,
            'user_id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name', ''),
            'roles': user.get('roles', ['student'])
        })

        return response, 200

    except Exception as e:
        print(f"Login Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Internal server error during login'}), 500

@auth.route('/me', methods=['GET'])
@verify_token
def get_current_user():
    try:
        current_user = request.current_user
        user = mongo.db.users.find_one({'_id': ObjectId(current_user['user_id'])})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'roles': user.get('roles', ['student'])
            }
        }), 200

    except Exception as e:
        print(f"Get User Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Internal server error while fetching user'}), 500 