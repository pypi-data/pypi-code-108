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
    _kind = "gage-chopping"

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
        self._pg.set_multiple_rec_average_count(self._state["record_count"])
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
        self._channel_names.append("ai0")
        self._channel_names.append("ai1")
        self._channel_names.append("ai2")
        self._channel_names.append("ai3")
        self._channel_names.append("ai0_a")
        self._channel_names.append("ai0_b")
        self._channel_names.append("ai0_c")
        self._channel_names.append("ai0_d")
        self._channel_names.append("ai0_diff_abcd")
        self._channel_names.append("ai0_diff_ab")
        self._channel_names.append("ai0_diff_ad")
        self._channel_units = {k: "V" for k in self._channel_names}
        self._samples: Dict[str, np.ndarray] = dict()
        self._segments: Dict[str, np.ndarray] = dict()
        self.set_segment_count(self._state["segment_count"])

    def get_edge_width_count(self) -> int:
        return self._state["edge_width_count"]

    def get_measured_samples(self):
        return self._samples

    def get_measured_segments(self):
        return self._segments

    def get_record_count(self) -> int:
        return self._state["record_count"]

    def get_segment_count(self) -> int:
        return self._state["segment_count"]

    async def _measure(self):
        out = dict()
        assert self._state["segment_count"] <= 4096  # soft limit just trying to prevent overflow
        assert self._state["edge_width_count"] > 0  # sanity
        # set segment_count, record_count
        segment_count = self._state["segment_count"]
        record_count = self._state["record_count"]
        self._pg.set_acquisition_config({"SegmentCount": segment_count})
        self._pg.set_multiple_rec_average_count(record_count)
        self._pg.commit()
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
        segments = {}
        for i in range(0, len(self._config["channels"])):
            segments.update(self._process_single_channel(i, segment_count, record_count))
        self._segments = segments
        # get edges
        if self._state["edge_width_count"]:
            gradient = np.gradient(segments["ai3"])
            edges = np.abs(gradient) > 0.1
            edges = np.convolve(edges, np.full(self._state["edge_width_count"], True))
        else:
            edges = np.full(segment_count, False)
        # get regions
        self._segments["regions"] = np.full(self._state["segment_count"], "", dtype="<U1")
        regions = {k: [] for k in self._config["segment_bins"].keys()}
        for k, v in self._config["segment_bins"].items():
            start = None
            for i, voltage in enumerate(segments["ai3"]):
                if v["min"] <= voltage <= v["max"] and i != segments["ai3"].size - 1 and not edges[i]:
                    if start is None:
                        start = i
                else:
                    if start is not None:
                        sl = slice(start, i)
                        regions[k].append(sl)
                        self._segments["regions"][sl] = k
                        start = None
        # take means
        out["ai0"] = np.mean(segments["ai0"])
        out["ai1"] = np.mean(segments["ai1"])
        out["ai2"] = np.mean(segments["ai2"])
        out["ai3"] = np.mean(segments["ai3"])
        out["ai0_a"] = np.mean(segments["ai0"][np.r_[tuple(regions["a"])]])
        out["ai0_b"] = np.mean(segments["ai0"][np.r_[tuple(regions["b"])]])
        out["ai0_c"] = np.mean(segments["ai0"][np.r_[tuple(regions["c"])]])
        out["ai0_d"] = np.mean(segments["ai0"][np.r_[tuple(regions["d"])]])
        out["ai0_diff_abcd"] = out["ai0_a"] - out["ai0_b"] + out["ai0_c"] - out["ai0_d"]
        out["ai0_diff_ab"] = out["ai0_b"] - out["ai0_a"]
        out["ai0_diff_ad"] = out["ai0_d"] - out["ai0_a"]
        return out

    def _process_single_channel(self, channel_index: int, segment_count: int, record_count: int) -> Dict[str, Any]:
        out = dict()
        out[f"ai{channel_index}"] = np.zeros(segment_count, dtype=float)
        for segment_index in range(self._state["segment_count"]):

            # samples
            seg = self._pg.transfer_data(
                channel_index=channel_index + 1,
                start_position=0,
                transfer_length=self._config["depth"],
                segment_index=segment_index + 1,
                transfer_mode=transfer_modes["data_32"],
            )[0]
            seg = np.array(seg, dtype=float)
            seg /= 2 ** 8  # THIS IS AN EXTRA FACTOR THAT I DO NOT UNDERSTAND!!!  -Blaise
            seg /= record_count  # firmware sums accoss all records internally
            seg *= -1
            seg += self._pg.get_system_info()["SampleOffset"]
            seg /= self._pg.get_system_info()["SampleResolution"]
            seg *= 2 * self._pg.get_channel_config(channel_index + 1)["InputRange"] / 1000
            seg += self._pg.get_channel_config(channel_index + 1)["DcOffset"]
            self._samples[f"ai{channel_index}"] = seg

            # signal
            start = self._config["channels"][channel_index]["signal_start_index"]
            stop = self._config["channels"][channel_index]["signal_stop_index"]
            signal = np.average(seg[start:stop])

            # baseline
            if self._config["channels"][channel_index]["use_baseline"]:
                start = self._config["channels"][channel_index]["baseline_start_index"]
                stop = self._config["channels"][channel_index]["baseline_stop_index"]
                baseline = np.average(seg[start:stop])
                out[f"ai{channel_index}"][segment_index] = signal - baseline
            else:
                out[f"ai{channel_index}"][segment_index] = signal

            # invert
            if self._config["channels"][channel_index]["invert"]:
                out[f"ai{channel_index}"][segment_index] *= -1

        return out

    def set_edge_width_count(self, count: int) -> None:
        self._state["edge_width_count"] = count

    def set_record_count(self, count: int) -> int:
        self._state["record_count"] = count
        return count  

    def set_segment_count(self, count: int) -> int:
        self._state["segment_count"] = count
        return count
