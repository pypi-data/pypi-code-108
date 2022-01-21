from functools import lru_cache

import numpy as np
import astropy.units as u
from numba import njit
import tables

from ctapipe.core import TelescopeComponent
from ctapipe.core.traits import (
    Path, IntTelescopeParameter,
    TelescopeParameter, FloatTelescopeParameter, Bool, Float
)

from ctapipe.calib.camera.gainselection import ThresholdGainSelector
from ctapipe.containers import MonitoringContainer
from ctapipe.io import HDF5TableReader, read_table
from .containers import LSTArrayEventContainer
from traitlets import Enum


from .constants import (
    N_GAINS, N_PIXELS, N_MODULES, N_SAMPLES, LOW_GAIN, HIGH_GAIN,
    N_PIXELS_MODULE, N_CAPACITORS_PIXEL, N_CAPACITORS_CHANNEL,
    LAST_RUN_WITH_OLD_FIRMWARE, CLOCK_FREQUENCY_KHZ,
    CHANNEL_ORDER_LOW_GAIN, CHANNEL_ORDER_HIGH_GAIN, N_CHANNELS_MODULE,
    PIXEL_INDEX,
)

__all__ = [
    'LSTR0Corrections',
]


@lru_cache()
def pixel_channel_indices(n_modules):
    module_index = np.repeat(np.arange(n_modules), 7)
    low_gain = module_index * N_CHANNELS_MODULE + np.tile(CHANNEL_ORDER_LOW_GAIN, n_modules)
    high_gain = module_index * N_CHANNELS_MODULE + np.tile(CHANNEL_ORDER_HIGH_GAIN, n_modules)
    return low_gain, high_gain


def get_first_capacitors_for_pixels(first_capacitor_id, expected_pixel_id=None):
    '''
    Get the first capacitor for each pixel / gain

    Parameters
    ----------
    first_capacitor_id: np.ndarray
        First capacitor array as delivered by the event builder,
        containing first capacitors for each DRS4 chip.
    expected_pixel_id: np.ndarray
        Array of the pixel ids corresponding to the positions in
        the data array.
        If given, will be used to reorder the start cells to pixel id order.

    Returns
    -------
    fc: np.ndarray
        First capacitors for each pixel in each gain, shape (N_GAINS, N_PIXELS)
    '''

    fc = np.zeros((N_GAINS, N_PIXELS), dtype='uint16')

    n_modules = first_capacitor_id.size // N_CHANNELS_MODULE

    low_gain_channels, high_gain_channels = pixel_channel_indices(n_modules)
    low_gain = first_capacitor_id[low_gain_channels]
    high_gain = first_capacitor_id[high_gain_channels]

    if expected_pixel_id is None:
        fc[LOW_GAIN] = low_gain
        fc[HIGH_GAIN] = high_gain
    else:
        fc[LOW_GAIN, expected_pixel_id] = low_gain
        fc[HIGH_GAIN, expected_pixel_id] = high_gain

    return fc


