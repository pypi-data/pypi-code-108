""" Poll models """

from __future__ import annotations
from glob import glob
import re
from pydantic import BaseModel, ValidationError, validator, root_validator, constr
import logging
import json
from pydantic.fields import Field, ModelField, PrivateAttr
import datetime
import itertools
from copy import deepcopy
from typing import Any, ClassVar, Dict, List, Optional, Union
from .primitives import TimeZone, ValueLabel

logger = logging.getLogger("nerddiary.bot.model")


class Poll(BaseModel):
    """Represents a single poll"""

    poll_name: constr(strip_whitespace=True, max_length=30) = Field(description="This polls user facing name")  # type: ignore # noqa: F722
    """ This polls user facing name """

    command: constr(strip_whitespace=True, max_length=32, regex=r"^[\da-z_]{1,32}$") = Field(default=None, description="Command for user call in a bot")  # type: ignore # noqa: F722

    description: str | None = Field(description="Poll long description", max_length=100)

    reminder_time: Optional[datetime.time] = Field(
        description="Poll auto-reminder time in user local time zone"
    )
    """ Poll auto-reminder time in user local time zone """

    questions: Dict[str, Question] = Field(
        description="Dictionary of polls questions. Question may either be given a type from a type definitions or system types, or an inline dict of selectable values"
    )
    """ Dictionary of polls questions. Question may either be given a type from a type definitions or system types, or an inline dict of selectable values """

    once_per_day: bool = Field(
        default=True, description="Whether this poll can only be asked once a day"
    )
    """ Whether this poll can only be asked once a day """

    hours_over_midgnight: Optional[int] = Field(
        default=3,
        description="For once per day polls - if poll timestamps if < `hours_over_midgnight`AM set it to previous day",
    )
    """ For once per day polls - if poll timestamps if < `hours_over_midgnight`AM set it to previous day """

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        if not self.command and re.match(
            r"^[\da-z_]{1,32}$", re.sub(r"\s+", "_", self.poll_name)
        ):
            self.command = re.sub(r"\s+", "_", self.poll_name)

    @validator("questions")
    def at_least_one_question_exist(cls, v):
        if len(v) == 0:
            raise ValueError("At least one question must be defined for a poll")

        return v

    @validator("questions")
    def dependant_question_must_exist(cls, v: Dict[str, Question]):
        # Check that dependant question exists and has already been processed (comes earlier)
        previous = []
        for name, question in v.items():
            if question.depends_on and question.depends_on not in previous:
                raise ValueError(
                    f"Question <{name}> depends on <{question.depends_on}> which is either not defined, or goes after this question"
                )

            previous.append(name)

        return v

    @validator("hours_over_midgnight")
    def check_once_per_day(cls, v, values: Dict[str, Any]):
        if not values["once_per_day"] and v:
            raise ValueError(
                "`hours_over_midgnight` can only be set for `once_per_day` polls"
            )

        return v


class Report(BaseModel):
    pass


