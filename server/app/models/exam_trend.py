from datetime import datetime
from bson import ObjectId

class ExamTrend:
    def __init__(self, subject, topic, difficulty, study_hours, grade, user_id, date=None):
        self.subject = subject
        self.topic = topic
        self.difficulty = difficulty
        self.study_hours = float(study_hours)
        self.grade = float(grade)
        self.user_id = user_id
        self.date = date or datetime.utcnow()
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'subject': self.subject,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'study_hours': self.study_hours,
            'grade': self.grade,
            'user_id': self.user_id,
            'date': self.date,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        return ExamTrend(
            subject=data.get('subject'),
            topic=data.get('topic'),
            difficulty=data.get('difficulty'),
            study_hours=data.get('study_hours'),
            grade=data.get('grade'),
            user_id=data.get('user_id'),
            date=data.get('date')
        ) 