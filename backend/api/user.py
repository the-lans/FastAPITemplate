from datetime import timedelta
from fastapi import Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from backend.app import app
from backend.models.user import Token, User, UserInDB
from backend.library.security import authenticate_user, create_access_token, get_password_hash
from backend.library.auth import role_authenticated
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES
from backend.api.base import BaseApp, BaseAppAuth


all_role_authentificated = role_authenticated('admin', 'user', 'restricted_user')
admin_role_authentificated = role_authenticated('admin')


async def set_response_headers(response: Response):
    # response.headers["Access-Control-Allow-Origin"] = f"http://{DB_SETTINGS['DOMAIN']}:{DB_SETTINGS['PORT']}"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT"
    return {"success": True}


@app.post("/login", response_model=Token, tags=["user"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_user = authenticate_user(form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": auth_user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/hash")
async def get_hash(password: str):
    return {"success": True, 'hash': get_password_hash(password)}


@app.get("/")
async def get_root(response: Response):
    return await set_response_headers(response)


@app.options("/")
async def options_root(response: Response):
    return await set_response_headers(response)


router = InferringRouter()


@cbv(router)
class UserApp(BaseAppAuth):
    @router.post("/signup", tags=["user"])
    @admin_role_authentificated
    async def create_user(self, current_user: User = Depends()):
        obj = await BaseApp.get_one_object(UserInDB.select().where(UserInDB.username == current_user.username))
        return await UserInDB.update_or_create(current_user, obj)

    @router.get("/api/user", tags=["user"])
    async def read_current_user(self):
        user_dict = await self.current_user.dict
        return user_dict


app.include_router(router)


if __name__ == "__main__":
    user = UserInDB(
        username='test',
        email='test@mail.ru',
        full_name='test',
        disabled=False,
        hashed_password=get_password_hash('test'),
    )
    user.save()
