from datetime import datetime
from bson import ObjectId

class LostFoundItem:
    def __init__(self, title, description, type, location, contact, user_id, date=None):
        self.title = title
        self.description = description
        self.type = type  # 'lost' or 'found'
        self.location = location
        self.contact = contact
        self.user_id = user_id
        self.date = date or datetime.utcnow()
        self.status = 'open'  # 'open', 'closed', 'resolved'
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'location': self.location,
            'contact': self.contact,
            'user_id': self.user_id,
            'date': self.date,
            'status': self.status,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        item = LostFoundItem(
            title=data.get('title'),
            description=data.get('description'),
            type=data.get('type'),
            location=data.get('location'),
            contact=data.get('contact'),
            user_id=data.get('user_id'),
            date=data.get('date')
        )
        item.status = data.get('status', 'open')
        item.created_at = data.get('created_at', datetime.utcnow())
        return item 