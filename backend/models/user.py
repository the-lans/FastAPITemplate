from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from peewee import TextField, BooleanField, DateTimeField
from backend.utils.base import FieldHidden


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username = TextField(null=False)  # str
    email = TextField(null=True)  # Optional[str] = None
    full_name = TextField(null=True)  # Optional[str] = None
    disabled = BooleanField(default=False)  # Optional[bool] = None


class UserInDB(User):
    hashed_password = TextField(null=False)  # str
    created = DateTimeField(default=datetime.now, _hidden=FieldHidden.WRITE)


class UserSchema(BaseModel):
    username: str
    password: str
