from pydantic import BaseModel


class UniMessage(BaseModel):
    class Config:
        extra = 'ignore'
