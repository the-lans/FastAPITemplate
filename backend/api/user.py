from datetime import timedelta
from fastapi import Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from backend.app import app
from backend.models.user import Token, User, UserInDB
from backend.library.security import authenticate_user, create_access_token, get_current_active_user
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.api.base import BaseApp
from backend.library.security import get_password_hash


async def set_response_headers(response: Response):
    # response.headers["Access-Control-Allow-Origin"] = f"http://{DB_SETTINGS['DOMAIN']}:{DB_SETTINGS['PORT']}"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT"
    return {"success": True}


@app.post("/login", response_model=Token, tags=["user"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup", tags=["user"])
async def create_user(current_user: User = Depends()):
    obj = await BaseApp.get_one_object(UserInDB.select().where(UserInDB.username == current_user.username))
    return await UserInDB.update_or_create(current_user, obj)


@app.get("/api/user", tags=["user"])
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    user_dict = await current_user.dict
    return user_dict


@app.get("/hash")
async def get_hash(password: str):
    return {"success": True, 'hash': get_password_hash(password)}


@app.get("/")
async def get_root(response: Response):
    return await set_response_headers(response)


@app.options("/")
async def options_root(response: Response):
    return await set_response_headers(response)


if __name__ == "__main__":
    user = UserInDB(
        username='test',
        email='test@mail.ru',
        full_name='test',
        disabled=False,
        hashed_password=get_password_hash('test'),
    )
    user.save()
