"""
Operation mode helper for DHW.
"""
from bosch_thermostat_client.const import AUTO, MANUAL, USED, VALUE, ON, OFF
from .base import OperationModeHelper


class NefitDhwOperationModeHelper(OperationModeHelper):
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
        if self._operation_mode.get(VALUE, OFF) == ON:
            return MANUAL
        return AUTO
