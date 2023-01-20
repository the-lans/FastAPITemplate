from abc import abstractmethod
import psycopg2
import peewee
import peewee_async
import peewee_asyncext
from peewee_migrate import Router
import testing.postgresql

from backend.library.tests.base import BaseTestCase


class InitDatabase:
    dbFactory: testing.postgresql.PostgresqlFactory
    db: peewee.Proxy
    manager: peewee_async.Manager
    migrations_dir: str

    def __init__(
        self,
        base_model,
        db: peewee.Proxy,
        manager: peewee_async.Manager,
        migrations_dir: str,
    ):
        self.db = db
        self.manager = manager
        self.migrations_dir = migrations_dir
        self.base_model = base_model
        self.dbFactory = testing.postgresql.PostgresqlFactory(
            cache_initialized_db=True, on_initialized=self.initialize_db
        )

    def create_temp_peewee_db(self, temb_db):
        peewee_db = peewee_asyncext.PostgresqlExtDatabase(**temb_db.dsn(), register_hstore=True)
        self.db.initialize(peewee_db)
        self.manager.initialize(peewee_async.Manager(self.db.obj))
        MODELS = self.all_models(self.base_model)
        peewee_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        peewee_db.connect()
        return peewee_db

    def initialize_db(self, temb_db):
        # enable hstore
        conn = psycopg2.connect(**temb_db.dsn())
        cursor = conn.cursor()
        cursor.execute('create extension hstore;')
        cursor.close()
        conn.commit()
        conn.close()
        db = self.create_temp_peewee_db(temb_db)
        Router(db, self.migrations_dir).run()

    @classmethod
    def all_models(cls, model):
        return set(model.__subclasses__()).union([s for c in model.__subclasses__() for s in cls.all_models(c)])


class TestCaseWithDB(BaseTestCase):
    @staticmethod
    @abstractmethod
    def get_init_db() -> InitDatabase:
        pass

    def setUp(self):
        init_db = self.get_init_db()
        self.temp_db = init_db.dbFactory()
        self.db = init_db.create_temp_peewee_db(self.temp_db)

    def tearDown(self):
        self.db.close()
        self.temp_db.stop()
