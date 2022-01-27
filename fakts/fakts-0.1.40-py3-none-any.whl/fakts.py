from typing import List
from fakts.middleware.base import FaktsMiddleware
from fakts.utils import update_nested
from koil import koil
import yaml
from fakts.grants.base import FaktsGrant
import os
from fakts.grants.yaml import YamlGrant
from fakts.middleware.environment.overwritten import OverwrittenEnvMiddleware
import logging
import sys

logger = logging.getLogger(__name__)


class Fakts:
    def __init__(
        self,
        *args,
        grants=[YamlGrant(filepath="bergen.yaml")],
        middlewares=[OverwrittenEnvMiddleware()],
        fakts_path="fakts.yaml",
        register=True,
        force_reload=False,
        subapp: str = None,
        hard_fakts={},
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.loaded = False
        self.grants: List[FaktsGrant] = grants
        self.middlewares: List[FaktsMiddleware] = middlewares
        self.grantExceptions = []
        self.hard_fakts = hard_fakts
        self.fakts = hard_fakts
        self.failedResponses = {}
        self.subapp = subapp
        self.fakts_path = f"{subapp}.{fakts_path}" if subapp else fakts_path

        try:
            config = self.load_config_from_file()
            self.fakts = update_nested(self.fakts, config)
            self.loaded = True
            logger.info(
                f"Loaded fakts from local file {self.fakts_path}. Delete this file or pass force_reload to Fakts"
            )
        except:
            logger.info(
                f"Couldn't load local conf-file {self.fakts_path}. We will have to refetch!"
            )

        if register:
            set_current_fakts(self)

    def load_config_from_file(self, filepath=None):
        with open(filepath or self.fakts_path, "r") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    async def aget(self, group_name, bypass_middleware=False):
        assert self.loaded, "Konfik needs to be loaded before we can access call load()"
        config = {**self.fakts}

        if not bypass_middleware:
            for middleware in self.middlewares:
                additional_config = await middleware.aparse(previous=config)
                config = update_nested(config, additional_config)

        for subgroup in group_name.split("."):
            try:
                config = config[subgroup]
            except KeyError as e:
                logger.error(f"Could't find {subgroup} in {config}")
                config = {}

        return config

    async def arefresh(self):
        await self.aload()

    def get(self, *args, **kwargs):
        return koil(self.aget(*args, **kwargs), **kwargs)

    async def aload(self):
        assert (
            len(self.grants) > 0
        ), "Please provide allowed Grants to retrieve the Fakts from"

        for grant in self.grants:
            try:
                additional_fakts = await grant.aload(previous=self.fakts)
                self.fakts = update_nested(self.fakts, additional_fakts)
                self.grantExceptions.append(None)
            except Exception as e:
                self.grantExceptions.append(e)

        assert (
            self.fakts != {}
        ), f"We did not received any valid Responses from our Grants"

        if self.fakts_path:
            with open(self.fakts_path, "w") as file:
                yaml.dump(self.fakts, file)

        self.loaded = True

    async def adelete(self):
        self.loaded = False
        self.fakts = self.hard_fakts  # reset to original state

        if self.fakts_path:
            os.remove(self.fakts_path)

    def load(self, **kwargs):
        return koil(self.aload(), **kwargs)

    def delete(self, **kwargs):
        return koil(self.adelete(), **kwargs)


CURRENT_FAKTS = None


def get_current_fakts(**kwargs) -> Fakts:
    global CURRENT_FAKTS
    if not CURRENT_FAKTS:
        CURRENT_FAKTS = Fakts(**kwargs)
    return CURRENT_FAKTS


def set_current_fakts(fakts) -> Fakts:
    global CURRENT_FAKTS
    if CURRENT_FAKTS:
        logger.error(
            "Hmm there was another fakts set, maybe thats cool but more likely not"
        )
    CURRENT_FAKTS = fakts
