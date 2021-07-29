from datetime import datetime
from typing import Optional
import peewee_async
import peewee_asyncext
from peewee import DateTimeField, Proxy, AutoField, Model

from backend.config import DB_NAME, DB_USER
from backend.library.func import FieldHidden


db = Proxy()
db.initialize(
    peewee_asyncext.PooledPostgresqlExtDatabase(
        DB_NAME,
        user=DB_USER,
        register_hstore=True,
        max_connections=8,
        stale_timeout=300,
        autorollback=True,
        connection_timeout=60,
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

    def update_or_create(self, obj, item):
        res = await obj.dict
        res.update(await self.dict)
        for key, val in res.items():
            setattr(obj, key, val)
        obj.save()
        return res

    class Meta:
        database = db


class BaseDBItem(BaseDBModel):
    created = DateTimeField(default=datetime.now, _hidden=FieldHidden.WRITE)
    swagger_ignore = True
