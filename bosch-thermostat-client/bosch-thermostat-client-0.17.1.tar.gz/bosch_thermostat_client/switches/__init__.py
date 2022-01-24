"""
Switches of Bosch thermostat.
"""
from bosch_thermostat_client.const import (
    ID,
    NAME,
    TYPE,
    NUMBER,
    TURN_ON,
    TURN_OFF,
    BINARY,
)
from bosch_thermostat_client.const.ivt import ALLOWED_VALUES
from bosch_thermostat_client.const.easycontrol import USED, BOOLEAN, FALSE, TRUE
from bosch_thermostat_client.helper import BoschEntities

from bosch_thermostat_client.exceptions import DeviceException
from .switch import Switch
from .boolean import BinarySwitch
from .number import NumberSwitch


class Switches(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, uri_prefix=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._connector = connector
        super().__init__(connector.get)
        self._items = {}
        self._number_switches = {}
        self._uri_prefix = uri_prefix

    async def initialize(self, switches):
        if not switches:
            return

        def get_switch_type(switch, retrieved):
            if ALLOWED_VALUES in retrieved:
                return self._items, Switch
            elif switch.get(TYPE, False) == BINARY and (
                retrieved.get(USED, False) or switch.get(TURN_ON)
            ):
                return self._items, BinarySwitch
            elif switch.get(TYPE, False) == NUMBER:
                return self._number_switches, NumberSwitch
            return None, None

        for switch_id, switch in switches.items():
            try:
                uri = (
                    f"{self._uri_prefix}/{switch[ID]}"
                    if self._uri_prefix
                    else switch[ID]
                )
                retrieved = await self._get(uri)

                items, ChoosenSwitch = get_switch_type(
                    switch=switch, retrieved=retrieved
                )
                if items is not None and ChoosenSwitch:
                    items[switch_id] = ChoosenSwitch(
                        connector=self._connector,
                        attr_id=switch_id,
                        name=switch[NAME],
                        path=uri,
                        result=retrieved,
                        on_turn_on=switch.get(TURN_ON, TRUE),
                        on_turn_off=switch.get(TURN_OFF, FALSE),
                    )
            except DeviceException:
                pass

    def __iter__(self):
        return iter(self._items.values())

    @property
    def switches(self):
        """Get switches list."""
        return self.get_items().values()

    @property
    def number_switches(self):
        """Get number switches."""
        return self._number_switches.values()
