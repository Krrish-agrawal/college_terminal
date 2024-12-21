from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, email, password_hash, roles=None):
        self.email = email
        self.password_hash = password_hash
        self.roles = roles or ['student']  # Default role
        self.joined_clubs = []
        self.joined_study_groups = []
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'email': self.email,
            'password_hash': self.password_hash,
            'roles': self.roles,
            'joined_clubs': self.joined_clubs,
            'joined_study_groups': self.joined_study_groups,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        user = User(
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            roles=data.get('roles', ['student'])
        )
        user.joined_clubs = data.get('joined_clubs', [])
        user.joined_study_groups = data.get('joined_study_groups', [])
        user.created_at = data.get('created_at', datetime.utcnow())
        return user 