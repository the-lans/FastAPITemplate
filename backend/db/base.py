from datetime import datetime
from typing import Optional
import peewee_async
import peewee_asyncext
from peewee import TextField, BooleanField, IntegerField, FloatField, DoubleField, DateField, DateTimeField, AutoField, Proxy, Model

from backend.config import DB_NAME, DB_USER
from backend.library.func import FieldHidden
from backend.db.fields import OptionsField


db = Proxy()
db.initialize(
    peewee_asyncext.PooledPostgresqlExtDatabase(
        DB_NAME,
        user=DB_USER,
        register_hstore=False,
        max_connections=8,
        autorollback=True,
        connection_timeout=60,
    )
)
manager: peewee_async.Manager = Proxy()
manager.initialize(peewee_async.Manager(db))


class BaseDBModel(Model):
    id = AutoField(help_text='Unique id of an object', _hidden=FieldHidden.WRITE)
    swagger_ignore = True
    not_editable = ['id']

    @classmethod
    def get_name(cls, postfix: Optional[str] = None):
        if postfix is None:
            return f'{cls.__name__.lower()}'
        else:
            return f'{cls.__name__.lower()}_{postfix}'

    @classmethod
    def get_cls_dict(cls, kwargs):
        return {key: kwargs[key] for key in cls._meta.columns.keys() if key in kwargs}

    @classmethod
    async def update_or_create(cls, obj, obj_db=None, ret=None):
        if ret is None:
            ret = {}
        obj_dict = cls.get_cls_dict(obj if isinstance(obj, dict) else await obj.dict)
        if obj_db is None:
            obj_db = cls(**obj_dict)
        else:
            for key, val in obj_dict.items():
                if key not in obj_db.not_editable:
                    setattr(obj_db, key, val)
        await obj_db.check()
        obj_db.save()
        ret.update(await obj_db.dict)
        return ret

    @classmethod
    def get_class(cls, name, parent, attr=None):
        conf = {
            TextField: str,
            IntegerField: int,
            FloatField: float,
            DoubleField: float,
            BooleanField: bool,
            OptionsField: str,
            DateField: datetime,
            DateTimeField: datetime,
        }
        # class_val = {str: '', int: 0, float: 0.0, bool: False, datetime: datetime.strptime('1970-01-01', '%Y-%m-%d')}
        class_val = {str: '', int: 0, float: 0.0, bool: False, datetime: ''}
        res_type = {key.strip('_'): conf[type(val)] for key, val in cls._meta.columns.items() if type(val) in conf}
        res = {key: class_val[val] for key, val in res_type.items()}

        @property
        async def get_dict(self):
            return {key: getattr(self, key) for key in res.keys()}

        res['dict'] = get_dict
        return type(name, (parent,), res)

    class Meta:
        database = db


class BaseDBItem(BaseDBModel):
    created = DateTimeField(default=datetime.now, _hidden=FieldHidden.WRITE)
    swagger_ignore = True
    not_editable = ['id', 'created']

    async def check(self):
        if not self.created:
            self.created = datetime.now()
