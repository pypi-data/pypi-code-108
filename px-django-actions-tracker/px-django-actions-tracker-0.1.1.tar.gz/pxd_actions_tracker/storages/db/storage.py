from typing import List, Optional
from uuid import UUID
from px_domains import Domain
import datetime

from .models import Log
from .signals import log_stored


__all__ = 'save',


def save(
    id: UUID,
    domain: Domain,
    created_at: datetime.datetime,
    tracking: Optional[List[str]] = [],
    message: Optional[str] = '',
    detail: Optional[str] = '',
) -> Log:
    instance = Log.objects.create(
        id=id,
        domain=domain,
        tracking=tracking,
        message=message,
        detail=detail,
        created_at=created_at
    )

    log_stored.send(Log, instance=instance)

    return instance
