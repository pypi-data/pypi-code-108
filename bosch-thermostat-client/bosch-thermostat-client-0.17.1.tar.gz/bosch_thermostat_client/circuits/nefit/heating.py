import logging
from .base import NefitCircuit
from bosch_thermostat_client.const import RESULT, VALUE, URI, ON, WRITE
from bosch_thermostat_client.const.nefit import MANUAL_OVERRIDE, MANUAL_STATUS
from bosch_thermostat_client.exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


class NefitHeatingCircuit(NefitCircuit):
    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        manual_override = False
        if self._op_mode.is_off:
            return False
        if self.min_temp < temperature < self.max_temp and target_temp != temperature:
            if self._op_mode.is_auto:
                target_uri = self._data[MANUAL_OVERRIDE][URI]
                manual_override = self._data[MANUAL_STATUS][URI]
            else:
                temp_setpoint = self._op_mode.temp_setpoint(setpoint_type=WRITE)
                target_uri = self._data[temp_setpoint][URI]
            if not target_uri:
                _LOGGER.debug("Not setting temp. Don't know how")
                return False
            result = await self._connector.put(target_uri, temperature)
            if manual_override:
                await self._connector.put(manual_override, ON)
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
    def support_target_temp(self):
        return True

    async def update_temp_after_ha_mode(self, old_setpoint, new_mode, old_mode):
        """Helper to fetch new temp. attribute if operation mode was changed."""
        different_mode = new_mode != old_mode
        try:
            if (
                different_mode
                and old_setpoint != self._temp_setpoint
                and self._op_mode.is_auto
            ):
                result = await self._connector.get(self._data[self._temp_setpoint][URI])
                self.process_results(result, self._temp_setpoint)
        except DeviceException as err:
            _LOGGER.debug(f"Can't update data for mode {new_mode}. Error: {err}")
            pass
        if different_mode:
            return 1
        return 0
