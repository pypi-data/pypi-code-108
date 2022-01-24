__all__ = ["Attune"]

import asyncio
from typing import Dict, Any, List, Union, Optional

import attune  # type: ignore
import yaqc  # type: ignore
from yaqd_core import HasLimits, IsHomeable, HasPosition, IsDaemon


class Attune(HasLimits, IsHomeable, HasPosition, IsDaemon):
    _kind = "attune"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._instrument = attune.load(name)

        self._setables = dict()
        for k, v in config["setables"].items():
            if isinstance(v, int):
                self._setables[k] = yaqc.Client(v)
            else:
                host, port = v.split(":")
                self._setables[k] = yaqc.Client(port=int(port), host=host)

        self._delays = dict()
        for k, v in config["delays"].items():
            if isinstance(v, int):
                self._delays[k] = yaqc.Client(v)
            else:
                host, port = v.split(":")
                self._delays[k] = yaqc.Client(port=int(port), host=host)
            self._delays[k].set_control_tune(self.name, self._state["arrangement"])
            self._delays[k].set_control_position(self.name, self._state["position"])

        self._set_limits()
        self._units = "nm"

    def _set_position(self, position):
        self.set_position_except(position)

    def set_position_except(self, position, exceptions=None):
        self._busy = True
        self._state["destination"] = position
        self._state["position"] = position
        if exceptions is None:
            exceptions = []
        for name, set_pos in self._instrument(position, self._state["arrangement"]).items():
            if name in exceptions:
                continue
            if isinstance(set_pos, str):
                self._setables[name].set_identifier(set_pos)
            elif set_pos is None:
                pass  # discrete with no default, leave it where it is
            else:
                self._setables[name].set_position(set_pos)
        for delay in self._delays.values():
            delay.set_control_position(self.name, position)
        self._state["position"] = position

    def get_instrument(self):
        return self._instrument.as_dict()

    def set_instrument(self, instrument):
        self._busy = True
        self._instrument = attune.Instrument(**instrument)
        attune.store(self._instrument)
        self.shutdown(restart=True)

    def get_arrangement(self):
        return self._state["arrangement"]

    def set_arrangement(self, arrangement):
        if arrangement is not None and arrangement not in self._instrument.arrangements.keys():
            raise ValueError("Arrangement not found")
        self._busy = True
        self._state["arrangement"] = arrangement
        self._set_limits()
        for delay in self._delays.values():
            delay.set_control_tune(self.name, arrangement)

    def get_all_arrangements(self):
        return list(self._instrument.arrangements.keys())

    def get_setable_yaq_params(self):
        return self._config["setables"]

    def get_setable_names(self):
        return list(self._setables.keys())

    def get_delay_yaq_params(self):
        return self._config["delays"]

    def get_delay_names(self):
        return list(self._delays.keys())

    def set_setable_positions(self, setables):
        self._busy = True
        for name, set_pos in setables.items():
            if isinstance(set_pos, str):
                self._setables[name].set_identifier(set_pos)
            elif set_pos is None:
                pass  # discrete with no default, leave it where it is
            else:
                self._setables[name].set_position(set_pos)

    def get_setable_positions(self):
        return {k: v.get_position() for k, v in self._setables.items()}

    def home_setables(self, setables):
        self._busy = True
        for name in setables:
            if hasattr(self._setables[name], "home"):
                self._setables[name].home()

    def home(self):
        self._busy = True
        self.home_setables(self._setables.keys())

    def get_dependent_hardware(self):
        ret = {
            k: v if isinstance(v, str) else f"localhost:{v}"
            for k, v in self.get_setable_yaq_params().items()
        }
        ret.update(
            **{
                k: v if isinstance(v, str) else f"localhost:{v}"
                for k, v in self.get_delay_yaq_params().items()
            }
        )
        return ret

    def _set_limits(self):
        if self._state["arrangement"] is None:
            min_ = float(min(x.ind_min for x in self._instrument.arrangements.values()))
            max_ = float(max(x.ind_max for x in self._instrument.arrangements.values()))
            self._state["hw_limits"] = (min_, max_)
        else:
            self._state["hw_limits"] = (
                float(self._instrument.arrangements[self._state["arrangement"]].ind_min),
                float(self._instrument.arrangements[self._state["arrangement"]].ind_max),
            )

    async def update_state(self):
        """Continually monitor and update the current daemon state."""
        while True:
            self._busy = any(sa.busy() for sa in self._setables.values()) or any(
                de.busy() for de in self._delays.values()
            )
            if self._busy:
                await asyncio.sleep(0.1)
            else:
                await self._busy_sig.wait()
