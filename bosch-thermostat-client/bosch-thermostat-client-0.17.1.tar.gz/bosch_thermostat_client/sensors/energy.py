import logging
from bosch_thermostat_client.const import (
    RESULT,
    URI,
    VALUE,
)
from bosch_thermostat_client.const.easycontrol import ENERGY, PAGINATION, USED
from .sensor import Sensor
from bosch_thermostat_client.exceptions import DeviceException

from datetime import timedelta

_LOGGER = logging.getLogger(__name__)


class EnergySensor(Sensor):
    def __init__(self, **kwargs):
        self._pagination_uri = kwargs.get(PAGINATION)
        self._page_number = None
        super().__init__(**kwargs)

    @property
    def kind(self):
        return ENERGY

    def process_results(self, result, time):
        """Convert multi-level json object to one level object."""

        def get_last_day():
            return time - timedelta(days=1)

        if result and VALUE in result:
            last_reset = get_last_day()
            day = last_reset.strftime("%d-%m-%Y")
            for row in reversed(result[VALUE]):
                if row["d"] == day:
                    self._data[self.attr_id][RESULT][VALUE] = row
                    self._data[self.attr_id][RESULT]["last_reset"] = last_reset.replace(
                        hour=23, minute=59, second=59, microsecond=0
                    )
                    return True

    @property
    def state(self):
        """Retrieve state of the record sensor."""
        return self._data[self.attr_id].get(RESULT, {}).get(VALUE)

    def build_uri(self):
        return f"{self._data[self.attr_id][URI]}?entry={int(self._page_number - 1)}"

    async def update(self, time=None):
        """Update info about Recording Sensor asynchronously."""
        try:
            pagination = await self._connector.get(self._pagination_uri)
            used = pagination.get(USED, False)
            if used == "true":
                self._page_number = pagination.get(VALUE, self._page_number)
        except DeviceException:
            pass
        try:
            if self._page_number:
                result = await self._connector.get(self.build_uri())
                self.process_results(result, time)
        except DeviceException as err:
            _LOGGER.error(
                f"Can't update data for {self.name}. Trying uri: {self._data[URI]}. Error message: {err}"
            )
            self._extra_message = f"Can't update data. Error: {err}"
