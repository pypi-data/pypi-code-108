from pydantic import BaseModel, root_validator
import uuid


def camel_case(string: str) -> str:
    return ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(string.split('_')))


def str_uuid():
    return str(uuid.uuid4())


class DynamoBaseModel(BaseModel):
    _pk_tag: str
    _pk_value: str = None
    _sk_tag: str
    _sk_value: str = None
    pk: str = None
    sk: str = None

    @root_validator
    def set_keys(cls, values):
        values["pk"] = values["pk"] or cls.create_tag(cls._pk_tag, cls._pk_value, values)
        values["sk"] = values["sk"] or cls.create_tag(cls._sk_tag, cls._sk_value, values)
        return values

    @classmethod
    def create_tag(cls, tag, value, values):
        return tag if not value else f"{tag}#{values[value]}"

    class Config:
        allow_population_by_field_name = True
        alias_generator = camel_case
