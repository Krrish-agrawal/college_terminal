from datetime import datetime
from bson import ObjectId

class SmartSellItem:
    def __init__(self, name, original_price, selling_price, duration_used, 
                 condition, description, contact, user_id, images=None):
        self.name = name
        self.original_price = float(original_price)
        self.selling_price = float(selling_price)
        self.duration_used = duration_used
        self.condition = condition
        self.description = description
        self.contact = contact
        self.user_id = user_id
        self.images = images or []
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'name': self.name,
            'original_price': self.original_price,
            'selling_price': self.selling_price,
            'duration_used': self.duration_used,
            'condition': self.condition,
            'description': self.description,
            'contact': self.contact,
            'user_id': self.user_id,
            'images': self.images,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        return SmartSellItem(
            name=data.get('name'),
            original_price=data.get('original_price'),
            selling_price=data.get('selling_price'),
            duration_used=data.get('duration_used'),
            condition=data.get('condition'),
            description=data.get('description'),
            contact=data.get('contact'),
            user_id=data.get('user_id'),
            images=data.get('images', [])
        ) 