class LSTR0Corrections(TelescopeComponent):
    """
    The base R0-level calibrator. Changes the r0 container.

    The R0 calibrator performs the camera-specific R0 calibration that is
    usually performed on the raw data by the camera server.
    This calibrator exists in lstchain for testing and prototyping purposes.
    """
    offset = IntTelescopeParameter(
        default_value=0,
        help=(
            'Define offset to be subtracted from the waveform *additionally*'
            ' to the drs4 pedestal offset. This only needs to be given when'
            ' the drs4 pedestal calibration is not applied or the offset of the'
            ' drs4 run is different from the data run'
        )
    ).tag(config=True)

    r1_sample_start = IntTelescopeParameter(
        default_value=3,
        help='Start sample for r1 waveform',
        allow_none=True,
    ).tag(config=True)

    r1_sample_end = IntTelescopeParameter(
        default_value=39,
        help='End sample for r1 waveform',
        allow_none=True,
    ).tag(config=True)

    drs4_pedestal_path = TelescopeParameter(
        trait=Path(exists=True, directory_ok=False, allow_none=True),
        allow_none=True,
        default_value=None,
        help=(
            'Path to the LST pedestal file'
            ', required when `apply_drs4_pedestal_correction=True`'
            ' or when using spike subtraction'
        ),
    ).tag(config=True)

    calibration_path = Path(
        None, exists=True, directory_ok=False, allow_none=True,
        help='Path to LST calibration file',
    ).tag(config=True)

    drs4_time_calibration_path = TelescopeParameter(
        trait=Path(exists=True, directory_ok=False, allow_none=True),
        help='Path to the time calibration file',
        default_value=None,
        allow_none=True,
    ).tag(config=True)

    calib_scale_high_gain = FloatTelescopeParameter(
        default_value=1.0,
        help='High gain waveform is multiplied by this number'
    ).tag(config=True)

    calib_scale_low_gain = FloatTelescopeParameter(
        default_value=1.0,
        help='Low gain waveform is multiplied by this number'
    ).tag(config=True)

    select_gain = Bool(
        default_value=True,
        help='Set to False to keep both gains.'
    ).tag(config=True)

    apply_drs4_pedestal_correction = Bool(
        default_value=True,
        help=(
            'Set to False to disable drs4 pedestal correction.'
            ' Providing the drs4_pedestal_path is required to perform this calibration'
        ),
    ).tag(config=True)

    apply_timelapse_correction = Bool(
        default_value=True,
        help='Set to False to disable drs4 timelapse correction'
    ).tag(config=True)

    apply_spike_correction = Bool(
        default_value=True,
        help='Set to False to disable drs4 spike correction'
    ).tag(config=True)

    add_calibration_timeshift = Bool(
        default_value=True,
        help=(
            'If true, time correction from the calibration'
            ' file is added to calibration.dl1.time'
        ),
    ).tag(config=True)

    gain_selection_threshold = Float(
        default_value=3500,
        help='Threshold for the ThresholdGainSelector.'
    ).tag(config=True)

    spike_correction_method = Enum(
        values=['subtraction', 'interpolation'],
        default_value='subtraction',
        help='Wheter to use spike subtraction (default) or interpolation',
    ).tag(config=True)

    def __init__(self, subarray, config=None, parent=None, **kwargs):
        """
        The R0 calibrator for LST data.
        Fill the r1 container.

        Parameters
        ----------
        """
        super().__init__(
            subarray=subarray, config=config, parent=parent, **kwargs
        )

        self.mon_data = None
        self.last_readout_time = {}
        self.first_cap = {}
        self.first_cap_old = {}
        self.fbn = {}
        self.fan = {}

        for tel_id in self.subarray.tel:
            shape = (N_GAINS, N_PIXELS, N_CAPACITORS_PIXEL)
            self.last_readout_time[tel_id] = np.zeros(shape, dtype='uint64')

            shape = (N_GAINS, N_PIXELS)
            self.first_cap[tel_id] = np.zeros(shape, dtype=int)
            self.first_cap_old[tel_id] = np.zeros(shape, dtype=int)

        if self.select_gain:
            self.gain_selector = ThresholdGainSelector(
                threshold=self.gain_selection_threshold,
                parent=self
            )
        else:
            self.gain_selector = None

        if self.calibration_path is not None:
            self.mon_data = self._read_calibration_file(self.calibration_path)

    def apply_drs4_corrections(self, event: LSTArrayEventContainer):
        self.update_first_capacitors(event)

        for tel_id, r0 in event.r0.tel.items():
            r1 = event.r1.tel[tel_id]
            # If r1 was not yet filled, copy of r0 converted
            if r1.waveform is None:
                r1.waveform = r0.waveform

            # float32 can represent all values of uint16 exactly,
            # so this does not loose precision.
            r1.waveform = r1.waveform.astype(np.float32, copy=False)

            # apply drs4 corrections
            if self.apply_drs4_pedestal_correction:
                self.subtract_pedestal(event, tel_id)

            if self.apply_timelapse_correction:
                self.time_lapse_corr(event, tel_id)

            if self.apply_spike_correction:
                if self.spike_correction_method == 'subtraction':
                    self.subtract_spikes(event, tel_id)
                else:
                    self.interpolate_spikes(event, tel_id)


            # remove samples at beginning / end of waveform
            start = self.r1_sample_start.tel[tel_id]
            end = self.r1_sample_end.tel[tel_id]
            r1.waveform = r1.waveform[..., start:end]

            if self.offset.tel[tel_id] != 0:
                r1.waveform -= self.offset.tel[tel_id]

            mon = event.mon.tel[tel_id]
            if r1.selected_gain_channel is None:
                r1.waveform[mon.pixel_status.hardware_failing_pixels] = 0.0
            else:
                broken = mon.pixel_status.hardware_failing_pixels[r1.selected_gain_channel, PIXEL_INDEX]
                r1.waveform[broken] = 0.0


    def update_first_capacitors(self, event: LSTArrayEventContainer):
        for tel_id, lst in event.lst.tel.items():
            self.first_cap_old[tel_id] = self.first_cap[tel_id]
            self.first_cap[tel_id] = get_first_capacitors_for_pixels(
                lst.evt.first_capacitor_id,
                lst.svc.pixel_ids,
            )

    def calibrate(self, event: LSTArrayEventContainer):
        for tel_id in event.r0.tel:
            r1 = event.r1.tel[tel_id]
            # if `apply_drs4_corrections` is False, we did not fill in the
            # waveform yet.
            if r1.waveform is None:
                r1.waveform = event.r0.tel[tel_id].waveform

            r1.waveform = r1.waveform.astype(np.float32, copy=False)

            # do gain selection before converting to pe
            # like eventbuilder will do
            if self.select_gain and r1.selected_gain_channel is None:
                r1.selected_gain_channel = self.gain_selector(r1.waveform)
                r1.waveform = r1.waveform[r1.selected_gain_channel, PIXEL_INDEX]

            # apply monitoring data corrections,
            # subtract pedestal and convert to pe
            if self.mon_data is not None:
                calibration = self.mon_data.tel[tel_id].calibration
                convert_to_pe(
                    waveform=r1.waveform,
                    calibration=calibration,
                    selected_gain_channel=r1.selected_gain_channel
                )

            broken_pixels = event.mon.tel[tel_id].pixel_status.hardware_failing_pixels
            if r1.selected_gain_channel is None:
                r1.waveform[broken_pixels] = 0.0
            else:
                r1.waveform[broken_pixels[r1.selected_gain_channel, PIXEL_INDEX]] = 0.0

            # store calibration data needed for dl1 calibration in ctapipe
            # first drs4 time shift (zeros if no calib file was given)
            time_shift = self.get_drs4_time_correction(
                tel_id, self.first_cap[tel_id],
                selected_gain_channel=r1.selected_gain_channel,
            )

            # time shift from flat fielding
            if self.mon_data is not None and self.add_calibration_timeshift:
                time_corr = self.mon_data.tel[tel_id].calibration.time_correction
                # time_shift is subtracted in ctapipe,
                # but time_correction should be added
                if r1.selected_gain_channel is not None:
                    time_shift -= time_corr[r1.selected_gain_channel, PIXEL_INDEX].to_value(u.ns)
                else:
                    time_shift -= time_corr.to_value(u.ns)

            event.calibration.tel[tel_id].dl1.time_shift = time_shift

            # needed for charge scaling in ctpaipe dl1 calib
            if r1.selected_gain_channel is not None:
                relative_factor = np.empty(N_PIXELS)
                relative_factor[r1.selected_gain_channel == HIGH_GAIN] = self.calib_scale_high_gain.tel[tel_id]
                relative_factor[r1.selected_gain_channel == LOW_GAIN] = self.calib_scale_low_gain.tel[tel_id]
            else:
                relative_factor = np.empty((N_GAINS, N_PIXELS))
                relative_factor[HIGH_GAIN] = self.calib_scale_high_gain.tel[tel_id]
                relative_factor[LOW_GAIN] = self.calib_scale_low_gain.tel[tel_id]

            event.calibration.tel[tel_id].dl1.relative_factor = relative_factor

    @staticmethod
    def _read_calibration_file(path):
        """
        Read the correction from hdf5 calibration file
        """
        mon = MonitoringContainer()

        with tables.open_file(path) as f:
            tel_ids = [
                int(key[4:]) for key in f.root._v_children.keys()
                if key.startswith('tel_')
            ]

        for tel_id in tel_ids:
            with HDF5TableReader(path) as h5_table:
                base = f'/tel_{tel_id}'
                # read the calibration data
                table = base + '/calibration'
                next(h5_table.read(table, mon.tel[tel_id].calibration))

                # read pedestal data
                table = base + '/pedestal'
                next(h5_table.read(table, mon.tel[tel_id].pedestal))

                # read flat-field data
                table = base + '/flatfield'
                next(h5_table.read(table, mon.tel[tel_id].flatfield))

                # read the pixel_status container
                table = base + '/pixel_status'
                next(h5_table.read(table, mon.tel[tel_id].pixel_status))

        return mon

    @staticmethod
    def load_drs4_time_calibration_file(path):
        """
        Function to load calibration file.
        """
        with tables.open_file(path, 'r') as f:
            fan = f.root.fan[:]
            fbn = f.root.fbn[:]

        return fan, fbn

    def load_drs4_time_calibration_file_for_tel(self, tel_id):
        self.fan[tel_id], self.fbn[tel_id] = self.load_drs4_time_calibration_file(
            self.drs4_time_calibration_path.tel[tel_id]
        )

    def get_drs4_time_correction(self, tel_id, first_capacitors, selected_gain_channel=None):
        """
        Return pulse time after time correction.
        """

        if self.drs4_time_calibration_path.tel[tel_id] is None:
            if selected_gain_channel is None:
                return np.zeros((N_GAINS, N_PIXELS))
            else:
                return np.zeros(N_PIXELS)

        # load calib file if not already done
        if tel_id not in self.fan:
            self.load_drs4_time_calibration_file_for_tel(tel_id)

        if selected_gain_channel is not None:
            return calc_drs4_time_correction_gain_selected(
                first_capacitors,
                selected_gain_channel,
                self.fan[tel_id],
                self.fbn[tel_id],
            )
        else:
            return calc_drs4_time_correction_both_gains(
                first_capacitors,
                self.fan[tel_id],
                self.fbn[tel_id],
            )

    @staticmethod
    @lru_cache(maxsize=4)
    def _get_drs4_pedestal_data(path, tel_id):
        """
        Function to load pedestal file.

        To make boundary conditions unnecessary,
        the first N_SAMPLES values are repeated at the end of the array

        The result is cached so we can repeatedly call this method
        using the configured path without reading it each time.
        """
        if path is None:
            raise ValueError(
                "DRS4 pedestal correction requested"
                " but no file provided for telescope"
            )

        table = read_table(path, f'/r1/monitoring/drs4_baseline/tel_{tel_id:03d}')

        pedestal_data = np.empty(
            (N_GAINS, N_PIXELS_MODULE * N_MODULES, N_CAPACITORS_PIXEL + N_SAMPLES),
            dtype=np.float32
        )
        pedestal_data[:, :, :N_CAPACITORS_PIXEL] = table[0]['baseline_mean']
        pedestal_data[:, :, N_CAPACITORS_PIXEL:] = pedestal_data[:, :, :N_SAMPLES]

        return pedestal_data

    @lru_cache(maxsize=4)
    def _get_spike_heights(self, path, tel_id):
        if path is None:
            raise ValueError(
                "DRS4 spike correction requested"
                " but no pedestal file provided for telescope"
            )

        table = read_table(path, f'/r1/monitoring/drs4_baseline/tel_{tel_id:03d}')
        spike_height = np.array(table[0]['spike_height'])
        return spike_height

    def subtract_pedestal(self, event, tel_id):
        """
        Subtract cell offset using pedestal file.
        Fill the R1 container.
        Parameters
        ----------
        event : `ctapipe` event-container
        tel_id : id of the telescope
        """
        pedestal = self._get_drs4_pedestal_data(
            self.drs4_pedestal_path.tel[tel_id],
            tel_id,
        )

        if event.r1.tel[tel_id].selected_gain_channel is None:
            subtract_pedestal(
                event.r1.tel[tel_id].waveform,
                self.first_cap[tel_id],
                pedestal,
            )
        else:
            subtract_pedestal_gain_selected(
                event.r1.tel[tel_id].waveform,
                self.first_cap[tel_id],
                pedestal,
                event.r1.tel[tel_id].selected_gain_channel,
            )


    def time_lapse_corr(self, event, tel_id):
        """
        Perform time lapse baseline corrections.
        Fill the R1 container or modifies R0 container.
        Parameters
        ----------
        event : `ctapipe` event-container
        tel_id : id of the telescope
        """
        lst = event.lst.tel[tel_id]

        # If R1 container exists, update it inplace
        if isinstance(event.r1.tel[tel_id].waveform, np.ndarray):
            container = event.r1.tel[tel_id]
        else:
            # Modify R0 container. This is to create pedestal files.
            container = event.r0.tel[tel_id]

        waveform = container.waveform.copy()

        # We have 2 functions: one for data from 2018/10/10 to 2019/11/04 and
        # one for data from 2019/11/05 (from Run 1574) after update firmware.
        # The old readout (before 2019/11/05) is shifted by 1 cell.
        run_id = event.lst.tel[tel_id].svc.configuration_id

        # not yet gain selected
        if event.r1.tel[tel_id].selected_gain_channel is None:
            apply_timelapse_correction(
                waveform=waveform,
                local_clock_counter=lst.evt.local_clock_counter,
                first_capacitors=self.first_cap[tel_id],
                last_readout_time=self.last_readout_time[tel_id],
                expected_pixels_id=lst.svc.pixel_ids,
                run_id=run_id,
            )
        else:
            apply_timelapse_correction_gain_selected(
                waveform=waveform,
                local_clock_counter=lst.evt.local_clock_counter,
                first_capacitors=self.first_cap[tel_id],
                last_readout_time=self.last_readout_time[tel_id],
                expected_pixels_id=lst.svc.pixel_ids,
                selected_gain_channel=event.r1.tel[tel_id].selected_gain_channel,
                run_id=run_id,
            )

        container.waveform = waveform

    def interpolate_spikes(self, event, tel_id):
        """
        Interpolate spikes at known positions from their neighboring values

        Mutates the R1 waveform.
        """
        run_id = event.lst.tel[tel_id].svc.configuration_id

        r1 = event.r1.tel[tel_id]
        if r1.selected_gain_channel is None:
            interpolate_spikes(
                waveform=r1.waveform,
                first_capacitors=self.first_cap[tel_id],
                previous_first_capacitors=self.first_cap_old[tel_id],
                run_id=run_id,
            )
        else:
            interpolate_spikes_gain_selected(
                waveform=r1.waveform,
                first_capacitors=self.first_cap[tel_id],
                previous_first_capacitors=self.first_cap_old[tel_id],
                selected_gain_channel=r1.selected_gain_channel,
                run_id=run_id,
            )

    def subtract_spikes(self, event, tel_id):
        """
        Subtract mean spike height from known spike positions

        Mutates the R1 waveform.
        """
        run_id = event.lst.tel[tel_id].svc.configuration_id
        spike_height = self._get_spike_heights(self.drs4_pedestal_path.tel[tel_id], tel_id)

        r1 = event.r1.tel[tel_id]
        if r1.selected_gain_channel is None:
            subtract_spikes(
                waveform=r1.waveform,
                first_capacitors=self.first_cap[tel_id],
                previous_first_capacitors=self.first_cap_old[tel_id],
                run_id=run_id,
                spike_height=spike_height
            )
        else:
            subtract_spikes_gain_selected(
                waveform=r1.waveform,
                first_capacitors=self.first_cap[tel_id],
                previous_first_capacitors=self.first_cap_old[tel_id],
                selected_gain_channel=r1.selected_gain_channel,
                run_id=run_id,
                spike_height=spike_height
            )


