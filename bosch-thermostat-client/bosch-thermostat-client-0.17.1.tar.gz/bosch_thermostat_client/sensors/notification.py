from bosch_thermostat_client.db import get_ivt_errors
from bosch_thermostat_client.const.ivt import INVALID
from .sensor import Sensor
from bosch_thermostat_client.const import (
    RESULT,
    VALUE,
    VALUES,
)


class NotificationSensor(Sensor):
    errorcodes = get_ivt_errors()

    def process_results(self, result, key=None, return_data=False):
        """Convert multi-level json object to one level object."""
        data = {RESULT: {}} if return_data else self._data[key]
        updated = False
        if result:
            vals = result.get(VALUES, [])
            if vals:
                data[RESULT] = {}
                for idx, val in enumerate(vals):
                    if "ccd" in val:
                        ccd = str(val["ccd"])
                        key_suffix = "" if idx == 0 else "_" + idx
                        data[RESULT][VALUE + key_suffix] = self.errorcodes.get(
                            ccd, {"title": "Unknown error"}
                        )["title"]
                        data[RESULT]["errorCode" + key_suffix] = val["dcd"] + "-" + ccd
                        for key, description in self.errorcodes.get(ccd, {}).items():
                            if isinstance(description, list):
                                for alternative in description:
                                    for altkey in alternative:
                                        data[RESULT][
                                            key + key_suffix + "_" + altkey
                                        ] = alternative[altkey]
                            else:
                                data[RESULT][key + key_suffix] = description
                    else:
                        data[RESULT] = {VALUE: val}
            else:
                data[RESULT] = {VALUE: "No notifications"}
            self._update_initialized = True
            updated = True
        else:
            data[RESULT] = {VALUE: "Unknown"}
        return data[RESULT] if return_data else updated

    @property
    def state(self):
        """Retrieve state of the circuit."""
        result = self._data[self.attr_id].get(RESULT)
        if VALUE in result:
            return result.get(VALUE, INVALID)
        return result
