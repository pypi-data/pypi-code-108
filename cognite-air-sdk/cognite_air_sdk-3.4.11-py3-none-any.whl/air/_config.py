from dataclasses import dataclass

from cognite.air.utils import strip_patch_from_version
from cognite.client import CogniteClient
from cognite.client.data_classes import Asset


@dataclass(frozen=True)
class AIRClientConfig:
    client: CogniteClient
    data_set_id: int
    schedule_asset: Asset
    schedule_asset_id: int
    schedule_asset_ext_id: str
    data_fields: dict
    data_fields_defs: dict
    model_name: str
    model_version: str
    local_testing: bool
    dev_write_back: bool

    @property
    def model_version_stripped(self):
        return strip_patch_from_version(self.model_version)

    def __post_init__(self):
        for name, exp_type in self.__annotations__.items():
            var = self.__dict__[name]
            if not isinstance(var, exp_type):
                raise TypeError(f"Expected field '{name}' to be of type '{exp_type}' not '{type(var)}'")
