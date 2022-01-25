from datetime import datetime

from pydantic import BaseModel


class BaseDataModel(BaseModel):
    object_id: str = None
    created_at: datetime
    updated_at: datetime

    def dict(self, **kwargs):
        hidden_fields = set([field for field in list(self.__fields__.keys()) if field[0] == '_'])
        kwargs.setdefault('exclude', hidden_fields)
        return super().dict(**kwargs)
