from pydantic import BaseModel, validator

from ..exceptions import StorageClientException
from ..validation.utils import get_formatted_validation_error

from ..secret_key_accessor import SecretKeyAccessor


class SecretsValidation(BaseModel):
    secret_key_accessor: SecretKeyAccessor = None

    class Config:
        arbitrary_types_allowed = True

    @validator("secret_key_accessor", always=True)
    def validate_secret_key_accessor(cls, value, values):
        if value is None:
            return value

        try:
            value.validate()
        except StorageClientException as e:
            if e.original_exception is not None:
                raise ValueError(
                    "incorrect secrets data format returned"
                    + get_formatted_validation_error(e.original_exception, prefix="  ")
                )
            else:
                raise ValueError(e)

        return value