def convert_to_pe(waveform, calibration, selected_gain_channel):
    if selected_gain_channel is None:
        waveform -= calibration.pedestal_per_sample[:, :, np.newaxis]
        waveform *= calibration.dc_to_pe[:, :, np.newaxis]
    else:
        waveform -= calibration.pedestal_per_sample[selected_gain_channel, PIXEL_INDEX, np.newaxis]
        waveform *= calibration.dc_to_pe[selected_gain_channel, PIXEL_INDEX, np.newaxis]


@njit(cache=True)
def interpolate_spike_A(waveform, position):
    """
    Numba function for interpolation spike type A.
    Change waveform array.
    """
    a = int(waveform[position - 1])
    b = int(waveform[position + 2])
    waveform[position] = waveform[position - 1] + (0.33 * (b - a))
    waveform[position + 1] = waveform[position - 1] + (0.66 * (b - a))


@njit(cache=True)
def get_spike_A_positions_base(current_first_cap, previous_first_cap, shift):
    '''
    Find spike positions.

    For the new firmware, use shift=0; for the old firmware shift=1.

    Parameters
    ----------
    current_first_cap: ndarray
        First capacitor of the current event
    previous_first_cap: ndarray
        First capacitor of the previous event

    Returns
    -------
    positions: list[int]
        List of spike positions
    '''
    last_in_first_half = N_CAPACITORS_CHANNEL // 2 - 1
    last_capacitor = (previous_first_cap + N_SAMPLES - 1) % N_CAPACITORS_CHANNEL

    # The correction is only needed for even last capacitor
    # in the first half of the DRS4 ring
    if last_capacitor % 2 != 0 or last_capacitor > last_in_first_half:
        # bad trickery to get numba to compile an empty list with type int
        # see https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html
        return [int(x) for x in range(0)]

    # we have two cases for spikes that can occur in each of the 4 channels
    base_positions = (
        N_CAPACITORS_PIXEL - last_capacitor - 2 - shift,
        last_capacitor - shift
    )

    positions = []
    for k in range(4):
        for base_position in base_positions:
            abspos = base_position + k * N_CAPACITORS_CHANNEL

            spike_A_position = (abspos - current_first_cap) % N_CAPACITORS_PIXEL

            # a spike affects the position itself and the two following slices
            # so we include also spikes two slices before the readout window
            spike_A_position_shifted = spike_A_position - N_CAPACITORS_PIXEL
            if spike_A_position < N_SAMPLES:
                positions.append(spike_A_position)
            elif spike_A_position_shifted >= -2:
                positions.append(spike_A_position_shifted)

    return positions


