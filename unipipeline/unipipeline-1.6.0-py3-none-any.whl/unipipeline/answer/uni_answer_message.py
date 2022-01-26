from datetime import datetime
from typing import TypeVar, Generic, Type, Optional, Dict, Any
from uuid import UUID

from unipipeline.errors.uni_payload_error import UniAnswerPayloadParsingError
from unipipeline.message.uni_message import UniMessage
from unipipeline.message_meta.uni_message_meta import UniMessageMeta

TMessage = TypeVar('TMessage', bound=UniMessage)


class UniAnswerMessage(Generic[TMessage]):

    def __init__(self, meta: UniMessageMeta, message_payload_type: Type[TMessage]) -> None:
        self._meta = meta
        self._message_payload_type = message_payload_type
        self._message_payload_cache: Optional[TMessage] = None

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
    def raw_payload(self) -> Dict[str, Any]:
        return self._meta.payload

    @property
    def payload(self) -> TMessage:
        if isinstance(self._message_payload_cache, UniMessage):
            return self._message_payload_cache  # type: ignore

        try:
            self._message_payload_cache = self._message_payload_type(**self._meta.payload)  # type: ignore
        except Exception as e:  # noqa
            raise UniAnswerPayloadParsingError(str(e))

        assert self._message_payload_cache is not None

        return self._message_payload_cache
