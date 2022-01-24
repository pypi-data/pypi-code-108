from .base import OperationModeHelper
from bosch_thermostat_client.const import MANUAL, SETPOINT, USED, VALUE
from bosch_thermostat_client.const.easycontrol import TARGET_TEMP


class EasyControlOperationModeHelper(OperationModeHelper):
    @property
    def available_modes(self):
        """Get Bosch operations modes."""
        return ["clock", "manual"]

    @property
    def mode_type(self):
        """Check if operation mode type is manual or auto."""
        if self._operation_mode.get(USED, True) != "false":
            return super().mode_type
        return MANUAL

    @property
    def current_mode(self):
        """Retrieve current mode of Circuit."""
        if self._operation_mode.get(USED, True) != "false":
            return self._operation_mode.get(VALUE, None)
        return MANUAL

    def temp_setpoint_read(self, mode=None):
        """Check which temp property to use. Key READ or WRITE"""
        if self.is_auto:
            return TARGET_TEMP
        mode = self.current_mode if not mode else mode
        return self._mode_to_setpoint.get(mode, {}).get(SETPOINT)
