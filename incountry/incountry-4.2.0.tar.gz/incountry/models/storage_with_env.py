import os
from typing import Dict, Optional

from pydantic import AnyHttpUrl, BaseModel, constr, StrictBool, StrictStr, validator, root_validator, conlist

from .custom_encryption_config import CustomEncryptionConfig
from .http_options import HttpOptions

from ..secret_key_accessor import SecretKeyAccessor


class StorageOptions(BaseModel):
    http_options: Optional[HttpOptions] = {}
    auth_endpoints: Dict[constr(min_length=1), AnyHttpUrl] = None
    normalize_keys: StrictBool = False
    hash_search_keys: StrictBool = True
    endpoint_mask: StrictStr = None
    countries_endpoint: AnyHttpUrl = None

    @validator("http_options", pre=True)
    def check_http_options(cls, value):
        if not isinstance(value, dict):
            raise ValueError("value is not a valid dict")
        return value

    @validator("countries_endpoint")
    def check_countries_endpoint_not_none(cls, value):
        if value is None:
            raise ValueError("cannot be None")
        return value

    @validator("auth_endpoints")
    def lowercase_auth_endpoint_keys(cls, value):
        lowercased = {}
        for key in value.keys():
            lowercased[key.lower()] = str(value[key])

        if "default" not in lowercased:
            raise ValueError("Missing default auth endpoint")

        return lowercased


class StorageWithEnv(BaseModel):
    environment_id: constr(strict=True, min_length=1) = None
    client_id: constr(strict=True, min_length=1) = None
    client_secret: constr(strict=True, min_length=1) = None
    oauth_token: constr(strict=True, min_length=1) = None
    endpoint: AnyHttpUrl = None
    debug: StrictBool = False
    options: StorageOptions = None
    encrypt: StrictBool = True
    secret_key_accessor: SecretKeyAccessor = None
    custom_encryption_configs: conlist(CustomEncryptionConfig, min_items=1) = None

    class Config:
        arbitrary_types_allowed = True

    @validator("options", pre=True)
    def check_options(cls, value):
        if not isinstance(value, dict):
            raise ValueError("value is not a valid dict")
        return value

    @validator("environment_id", pre=True, always=True)
    def environment_id_env(cls, value):
        res = value or os.environ.get("INC_ENVIRONMENT_ID")
        if res is None:
            raise ValueError(
                "Cannot be None. Please pass a valid environment_id param or set INC_ENVIRONMENT_ID env var"
            )
        return res

    @validator("endpoint", pre=True, always=True)
    def endpoint_env(cls, value):
        if value is not None and not isinstance(value, str) or isinstance(value, str) and len(value) == 0:
            raise ValueError("should be a valid URL")
        return value or os.environ.get("INC_ENDPOINT")

    # authentication methods
    @root_validator(pre=True)
    def validate_auth_methods(cls, values):
        client_id = values.get("client_id", None)
        client_secret = values.get("client_secret", None)
        oauth_token = values.get("oauth_token", None)
        has_oauth_creds = client_id is not None or client_secret is not None

        if oauth_token is not None and has_oauth_creds:
            raise ValueError(
                f"Please choose either authorization using oAuth token or "
                f"oAuth credentials (client_id + client_secret), not both"
            )

        values["client_id"] = values.get("client_id", os.environ.get("INC_CLIENT_ID"))
        values["client_secret"] = values.get("client_secret", os.environ.get("INC_CLIENT_SECRET"))
        return values

    @root_validator
    def check_auth_methods_for_nones(cls, values):
        has_oauth_creds = values.get("client_id", None) is not None or values.get("client_secret", None) is not None
        has_oauth_token = values.get("oauth_token", None) is not None

        if has_oauth_creds:
            if values["client_id"] is None:
                raise ValueError(
                    "  client_id - Cannot be None. Please pass a valid client_id param or set INC_CLIENT_ID env var"
                )
            if values["client_secret"] is None:
                raise ValueError(
                    f"  client_secret - Cannot be None. "
                    f"Please pass a valid client_secret param or set INC_CLIENT_SECRET env var"
                )

        if not has_oauth_creds and not has_oauth_token:
            raise ValueError("Please provide valid oAuth (client_id + client_secret) credentials or oAuth token")

        return values

    # secret_key_accessor with custom_encryption_configs
    @root_validator
    def init(cls, values):
        secret_key_accessor = values.get("secret_key_accessor", None)
        custom_encryption_configs = values.get("custom_encryption_configs", None)

        if custom_encryption_configs is not None and secret_key_accessor is None:
            raise ValueError(
                f"secret_key_accessor - provide a valid secret_key_accessor param "
                f"of class {SecretKeyAccessor.__name__} to use custom encryption"
            )
        elif custom_encryption_configs is not None:
            secret_key_accessor.enable_custom_encryption_keys()

        return values

    @validator("secret_key_accessor", always=True)
    def validate_secret_key_accessor(cls, value, values):
        if "encrypt" not in values or values["encrypt"] is False:
            return value
        if values["encrypt"] is True and not isinstance(value, SecretKeyAccessor):
            raise ValueError(f"Encryption is On. Please provide a valid instance of {SecretKeyAccessor.__name__}")

        return value

    @validator("custom_encryption_configs", each_item=True)
    def custom_encryption_configs_to_dict(cls, value):
        return value.dict()

    @validator("custom_encryption_configs")
    def check_versions(cls, value, values):
        if value is None:
            return value

        has_current_version = False
        versions = []
        for custom_encryption_config in value:
            if custom_encryption_config["version"] in versions:
                raise ValueError("Versions must be unique")
            versions.append(custom_encryption_config["version"])
            if custom_encryption_config.get("isCurrent", False) is True:
                if has_current_version:
                    raise ValueError("There must be at most one current version of custom encryption")
                else:
                    has_current_version = True
        return value
