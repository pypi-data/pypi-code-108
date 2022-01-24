__all__ = ["AttuneDelay"]

import asyncio
from typing import Dict, Any, List, Union

import attune  # type: ignore
import pint  # type: ignore
import yaqc  # type: ignore
from yaqd_core import HasLimits, IsHomeable, HasPosition, IsDaemon
import WrightTools as wt  # type: ignore


class AttuneDelay(HasLimits, IsHomeable, HasPosition, IsDaemon):
    _kind = "attune-delay"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        try:
            self._instrument = attune.load(f"autonomic_{name}")
        except ValueError:
            self._instrument = attune.Instrument({}, {}, name=f"autonomic_{name}")
            attune.store(self._instrument)

        if isinstance(config["wrapped_daemon"], int):
            self._wrapped_daemon = yaqc.Client(config["wrapped_daemon"])
        else:
            host, port = config["wrapped_daemon"].split(":")
            self._wrapped_daemon = yaqc.Client(port=int(port), host=host)

        self._ureg = pint.UnitRegistry()
        self._ureg.enable_contexts(wt.units.delay, num_pass=config["factor"])

        self._units = "ps"

    def _set_position(self, position):
        delay = self._ureg.Quantity(position, self._units)
        delay += self._ureg.Quantity(self.get_offset(), self._units)
        mm = delay.to("mm")
        mm_with_zero = mm.magnitude + self._state["zero_position"]
        self._wrapped_daemon.set_position(mm_with_zero)
        self._set_limits()

    def get_offset(self):
        res = 0.0
        for key, active in self._state["control_active"].items():
            if not active:
                continue
            if not key in self._instrument.arrangements:
                continue
            arrangement = self._state["control_tunes"].get(key)
            if not arrangement:
                continue
            if not arrangement in self._instrument[key].keys():
                continue
            res += self._instrument[key][arrangement](self._state["control_position"][key])
        return res

    def get_instrument(self):
        return self._instrument.as_dict()

    def set_instrument(self, instrument):
        self._busy = True
        self._instrument = attune.Instrument(**instrument)
        attune.store(self._instrument)
        self.shutdown(restart=True)

    def set_control_position(self, control: str, position: float):
        self._state["control_position"][control] = position
        if self._state["control_active"].get(control):
            self.set_position(self._state["destination"])

    def get_control_positions(self):
        return self._state["control_position"]

    def set_control_tune(self, control: str, tune: Union[None, str]):
        self._state["control_tunes"][control] = tune
        if self._state["control_active"].get(control):
            self.set_position(self._state["destination"])

    def get_control_tunes(self):
        return self._state["control_tunes"]

    def set_control_active(self, control: str, active: bool):
        self._state["control_active"][control] = active
        self.set_position(self._state["destination"])

    def get_control_active(self):
        return self._state["control_active"]

    def home(self):
        self._busy = True
        self._wrapped_daemon.home()

    def get_dependent_hardware(self):
        return {"stage": f"{self._wrapped_daemon._host}:{self._wrapped_daemon._port}"}

    def _set_limits(self):
        min_, max_ = self._wrapped_daemon.get_limits()
        min_ = self._to_ps(min_)
        max_ = self._to_ps(max_)
        if min_ < max_:
            self._state["hw_limits"] = (min_, max_)
        else:
            self._state["hw_limits"] = (max_, min_)

    def _to_ps(self, mm):
        mm -= self._state["zero_position"]
        mm = self._ureg.Quantity(mm, "mm")
        offset = self.get_offset()
        ps = mm.to(self._units).magnitude - offset
        return float(ps)

    async def update_state(self):
        """Continually monitor and update the current daemon state."""
        while True:
            self._busy = self._wrapped_daemon.busy()
            self._state["position"] = self._to_ps(self._wrapped_daemon.get_position())
            if self._busy:
                await asyncio.sleep(0.01)
            else:
                await asyncio.sleep(0.1)

    def set_zero_position(self, position: float):
        self._state["zero_position"] = position

        # Zero curves
        for arr in self._instrument.arrangements:
            tune = self._state["control_tunes"].get(arr)
            if tune in self._instrument[arr].keys():
                self._instrument = attune.offset_to(
                    self._instrument,
                    arr,
                    tune,
                    0,
                    self._state["control_position"][arr],
                )
        attune.store(self._instrument)

        self.set_position(self.get_destination())

    def get_zero_position(self):
        return self._state["zero_position"]

    def get_zero_position_units(self):
        return self._wrapped_daemon.get_units()

    def get_zero_position_limits(self):
        return self._wrapped_daemon.get_limits()
