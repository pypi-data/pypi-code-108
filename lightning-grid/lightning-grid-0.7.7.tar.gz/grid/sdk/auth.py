from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Union

from grid.sdk import env


@dataclass(unsafe_hash=True)
class Credentials:
    user_id: str
    api_key: str

    @classmethod
    def from_locale(cls) -> "Credentials":
        """Instantiates the credentials using implicit locale.

        First use environment variables, otherwise look for credentials stored in file.

        Returns
        -------
        Credentials
            instantiated credentials object.
        """
        # if user has environment variables, use that
        user_id = os.getenv('GRID_USER_ID')
        api_key = os.getenv('GRID_API_KEY')
        grid_url = os.getenv('GRID_URL')
        if grid_url:
            env.GRID_URL = grid_url
        if user_id and api_key:
            return cls(user_id=user_id, api_key=api_key)

        # otherwise overwrite look for credentials stored locally as a file
        if os.getenv("CI"):
            p = Path.home() / ".grid" / "credentials.json"
        else:
            p = Path(os.getenv('GRID_CREDENTIAL_PATH', Path.home() / ".grid" / "credentials.json"))

        if not p.exists():
            raise PermissionError('No credentials available. Did you login?')
        with p.open() as f:
            credentials = json.load(f)

        return cls(
            user_id=credentials['UserID'],
            api_key=credentials['APIKey'],
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Credentials":
        """Instantiates the credentials using specified file path.

        Parameters
        ----------
        path
            file path to the config yaml or json on disk.

        Returns
        -------
        Credentials
            instantiated credentials object.
        """
        p = Path(path).absolute()
        if not p.exists():
            raise PermissionError('No credentials available. Did you login?')
        with p.open() as f:
            credentials = json.load(f)

        return cls(
            user_id=credentials['UserID'],
            api_key=credentials['APIKey'],
        )
