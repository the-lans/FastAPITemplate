from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends

from backend.app import app
from backend.models.item import Item, ItemInDB
from backend.api.base import BaseAppAuth

router = InferringRouter()


@cbv(router)
class MainApp(BaseAppAuth):
    @router.get("/api/items/list", tags=["MainApp"])
    async def get_items(self):
        return await self.get_list(ItemInDB)

    @router.get("/api/items/{item_id}", tags=["MainApp"])
    async def get_item(self, item_id: int):
        obj = await self.get_one_object(ItemInDB.select().where(ItemInDB.id == item_id))
        res = {"success": False} if obj is None else {"success": True}
        if obj is not None:
            res.update(await obj.dict)
        return res

    @router.post("/api/items/new", tags=["MainApp"])
    async def new_item(self, item: Item = Depends()):
        item_dict = ItemInDB.get_cls_dict(await item.dict)
        obj = ItemInDB(**item_dict)
        await obj.check()
        obj.save()
        return await obj.dict

    @router.put("/api/items/{item_id}", tags=["MainApp"])
    async def update_item(self, item_id: int, item: Item = Depends()):
        obj = await self.get_one_object(Item.select().where(Item.id == item_id))
        return await item.update_or_create(obj)


app.include_router(router)
