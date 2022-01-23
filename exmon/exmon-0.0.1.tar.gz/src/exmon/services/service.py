from exmon.alarm import Alarm
from exmon.exceptions import ServiceExcpetion


class Service:
    """ Base Class for Services. """

    # name of the service
    _name: str = 'BaseService'

    def __call__(self, data: Alarm) -> None:

        try:
            raise Exception(
                'This is the Base Service. It shouldnt be used in production!'
            )
        except Exception as exc:
            raise ServiceExcpetion(self, exc) from exc

    def __str__(self) -> str:
        """returns name of service."""
        return self._name
