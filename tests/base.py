from typing import Optional, Dict
from fastapi.testclient import TestClient
from peewee import Model
import atexit
from os.path import join
from fastapi import FastAPI, Response
import requests
import json

from backend.api import app
from backend.library.tests.db import TestCaseWithDB, InitDatabase
from backend.db.base import BaseDBModel, db, manager
from backend.config import DEFAULT_WORK_DIR
from backend.models.user import UserInDB
from backend.library.security import get_password_hash
from backend.library.tests.utils import faker


init_db = InitDatabase(BaseDBModel, db, manager, join(DEFAULT_WORK_DIR, 'migrations'))
atexit.register(init_db.dbFactory.clear_cache)


class TestCase(TestCaseWithDB):
    test_role = ['user']

    def setUp(self):
        super().setUp()
        self._app = self.get_app()
        self.client = self.get_http_client()
        self.test_user = faker.user_name()
        self.test_pass = faker.password()
        self.test_email = faker.email()
        self.new_session()
        self.user = self.create_user()
        self.set_token()

    @staticmethod
    def get_init_db() -> InitDatabase:
        return init_db

    def new_session(self):
        self.session = requests.Session()

    @staticmethod
    def get_app() -> FastAPI:
        return app

    def get_http_client(self) -> TestClient:
        return TestClient(self._app)

    def create_user(self, user: Optional[Dict] = None) -> Model:
        if user is None:
            user_db = UserInDB(
                username=self.test_user,
                hashed_password=get_password_hash(self.test_pass),
                email=self.test_email,
                full_name=self.test_user,
                role=','.join(self.test_role),
                disabled=False,
            )
        else:
            user_db = UserInDB(**user)
        user_db.save()
        return user_db

    def login(self, username: str = None, password: str = None) -> Response:
        if username is None:
            username = self.test_user
        if password is None:
            password = self.test_pass
        response = self.client.post("/login", data={'username': username, 'password': password})
        assert response.status_code == 200
        return response

    def signup(self, **kwargs) -> Response:
        return self.post("/signup", params=kwargs)

    def logout(self):
        response = self.client.get("/logout")
        assert response.status_code == 200

    def set_token(self, response: Response = None):
        if response is None:
            response = self.login()
        data = json.loads(response.content)
        self.token = data['token_type'] + ' ' + data['access_token']

    def prepare(self, kwargs):
        if self.token:
            header = {'Authorization': self.token}
            if 'headers' in kwargs:
                kwargs['headers'].update(header)
            else:
                kwargs['headers'] = header
        return kwargs

    def get(self, url, **kwargs):
        return self.client.get(url, **self.prepare(kwargs))

    def post(self, url, **kwargs):
        return self.client.post(url, **self.prepare(kwargs))

    def put(self, url, **kwargs):
        return self.client.put(url, **self.prepare(kwargs))

    def delete(self, url, **kwargs):
        return self.client.delete(url, **self.prepare(kwargs))
