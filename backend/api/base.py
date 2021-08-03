from fastapi import Depends

from backend.models.user import User
from backend.library.security import get_current_active_user
from backend.db.base import manager


class BaseApp:
    @classmethod
    async def prepare(cls, obj_db):
        return {"success": False} if obj_db is None else {"success": True}

    @staticmethod
    async def get_one_object(query):
        query_res = await manager.execute(query)
        return query_res[0] if len(query_res) > 0 else None

    @staticmethod
    async def get_list(cls, name='items'):
        objs = []
        for obj in await manager.execute(cls.select()):
            objs.append(await obj.dict)
        return {name: objs}


class BaseAppAuth(BaseApp):
    current_user: User = Depends(get_current_active_user)
