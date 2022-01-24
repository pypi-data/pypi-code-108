import logging
from ..circuit import Circuit
from bosch_thermostat_client.const import (
    DHW,
    STATUS,
    DEFAULT_MIN_TEMP,
    MIN_REF,
    DEFAULT_MAX_TEMP,
    MAX_REF,
    HA_NAME,
    RESULT,
    VALUE,
    URI,
    MIN_VALUE,
    MAX_VALUE,
    OFF,
    MODE_TO_SETPOINT,
)


from bosch_thermostat_client.const.nefit import (
    CIRCUIT_TYPES,
)

from bosch_thermostat_client.operation_mode.nefit_dhw import NefitDhwOperationModeHelper

_LOGGER = logging.getLogger(__name__)


class NefitCircuit(Circuit):
    def __init__(self, connector, attr_id, db, _type, bus_type, current_date, **kwargs):
        super().__init__(connector, attr_id, db, CIRCUIT_TYPES[_type], bus_type)
        if _type == DHW:
            self._op_mode = NefitDhwOperationModeHelper(
                self.name, self._db.get(MODE_TO_SETPOINT)
            )

    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._state:
            return True if self.get_value(STATUS) else False

    @property
    def min_temp(self):
        """Retrieve minimum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MIN_TEMP
        else:
            return self.get_property(self._db[MIN_REF]).get(MIN_VALUE, DEFAULT_MIN_TEMP)

    @property
    def max_temp(self):
        """Retrieve maximum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MAX_TEMP
        else:
            return self.get_property(self._db[MAX_REF]).get(MAX_VALUE, DEFAULT_MAX_TEMP)

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        if self._op_mode.is_off:
            self._target_temp = 0
            return self._target_temp
        if self._temp_setpoint:
            target_temp = self.get_value(self._temp_setpoint, 0)
            if target_temp > 0:
                self._target_temp = target_temp
                return self._target_temp

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        if self._op_mode.is_off:
            return False
        if self.min_temp < temperature < self.max_temp and target_temp != temperature:
            if self._temp_setpoint:
                target_uri = self._data[self._temp_setpoint][URI]
            if not target_uri:
                _LOGGER.debug("Not setting temp. Don't know how")
                return False
            result = await self._connector.put(target_uri, temperature)
            _LOGGER.debug("Set temperature for %s with result %s", self.name, result)
            if result:
                if self._temp_setpoint:
                    self._data[self._temp_setpoint][RESULT][VALUE] = temperature
                return True
        _LOGGER.error(
            "Setting temperature not allowed in this mode. Temperature is probably out of range MIN-MAX!"
        )
        return False

    @property
    def schedule(self):
        """Nefit doesn't use schedule or/and don't need it."""
        return None

    @property
    def ha_modes(self):
        """Retrieve HA modes."""
        return [v[HA_NAME] for v in self._hastates]

    @property
    def setpoint(self):
        """
        Retrieve setpoint in which is currently Circuit.
        Might be equal to operation_mode, might me taken from schedule.
        """
        if self._op_mode.is_off:
            return OFF
        if self._op_mode.is_manual:
            return self._op_mode.current_mode

    @property
    def support_target_temp(self):
        return False
