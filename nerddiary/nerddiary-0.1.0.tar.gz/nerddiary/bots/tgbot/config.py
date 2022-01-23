from __future__ import annotations
import logging
import json
import datetime

from pydantic import (
    BaseSettings,
    ValidationError,
    DirectoryPath,
    validator,
    PrivateAttr,
)
from pydantic.fields import Field

from nerddiary.bot.model import TimeZone, QuestionType, User
from nerddiary.bot.data import DataProvider

from typing import Any, ClassVar, Dict, List, Optional

logger = logging.getLogger("nerddiary.bot.config")


class BotConfig(BaseSettings):
    _config_file_path: ClassVar[str] = ""
    bot_debug: bool = False
    admins: List[int] = []
    user_conf_path: DirectoryPath
    default_timezone: TimeZone
    question_types: Optional[Dict[str, QuestionType]]
    default_user: Optional[User]
    _data_provider: DataProvider = PrivateAttr()
    data_provider_name: str = Field(
        default="sqllite", description="Data provider to use to srote poll answers"
    )
    """ Data provider to use to srote poll answers """

    data_provider_params: Dict[str, Any] | None = {"base_path": "data"}
    reminder_time: Optional[datetime.time] = Field(
        description="Poll auto-reminder time in user local time zone"
    )
    """ Poll auto-reminder time in user local time zone """
    conversation_timeout: Optional[datetime.timedelta] = Field(
        default=datetime.timedelta(minutes=5),
        description="Timeout for conversation expressed in timedelta (see https://pydantic-docs.helpmanual.io/usage/types/#datetime-types for supported formats)",
    )
    """ Timeout for conversation expressed in timedelta (see https://pydantic-docs.helpmanual.io/usage/types/#datetime-types for supported formats) """

    @validator("data_provider_name")
    def data_provider_must_be_supported(cls, v):
        if v not in DataProvider.supported_providers:
            raise ValueError(f"Data provider <{v}> is not supported")

        return v

    def __init__(self, **data) -> None:
        super().__init__(**data)

        self._data_provider = DataProvider.get_data_provider(
            self.data_provider_name, self.data_provider_params
        )

    class Config:
        title = "Bot Configuration"
        extra = "forbid"
        env_prefix = "NERDDIARY_"

    @classmethod
    def load_config(cls, config_file_path: str | None = None) -> BotConfig:
        if config_file_path:
            cls._config_file_path = config_file_path

        logger.debug(f"Reading config file at: {cls._config_file_path}")

        bot_config_raw = ""

        try:
            with open(cls._config_file_path) as json_data_file:
                config_raw = json.load(json_data_file)
                bot_config_raw = config_raw.get("bot", None)

                if not bot_config_raw:
                    raise ValueError("Invalid configuration file. 'Bot' key is missing")

        except OSError:
            logger.error(
                f"File at '{cls._config_file_path}' doesn't exist or can't be open"
            )

            raise ValueError(
                f"File at '{cls._config_file_path}' doesn't exist or can't be open"
            )

        return cls.parse_obj(bot_config_raw)


if __name__ == "__main__":
    try:
        conf = BotConfig.load_config("./testdata/bot_config_test.json")
    except ValidationError as e:
        print(e)
        exit(0)

    print(conf)
    # print(BotConfig.schema_json(indent=2))
