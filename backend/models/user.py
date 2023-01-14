from typing import Optional
from pydantic import BaseModel
from peewee import TextField, BooleanField

from backend.db.base import BaseDBItem
from backend.models.base import BaseItem


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseItem):
    username: str
    hashed_password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = 'restricted_user'
    disabled: Optional[bool] = None

    @property
    async def dict(self):
        return {
            'username': self.username,
            'hashed_password': self.hashed_password,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'disabled': self.disabled,
        }


class UserInDB(BaseDBItem):
    username = TextField(null=False)  # str
    hashed_password = TextField(null=False)  # str
    email = TextField(null=True)  # Optional[str] = None
    full_name = TextField(null=True)  # Optional[str] = None
    role = TextField(null=True, default='restricted_user')
    disabled = BooleanField(default=False)  # Optional[bool] = None

    @property
    async def dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'disabled': self.disabled,
            'hashed_password': self.hashed_password,
        }

    class Meta:
        table_name = 'users'


class UserSchema(BaseModel):
    username: str
    password: str
