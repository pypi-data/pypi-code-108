#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import Any
from typing import cast
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from aiohttp import ClientResponseError
from aiohttp import ClientSession
from fastapi.encoders import jsonable_encoder
from jsonschema import validate
from pydantic import AnyHttpUrl
from ramodels.lora import Facet
from ramodels.lora import ITSystem
from ramodels.lora import Klasse
from ramodels.lora import Organisation
from ramodels.lora._shared import LoraBase

from raclients.modelclientbase import ModelClientBase


class ModelClient(ModelClientBase):
    __mox_path_map = {
        Organisation: "/organisation/organisation",
        Facet: "/klassifikation/facet",
        Klasse: "/klassifikation/klasse",
        ITSystem: "/organisation/itsystem",
    }

    def __init__(
        self,
        base_url: AnyHttpUrl = AnyHttpUrl(
            "http://localhost:8080", scheme="http", host="localhost"
        ),
        validate: bool = True,
        *args: Any,
        **kwargs: Optional[Any],
    ):
        self.validate: bool = validate
        self.schema_cache: Dict[LoraBase, Dict[str, Any]] = {}
        super().__init__(base_url, *args, **kwargs)  # type: ignore

    async def _fetch_schema(self, session: ClientSession, url: str) -> Dict[str, Any]:
        """Fetch jsonschema from LoRa."""
        response = await session.get(url)
        response.raise_for_status()
        return cast(Dict[str, Any], await response.json())

    async def _get_schema(
        self, session: ClientSession, current_type: Type[LoraBase]
    ) -> Dict[str, Any]:
        schema = self.schema_cache.get(current_type)
        if schema:
            return schema

        generic_url = self._base_url + self.__mox_path_map[current_type]
        url = generic_url + "/schema"
        schema = await self._fetch_schema(session, url)
        self.schema_cache[current_type] = schema
        return schema

    def _get_healthcheck_tuples(self) -> List[Tuple[str, str]]:
        return [("/version/", "lora_version")]

    def _get_path_map(self) -> Dict[LoraBase, str]:
        return self.__mox_path_map

    async def _post_single_to_backend(
        self, current_type: Type[LoraBase], obj: LoraBase
    ) -> Any:
        """

        :param current_type: Redundant, only pass it because we already have it
        :param obj:
        :return:
        """
        session: ClientSession = await self._verify_session()

        uuid = obj.uuid
        # TODO, PENDING: https://github.com/samuelcolvin/pydantic/pull/2231
        # for now, uuid is included, and has to be excluded when converted to json
        jsonified = jsonable_encoder(
            obj=obj, by_alias=True, exclude={"uuid"}, exclude_none=True
        )
        generic_url = self._base_url + self.__mox_path_map[current_type]

        if self.validate:
            schema = await self._get_schema(session, current_type)
            validate(instance=jsonified, schema=schema)
        assert uuid is not None
        async with session.put(generic_url + f"/{uuid}", json=jsonified) as response:
            resp_json = await response.json()
            try:
                response.raise_for_status()
            except ClientResponseError as client_err:
                if "description" in resp_json:
                    client_err.message = resp_json["description"]
                raise client_err
            return resp_json

    async def load_lora_objs(
        self, objs: Iterable[LoraBase], disable_progressbar: bool = False
    ) -> List[Any]:
        """Lazy init client session to ensure created within async context

        Args:
            objs (Iterable[LoraBase]): LoRa objects to load
            disable_progressbar (bool, optional): Whether to disable the progress bar.
                Defaults to False.

        Returns:
            List[Any]: List of JSON responses.
        """
        return await self._submit_payloads(
            objs, disable_progressbar=disable_progressbar
        )
