import datetime
import logging
from abc import ABC
from typing import Union, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TimeSeries(ABC):
    def __init__(self, **kwargs):
        """ Abstract Baseclass representing TimeSeries like measurements

        Parameters
        ----------
        kwargs
        """
        self.rdy_format_version = kwargs["rdy_format_version"]
        kwargs.pop("rdy_format_version")
        kwargs.pop("__class__")

        for k, v in kwargs.items():  # Replaces None values arguments with empty lists
            if v is None and k != "rdy_format_version":
                kwargs[k] = np.array([])
            else:
                if type(v) == np.ndarray:
                    kwargs[k] = v
                else:
                    kwargs[k] = np.array(v)

            if k != "time" and len(kwargs["time"]) > 0 and len(v) == 0:
                kwargs[k] = np.zeros(len(kwargs["time"]))

        self.__dict__.update(kwargs)

        self._time: np.ndarray = np.array(self.time)  # Original unadjusted timestamps
        self._timedelta: np.ndarray = np.diff(self._time)

        if self.rdy_format_version and self.rdy_format_version <= 1.2:
            self._time = (self._time * 1e9).astype(np.int64)

        self.time = self._time.copy()

    def __len__(self):
        if np.array_equal(self.time, np.array(None)):
            return 0
        else:
            return len(self.time)

    def __repr__(self):
        return "Length: %d, Duration: %s, Mean sample rate: %.3f Hz" % (len(self._time),
                                                                        str(datetime.timedelta(
                                                                            seconds=self.get_duration())),
                                                                        self.get_sample_rate())

    def cutoff(self, timestamp_when_started: int, timestamp_when_stopped: int):
        """ Cuts off measurement values saved before/after the measurement was started/stopped

        Parameters
        ----------
        timestamp_when_started: int
            Timestamp when the measurement was started (i.e., when the recording button was pressed)
        timestamp_when_stopped: int
            Timestamp when the measurement was stopped (i.e., when the (stop) recording button was pressed)
        """
        if timestamp_when_started and timestamp_when_stopped:
            if timestamp_when_started >= timestamp_when_stopped:
                raise ValueError("timestamp_when_stopped must be greater than timestamp_when_started")

            if len(self.time) > 0 and self.time[0] != 0:
                d = self.__dict__.copy()

                for key in ["rdy_format_version"]:
                    d.pop(key)

                t = d["time"]
                idxs = np.where(np.logical_and(t >= timestamp_when_started, t <= timestamp_when_stopped))
                for k, v in d.items():
                    if len(t) == len(v):
                        self.__setattr__(k, v[idxs])

                self._timedelta: np.ndarray = np.diff(self._time)
            else:
                logger.info("Cannot cutoff series if series is empty or series already starts at 0")
        else:
            logger.warning("timestamp_when_started and/or timestamp_when_stopped are None")

        pass

    def to_df(self) -> pd.DataFrame:
        """ Converts the Series to a Pandas DataFrame

        Returns
        -------
            pd.DataFrame

        """
        d = self.__dict__.copy()
        d.pop("rdy_format_version")
        d.pop("_timedelta")
        return pd.DataFrame(dict([(k, pd.Series(v)) for k, v in d.items()])).set_index("time")

    def get_sub_series_names(self) -> list:
        """ Returns names of sub series (e.g., acc_x, acc_y, acc_z)

        Returns
        -------
            list
        """
        d = self.__dict__.copy()

        for k in ["rdy_format_version", "time", "_time", "_timedelta"]:
            d.pop(k)

        return list(d.keys())

    def get_duration(self) -> float:
        """ Calculates the duration of the TimeSeries in seconds

        Returns
        -------
            float
        """
        if not np.array_equal(self._time, np.array(None)) and len(self._time) > 0:
            if type(self._time[0]) == np.int64:
                duration: float = (self._time[-1] - self._time[0]) * 1e-9
            else:
                duration: float = (self._time[-1] - self._time[0])
        else:
            duration: float = 0.0

        return duration

    def get_sample_rate(self) -> float:
        """ Calculates the sample rate of the TimeSeries

        Returns
        -------
            float
        """
        if not np.array_equal(self._time, np.array(None)) and self.get_duration() > 0:
            mean_timedelta = self._timedelta.mean()
            sample_rate = 1 / (mean_timedelta * 1e-9) if mean_timedelta != 0.0 else 0.0
        else:
            sample_rate = 0.0

        return sample_rate

    def is_empty(self) -> bool:
        """ Checks whether the TimeSeries contains any values

        Returns
        -------
            bool
        """
        if len(self) == 0:
            return True
        else:
            return False

    def synchronize(self, method: str, sync_timestamp: Union[int, np.int64] = 0,
                    sync_time: np.datetime64 = np.datetime64(0, "s"), timedelta_unit='timedelta64[ns]'):
        """

        Parameters
        ----------
        method: str
            Sync method, must be either "timestamp", "device_time", "gps_time" or "ntp_time".
        sync_timestamp: int
            Timestamp used to synchronize timeseries
        sync_time: np.datetime64
            Sync to bes used for synchronizing
        timedelta_unit: str
            Timedelta unit
        """
        if sync_timestamp and type(sync_timestamp) not in [int, np.int64]:
            raise ValueError(
                "sync_timestamp must be integer for method %s, not %s" % (method, str(type(sync_timestamp))))

        if type(sync_time) != np.datetime64:
            raise ValueError(
                "sync_time must be np.datetime64 for method %s, not %s" % (method, str(type(sync_timestamp))))

        if not np.array_equal(self._time, np.array(None)) and len(self._time) > 0:
            if method == "timestamp":
                if self._time[0] == 0:
                    logger.info("Timeseries already starts at 0, timestamp syncing not appropriate")
                    self.time = self._time.astype(timedelta_unit)
                else:
                    if sync_timestamp:
                        self.time = (self._time - sync_timestamp).astype(timedelta_unit)
                    else:
                        logger.warning("sync_timestamp is None, using first timestamp for timeseries syncing")
                        self.time = (self._time - self._time[0]).astype(timedelta_unit)

            elif method == "device_time":
                if self._time[0] == 0:
                    logger.info("Timeseries already starts at 0, timestamp syncing not appropriate")
                    self.time = self._time.astype(timedelta_unit) + sync_time
                else:
                    self.time = (self._time - sync_timestamp).astype(timedelta_unit) + sync_time
            elif method == "gps_time" or method == "ntp_time":
                if self._time[0] == 0:
                    logger.info("Timeseries already starts at 0, cant sync to due to lack of proper timestamp")
                else:
                    self.time = (self._time - sync_timestamp).astype(timedelta_unit) + sync_time
                pass
            else:
                raise ValueError("Method %s not supported" % method)
        else:
            logger.info("Trying to synchronize timestamps on empty %s" % self.__class__.__name__)


class AccelerationSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 acc_x: Union[list, np.ndarray] = None,
                 acc_y: Union[list, np.ndarray] = None,
                 acc_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing acceleration values
        See https://developer.android.com/guide/topics/sensors/sensors_overview for more information
        on Android sensors


        Parameters
        ----------
        time
        acc_x
        acc_y
        acc_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(AccelerationSeries, self).__init__(**args)


class AccelerationUncalibratedSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 acc_uncal_x: Union[list, np.ndarray] = None,
                 acc_uncal_y: Union[list, np.ndarray] = None,
                 acc_uncal_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing uncalibrated acceleration values

        Parameters
        ----------
        time
        acc_uncal_x
        acc_uncal_y
        acc_uncal_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(AccelerationUncalibratedSeries, self).__init__(**args)


class LinearAccelerationSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 lin_acc_x: Union[list, np.ndarray] = None,
                 lin_acc_y: Union[list, np.ndarray] = None,
                 lin_acc_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None, **kwargs):
        """ Series containing linear acceleration values (i.e. without g)

        Parameters
        ----------
        time
        lin_acc_x
        lin_acc_y
        lin_acc_z
        rdy_format_version
        kwargs
        """
        args = locals().copy()
        args.pop("self")
        args.pop("kwargs")
        super(LinearAccelerationSeries, self).__init__(**args)

        if "acc_x" in kwargs and kwargs["acc_x"] is None:
            kwargs["acc_x"] = []

        if "acc_y" in kwargs and kwargs["acc_y"] is None:
            kwargs["acc_y"] = []

        if "acc_z" in kwargs and kwargs["acc_z"] is None:
            kwargs["acc_z"] = []

        self.lin_acc_x: np.ndarray = np.array(kwargs["acc_x"]) if "acc_x" in kwargs else np.array(lin_acc_x)
        self.lin_acc_y: np.ndarray = np.array(kwargs["acc_y"]) if "acc_y" in kwargs else np.array(lin_acc_y)
        self.lin_acc_z: np.ndarray = np.array(kwargs["acc_z"]) if "acc_z" in kwargs else np.array(lin_acc_z)


class MagnetometerSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 mag_x: Union[list, np.ndarray] = None,
                 mag_y: Union[list, np.ndarray] = None,
                 mag_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing magnetic field values

        Parameters
        ----------
        time
        mag_x
        mag_y
        mag_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(MagnetometerSeries, self).__init__(**args)


class MagnetometerUncalibratedSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 mag_uncal_x: Union[list, np.ndarray] = None,
                 mag_uncal_y: Union[list, np.ndarray] = None,
                 mag_uncal_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing uncalibrated magnetic field values

        Parameters
        ----------
        time
        mag_uncal_x
        mag_uncal_y
        mag_uncal_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(MagnetometerUncalibratedSeries, self).__init__(**args)


class NMEAMessageSeries(TimeSeries):
    def __init__(self,
                 time: Union[list, np.ndarray] = None,
                 utc_time: Union[list, np.ndarray] = None,
                 msg: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing raw NMEA strings from GNSS chipset
        See https://www.wikiwand.com/en/NMEA_0183 for more information on NMEA messages

        Parameters
        ----------
        time
        utc_time
        msg
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(NMEAMessageSeries, self).__init__(**args)


class GNSSClockMeasurementSeries(TimeSeries):
    def __init__(self,
                 time: Union[list, np.ndarray] = None,
                 bias_nanos: Union[list, np.ndarray] = None,
                 bias_uncertainty_nanos: Union[list, np.ndarray] = None,
                 drift_nanos_per_second: Union[list, np.ndarray] = None,
                 drift_uncertainty_nanos_per_second: Union[list, np.ndarray] = None,
                 elapsed_realtime_nanos: Union[list, np.ndarray] = None,
                 elapsed_realtime_uncertainty_nanos: Union[list, np.ndarray] = None,
                 full_bias_nanos: Union[list, np.ndarray] = None,
                 hardware_clock_discontinuity_count: Union[list, np.ndarray] = None,
                 leap_second: Union[list, np.ndarray] = None,
                 reference_carrier_frequency_hz_for_isb: Union[list, np.ndarray] = None,
                 reference_code_type_for_isb: Union[list, np.ndarray] = None,
                 reference_constellation_type_for_isb: Union[list, np.ndarray] = None,
                 time_nanos: Union[list, np.ndarray] = None,
                 time_uncertainty_nanos: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing raw GNSS clock values
        See https://developer.android.com/reference/android/location/GnssClock for more information on individual
        parameters

        Parameters
        ----------
        time
        bias_nanos
        bias_uncertainty_nanos
        drift_nanos_per_second
        drift_uncertainty_nanos_per_second
        elapsed_realtime_nanos
        elapsed_realtime_uncertainty_nanos
        full_bias_nanos
        hardware_clock_discontinuity_count
        leap_second
        reference_carrier_frequency_hz_for_isb
        reference_code_type_for_isb
        reference_constellation_type_for_isb
        time_nanos
        time_uncertainty_nanos
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(GNSSClockMeasurementSeries, self).__init__(**args)


class GNSSMeasurementSeries(TimeSeries):
    # noinspection PyPep8Naming
    def __init__(self,
                 time: Union[list, np.ndarray] = None,
                 accumulated_delta_range_meters: Union[list, np.ndarray] = None,
                 accumulated_delta_range_state: Union[list, np.ndarray] = None,
                 accumulated_delta_range_uncertainty_meters: Union[list, np.ndarray] = None,
                 automatic_gain_control_level_db: Union[list, np.ndarray] = None,
                 baseband_cn0DbHz: Union[list, np.ndarray] = None,
                 carrier_cycles: Union[list, np.ndarray] = None,
                 carrier_frequency_hz: Union[list, np.ndarray] = None,
                 carrier_phase: Union[list, np.ndarray] = None,
                 carrier_phase_uncertainty: Union[list, np.ndarray] = None,
                 cn0DbHz: Union[list, np.ndarray] = None,
                 code_type: Union[list, np.ndarray] = None,
                 constellation_type: Union[list, np.ndarray] = None,
                 full_inter_signal_bias_nanos: Union[list, np.ndarray] = None,
                 full_inter_signal_bias_uncertainty_nanos: Union[list, np.ndarray] = None,
                 multipath_indicator: Union[list, np.ndarray] = None,
                 pseudorange_rate_meters_per_second: Union[list, np.ndarray] = None,
                 pseudorange_rate_uncertainty_meters_per_second: Union[list, np.ndarray] = None,
                 received_sv_time_nanos: Union[list, np.ndarray] = None,
                 received_sv_time_uncertainty_nanos: Union[list, np.ndarray] = None,
                 satellite_inter_signal_bias_nanos: Union[list, np.ndarray] = None,
                 satellite_inter_signal_bias_uncertainty_nanos: Union[list, np.ndarray] = None,
                 snrInDb: Union[list, np.ndarray] = None,
                 state: Union[list, np.ndarray] = None,
                 svid: Union[list, np.ndarray] = None,
                 time_offset_nanos: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing raw GNSS measurements
        See https://developer.android.com/reference/android/location/GnssMeasurement for more information on
        specific values

        Parameters
        ----------
        time
        accumulated_delta_range_meters
        accumulated_delta_range_state
        accumulated_delta_range_uncertainty_meters
        automatic_gain_control_level_db
        baseband_cn0DbHz
        carrier_cycles
        carrier_frequency_hz
        carrier_phase
        carrier_phase_uncertainty
        cn0DbHz
        code_type
        constellation_type
        full_inter_signal_bias_nanos
        full_inter_signal_bias_uncertainty_nanos
        multipath_indicator
        pseudorange_rate_meters_per_second
        pseudorange_rate_uncertainty_meters_per_second
        received_sv_time_nanos
        received_sv_time_uncertainty_nanos
        satellite_inter_signal_bias_nanos
        satellite_inter_signal_bias_uncertainty_nanos
        snrInDb
        state
        svid
        time_offset_nanos
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(GNSSMeasurementSeries, self).__init__(**args)


class OrientationSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 azimuth: Union[list, np.ndarray] = None,
                 pitch: Union[list, np.ndarray] = None,
                 roll: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing orientation values

        Parameters
        ----------
        time
        azimuth
        pitch
        roll
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(OrientationSeries, self).__init__(**args)


class GyroSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 w_x: Union[list, np.ndarray] = None,
                 w_y: Union[list, np.ndarray] = None,
                 w_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing gyro values

        Parameters
        ----------
        time
        w_x
        w_y
        w_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(GyroSeries, self).__init__(**args)


class GyroUncalibratedSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 w_uncal_x: Union[list, np.ndarray] = None,
                 w_uncal_y: Union[list, np.ndarray] = None,
                 w_uncal_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing uncalibrated gyro values

        Parameters
        ----------
        time
        w_uncal_x
        w_uncal_y
        w_uncal_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(GyroUncalibratedSeries, self).__init__(**args)


class RotationSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 rot_x: Union[list, np.ndarray] = None,
                 rot_y: Union[list, np.ndarray] = None,
                 rot_z: Union[list, np.ndarray] = None,
                 cos_phi: Union[list, np.ndarray] = None,
                 heading_acc: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing rotation values

        Parameters
        ----------
        time
        rot_x
        rot_y
        rot_z
        cos_phi
        heading_acc
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(RotationSeries, self).__init__(**args)


class GPSSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 lat: Union[list, np.ndarray] = None,
                 lon: Union[list, np.ndarray] = None,
                 altitude: Union[list, np.ndarray] = None,
                 bearing: Union[list, np.ndarray] = None,
                 speed: Union[list, np.ndarray] = None,
                 hor_acc: Union[list, np.ndarray] = None,
                 ver_acc: Union[list, np.ndarray] = None,
                 bear_acc: Union[list, np.ndarray] = None,
                 speed_acc: Union[list, np.ndarray] = None,
                 utc_time: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """ Series containing GPS values

        Parameters
        ----------
        time
        lat
        lon
        altitude
        bearing
        speed
        hor_acc
        ver_acc
        bear_acc
        speed_acc
        utc_time
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(GPSSeries, self).__init__(**args)

    def to_ipyleaflef(self) -> List[list]:
        """

        Returns
        -------

        """
        if np.array_equal(self.lat, np.array(None)) and np.array_equal(self.lat, np.array(None)):
            logger.warning("Coordinates are empty")
            return [[]]
        elif len(self.lat) == 0 and len(self.lon) == 0:
            logger.warning("Coordinates are empty")
            return [[]]
        else:
            return [[lat, lon] for lat, lon in zip(self.lat, self.lon)]


class PressureSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 pressure: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """

        Parameters
        ----------
        time
        pressure
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(PressureSeries, self).__init__(**args)


class TemperatureSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 temperature: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """

        Parameters
        ----------
        time
        temperature
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(TemperatureSeries, self).__init__(**args)


class HumiditySeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 humidity: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """

        Parameters
        ----------
        time
        humidity
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(HumiditySeries, self).__init__(**args)


class LightSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 light: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """

        Parameters
        ----------
        time
        light
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(LightSeries, self).__init__(**args)


class WzSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 wz_x: Union[list, np.ndarray] = None,
                 wz_y: Union[list, np.ndarray] = None,
                 wz_z: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """

        Parameters
        ----------
        time
        wz_x
        wz_y
        wz_z
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(WzSeries, self).__init__(**args)


class SubjectiveComfortSeries(TimeSeries):
    def __init__(self, time: Union[list, np.ndarray] = None,
                 comfort: Union[list, np.ndarray] = None,
                 rdy_format_version: float = None):
        """

        Parameters
        ----------
        time
        comfort
        rdy_format_version
        """
        args = locals().copy()
        args.pop("self")
        super(SubjectiveComfortSeries, self).__init__(**args)
