"""Peewee migrations -- 002_ITEM.py.
"""

from peewee import SQL, Model, AutoField, DateTimeField, TextField, BooleanField, FloatField
from backend.db.fields import OptionsField


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class ItemInDB(Model):
        id = AutoField()
        created = DateTimeField(constraints=[SQL('DEFAULT now()')])
        name = TextField(null=False)
        price = FloatField(null=True)
        is_offer = BooleanField(default=False)
        status = OptionsField(
            [
                'new',
                'old',
                'vip',
            ],
            default='new',
        )

        class Meta:
            table_name = 'items'


def rollback(migrator, database, fake=False, **kwargs):
    migrator.remove_model('items')
