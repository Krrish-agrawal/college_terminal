from datetime import datetime
from bson import ObjectId

class Club:
    def __init__(self, name, description, owner_id, social_links=None):
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.social_links = social_links or {}
        self.members = [owner_id]  # Owner is automatically a member
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'social_links': self.social_links,
            'members': self.members,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        club = Club(
            name=data.get('name'),
            description=data.get('description'),
            owner_id=data.get('owner_id'),
            social_links=data.get('social_links', {})
        )
        club.members = data.get('members', [club.owner_id])
        club.created_at = data.get('created_at', datetime.utcnow())
        return club 