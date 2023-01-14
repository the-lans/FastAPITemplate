from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends, Response

from backend.app import app
from backend.models.item import Item, ItemInDB
from backend.api.base import BaseAppAuth
from backend.api.user import set_response_headers


router = InferringRouter()


@cbv(router)
class MainApp(BaseAppAuth):
    @classmethod
    async def get_object_id(cls, item_id):
        return await cls.get_one_object(ItemInDB.select().where(ItemInDB.id == item_id))

    @router.get("/api/items/list", tags=["MainApp"])
    async def get_items(self):
        return await self.get_list(ItemInDB)

    @router.get("/api/items/{item_id}", tags=["MainApp"])
    async def get_item(self, item_id: int):
        item_db = await self.get_object_id(item_id)
        res = await self.prepare(item_db)
        if item_db is not None:
            res.update(await item_db.dict)
        return res

    @router.post("/api/items/new", tags=["MainApp"])
    async def new_item(self, item: Item = Depends()):
        return await ItemInDB.update_or_create(item, ret={"success": True})

    @router.put("/api/items/{item_id}", tags=["MainApp"])
    async def update_item(self, item_id: int, item: Item = Depends()):
        item_db = await self.get_object_id(item_id)
        res = await self.prepare(item_db)
        if item_db is not None:
            return await ItemInDB.update_or_create(item, item_db, ret=res)
        return res


app.include_router(router)


@app.options("/api/template/list", tags=["MainApp"])
async def options_object_id(response: Response):
    return await set_response_headers(response)


@app.options("/api/items/{item_id}", tags=["MainApp"])
async def options_item(response: Response):
    return await set_response_headers(response)


@app.options("/api/items/new", tags=["MainApp"])
async def options_new_item(response: Response):
    return await set_response_headers(response)


@app.options("/api/items/{item_id}", tags=["MainApp"])
async def options_update_item(response: Response):
    return await set_response_headers(response)
