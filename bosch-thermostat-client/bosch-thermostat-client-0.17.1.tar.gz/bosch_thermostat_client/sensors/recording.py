import logging
from bosch_thermostat_client.const import (
    RESULT,
    URI,
    VALUE,
    INTERVAL,
    RECORDINGS,
    RECORDING,
    TEMP_CELSIUS,
    ENERGY_KILO_WATT_HOUR,
)
from .sensor import Sensor
from bosch_thermostat_client.exceptions import DeviceException

from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


class RecordingSensor(Sensor):
    def __init__(self, path, **kwargs):
        super().__init__(path=path, **kwargs)

        def unit_chooser():
            if any(x in path.lower() for x in ["energy", "power"]):
                return ENERGY_KILO_WATT_HOUR
            if any(x in path.lower() for x in ["temp", "outdoor"]):
                return TEMP_CELSIUS
            return None

        self._unit_of_measurement = unit_chooser()

    @property
    def kind(self):
        return RECORDINGS

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    def process_results(self, result, time):
        """Convert multi-level json object to one level object."""

        def get_last_full_hour():
            return time - timedelta(hours=1)

        if result and RECORDING in result:
            last_hour = get_last_full_hour()
            recording = result[RECORDING][last_hour.hour - 1]
            if recording["c"] == 0:
                return False
            self._data[self.attr_id][RESULT][VALUE] = round(
                (recording["y"] / recording["c"]), 1
            )
            self._data[self.attr_id][RESULT]["last_reset"] = last_hour.replace(
                minute=0, second=0, microsecond=0
            )
            return True

    @property
    def state(self):
        """Retrieve state of the record sensor."""
        return self._data[self.attr_id].get(RESULT, {}).get(VALUE)

    def build_uri(self, time):
        interval = (time - timedelta(hours=1)).strftime("%Y-%m-%d")
        return f"{self._data[self.attr_id][URI]}?{INTERVAL}={interval}"

    async def update(self, time=datetime.utcnow()):
        """Update info about Recording Sensor asynchronously."""
        try:
            result = await self._connector.get(self.build_uri(time))
            self.process_results(result, time)
        except DeviceException as err:
            _LOGGER.error(
                f"Can't update data for {self.name}. Trying uri: {self._data[URI]}. Error message: {err}"
            )
            self._extra_message = f"Can't update data. Error: {err}"
