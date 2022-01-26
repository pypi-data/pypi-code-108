from pydantic import BaseModel


class UniDynamicDefinition(BaseModel):
    class Config:
        extra = 'ignore'
        allow_mutation = False
        frozen = True