@njit(cache=True)
def get_spike_A_positions(current_first_cap, previous_first_cap):
    """
    Find spike positions for the old firmware.

    This is function for data starting at 2019/11/05 with new firmware.

    Parameters
    ----------
    current_first_cap: ndarray
        First capacitor of the current event
    previous_first_cap: ndarray
        First capacitor of the previous event

    Returns
    -------
    positions: list[int]
        List of spike positions
    """
    return get_spike_A_positions_base(
        current_first_cap=current_first_cap,
        previous_first_cap=previous_first_cap,
        shift=0
    )


@njit(cache=True)
def get_spike_A_positions_old_firmware(current_first_cap, previous_first_cap):
    """
    Find spike positions for the old firmware.

    This is function for data from 2018/10/10 to 2019/11/04 with old firmware.

    Parameters
    ----------
    current_first_cap: ndarray
        First capacitor of the current event
    previous_first_cap: ndarray
        First capacitor of the previous event

    Returns
    -------
    positions: list[int]
        List of spike positions
    """
    return get_spike_A_positions_base(
        current_first_cap=current_first_cap,
        previous_first_cap=previous_first_cap,
        shift=1
    )


@njit(cache=True)
def interpolate_spike_positions(waveform, positions):
    '''Interpolate all spikes at given positions in waveform'''
    for spike_A_position in positions:
        if 2 < spike_A_position < (N_SAMPLES - 2):
            interpolate_spike_A(waveform, spike_A_position)


