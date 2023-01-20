from typing import Dict
from fastapi import Response
import json

from backend.library.security import get_password_hash
from backend.library.tests.utils import faker
from tests.base import TestCase


class TestCaseApp(TestCase):
    def setUp(self):
        super().setUp()
        self.sample_one = {
            'name': 'product',
            'price': 10.2,
            'is_offer': True,
            'status': 'new',
        }

    @staticmethod
    def assert_user(data: Dict, response: Response):
        assert response.status_code == 200
        rdata = json.loads(response.content)
        assert rdata["username"] == data["username"]
        assert rdata["email"] == data["email"]
        assert rdata["role"] == data["role"]
        assert rdata["hashed_password"] == data["hashed_password"]

    def assert_item(self, response: Response, item_id: int, params: dict = None):
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['id'] == item_id
        assert data['name'] == self.sample_one['name']
        if params is not None:
            for key, val in params.items():
                assert data[key] == val

    def assert_item_new(self, sample: Dict):
        response = self.post(f"/api/items/new", params=sample)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['name'] == sample['name']
        return data['id'], data

    def test_pipeline(self):
        self.setUp()

        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json() == {"success": True}

        item_id, data = self.assert_item_new(self.sample_one)
        assert data['price'] == self.sample_one['price']

        params = {'status': 'vip'}
        response = self.put(f"api/items/{item_id}", params=params)
        self.assert_item(response, item_id, params)

        response = self.get(f"api/items/{item_id}")
        self.assert_item(response, item_id, params)

        response = self.get("api/items/list")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'items' in data
        item_one = data['items'][0]
        assert item_one['id'] == item_id
        assert item_one['status'] == params['status']

        self.tearDown()

    def test_signup(self):
        self.setUp()
        data = {
            'username': faker.user_name(),
            'hashed_password': get_password_hash(faker.password()),
            'email': faker.email(),
            'role': ','.join(self.test_role),
            'disabled': False,
        }
        response = self.signup(**data)
        assert response.status_code == 403

        username = faker.user_name()
        psw = faker.password()
        admin = {
            'username': username,
            'hashed_password': get_password_hash(psw),
            'email': faker.email(),
            'role': ','.join(['admin', 'user']),
            'disabled': False,
        }
        self.new_session()
        self.user = self.create_user(admin)
        response = self.login(username, psw)
        self.set_token(response)
        assert response.status_code == 200

        self.assert_user(admin, self.get("/api/user"))
        self.assert_user(data, self.signup(**data))

        self.tearDown()

    def test_without_token(self):
        self.setUp()

        item_id, _ = self.assert_item_new(self.sample_one)

        response = self.client.get(f"api/items/{item_id}")
        assert response.status_code == 401

        response = self.get(f"api/items/{item_id}")
        assert response.status_code == 200

        self.tearDown()
