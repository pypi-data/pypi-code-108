import logging

from bosch_thermostat_client.const import (
    NAME,
    RESULT,
    URI,
    REGULAR,
    VALUE,
)
from bosch_thermostat_client.exceptions import DeviceException
from bosch_thermostat_client.helper import check_base64

from .sensor import Sensor

_LOGGER = logging.getLogger(__name__)


class CrawlSensor(Sensor):
    def __init__(self, state=None, kind=REGULAR, **kwargs):
        self._kind = kind
        super().__init__(**kwargs)
        self._state_key = state

    @property
    def kind(self):
        return self._kind

    @property
    def name(self):
        name = self.get_value(NAME)
        return name if name else super().name

    async def update(self):
        """Update info about Crawl Sensor asynchronously."""

        def process_result(result):
            if len(result) == 1:
                for key, value in result[0].items():
                    result[0][key] = check_base64(value)
                if self._state_key:
                    result[0][VALUE] = result[0].get(self._state_key)
                return result[0]
            return result

        try:
            for key, item in self._data.items():
                result = await self._connector.get(item[URI])
                self._data[key][RESULT] = process_result(result.get(VALUE))
            self._state = True
        except DeviceException as err:
            _LOGGER.error(
                f"Can't update data for {self.name}. Trying uri: {item[URI]}. Error message: {err}"
            )
            self._state = False
            self._extra_message = f"Can't update data. Error: {err}"

    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._kind == "array" and self._state_key:
            return self._data[self.attr_id].get(RESULT).get(self._state_key)
        else:
            return super().state
