import json
import os
import time
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, validator

from .errors import CorruptedConfigFile

CONFIG_VERSION = (1, 0, 0)


class LevoAuthConfig(BaseModel):
    """Levo CLI Auth config, that will be persisted locally."""

    access_token: str
    refresh_token: str
    id_token: str
    scope: str
    expires_in: int
    expiry: Optional[float] = None
    token_type: str = "Bearer"

    def has_valid_tokens(self):
        """Checks if the persisted access token and refresh token are valid."""
        return self.access_token and self.refresh_token

    def is_access_token_expired(self):
        """Checks if the persisted access token has expired."""
        return not self.expiry > time.time()

    @validator("expiry", pre=True, always=True)
    def default_expiry(cls, v, *, values):
        return v or (time.time() + values["expires_in"])


class LevoConfig(BaseModel):
    """Levo CLI config, that will be persisted locally."""

    auth: LevoAuthConfig
    organization_id: str
    organization_name: str
    workspace_id: Optional[str]
    workspace_name: Optional[str]
    # Config version
    config_version = CONFIG_VERSION

    @classmethod
    def from_file(cls, path: str) -> Optional["LevoConfig"]:
        try:
            with open(path, "r") as conf_file:
                return cls(**json.load(conf_file))
        except FileNotFoundError as e:
            return None
        except Exception as exc:
            if isinstance(exc, json.JSONDecodeError) and not exc.doc:
                # File exists, but is empty
                return None
            raise CorruptedConfigFile(path=path) from exc

    def write_to_file(self, path: str):
        if not os.path.exists(os.path.dirname(path)):
            Path(os.path.dirname(path)).mkdir(mode=0o700, parents=True, exist_ok=True)

        # Write the config to the file with 0600 permissions
        conf_fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode=0o600)
        with os.fdopen(conf_fd, "w") as config_file:
            json.dump(self.dict(), config_file, indent=2)

    @validator("workspace_id")
    def prevent_none_workspace_id(cls, w):
        assert w is not None, "workspace_id may not be None"
        return w

    @validator("workspace_name")
    def prevent_none_workspace_name(cls, w):
        assert w is not None, "workspace_name may not be None"
        return w


def try_get_config(path: str) -> Union[LevoConfig, None]:
    return LevoConfig.from_file(path)
