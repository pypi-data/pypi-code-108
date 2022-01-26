from datetime import datetime
from typing import TypeVar, Optional, Generic, Type
from uuid import UUID

from unipipeline.errors.uni_payload_error import UniPayloadParsingError
from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager
from unipipeline.message.uni_message import UniMessage
from unipipeline.message_meta.uni_message_meta import UniMessageMeta

TInputMsgPayload = TypeVar('TInputMsgPayload', bound=UniMessage)
TAnswerMsgPayload = TypeVar('TAnswerMsgPayload', bound=Optional[UniMessage])


class UniWorkerConsumerMessage(Generic[TInputMsgPayload]):
    def __init__(self, message_input: Type[TInputMsgPayload], manager: UniBrokerMessageManager, meta: UniMessageMeta) -> None:
        self._message_manager = manager
        self._meta = meta
        self._message_input_payload_type = message_input
        self._message_payload_cache: Optional[TInputMsgPayload] = None
        self._acknowledged_or_rejected = False

    def ack(self) -> None:
        if not self._acknowledged_or_rejected:
            self._message_manager.ack()
            self._acknowledged_or_rejected = True

    def reject(self) -> None:
        if not self._acknowledged_or_rejected:
            self._message_manager.reject()
            self._acknowledged_or_rejected = True

    @property
    def id(self) -> UUID:
        return self._meta.id

    @property
    def date_created(self) -> datetime:
        return self._meta.date_created

    @property
    def worker_creator(self) -> Optional[str]:
        return self._meta.worker_creator

    @property
    def payload(self) -> TInputMsgPayload:
        if isinstance(self._message_payload_cache, UniMessage):
            return self._message_payload_cache  # type: ignore

        try:
            self._message_payload_cache = self._message_input_payload_type(**self._meta.payload)  # type: ignore
        except Exception as e:  # noqa
            raise UniPayloadParsingError(str(e))

        return self._message_payload_cache
