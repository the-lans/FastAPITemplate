from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from peewee import TextField, BooleanField

from backend.db.base import BaseDBItem


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    created: datetime
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    @property
    async def dict(self):
        return {'created': self.created,
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'disabled': self.disabled,
                }


class UserInDB(BaseDBItem):
    username = TextField(null=False)  # str
    email = TextField(null=True)  # Optional[str] = None
    full_name = TextField(null=True)  # Optional[str] = None
    disabled = BooleanField(default=False)  # Optional[bool] = None
    hashed_password = TextField(null=False)  # str


class UserSchema(BaseModel):
    username: str
    password: str
