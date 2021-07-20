from typing import Optional
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends
from backend.app import app
from backend.models.item import Item
from backend.models.user import User
from backend.security import get_current_active_user

router = InferringRouter()


@cbv(router)
class Foo:
    current_user: User = Depends(get_current_active_user)

    @router.get("/", tags=["Foo"])
    async def read_root(self):
        return {"Hello": "World"}

    @router.get("/items/{item_id}", tags=["Foo"])
    async def read_item(self, item_id: int, q: Optional[str] = None):
        return {"item_id": item_id, "q": q}

    @router.put("/items/{item_id}", tags=["Foo"])
    async def update_item(self, item_id: int, item: Item):
        return {"item_name": item.name, "item_id": item_id}


app.include_router(router)
