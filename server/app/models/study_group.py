from datetime import datetime
from bson import ObjectId

class StudyGroup:
    def __init__(self, name, topic, description, owner_id, meeting_time=None, max_members=10):
        self.name = name
        self.topic = topic
        self.description = description
        self.owner_id = owner_id
        self.meeting_time = meeting_time
        self.max_members = max_members
        self.members = [owner_id]  # Owner is automatically a member
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'name': self.name,
            'topic': self.topic,
            'description': self.description,
            'owner_id': self.owner_id,
            'meeting_time': self.meeting_time,
            'max_members': self.max_members,
            'members': self.members,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        group = StudyGroup(
            name=data.get('name'),
            topic=data.get('topic'),
            description=data.get('description'),
            owner_id=data.get('owner_id'),
            meeting_time=data.get('meeting_time'),
            max_members=data.get('max_members', 10)
        )
        group.members = data.get('members', [group.owner_id])
        group.created_at = data.get('created_at', datetime.utcnow())
        return group 