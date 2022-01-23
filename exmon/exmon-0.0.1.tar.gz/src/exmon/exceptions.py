from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from exmon.services import Service


class ServiceExcpetion(Exception):
    """Exception raised when a service failed to send its data.

    Args:
        service (:obj:`Service`): the service that failed.
        exc (:obj:`BaseException`): exception that caused the service to fail.
    """

    def __init__(self, service: Service, exc: BaseException) -> None:
        super().__init__()
        self.service = service
        self.exc = exc

    def __str__(self) -> str:
        return f'{self.service._name} stopped: {str(self.exc)}'
