import peewee_async
import peewee_asyncext
from internal_tooling_utils.db.base import BaseModelParent, FieldHidden
from peewee import DateTimeField, TextField, Proxy, AutoField


db = Proxy()
db.initialize(
    peewee_asyncext.PooledPostgresqlExtDatabase(
        f'mlflow', user='postgres', register_hstore=True, max_connections=6, autorollback=True
    )
)
manager: peewee_async.Manager = Proxy()
manager.initialize(peewee_async.Manager(db))


class BaseDBModel(BaseModelParent.new_base_model(db, manager)):
    id = AutoField(help_text='Unique id of an object', _hidden=FieldHidden.WRITE)
    swagger_ignore = True

    @classmethod
    def get_name(cls, postfix: str = 'common'):
        return f'{cls.__name__.lower()}_{postfix}'
