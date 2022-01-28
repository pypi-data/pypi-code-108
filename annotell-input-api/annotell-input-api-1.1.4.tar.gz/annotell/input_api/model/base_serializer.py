from typing import Dict

from humps import camel
from pydantic import BaseModel


def to_camel_case(string: str) -> str:
    return camel.case(string)


class BaseSerializer(BaseModel):

    @classmethod
    def from_json(cls, js: Dict):
        return cls.parse_obj(js)

    def to_dict(self, by_alias=True) -> Dict:
        return self.dict(exclude_none=True, by_alias=by_alias)

    class Config:
        alias_generator = to_camel_case
        orm_mode = True
        allow_population_by_field_name = True
