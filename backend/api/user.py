from datetime import timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.app import app
from backend.models.user import Token, User, UserInDB
from backend.library.security import authenticate_user, create_access_token, get_current_active_user
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, users_db


@app.post("/user/login", response_model=Token, tags=["user"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/user/signup", tags=["user"])
async def create_user(current_user: UserInDB = Depends()):
    users_db[current_user.username] = dict(current_user)  # replace with db call, making sure to hash the password first
    return {"success": True}


@app.get("/users/me/", response_model=User, tags=["user"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/", tags=["user"])
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
