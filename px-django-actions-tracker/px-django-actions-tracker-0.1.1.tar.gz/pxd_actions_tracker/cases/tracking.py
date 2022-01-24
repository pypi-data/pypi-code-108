from uuid import uuid4
from contextlib import ContextDecorator

from ..const import TRACKING
from ..signals import tracking_enter, tracking_exit


__all__ = 'track', 'uuid_track',


class track(ContextDecorator):
    def __init__(self, tracking_code: str):
        assert tracking_code != '', (
            'Tracking code must be anything useful, not just an empty string.'
        )

        self.tracking_code = tracking_code
        self.token = None

    def __enter__(self):
        current = TRACKING.get() or []

        self.token = TRACKING.set(current + [self.tracking_code])
        tracking_enter.send(self, code=self.tracking_code)

        return self

    def __exit__(self, *exc):
        TRACKING.reset(self.token)
        tracking_exit.send(self, code=self.tracking_code)

        return False


def uuid_track(*args, **kwargs):
    return track(str(uuid4()), *args, **kwargs)
