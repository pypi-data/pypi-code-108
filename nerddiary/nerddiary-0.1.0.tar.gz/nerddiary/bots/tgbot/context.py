from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr
from telegram.ext import JobQueue

from .model import User, Poll
from .workflow import BotWorkflow
from .data import DataConnection

from typing import Dict


class ChatContext(BaseModel):
    """Context used for chat_data within a single chat"""

    chat_id: int
    config: User
    username: str | None
    job_queue: JobQueue | None
    data_connection: DataConnection = Field(
        exclude=True
    )  # do not dump cause it stores password
    active_messages: Dict[int, MessageContext] = PrivateAttr(default={})
    jobs: Dict[str, ChatJobContext] = PrivateAttr(default={})
    poll_last_timestamps: Dict[str, datetime] = PrivateAttr(default={})


class JobContext(BaseModel, ABC):
    @property
    @abstractmethod
    def job_key(self) -> str:
        pass


class ChatJobContext(JobContext):
    """Context used for jobs related to a single chat"""

    chat_context: ChatContext
    job_name: str

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.chat_context.jobs[self.job_key] = self

    @property
    def job_key(self) -> str:
        return str(self.chat_id) + "_" + self.job_name

    # Convenience propoerties
    @property
    def chat_id(self) -> int:
        return self.chat_context.chat_id

    @property
    def username(self) -> str | None:
        return self.chat_context.username


class NewPollJobContext(ChatJobContext):
    """Special job context used for initiating a new poll"""

    poll_key: str


class ActivePollJobContext(ChatJobContext):
    """Special job context used for jobs within an active poll (e.g. delays)"""

    active_poll: ActivePollContext


class MessageContext(BaseModel):
    """Context used for particular message within a single chat."""

    chat_context: ChatContext
    from_callback: bool
    message_id: int


class NewPollContext(MessageContext):
    poll_key: str


class ActivePollContext(MessageContext):
    poll_key: str
    poll_config: Poll = Field(repr=False)
    poll_workflow: BotWorkflow | None = Field(default=None, repr=False)
    cancelled: bool = False
    delay_job_context: ActivePollJobContext | None = None

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.chat_context.active_messages[self.message_id] = self

        if not self.poll_workflow:
            self.reset_workflow()

    def reset_workflow(self) -> None:
        self.poll_workflow = BotWorkflow(
            self.poll_config, self.chat_context.config  # type:ignore
        )

    def replace_message(self, message_id: int):
        if self.message_id != message_id:
            self.chat_context.active_messages[message_id] = self
            del self.chat_context.active_messages[self.message_id]
            self.message_id = message_id
