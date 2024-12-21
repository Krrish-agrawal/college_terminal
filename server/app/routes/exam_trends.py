from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from app import mongo
from app.models.exam_trend import ExamTrend
from app.utils.trend_analyzer import TrendAnalyzer
from app.utils.auth_middleware import verify_token

exam_trends = Blueprint('exam_trends', __name__)
trend_analyzer = TrendAnalyzer()

@exam_trends.route('', methods=['GET'])
@verify_token
def get_trends():
    """Fetch user's exam trends"""
    try:
        current_user = request.current_user
        user_id = ObjectId(current_user['user_id'])

        # Get user's exam data
        trends = list(mongo.db.exam_trends.find(
            {'user_id': user_id}
        ).sort('date', -1))

        # Convert ObjectId and dates to string
        for trend in trends:
            trend['_id'] = str(trend['_id'])
            trend['user_id'] = str(trend['user_id'])
            trend['date'] = trend['date'].isoformat()
            trend['created_at'] = trend['created_at'].isoformat()

        return jsonify(trends), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_trends.route('', methods=['POST'])
@verify_token
def create_trend():
    """Add new exam data and get analysis"""
    try:
        data = request.get_json()
        current_user = request.current_user

        # Validate required fields
        required_fields = ['subject', 'topic', 'difficulty', 'studyHours', 'grade', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate numeric fields
        try:
            study_hours = float(data['studyHours'])
            grade = float(data['grade'])
            if not (0 <= grade <= 100) or study_hours < 0:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Invalid study hours or grade'}), 400

        # Create new trend entry
        new_trend = ExamTrend(
            subject=data['subject'],
            topic=data['topic'],
            difficulty=data['difficulty'],
            study_hours=study_hours,
            grade=grade,
            user_id=ObjectId(current_user['user_id']),
            date=datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        )

        # Insert into database
        result = mongo.db.exam_trends.insert_one(new_trend.to_dict())
        
        # Get all user's exam data for analysis
        all_trends = list(mongo.db.exam_trends.find({'user_id': ObjectId(current_user['user_id'])}))
        
        # Analyze trends
        insights = trend_analyzer.analyze_trends(all_trends)
        
        # Get the created entry
        created_trend = mongo.db.exam_trends.find_one({'_id': result.inserted_id})
        
        # Prepare response
        created_trend['_id'] = str(created_trend['_id'])
        created_trend['user_id'] = str(created_trend['user_id'])
        created_trend['date'] = created_trend['date'].isoformat()
        created_trend['created_at'] = created_trend['created_at'].isoformat()

        return jsonify({
            'trend': created_trend,
            'insights': insights
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_trends.route('/analysis', methods=['GET'])
@verify_token
def get_analysis():
    """Get trend analysis for user's exam data"""
    try:
        current_user = request.current_user
        user_id = ObjectId(current_user['user_id'])

        # Get all user's exam data
        trends = list(mongo.db.exam_trends.find({'user_id': user_id}))
        
        # Analyze trends
        insights = trend_analyzer.analyze_trends(trends)

        return jsonify({
            'insights': insights
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500 