@njit(cache=True)
def interpolate_spikes(waveform, first_capacitors, previous_first_capacitors, run_id):
    """
    Interpolate Spike type A. Modifies waveform in place

    Parameters
    ----------
    waveform : ndarray
        Waveform stored in a numpy array of shape
        (N_GAINS, N_PIXELS, N_SAMPLES).
    first_capacitors : ndarray
        Value of first capacitor stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    previous_first_capacitors : ndarray
        Value of first capacitor from previous event
        stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    """
    for gain in range(N_GAINS):
        for pixel in range(N_PIXELS):
            current_fc = first_capacitors[gain, pixel]
            last_fc = previous_first_capacitors[gain, pixel]

            if run_id > LAST_RUN_WITH_OLD_FIRMWARE:
                positions = get_spike_A_positions(current_fc, last_fc)
            else:
                positions = get_spike_A_positions_old_firmware(current_fc, last_fc)

            interpolate_spike_positions(
                waveform=waveform[gain, pixel],
                positions=positions,
            )


@njit(cache=True)
def interpolate_spikes_gain_selected(waveform, first_capacitors, previous_first_capacitors, selected_gain_channel, run_id):
    """
    Interpolate Spike type A. Modifies waveform in place

    Parameters
    ----------
    waveform : ndarray
        Waveform stored in a numpy array of shape
        (N_GAINS, N_PIXELS, N_SAMPLES).
    first_capacitors : ndarray
        Value of first capacitor stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    previous_first_capacitors : ndarray
        Value of first capacitor from previous event
        stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    selected_gain_channel: ndarray
        ndarray of shape (N_PIXELS, ) containing the selected gain channel
        for each pixel
    run_id: int
        Run id of the run, used to determine if code for new firmware
        or old firmware has to be used
    """

    for pixel in range(N_PIXELS):
        gain = selected_gain_channel[pixel]
        current_fc = first_capacitors[gain, pixel]
        last_fc = previous_first_capacitors[gain, pixel]

        if run_id > LAST_RUN_WITH_OLD_FIRMWARE:
            positions = get_spike_A_positions(current_fc, last_fc)
        else:
            positions = get_spike_A_positions_old_firmware(current_fc, last_fc)

        interpolate_spike_positions(
            waveform=waveform[pixel],
            positions=positions,
        )


