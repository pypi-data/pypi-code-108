from pydantic import BaseModel

from whizbang.util.string_helpers import snake_to_camel


class PydanticModelBase(BaseModel):
    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True
