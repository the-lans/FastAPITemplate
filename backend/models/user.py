from typing import Optional
from pydantic import BaseModel
from peewee import TextField, BooleanField

from backend.db.base import BaseDBItem


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseDBItem):
    username = TextField(null=False)  # str
    email = TextField(null=True)  # Optional[str] = None
    full_name = TextField(null=True)  # Optional[str] = None
    disabled = BooleanField(default=False)  # Optional[bool] = None


class UserInDB(User):
    hashed_password = TextField(null=False)  # str


class UserSchema(BaseModel):
    username: str
    password: str
