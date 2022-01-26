import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel

from unipipeline.answer.uni_answer_params import UniAnswerParams
from unipipeline.message_meta.uni_message_meta_err import UniMessageMetaErr
from unipipeline.message_meta.uni_message_meta_error_topic import UniMessageMetaErrTopic


class UniMessageMeta(BaseModel):
    id: UUID
    date_created: datetime
    payload: Dict[str, Any]

    parent: Optional[Dict[str, Any]]
    error: Optional[UniMessageMetaErr]

    unwrapped: bool
    answer_params: Optional[UniAnswerParams]

    worker_creator: Optional[str]  # name of worker who created it

    ttl_s: Optional[int] = None

    class Config:
        frozen = True
        extra = 'forbid'

    @property
    def need_answer(self) -> bool:
        return self.answer_params is not None

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @staticmethod
    def create_new(data: Dict[str, Any], unwrapped: bool, answer_params: Optional[UniAnswerParams] = None, error: Optional[UniMessageMetaErr] = None) -> 'UniMessageMeta':
        return UniMessageMeta(
            id=uuid.uuid4(),
            date_created=datetime.now(),
            payload=data,
            parent=None,
            error=error,
            answer_params=answer_params,
            unwrapped=unwrapped,
        )

    def create_child(self, payload: Dict[str, Any], unwrapped: bool, answer_params: Optional[UniAnswerParams] = None) -> 'UniMessageMeta':
        return UniMessageMeta(
            id=uuid.uuid4(),
            date_created=datetime.now(),
            payload=payload,
            parent=self.dict(),
            unwrapped=unwrapped,
            answer_params=answer_params,
            error=None,
        )

    def create_error_child(self, error_topic: UniMessageMetaErrTopic, error: Exception) -> 'UniMessageMeta':
        return UniMessageMeta(
            id=self.id,
            date_created=self.date_created,
            payload=self.payload,
            parent=self.dict(),
            unwrapped=self.unwrapped,
            answer_params=self.answer_params,
            error=UniMessageMetaErr(
                error_topic=error_topic,
                error_type=type(error).__name__,
                error_message=str(error),
                retry_times=self.error.retry_times + 1 if self.error is not None else 0
            ),
        )
