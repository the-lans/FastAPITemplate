from datetime import datetime
from typing import Optional
import peewee_async
import peewee_asyncext
from peewee import DateTimeField, TextField, Proxy, AutoField, Model

from backend.config import DB_NAME, DB_USER
from backend.lib.func import FieldHidden


db = Proxy()
db.initialize(
    peewee_asyncext.PooledPostgresqlExtDatabase(
        DB_NAME, user=DB_USER, register_hstore=True, max_connections=8, stale_timeout=300, autorollback=True
    )
)
manager: peewee_async.Manager = Proxy()
manager.initialize(peewee_async.Manager(db))


class BaseDBModel(Model):
    id = AutoField(help_text='Unique id of an object', _hidden=FieldHidden.WRITE)
    swagger_ignore = True

    @classmethod
    def get_name(cls, postfix: Optional[str] = None):
        if postfix is None:
            return f'{cls.__name__.lower()}'
        else:
            return f'{cls.__name__.lower()}_{postfix}'

    class Meta:
        database = db


class BaseDBItem(BaseDBModel):
    created = DateTimeField(default=datetime.now, _hidden=FieldHidden.WRITE)
    swagger_ignore = True