@njit(cache=True)
def subtract_spikes_at_positions(waveform, positions, spike_height):
    '''Subtract the spikes at given positions in waveform'''
    for spike_position in positions:
        for i in range(3):
            sample = spike_position + i
            if 0 <= sample < N_SAMPLES:
                waveform[sample] -= spike_height[i]


@njit(cache=True)
def subtract_spikes(
    waveform,
    first_capacitors,
    previous_first_capacitors,
    run_id,
    spike_height,
):
    """
    Subtract mean spike heights for spike type A.

    Modifies waveform in place.

    Parameters
    ----------
    waveform : ndarray
        Waveform stored in a numpy array of shape
        (N_GAINS, N_PIXELS, N_SAMPLES).
    first_capacitors : ndarray
        Value of first capacitor stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    previous_first_capacitors : ndarray
        Value of first capacitor from previous event
        stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    run_id: int
        Run id of the run, used to determine if code for new firmware
        or old firmware has to be used
    spike_height: ndarray
        ndarry of shape (N_GAINS, N_PIXELS, 3) of the three spike_heights
    """
    for gain in range(N_GAINS):
        for pixel in range(N_PIXELS):
            current_fc = first_capacitors[gain, pixel]
            last_fc = previous_first_capacitors[gain, pixel]

            if run_id > LAST_RUN_WITH_OLD_FIRMWARE:
                positions = get_spike_A_positions(current_fc, last_fc)
            else:
                positions = get_spike_A_positions_old_firmware(current_fc, last_fc)

            subtract_spikes_at_positions(
                waveform=waveform[gain, pixel],
                positions=positions,
                spike_height=spike_height[gain, pixel],
            )


@njit(cache=True)
def subtract_spikes_gain_selected(
    waveform,
    first_capacitors,
    previous_first_capacitors,
    selected_gain_channel,
    run_id,
    spike_height,
):
    """
    Subtract mean spike heights for spike type A for gain selected input data

    Modifies waveform in place.

    Parameters
    ----------
    waveform : ndarray
        Waveform stored in a numpy array of shape
        (N_GAINS, N_PIXELS, N_SAMPLES).
    first_capacitors : ndarray
        Value of first capacitor stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    previous_first_capacitors : ndarray
        Value of first capacitor from previous event
        stored in a numpy array of shape
        (N_GAINS, N_PIXELS).
    selected_gain_channel: ndarray
        ndarray of shape (N_PIXELS, ) containing the selected gain channel
        for each pixel
    run_id: int
        Run id of the run, used to determine if code for new firmware
        or old firmware has to be used
    spike_height: ndarray
        ndarry of shape (N_GAINS, N_PIXELS, 3) of the three spike_heights
    """

    for pixel in range(N_PIXELS):
        gain = selected_gain_channel[pixel]
        current_fc = first_capacitors[gain, pixel]
        last_fc = previous_first_capacitors[gain, pixel]

        if run_id > LAST_RUN_WITH_OLD_FIRMWARE:
            positions = get_spike_A_positions(current_fc, last_fc)
        else:
            positions = get_spike_A_positions_old_firmware(current_fc, last_fc)

        subtract_spikes_at_positions(
            waveform=waveform[pixel],
            positions=positions,
            spike_height=spike_height[gain, pixel],
        )


