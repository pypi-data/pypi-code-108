__all__ = ["CompuScope"]


import asyncio
import time
from typing import Dict, Any, List

import numpy as np  # type: ignore

from yaqd_core import HasMeasureTrigger, IsSensor, IsDaemon

from ._constants import acq_status_codes, transfer_modes
from ._pygage import PyGage


impedences = {
    "fifty": 50,
    "onemeg": 1_000_000
}


class CompuScope(HasMeasureTrigger, IsSensor, IsDaemon):
    _kind = "gage-compuscope"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._pg = PyGage()
        # acqusition config
        config = {}
        config["Mode"] = self._config["mode"]
        config["SampleRate"] = self._config["sample_rate"]
        config["Depth"] = self._config["depth"]
        config["SegmentSize"] = self._config["segment_size"]
        config["TriggerDelay"] = self._config["trigger_delay"]
        config["SegmentCount"] = self._state["segment_count"]
        config["TriggerTimeOut"] = self._config["trigger_time_out"]
        config["TriggerHoldOff"] = self._config["trigger_hold_off"]
        config["ExtClk"] = int(self._config["ext_clk"])
        config["TimeStampMode"] = self._config["time_stamp_mode"]
        config["TimeStampClock"] = self._config["time_stamp_clock"]
        self._pg.set_acquisition_config(config)
        self._pg.set_multiple_rec_average_count(self._config["record_count"])
        # channel config
        for channel_index, channel in enumerate(self._config["channels"]):
            config = {}
            config["InputRange"] = channel["range"]
            couplings = {"DC": 1, "AC": 2}
            config["Coupling"] = couplings[channel["coupling"]]
            config["Impedance"] = impedences[channel["impedance"]]
            config["DiffInput"] = int(channel["diff_input"])
            config["DirectADC"] = int(channel["direct_adc"])
            config["Filter"] = int(channel["filter"])
            config["DcOffset"] = channel["dc_offset"]
            self._pg.set_channel_config(channel_index + 1, config)
        # trigger config
        for trigger_index, trigger in enumerate(self._config["triggers"]):
            config = {}
            config["Condition"] = trigger["condition"]
            config["Level"] = trigger["level"]
            config["Source"] = trigger["source"]
            config["InputRange"] = trigger["range"]
            config["Impedance"] = impedences[channel["impedance"]]
            config["Relation"] = 0
            self._pg.set_trigger_config(trigger_index + 1, config)
        # finish
        self._pg.commit()
        self._channel_names = []
        for i in range(0, len(self._config["channels"])):
            self._channel_names.append(f"channel{i+1}")
            if self._config["channels"][i]["use_baseline"]:
                self._channel_names.append(f"channel{i+1}_signal")
                self._channel_names.append(f"channel{i+1}_baseline")
        self._channel_units = {k: "V" for k in self._channel_names}
        self._samples: Dict[str, np.ndarray] = dict()
        self.set_segment_count(self._state["segment_count"])

    def get_measured_samples(self):
        return self._samples

    def get_segment_count(self) -> int:
        return self._state["segment_count"]

    async def _measure(self):
        assert self._state["segment_count"] <= 4096  # soft limit just trying to prevent overflow
        # start capture
        self._pg.start_capture()
        # wait for capture to complete
        before = time.time()
        while True:
            code = self._pg.get_status()
            if acq_status_codes[code] == "ACQ_STATUS_READY":
                break
            await asyncio.sleep(0)
        print("TIME WAITED", time.time() - before)
        # read out
        out = {}
        for i in range(0, len(self._config["channels"])):
            out.update(self._process_single_channel(i))
        print(out)
        return out

    def _process_single_channel(self, channel_index: int) -> Dict[str, float]:
        out = dict()
        # TODO: think about perhaps other dtypes
        buffer = np.zeros(self._config["depth"], dtype=float)
        for segment in range(self._state["segment_count"]):
            # TODO: get segment count from gage
            # TODO: guess transfer mode from if multirecord averaging
            seg = self._pg.transfer_data(
                channel_index=channel_index + 1,
                start_position=0,
                transfer_length=self._config["depth"],
                segment_index=segment + 1,
                transfer_mode=transfer_modes["data_32"],
            )[0]
            seg = np.array(seg, dtype=float)
            buffer += seg
        # process samples array
        buffer /= 2 ** 8  # THIS IS AN EXTRA FACTOR THAT I DO NOT UNDERSTAND!!!  -Blaise
        buffer /= self._state["segment_count"]  # we summed across all segments before
        buffer /= self._config["record_count"]  # firmware sums accoss all records internally
        buffer *= -1
        buffer += self._pg.get_system_info()["SampleOffset"]
        buffer /= self._pg.get_system_info()["SampleResolution"]
        buffer *= 2 * self._pg.get_channel_config(channel_index + 1)["InputRange"] / 1000
        buffer += self._pg.get_channel_config(channel_index + 1)["DcOffset"]
        self._samples[f"channel{channel_index+1}"] = buffer
        # signal
        start = self._config["channels"][channel_index]["signal_start_index"]
        stop = self._config["channels"][channel_index]["signal_stop_index"]
        signal = np.average(buffer[start:stop])
        # baseline
        if self._config["channels"][channel_index]["use_baseline"]:
            start = self._config["channels"][channel_index]["baseline_start_index"]
            stop = self._config["channels"][channel_index]["baseline_stop_index"]
            baseline = np.average(buffer[start:stop])
            out[f"channel{channel_index+1}"] = signal - baseline
            out[f"channel{channel_index+1}_signal"] = signal
            out[f"channel{channel_index+1}_baseline"] = baseline
        else:
            out[f"channel{channel_index+1}"] = signal
        # invert
        if self._config["channels"][channel_index]["invert"]:
            out[f"channel{channel_index+1}"] *= -1
        return out

    def set_segment_count(self, count: int) -> int:
        self._state["segment_count"] = count
        self._pg.set_acquisition_config({"SegmentCount": self._state["segment_count"]})
        self._pg.commit()
        return count
