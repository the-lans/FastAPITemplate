from datetime import timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.app import app
from backend.models.user import Token, User, UserInDB
from backend.library.security import authenticate_user, create_access_token, get_current_active_user
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES


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
async def create_user(current_user: UserInDB = Depends()):
    obj = UserInDB.get(UserInDB.username == current_user.username)
    return current_user.update_or_create(obj)


@app.get("/api/user", response_model=User, tags=["user"])
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/")
async def get_root():
    return {"success": True}
