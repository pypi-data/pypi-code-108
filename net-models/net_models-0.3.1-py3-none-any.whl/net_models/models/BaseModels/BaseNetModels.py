# Standard Libraries
import yaml
import json
# Third party packages
from pydantic import BaseModel, validate_model, Extra
# Local package
from net_models.fields import GENERIC_OBJECT_NAME
from net_models.utils.CustomYamlDumper import CustomYamlDumper
# Local module

__all__ = ['BaseNetModel', 'VendorIndependentBaseModel', 'NamedModel']

class BaseNetModel(BaseModel):
    """Base Network Config Model Class"""

    class Config:
        extra = Extra.forbid
        anystr_strip_whitespace = True
        validate_assignment = True

    def check(self):
        for field_name, field_props in self.__fields__.items():
            field = getattr(self, field_name)
        if isinstance(field, BaseNetModel):
            field.check()
        elif isinstance(field, list):
            [x.check() for x in field if isinstance(x, BaseNetModel)]
        elif isinstance(field, dict):
            [v.check() for k,v in field.items() if isinstance(v, BaseNetModel)]

        *_, validation_error = validate_model(self.__class__, self.__dict__)
        if validation_error:
            raise validation_error

    def serial_dict(self, exclude_none: bool = False, **kwargs) -> dict:
        return json.loads(self.json(exclude_none=exclude_none, **kwargs))

    def yaml(self, indent: int = 2, exclude_none: bool = False, **kwargs):
        return yaml.dump(data=self.dict(exclude_none=exclude_none, **kwargs), Dumper=CustomYamlDumper, indent=indent)

    def clone(self):
        return self.__class__.parse_obj(self.dict())




class VendorIndependentBaseModel(BaseNetModel):
    """Vendor Independent Base Model Class"""

    pass

class NamedModel(BaseNetModel):

    name: GENERIC_OBJECT_NAME