from typing import Optional
import functools
import asyncio
from datetime import timedelta, datetime
import jwt
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN
from fastapi import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from backend.db.base import get_or_create


AUTH_TOKEN_NAME = 'Token'


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(header_authorization)
        cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)
        scheme = ""
        param = {}

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            else:
                return None
        return param


class Authenticator:
    def applicable_to(self, handler: Request):
        return True

    def verify(self, handler, args, kwargs) -> str:  # None means success
        raise NotImplementedError


def authenticated(*authenticators: Authenticator):
    def decorator(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            auths = filter(lambda item: item.applicable_to(self), authenticators)
            errors = []
            for auth in auths:
                verify_call = auth.verify(self, args, kwargs)
                res = await verify_call if asyncio.iscoroutinefunction(auth.verify) else verify_call
                if res is None:
                    result = method(self, *args, **kwargs)
                    return await result if asyncio.iscoroutinefunction(method) else result
                else:
                    errors.append(res)
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=' | '.join(errors))

        return wrapper

    return decorator


class DecoratorAuthenticator(Authenticator):
    def __init__(self, decorator, custom_message=None):
        self.decorator = decorator
        self.custom_message = custom_message

    def verify(self, handler, args, kwargs):
        @self.decorator
        def test_method(self, *args, **kwargs):
            pass

        try:
            test_method(handler, *args, **kwargs)
        except HTTPException as e:
            return self.custom_message or str(e)


class TokenAuthenticator(Authenticator):
    def __init__(self, user_model, jwt_token, data_dir: str = None):
        self.user_model = user_model
        self.JWT_TOKEN = jwt_token
        self.DATA_DIR = data_dir

    def applicable_to(self, handler: Request):
        return (
            AUTH_TOKEN_NAME in handler.headers or AUTH_TOKEN_NAME in handler.cookies or 'token' in handler.path_params
        )

    async def verify(self, handler: Request, args, kwargs):
        auth_cookie = handler.cookies.get(AUTH_TOKEN_NAME)
        token = (
            handler.headers.get(AUTH_TOKEN_NAME)
            or (auth_cookie if auth_cookie else None)
            or (handler.path_params.get('token') if 'token' in handler.path_params else None)
        )

        try:
            data = self.verify_token(token)
            defaults = {'password': ''}
            if 'username' in data:
                defaults['email'] = data.get('email', '')
                handler.current_user, created = await get_or_create(
                    self.user_model, username=data['username'], defaults=defaults
                )
            elif 'email' in data:
                defaults['username'] = data.get('username', '')
                handler.current_user, created = await get_or_create(
                    self.user_model, email=data['email'], defaults=defaults
                )
        except jwt.exceptions.InvalidTokenError:
            return 'JWT Signature verification failed'
        except AssertionError as e:
            return str(e)

    def verify_token(self, token):
        try:
            data = jwt.decode(token, self.JWT_TOKEN)
            assert 'exp' in data
            return data
        except AssertionError:
            raise jwt.exceptions.InvalidTokenError()


class CustomTokenAuthenticator(TokenAuthenticator):
    def applicable_to(self, handler):
        return hasattr(handler, 'token')

    def verify(self, handler, args, kwargs):
        try:
            self.verify_token(handler.token)
            return None
        except jwt.exceptions.InvalidTokenError:
            return 'JWT Signature verification failed'


class RolesAuthenticator(Authenticator):
    def __init__(self, *roles):
        self.roles = roles

    def verify(self, handler, args, kwargs):
        current_user_roles = (
            set(handler.current_user.role)
            if isinstance(handler.current_user.role, list)
            else set(map(lambda item: item.strip(), handler.current_user.role.split(',')))
        )
        if not current_user_roles & set(self.roles):
            return f"Only roles {', '.join(self.roles)} can do it"


class WebAuthenticator(Authenticator):
    def verify(self, handler, args, kwargs):
        if handler.current_user is None:
            return 'Not logged in'


web_authenticated = authenticated(WebAuthenticator())


def get_any_authenticated(user_model, jwt_token, data_dir: str = None):
    return authenticated(WebAuthenticator(), TokenAuthenticator(user_model, jwt_token, data_dir))


def get_custom_token_authenticated(user_model, jwt_token, data_dir: str = None):
    return authenticated(
        CustomTokenAuthenticator(user_model, jwt_token),
        WebAuthenticator(),
        TokenAuthenticator(user_model, jwt_token, data_dir),
    )


def role_authenticated(*roles):
    return authenticated(RolesAuthenticator(*roles))


def ip_authenticated(ip):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.request.remote_ip != ip:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Only client with certain IP can do it")
            else:
                return method(self, *args, **kwargs)

        return wrapper

    return decorator


localhosted = ip_authenticated('127.0.0.1')


def generate_token(data: dict = None, jwt_token: str = None) -> str:
    if data is None:
        data = {}
    ttl = timedelta(days=1)
    data.update({'exp': (datetime.now() + ttl).timestamp()})
    return jwt.encode(data, jwt_token, algorithm='HS256').decode()
