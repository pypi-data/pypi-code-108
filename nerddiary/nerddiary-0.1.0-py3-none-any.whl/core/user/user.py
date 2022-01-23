""" Poll models """

from __future__ import annotations
from glob import glob
from pydantic import BaseModel, ValidationError
import logging
import json
from pydantic.fields import Field
from typing import Any, Dict, Optional, List
from ..poll.primitives import TimeZone
from ..poll.poll import Poll
from ..report.report import Report

logger = logging.getLogger("nerddiary.bot.model")


class User(BaseModel):
    id: int = Field(description="This user id")
    username: str | None = Field(default=None, description="Optional user name")
    config_file_path: str = Field(description="Path to config file")
    encrypt_data: bool = Field(
        True, description="Whether poll data should be stored encrypted"
    )
    timezone: Optional[TimeZone]
    polls: Optional[List[Poll]]
    reports: Optional[List[Report]]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        # convert_reminder_times_to_local_if_set
        if self.polls:
            for poll in self.polls:
                if poll.reminder_time:
                    poll.reminder_time = poll.reminder_time.replace(
                        tzinfo=self.timezone
                    )

    @classmethod
    def from_file(
        cls,
        id: int,
        config_file_path: str,
        default_timezone: TimeZone,
        ext_question_types: Dict[str, QuestionType] | None,
    ) -> User:

        logger.debug(f"Reading user config file at: {config_file_path}")

        # Adding chat_id to config
        config = {"id": id, "config_file_path": config_file_path}

        try:
            with open(config_file_path) as json_data_file:
                config |= json.load(json_data_file)
        except OSError:
            logger.error(f"File at '{config_file_path}' doesn't exist or can't be open")

            raise ValueError(
                f"File at '{config_file_path}' doesn't exist or can't be open"
            )

        # If timezone not set, use the default one
        if config.get("timezone", None) is None:
            config["timezone"] = default_timezone.tzname

        # If question types passed, add them
        if ext_question_types:
            if not config.get("question_types", None):
                config["question_types"] = {}

            config["question_types"] |= ext_question_types

        return cls.parse_obj(config)

    @classmethod
    def from_folder(
        cls,
        folder: str,
        default_timezone: TimeZone,
        ext_question_types: Dict[str, QuestionType] | None,
    ) -> Dict[int, User]:
        config_files = glob(f"{folder}/user_conf_*.json")

        ret = {}

        for config_file_path in config_files:
            id = int(config_file_path.split("_")[2][:-5])
            ret[id] = User.from_file(
                id,
                config_file_path,
                default_timezone,
                ext_question_types,
            )

        return ret

    class Config:
        title = "User Configuration"
        extra = "forbid"


if __name__ == "__main__":
    # print(User.schema_json(indent=2))

    try:
        from nerddiary.bot.config import BotConfig

        bot_conf = BotConfig.load_config("./testdata/bot_config_test.json")
        user_conf = User.from_folder(
            bot_conf.user_conf_path.name,
            bot_conf.default_timezone,
            bot_conf.question_types,
        )
    except ValidationError as e:
        print(e)
        exit(0)

    print(user_conf)