class User(BaseModel):
    id: int = Field(description="This user id")
    config_file_path: str = Field(description="Path to config file")
    encrypt_data: bool = Field(
        True, description="Whether poll data should be stored encrypted"
    )
    timezone: Optional[TimeZone]
    question_types: Optional[Dict[str, QuestionType]]
    polls: Optional[Dict[str, Poll]]
    reports: Optional[Dict[str, Report]]

    @validator("question_types", each_item=True)
    def type_definitions_minimal_fields(cls, v: QuestionType):
        if not v._system and not v.select:
            raise ValueError("Type definition is missing a select list")

        return v

    @validator("question_types")
    def system_type_names_may_not_be_used(cls, v: Dict[str, QuestionType]):
        for name in v:
            if name in SystemQuestionType.get_system_types_def():
                raise ValueError(f"System type <{name}> can't be redefined")

        return v

    @validator("polls", each_item=True)
    def convert_reminder_times_to_local_if_set(cls, v: Poll, values: Dict[str, Any]):
        if v.reminder_time:
            v.reminder_time = v.reminder_time.replace(tzinfo=values["timezone"])

        return v

    @validator("polls", each_item=True)
    def question_type_check_and_inject(cls, v: Poll, values: Dict[str, Any]):
        for question in v.questions.values():
            # If type was set - injecting from type definition
            if question.type:
                sys_type_defs = SystemQuestionType.get_system_types_def()

                custom_type_defs: Dict[str, QuestionType] = values.get(
                    "question_types", None
                )
                if custom_type_defs:
                    type_defs = sys_type_defs | custom_type_defs
                else:
                    type_defs = sys_type_defs

                if not type_defs:
                    raise ValueError("No type definitions exist. Not even system ones")

                q_type = type_defs.get(question.type, None)
                if not q_type:
                    raise ValueError(
                        f"Type definition for <{question.type}> is missing"
                    )

                for field in q_type.__fields_set__:
                    setattr(question, field, deepcopy(getattr(q_type, field)))

                question._must_depend = q_type._must_depend

        return v

    @validator("polls", each_item=True)
    def check_depends_on_supported_type(cls, v: Poll, values: Dict[str, Any]):
        for name, question in v.questions.items():
            # If type was set - injecting from type definition
            if question.depends_on:

                if not question.check_dependant_type(v.questions[question.depends_on]):
                    raise ValueError(
                        f"Question <{name}> is of type that can't depend on question <{question.depends_on}>"
                    )

                if not question._must_depend:
                    raise ValueError(
                        f"Question <{name}> depends on <{question.depends_on}> but is not of a type that can be dependant"
                    )

        return v

    @validator("polls")
    def validate_and_add_unique_question_selects_keys(
        cls, v: Dict[str, Poll], values: Dict[str, Any]
    ):
        # Used to assign unique keys to all answer keys across all polls
        callback_counter = itertools.count()
        for poll in v.values():
            # Used to set _order field for a question
            question_counter = itertools.count()

            for name, question in poll.questions.items():
                # Add unique counter to answer keys, used for callback data (see process_select handler)
                if not question.depends_on and question.select:
                    new_select = {}

                    for sel_name, sel_val in question.select.items():
                        new_key = str(next(callback_counter)) + "_" + sel_name
                        new_select[new_key] = ValueLabel(  # type: ignore
                            value=sel_name, label=sel_val.label  # type: ignore
                        )  # type: ignore

                        if question.delay_on and sel_name in question.delay_on:
                            question.delay_on.remove(sel_name)
                            question.delay_on.append(new_key)

                    question.select = new_select
                elif question.select:

                    # Get all possible answers from dependant question, check we have select for its original value and replace dict key
                    if poll.questions[question.depends_on].depends_on:  # type: ignore
                        # We can't immediatelly delete old keys, because multiple dependant answers can have same value, but will have different key
                        postponed_delete = set()

                        for sub_answer in poll.questions[
                            question.depends_on
                        ].select.values():  # type: ignore
                            for a_name, answer in sub_answer.items():  # type: ignore
                                if answer.value not in question.select:  # type: ignore
                                    raise ValueError(
                                        f"Question <{name}> depends on <{question.depends_on}> but doesn't have selects for answer <{a_name}> from dependant question"
                                    )
                                else:
                                    # Replace key
                                    question.select[a_name] = question.select[  # type: ignore
                                        answer.value
                                    ]  # type: ignore

                                    postponed_delete.add(answer.value)

                        # Now delete old keys
                        for del_key in postponed_delete:
                            del question.select[del_key]

                    else:
                        for a_name, answer in poll.questions[
                            question.depends_on
                        ].select.items():  # type: ignore
                            if answer.value not in question.select:  # type: ignore
                                raise ValueError(
                                    f"Question <{name}> depends on <{question.depends_on}> but doesn't have selects for answer <{a_name}> from dependant question"
                                )
                            else:
                                # Replace key
                                question.select[a_name] = question.select[  # type: ignore
                                    answer.value  # type: ignore
                                ]

                                del question.select[answer.value]  # type: ignore

                    # We can't immediatelly delete old keys for delay list, because we are chaning current select keys on the fly
                    postponed_delete_delay_keys = set()

                    for sub_name, sub_select in question.select.items():
                        new_select = {}

                        for sel_name, sel_val in sub_select.items():  # type: ignore
                            new_key = str(next(callback_counter)) + "_" + sel_name
                            new_select[new_key] = ValueLabel(
                                value=sel_name, label=sel_val.label
                            )
                            if question.delay_on and sel_name in question.delay_on:
                                postponed_delete_delay_keys.add(sel_name)
                                question.delay_on.append(new_key)

                        question.select[sub_name] = new_select  # type: ignore

                    if postponed_delete_delay_keys:
                        question.delay_on = list(
                            set(question.delay_on) - postponed_delete_delay_keys  # type: ignore
                        )

                # Check we actually have keys to delay on
                if question.delay_on:
                    all_exist = False
                    if question.depends_on:
                        all_exist = all(
                            map(
                                lambda x: x
                                in list(
                                    itertools.chain(
                                        *[
                                            list(sub_a.keys())  # type: ignore
                                            for sub_a in question.select.values()
                                        ]
                                    )
                                ),
                                question.delay_on,
                            )
                        )
                    else:
                        all_exist = all(
                            map(lambda x: x in question.select, question.delay_on)  # type: ignore
                        )

                    if not all_exist:
                        raise ValueError(
                            f"Question <{name}> should delay on <{question.delay_on}> but some of these values are not in select"
                        )

                question._order = next(question_counter)

        return v

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
