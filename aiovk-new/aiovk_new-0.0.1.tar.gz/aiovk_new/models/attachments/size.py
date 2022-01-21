from pydantic import BaseModel, AnyUrl


class Size(BaseModel):
    height: int
    width: int

    type: str

    url: AnyUrl
