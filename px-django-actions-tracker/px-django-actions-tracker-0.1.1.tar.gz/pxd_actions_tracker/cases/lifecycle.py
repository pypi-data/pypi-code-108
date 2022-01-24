from typing import List, Optional
import threading
from uuid import uuid4, UUID
from datetime import datetime, timezone

from ..conf import settings
from ..const import TRACKING, LogOperate
from ..signals import log_created


__all__ = 'log', 'commit_log', 'create_log',


def log(
    domain: str,
    message: str = '',
    tracking: Optional[List[str]] = None,
    detail: Optional[dict] = None,
    operate: Optional[LogOperate] = None,
) -> UUID:
    id = uuid4()
    detail = {} if detail is None else detail
    tracking = TRACKING.get() if tracking is None else tracking
    created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

    commit_log(
        operate=settings.OPERATE if operate is None else operate,
        kwargs={
            'id': id,
            'domain': domain,
            'tracking': tracking,
            'message': message,
            'detail': detail,
            'created_at': created_at
        }
    )

    return id


def commit_log(
    operate, args: list = [], kwargs: dict = {}
):
    if LogOperate.STRAIGHT == operate:
        return create_log(*args, **kwargs)

    if LogOperate.THREADING == operate:
        thread = threading.Thread(
            target=create_log,
            name='Logger',
            args=args,
            kwargs=kwargs,
            daemon=True
        )
        thread.start()


def create_log(id, domain, tracking, message, detail, created_at):
    instance = settings.get_saver()(
        id=id,
        domain=domain,
        tracking=tracking,
        message=message,
        detail=detail,
        created_at=created_at
    )
    log_created.send(settings.SAVER, instance=instance)

    return instance
