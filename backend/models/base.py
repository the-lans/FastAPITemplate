from datetime import datetime
from pydantic import BaseModel


class BaseItem(BaseModel):
    _created: datetime

    @classmethod
    def get_cls_dict(cls, kwargs):
        return {key: kwargs[key] for key in cls.__fields__.keys() if key in kwargs}
