from peewee import TextField, BooleanField, FloatField
from typing import Optional

from backend.models.base import BaseItem
from backend.db.base import BaseDBItem
from backend.db.fields import OptionsField


class ItemInDB(BaseDBItem):
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

    async def check(self):
        await super().check()
        if not self.status:
            self.status = 'new'

    class Meta:
        table_name = 'items'


"""
class Item(BaseItem):
    name: str
    price: float
    is_offer: Optional[bool]
    status: str

    @property
    async def dict(self):
        return {
            'created': self._created,
            'name': self.name,
            'price': self.price,
            'is_offer': self.is_offer,
            'status': self.status,
        }
"""

Item = ItemInDB.get_class('Item', BaseItem)
