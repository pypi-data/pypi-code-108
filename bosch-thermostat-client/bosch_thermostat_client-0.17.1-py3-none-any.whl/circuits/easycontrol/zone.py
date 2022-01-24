from .base import EasycontrolCircuit
from bosch_thermostat_client.const import (
    HVAC_ACTION,
    HVAC_HEAT,
    HVAC_OFF,
    NAME,
    STATUS,
    MODE_TO_SETPOINT,
    ID,
    ACTIVE_PROGRAM,
    URI,
)
from bosch_thermostat_client.operation_mode import EasyControlOperationModeHelper
from bosch_thermostat_client.const.easycontrol import IDLE


class EasyZoneCircuit(EasycontrolCircuit):
    def __init__(
        self, connector, attr_id, db, _type, bus_type, current_date=None, **kwargs
    ):
        super().__init__(
            connector=connector,
            attr_id=attr_id,
            db=db,
            _type=_type,
            bus_type=bus_type,
            current_date=current_date,
        )
        self._op_mode = EasyControlOperationModeHelper(
            self.name, self._db.get(MODE_TO_SETPOINT)
        )

        self._zone_program = kwargs.get("zone_program")

    @property
    def name(self):
        name = self.get_value(NAME)
        return name if name else super().name

    @property
    def schedule(self):
        """Easy control might not need schedule."""
        return None

    async def initialize(self):
        """Check each uri if return json with values."""
        await self.update_requested_key(STATUS)
        await self.update_requested_key(NAME)

    async def update(self):
        await self._zone_program.update()
        await super().update()

    @property
    def hvac_action(self):
        hvac_uri = self._db.get(HVAC_ACTION)
        if hvac_uri:
            hv_value = self.get_value(hvac_uri)
            if hv_value == IDLE:
                return HVAC_OFF
            else:
                return HVAC_HEAT

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        if self._op_mode.is_off:
            self._target_temp = 0
            return self._target_temp
        target_temp = self.get_value(self._op_mode.temp_setpoint_read(), 0)
        if target_temp > 0:
            self._target_temp = target_temp
            return self._target_temp

    @property
    def support_presets(self):
        if self._op_mode.is_auto and self._zone_program.preset_names:
            return True
        return False

    @property
    def preset_modes(self):
        return self._zone_program.preset_names

    def get_activeswitchprogram(self):
        """
        Retrieve active program from thermostat.
        If ActiveSwitch program is not present
        then take first one from the list from result.
        """
        if len(self._program_list) > 0:
            active_id = self.get_value(ACTIVE_PROGRAM)
            for program in self._program_list:
                if active_id == program[ID]:
                    return program[NAME]

    @property
    def preset_mode(self):
        return self._zone_program.preset_name(self.get_value(ACTIVE_PROGRAM))

    async def set_preset_mode(self, preset_mode):
        preset_id = self._zone_program.get_preset_index_by_name(preset_mode)
        if not preset_id:
            return
        act_program = self._data.get(ACTIVE_PROGRAM, {})
        active_program_uri = act_program[URI]
        result = await self._connector.put(active_program_uri, preset_id)
        await self.update_requested_key(ACTIVE_PROGRAM)
        return result