@njit(cache=True)
def subtract_pedestal(
    waveform,
    first_capacitors,
    pedestal_value_array,
):
    """
    Numba function to subtract the drs4 pedestal.
    Mutates input array inplace
    """

    for gain in range(N_GAINS):
        for pixel_id in range(N_PIXELS):
            # waveform is already reordered to pixel ids,
            # the first caps are not, so we need to translate here.
            first_cap = first_capacitors[gain, pixel_id]
            pedestal = pedestal_value_array[gain, pixel_id, first_cap:first_cap + N_SAMPLES]
            waveform[gain, pixel_id] -= pedestal


@njit(cache=True)
def subtract_pedestal_gain_selected(
    waveform,
    first_capacitors,
    pedestal_value_array,
    selected_gain_channel,
):
    """
    Numba function to subtract the drs4 pedestal.
    Mutates input array inplace
    """
    for pixel_id in range(N_PIXELS):
        gain = selected_gain_channel[pixel_id]
        # waveform is already reordered to pixel ids,
        # the first caps are not, so we need to translate here.
        first_cap = first_capacitors[gain, pixel_id]
        pedestal = pedestal_value_array[gain, pixel_id, first_cap:first_cap + N_SAMPLES]
        waveform[pixel_id] -= pedestal


@njit(cache=True)
def apply_timelapse_correction_pixel(
    waveform,
    first_capacitor,
    time_now,
    last_readout_time
):
    '''
    Apply timelapse correction for a single pixel.
    All inputs are numbers / arrays only for the given pixel / gain channel.
    '''
    for sample in range(N_SAMPLES):
        capacitor = (first_capacitor + sample) % N_CAPACITORS_PIXEL

        last_readout_time_cap = last_readout_time[capacitor]

        # apply correction if last readout available
        if last_readout_time_cap > 0:
            time_diff = time_now - last_readout_time_cap
            time_diff_ms = time_diff / CLOCK_FREQUENCY_KHZ

            # FIXME: Why only for values < 100 ms, negligible otherwise?
            if time_diff_ms < 100:
                waveform[sample] -= ped_time(time_diff_ms)


@njit(cache=True)
def update_last_readout_time(
    pixel_in_module,
    first_capacitor,
    time_now,
    last_readout_time
):
    # update the last read time for all samples
    for sample in range(N_SAMPLES):
        capacitor = (first_capacitor + sample) % N_CAPACITORS_PIXEL
        last_readout_time[capacitor] = time_now

    # now the magic of Dragon,
    # extra conditions on the number of capacitor times being updated
    # if the ROI is in the last quarter of each DRS4
    # for even channel numbers extra 12 slices are read in a different place
    # code from Takayuki & Julian
    # largely refactored by M. Nöthe
    if (pixel_in_module % 2) == 0:
        first_capacitor_in_channel = first_capacitor % N_CAPACITORS_CHANNEL
        if 767 < first_capacitor_in_channel < 1013:
            start = first_capacitor + N_CAPACITORS_CHANNEL
            end = start + 12
            for capacitor in range(start, end):
                last_readout_time[capacitor % N_CAPACITORS_PIXEL] = time_now

        elif first_capacitor_in_channel >= 1013:
            start = first_capacitor + N_CAPACITORS_CHANNEL
            channel = first_capacitor // N_CAPACITORS_CHANNEL
            end = (channel + 2) * N_CAPACITORS_CHANNEL
            for capacitor in range(start, end):
                last_readout_time[capacitor % N_CAPACITORS_PIXEL] = time_now


@njit(cache=True)
def update_last_readout_time_old_firmware(pixel_in_module, first_capacitor, time_now, last_readout_time):
    for sample in range(-1, N_SAMPLES - 1):
        capacitor = (first_capacitor + sample) % N_CAPACITORS_PIXEL
        last_readout_time[capacitor] = time_now

    # now the magic of Dragon,
    # if the ROI is in the last quarter of each DRS4
    # for even channel numbers extra 12 slices are read in a different place
    # code from Takayuki & Julian
    # largely refactored by M. Nöthe
    if pixel_in_module % 2 == 0:
        first_capacitor_in_channel = first_capacitor % N_CAPACITORS_CHANNEL
        if 766 < first_capacitor_in_channel < 1013:
            start = first_capacitor + N_CAPACITORS_CHANNEL - 1
            end = first_capacitor + N_CAPACITORS_CHANNEL + 11
            for capacitor in range(start, end):
                last_readout_time[capacitor % N_CAPACITORS_PIXEL] = time_now

        elif first_capacitor_in_channel >= 1013:
            start = first_capacitor + N_CAPACITORS_CHANNEL
            channel = first_capacitor // N_CAPACITORS_CHANNEL
            end = (channel + 2) * N_CAPACITORS_CHANNEL
            for capacitor in range(start, end):
                last_readout_time[capacitor % N_CAPACITORS_PIXEL] = time_now


