"""
Class to control /program/list in EasyControl.
"""
from datetime import datetime, timedelta
from bosch_thermostat_client.const import NAME, ID, VALUE
from bosch_thermostat_client.helper import check_base64


class ZonePrograms:
    def __init__(self, program_uri, connector):
        self._last_updated = None
        self._program_uri = program_uri
        self._connector = connector
        self._programs = {}

    async def update(self):
        now = datetime.now()
        if self._last_updated and now - self._last_updated < timedelta(minutes=10):
            return
        res = await self._connector.get(self._program_uri)
        program_list = res.get(VALUE, [])
        for item in program_list:
            name = check_base64(item[NAME])
            self._programs[item[ID]] = name if name else item[ID]
        self._last_updated = datetime.now()

    @property
    def preset_names(self):
        return list(self._programs.values())

    def preset_name(self, active_program):
        return self._programs.get(active_program)

    def get_preset_index_by_name(self, name):
        for id, program_name in self._programs.items():
            if program_name == name:
                return id
