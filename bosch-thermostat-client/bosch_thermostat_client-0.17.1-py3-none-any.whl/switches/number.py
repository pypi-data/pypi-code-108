import logging
from bosch_thermostat_client.const import (
    NUMBER,
    RESULT,
    URI,
    VALUE,
    UNITS,
    MAX_VALUE,
    MIN_VALUE,
)
from bosch_thermostat_client.helper import BoschSingleEntity
from .switch import BaseSwitch

_LOGGER = logging.getLogger(__name__)


class NumberSwitch(BaseSwitch, BoschSingleEntity):
    """Number switch object."""

    _type = NUMBER
    _allowed_types = NUMBER

    def check_state(self, value=0):
        return value

    @property
    def unit_of_measurement(self):
        return self.get_property(self.attr_id).get(UNITS)

    @property
    def max_value(self):
        return self.get_property(self.attr_id).get(MAX_VALUE, 100)

    @property
    def min_value(self):
        return self.get_property(self.attr_id).get(MIN_VALUE, 15)

    async def set_value(self, value):
        if self.min_value <= value <= self.max_value:
            _LOGGER.debug("Trying to set number %s.", value)
            await self._connector.put(self._data[self.attr_id][URI], value)
            self._data[self.attr_id][RESULT][VALUE] = value
            _LOGGER.debug("Device accepted new value %s.", value)
