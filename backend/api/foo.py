from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends

from backend.app import app
from backend.models.item import Item
from backend.models.user import User
from backend.library.security import get_current_active_user

router = InferringRouter()


@cbv(router)
class Foo:
    current_user: User = Depends(get_current_active_user)
    data: dict = {}
    item_id: int = 0

    @router.get("/", tags=["Foo"])
    async def get_root(self):
        return {"Hello": "World"}

    @router.get("/items/list/?", tags=["Foo"])
    async def get_list(self):
        return self.data

    @router.get("/items/{item_id}", tags=["Foo"])
    async def get_item(self, item_id: int):
        return {item_id: self.data[item_id]}

    @router.post("/items/new", tags=["Foo"])
    async def new_item(self, item: Item):
        self.data[self.item_id] = item
        res = {"item_id": self.item_id}
        self.item_id += 1
        return res

    @router.put("/items/{item_id}", tags=["Foo"])
    async def update_item(self, item_id: int, item: Item):
        self.data[item_id] = item
        return {"item_id": item_id}


app.include_router(router)
