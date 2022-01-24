import logging
from ..circuit import Circuit
from bosch_thermostat_client.const import (
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
    USED,
)

_LOGGER = logging.getLogger(__name__)


from bosch_thermostat_client.const.easycontrol import CIRCUIT_TYPES


class EasycontrolCircuit(Circuit):
    def __init__(self, connector, attr_id, db, _type, bus_type, **kwargs):
        super().__init__(connector, attr_id, db, CIRCUIT_TYPES[_type], bus_type)

    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._state:
            return self.get_value(STATUS, False)

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

    @property
    def support_target_temp(self):
        temp_setpoint = self.get_property(self._temp_setpoint)
        return temp_setpoint.get(USED, True) != "false"

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        if self._op_mode.is_off:
            return False
        if self.min_temp <= temperature <= self.max_temp and target_temp != temperature:
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
            else:
                _LOGGER.error("Don't get proper response from setting temperature.")
        else:
            _LOGGER.error(
                "Setting temperature not allowed in this mode. Temperature is probably out of range MIN-MAX!"
            )
        return False

    @property
    def schedule(self):
        """Easycontrol doesn't need schedule."""
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
    def support_charge(self):
        """Is DHW support charge."""
        return True
