from fastapi import Depends

from backend.models.user import UserInDB
from backend.library.security import get_current_active_user
from backend.db.base import execute


class BaseApp:
    @classmethod
    async def prepare(cls, obj_db):
        return {"success": obj_db is not None}

    @staticmethod
    async def get_one_object(query):
        query_res = await execute(query)
        return query_res[0] if len(query_res) > 0 else None

    @staticmethod
    async def get_list(cls, name='items'):
        objs = []
        for obj in await execute(cls.select().order_by(cls.id)):
            objs.append(await obj.dict)
        return {name: objs}


class BaseAppAuth(BaseApp):
    current_user: UserInDB = Depends(get_current_active_user)
