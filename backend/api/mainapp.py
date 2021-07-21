from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends

from backend.app import app
from backend.models.item import Item
from backend.models.user import User
from backend.library.security import get_current_active_user

router = InferringRouter()


@cbv(router)
class MainApp:
    current_user: User = Depends(get_current_active_user)

    @router.get("/api/items/list/?", tags=["MainApp"])
    async def get_list(self):
        objs = []
        for obj in Item.select():
            objs.append(await obj.dict)
        return {'items': objs}

    @router.get("/api/items/{item_id}", tags=["MainApp"])
    async def get_item(self, item_id: int):
        obj = Item.get(Item.id == item_id)
        res = await obj.dict
        return res

    @router.post("/api/items/new", tags=["MainApp"])
    async def new_item(self, item: Item):
        obj = Item.create(**await item.dict)
        res = await obj.dict
        return res

    @router.put("/api/items/{item_id}", tags=["MainApp"])
    async def update_item(self, item_id: int, item: Item):
        obj = Item.get(Item.id == item_id)
        res = await obj.dict
        res.update(await item.dict)
        for key, val in res.items():
            setattr(obj, key, val)
        obj.save()
        return res


app.include_router(router)
