from peewee import TextField, BooleanField, FloatField
from backend.db.base import BaseDBItem
from backend.db.fields import OptionsField


class Item(BaseDBItem):
    name = TextField(null=False)  # str
    price = FloatField(null=True)  # float
    is_offer = BooleanField(default=False)  # Optional[bool]
    status = OptionsField(
        [
            'new',
            'old',
            'vip',
        ],
        default='new',
    )

    @property
    async def dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'name': self.name,
            'price': self.price,
            'is_offer': self.is_offer,
            'status': self.status,
        }
