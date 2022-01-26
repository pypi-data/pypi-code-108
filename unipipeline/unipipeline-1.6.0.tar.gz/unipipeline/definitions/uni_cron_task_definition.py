from typing import Optional, Any, Dict
from uuid import UUID

from pydantic import root_validator, validator

from unipipeline.definitions.uni_definition import UniDefinition
from unipipeline.definitions.uni_worker_definition import UniWorkerDefinition


class UniCronTaskDefinition(UniDefinition):
    id: UUID
    name: str
    worker: UniWorkerDefinition
    when: Optional[str]
    every_sec: Optional[int]
    alone: bool

    @validator('every_sec')
    def validate_every_sec(cls, v: Optional[int], values: Dict[str, Any], **kwargs: Any) -> Optional[int]:
        if v is None:
            return v
        if not isinstance(v, int):
            TypeError('Invalid type. must be int')
        if v <= 1:
            raise ValueError('Must be > 1')
        if 60 % v:
            raise ValueError('60 must be a multiple of N')
        return v

    @root_validator()
    def validate_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        when = values.get('when', None)
        every_sec = values.get('every_sec', None)
        if not ((when is not None) ^ (every_sec is not None)):
            raise ValueError(f'cron "{values["name"]}" has property conflict in (when, every_sec). one from it must be None')
        return values
