from typing import Dict, Literal, Optional

import aiohttp
import requests

from axew import (
    InvalidParams,
    Entry,
    BASE_URL,
    EntryNotFound,
    MAX_SIZE,
    ValidationError,
    BadRequest,
    BaseAxewException,
)


class AxewClient:
    def __init__(self):
        self.cache: Dict[str, Entry] = {}

    @staticmethod
    def create_entry(data: Dict) -> Entry:
        return Entry(**data)

    @staticmethod
    def validate_entry(
        code: str,
        error: Optional[str] = "",
        name: Optional[str] = "",
        description: Optional[str] = "",
    ) -> None:
        """
        Validates the given items are within size limits.

        Parameters
        ----------
        code: str
            ...
        error: Optional[str]
            ...
        name: Optional[str]
            ...
        description: Optional[str]
            ...

        Returns
        -------
        None
            This entry is valid

        Raises
        ------
        ValidationError
            The given item is out of size
        """
        if len(code) > MAX_SIZE["code"]:
            raise ValidationError("code", MAX_SIZE["code"])

        if error and len(error) > MAX_SIZE["error"]:
            raise ValidationError("error", MAX_SIZE["error"])

        if name and len(name) > MAX_SIZE["name"]:
            raise ValidationError("name", MAX_SIZE["name"])

        if description and len(description) > MAX_SIZE["description"]:
            raise ValidationError("description", MAX_SIZE["description"])

    def create_paste(
        self,
        *,
        code: str,
        error: str = "",
        name: str = "",
        description: str = "",
    ) -> Entry:
        """Creates a new paste

        Parameters
        ----------
        code : str
            The code portion of the paste
        error : str, optional
            The error portion of the paste
        name : str, optional
            What to name this entry
        description : str, optional
            A short description of this entry

        Returns
        -------
        Entry
            The created entry

        Raises
        ------
        InvalidParams
            Invalid provided arguments
        ValidationError
            The given arguments were too long
        """
        self.validate_entry(code, error, name, description)
        data = {"code": code}
        if error:
            data["error"] = error

        if name:
            data["name"] = name

        if description:
            data["description"] = description

        r = requests.post(f"{BASE_URL}/v1/entries/", json=data)
        return_data = r.json()
        if r.status_code == 400:
            raise BadRequest(return_data["message"])

        elif r.status_code == 422:
            raise BaseAxewException(str(return_data))

        entry = self.create_entry(return_data)
        self.cache[entry.uuid] = entry

        return entry

    def get_paste(self, uuid: str) -> Entry:
        """Returns the given Entry for a uuid

        Parameters
        ----------
        uuid : str
            The uuid for the entry you wish to fetch

        Returns
        -------
        Entry
            The entry for said uuid

        Raises
        ------
        EntryNotFound
            Couldn't find an entry with that uuid
        """
        if uuid in self.cache:
            return self.cache[uuid]

        r = requests.get(f"{BASE_URL}/v1/entries/{uuid}/")
        if r.status_code != 200:
            raise EntryNotFound

        return_data = r.json()
        entry: Entry = self.create_entry(return_data)
        return entry
