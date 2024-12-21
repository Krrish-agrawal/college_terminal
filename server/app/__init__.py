from flask import Flask, send_from_directory, request, jsonify, make_response
from flask_pymongo import PyMongo
from flask_cors import CORS
from app.config import Config
import os

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Single CORS configuration
    CORS(app, 
         resources={
             r"/*": {
                 "origins": ["http://localhost:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "expose_headers": ["Content-Range", "X-Content-Range"],
                 "supports_credentials": True,
                 "max_age": 120
             }
         }
    )
    
    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin == 'http://localhost:3000':
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        if request.method == 'OPTIONS':
            response.status_code = 200
        return response
    
    # Initialize MongoDB with connection status logging
    try:
        mongo.init_app(app)
        # Test the connection
        mongo.db.command('ping')
        print("\n✅ MongoDB Connected Successfully!\n")
    except Exception as e:
        print(f"\n❌ MongoDB Connection Failed: {str(e)}\n")
        raise e
    
    # Ensure required directories exist
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create MongoDB indexes
    with app.app_context():
        try:
            # Users collection indexes
            mongo.db.users.create_index('email', unique=True)
            
            # Clubs collection indexes
            mongo.db.clubs.create_index('name', unique=True)
            mongo.db.clubs.create_index('owner_id')
            mongo.db.clubs.create_index('members')
            
            # Study groups indexes
            mongo.db.study_groups.create_index('name')
            mongo.db.study_groups.create_index('owner_id')
            mongo.db.study_groups.create_index('members')
            
            # Lost and found indexes
            mongo.db.lost_found.create_index([('status', 1), ('created_at', -1)])
            mongo.db.lost_found.create_index('user_id')
            
            # Exam trends indexes
            mongo.db.exam_trends.create_index([('user_id', 1), ('created_at', -1)])
            mongo.db.exam_trends.create_index([('subject', 1), ('created_at', -1)])
            
            # Smart sell indexes
            mongo.db.smart_sell.create_index([('created_at', -1)])
            mongo.db.smart_sell.create_index('user_id')
            
            print("✅ MongoDB Indexes Created Successfully!")
        except Exception as e:
            print(f"❌ Error Creating Indexes: {str(e)}")

    # Register blueprints
    from app.routes.auth import auth
    from app.routes.clubs import clubs
    from app.routes.lost_found import lost_found
    from app.routes.study_groups import study_groups
    from app.routes.exam_trends import exam_trends
    from app.routes.smart_sell import smart_sell

    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(clubs, url_prefix='/api/clubs')
    app.register_blueprint(lost_found, url_prefix='/api/lost-found')
    app.register_blueprint(study_groups, url_prefix='/api/study-groups')
    app.register_blueprint(exam_trends, url_prefix='/api/exam-trends')
    app.register_blueprint(smart_sell, url_prefix='/api/smart-sell')

    # Add this before your other routes
    @app.route('/favicon.ico')
    def favicon():
        """Handle favicon requests"""
        try:
            # First try to serve from static directory
            return send_from_directory(
                os.path.join(app.root_path, 'static'),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon'
            )
        except:
            # If favicon doesn't exist, return empty response
            return '', 204

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app 