@njit(cache=True)
def apply_timelapse_correction(
    waveform,
    local_clock_counter,
    first_capacitors,
    last_readout_time,
    expected_pixels_id,
    run_id,
):
    """
    Apply time lapse baseline correction for data not yet gain selected.

    Mutates the waveform and last_readout_time arrays.
    """
    n_modules = len(expected_pixels_id) // N_PIXELS_MODULE
    for gain in range(N_GAINS):
        for module in range(n_modules):
            time_now = local_clock_counter[module]
            for pixel_in_module in range(N_PIXELS_MODULE):
                pixel_index = module * N_PIXELS_MODULE + pixel_in_module
                pixel_id = expected_pixels_id[pixel_index]

                apply_timelapse_correction_pixel(
                    waveform=waveform[gain, pixel_id],
                    first_capacitor=first_capacitors[gain, pixel_id],
                    time_now=time_now,
                    last_readout_time=last_readout_time[gain, pixel_id],
                )

                if run_id > LAST_RUN_WITH_OLD_FIRMWARE:
                    update_last_readout_time(
                        pixel_in_module=pixel_in_module,
                        first_capacitor=first_capacitors[gain, pixel_id],
                        time_now=time_now,
                        last_readout_time=last_readout_time[gain, pixel_id],
                    )
                else:
                    update_last_readout_time_old_firmware(
                        pixel_in_module=pixel_in_module,
                        first_capacitor=first_capacitors[gain, pixel_id],
                        time_now=time_now,
                        last_readout_time=last_readout_time[gain, pixel_id],
                    )


@njit(cache=True)
def apply_timelapse_correction_gain_selected(
    waveform,
    local_clock_counter,
    first_capacitors,
    last_readout_time,
    expected_pixels_id,
    selected_gain_channel,
    run_id,
):
    """
    Apply time lapse baseline correction to already gain selected data.

    Mutates the waveform and last_readout_time arrays.
    """
    n_modules = len(expected_pixels_id) // N_PIXELS_MODULE
    for module in range(n_modules):
        time_now = local_clock_counter[module]
        for pixel_in_module in range(N_PIXELS_MODULE):

            pixel_index = module * N_PIXELS_MODULE + pixel_in_module
            pixel_id = expected_pixels_id[pixel_index]
            gain = selected_gain_channel[pixel_id]

            apply_timelapse_correction_pixel(
                waveform=waveform[pixel_id],
                first_capacitor=first_capacitors[gain, pixel_id],
                time_now=time_now,
                last_readout_time=last_readout_time[gain, pixel_id],
            )

            # we need to update the last readout times of all gains
            # not just the selected channel
            for gain in range(N_GAINS):
                if run_id > LAST_RUN_WITH_OLD_FIRMWARE:
                    update_last_readout_time(
                        pixel_in_module=pixel_in_module,
                        first_capacitor=first_capacitors[gain, pixel_id],
                        time_now=time_now,
                        last_readout_time=last_readout_time[gain, pixel_id],
                    )
                else:
                    update_last_readout_time_old_firmware(
                        pixel_in_module=pixel_in_module,
                        first_capacitor=first_capacitors[gain, pixel_id],
                        time_now=time_now,
                        last_readout_time=last_readout_time[gain, pixel_id],
                    )


@njit(cache=True)
def ped_time(timediff):
    """
    Power law function for time lapse baseline correction.
    Coefficients from curve fitting to dragon test data
    at temperature 20 degC
    """
    # old values at 30 degC (used till release v0.4.5)
    # return 27.33 * np.power(timediff, -0.24) - 10.4

    # new values at 20 degC, provided by Yokiho Kobayashi 2/3/2020
    # see also Yokiho's talk in https://indico.cta-observatory.org/event/2664/
    return 32.99 * timediff**(-0.22) - 11.9



@njit(cache=True)
def calc_drs4_time_correction_gain_selected(
    first_capacitors, selected_gain_channel, fan, fbn
):
    _n_gains, n_pixels, n_harmonics = fan.shape
    time = np.zeros(n_pixels)

    for pixel in range(n_pixels):
        gain = selected_gain_channel[pixel]
        first_capacitor = first_capacitors[gain, pixel]
        time[pixel] = calc_fourier_time_correction(
            first_capacitor, fan[gain, pixel], fbn[gain, pixel]
        )
    return time


@njit(cache=True)
def calc_drs4_time_correction_both_gains(
    first_capacitors, fan, fbn
):
    time = np.zeros((N_GAINS, N_PIXELS))

    for gain in range(N_GAINS):
        for pixel in range(N_PIXELS):
            first_capacitor = first_capacitors[gain, pixel]
            time[gain, pixel] = calc_fourier_time_correction(
                first_capacitor, fan[gain, pixel], fbn[gain, pixel]
            )
    return time


@njit(cache=True)
def calc_fourier_time_correction(first_capacitor, fan, fbn):
    n_harmonics = len(fan)

    time = 0
    first_capacitor = first_capacitor % N_CAPACITORS_CHANNEL

    for harmonic in range(1, n_harmonics):
        a = fan[harmonic]
        b = fbn[harmonic]
        omega = harmonic * (2 * np.pi / N_CAPACITORS_CHANNEL)

        time += a * np.cos(omega * first_capacitor)
        time += b * np.sin(omega * first_capacitor)

    return time
