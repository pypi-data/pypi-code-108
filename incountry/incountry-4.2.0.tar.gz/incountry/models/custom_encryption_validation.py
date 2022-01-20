from pydantic import BaseModel, validator, conlist

from .custom_encryption_config import CustomEncryptionConfig

from ..secret_key_accessor import SecretKeyAccessor


class CustomEncryptionValidation(BaseModel):
    secret_key_accessor: SecretKeyAccessor = None
    custom_encryption_configs: conlist(CustomEncryptionConfig, min_items=1) = None

    class Config:
        arbitrary_types_allowed = True

    @validator("custom_encryption_configs", each_item=True)
    def validate_methods(cls, value, values):
        from ..validation.validate_custom_encryption_config import validate_custom_encryption_config

        config_as_dict = value.dict()

        validate_custom_encryption_config(config_as_dict, values["secret_key_accessor"].get_secrets_raw())

        return config_as_dict
