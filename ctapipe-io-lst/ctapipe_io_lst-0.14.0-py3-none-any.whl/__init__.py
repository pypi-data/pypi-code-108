# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
EventSource for LSTCam protobuf-fits.fz-files.
"""
import numpy as np
from astropy import units as u
from pkg_resources import resource_filename
import os
from os import listdir
from ctapipe.core import Provenance
from ctapipe.instrument import (
    TelescopeDescription,
    SubarrayDescription,
    CameraDescription,
    CameraReadout,
    CameraGeometry,
    OpticsDescription,
)
from enum import IntFlag, auto

from ctapipe.io import EventSource, read_table
from ctapipe.io.datalevels import DataLevel
from ctapipe.core.traits import Bool, Float, Enum, Path
from ctapipe.containers import (
    PixelStatusContainer, EventType, R0CameraContainer, R1CameraContainer,
)
from ctapipe.coordinates import CameraFrame

from .multifiles import MultiFiles
from .containers import LSTArrayEventContainer, LSTServiceContainer
from .version import __version__
from .calibration import LSTR0Corrections
from .event_time import EventTimeCalculator
from .pointing import PointingSource
from .anyarray_dtypes import (
    CDTS_AFTER_37201_DTYPE,
    CDTS_BEFORE_37201_DTYPE,
    SWAT_DTYPE,
    DRAGON_COUNTERS_DTYPE,
    TIB_DTYPE,
)
from .constants import (
    HIGH_GAIN, N_GAINS, N_PIXELS, N_SAMPLES
)

__all__ = ['LSTEventSource', '__version__']


class TriggerBits(IntFlag):
    '''
    See TIB User manual
    '''
    MONO = auto()
    STEREO = auto()
    CALIBRATION = auto()
    SINGLE_PE = auto()
    SOFTWARE = auto()
    PEDESTAL = auto()
    SLOW_CONTROL = auto()

    PHYSICS = MONO | STEREO
    OTHER = CALIBRATION | SINGLE_PE | SOFTWARE | PEDESTAL | SLOW_CONTROL


class PixelStatus(IntFlag):
    '''
    Pixel status information

    See Section A.5 of the CTA R1 Data Model:
    https://forge.in2p3.fr/dmsf/files/8627
    '''
    RESERVED_0 = auto()
    RESERVED_1 = auto()
    HIGH_GAIN_STORED = auto()
    LOW_GAIN_STORED = auto()
    SATURATED = auto()
    PIXEL_TRIGGER_1 = auto()
    PIXEL_TRIGGER_2 = auto()
    PIXEL_TRIGGER_3 = auto()

    BOTH_GAINS_STORED = HIGH_GAIN_STORED | LOW_GAIN_STORED

OPTICS = OpticsDescription(
    'LST',
    equivalent_focal_length=u.Quantity(28, u.m),
    num_mirrors=1,
    mirror_area=u.Quantity(386.73, u.m**2),
    num_mirror_tiles=198,
)


def get_channel_info(pixel_status):
    '''
    Extract the channel info bits from the pixel_status array.
    See R1 data model, https://forge.in2p3.fr/boards/313/topics/3033

    Returns
    -------
    channel_status: ndarray[uint8]
        0: pixel not read out (defect)
        1: high-gain read out
        2: low-gain read out
        3: both gains read out
    '''
    return (pixel_status & 0b1100) >> 2


def load_camera_geometry(version=4):
    ''' Load camera geometry from bundled resources of this repo '''
    f = resource_filename(
        'ctapipe_io_lst', f'resources/LSTCam-{version:03d}.camgeom.fits.gz'
    )
    Provenance().add_input_file(f, role="CameraGeometry")
    cam = CameraGeometry.from_table(f)
    cam.frame = CameraFrame(focal_length=OPTICS.equivalent_focal_length)
    return cam


def read_pulse_shapes():

    '''
    Reads in the data on the pulse shapes and readout speed, from an external file

    Returns
    -------
    (daq_time_per_sample, pulse_shape_time_step, pulse shapes)
        daq_time_per_sample: time between samples in the actual DAQ (ns, astropy quantity)
        pulse_shape_time_step: time between samples in the returned single-p.e pulse shape (ns, astropy
    quantity)
        pulse shapes: Single-p.e. pulse shapes, ndarray of shape (2, 1640)
    '''

    # temporary replace the reference pulse shape
    # ("oversampled_pulse_LST_8dynode_pix6_20200204.dat")
    # with a dummy one in order to disable the charge corrections in the charge extractor
    infilename = resource_filename(
        'ctapipe_io_lst',
        'resources/oversampled_pulse_LST_8dynode_pix6_20200204.dat'
    )

    data = np.genfromtxt(infilename, dtype='float', comments='#')
    Provenance().add_input_file(infilename, role="PulseShapes")
    daq_time_per_sample = data[0, 0] * u.ns
    pulse_shape_time_step = data[0, 1] * u.ns

    # Note we have to transpose the pulse shapes array to provide what ctapipe
    # expects:
    return daq_time_per_sample, pulse_shape_time_step, data[1:].T


class LSTEventSource(EventSource):
    """
    EventSource for LST R0 data.
    """
    multi_streams = Bool(
        True,
        help='Read in parallel all streams '
    ).tag(config=True)

    min_flatfield_adc = Float(
        default_value=3000.0,
        help=(
            'Events with that have more than ``min_flatfield_pixel_fraction``'
            ' of the pixels inside [``min_flatfield_adc``, ``max_flatfield_adc``]'
            ' get tagged as EventType.FLATFIELD'
        ),
    ).tag(config=True)

    max_flatfield_adc = Float(
        default_value=12000.0,
        help=(
            'Events with that have more than ``min_flatfield_pixel_fraction``'
            ' of the pixels inside [``min_flatfield_adc``, ``max_flatfield_adc``]'
            ' get tagged as EventType.FLATFIELD'
        ),
    ).tag(config=True)

    min_flatfield_pixel_fraction = Float(
        default_value=0.8,
        help=(
            'Events with that have more than ``min_flatfield_pixel_fraction``'
            ' of the pixels inside [``min_flatfield_pe``, ``max_flatfield_pe``]'
            ' get tagged as EventType.FLATFIELD'
        ),
    ).tag(config=True)

    default_trigger_type = Enum(
        ['ucts', 'tib'], default_value='ucts',
        help=(
            'Default source for trigger type information.'
            ' For older data, tib might be the better choice but for data newer'
            ' than 2020-06-25, ucts is the preferred option. The source will still'
            ' fallback to the other device if the chosen default device is not '
            ' available'
        )
    ).tag(config=True)

    use_flatfield_heuristic = Bool(
        default_value=True,
        help=(
            'If true, try to identify flat field events independent of the'
            ' trigger type in the event. See option ``min_flatfield_adc``'
        ),
    ).tag(config=True)

    calibrate_flatfields_and_pedestals = Bool(
        default_value=True,
        help='If True, flat field and pedestal events are also calibrated.'
    ).tag(config=True)

    apply_drs4_corrections = Bool(
        default_value=True,
        help=(
            'Apply DRS4 corrections.'
            ' If True, this will fill R1 waveforms with the corrections applied'
            ' Use the options for the LSTR0Corrections to configure which'
            ' corrections are applied'
        ),
    ).tag(config=True)

    trigger_information = Bool(
        default_value=True,
        help='Fill trigger information.'
    ).tag(config=True)

    pointing_information = Bool(
        default_value=True,
        help=(
            'Fill pointing information.'
            ' Requires specifying `PointingSource.drive_report_path`'
        ),
    ).tag(config=True)

    pedestal_ids_path = Path(
        default_value=None,
        exists=True,
        allow_none=True,
        help=(
            'Path to a file containing the ids of the interleaved pedestal events'
            ' for the current input file'
        )
    )

    classes = [PointingSource, EventTimeCalculator, LSTR0Corrections]

    def __init__(self, input_url=None, **kwargs):
        '''
        Create a new LSTEventSource.

        Parameters
        ----------
        input_url: Path
            Path to or url understood by ``ctapipe.core.traits.Path``.
            If ``multi_streams`` is ``True``, the source will try to read all
            streams matching the given ``input_url``
        **kwargs:
            Any of the traitlets. See ``LSTEventSource.class_print_help``
        '''
        super().__init__(input_url=input_url, **kwargs)

        if self.multi_streams:
            # test how many streams are there:
            # file name must be [stream name]Run[all the rest]
            # All the files with the same [all the rest] are opened

            path, name = os.path.split(os.path.abspath(self.input_url))
            if 'Run' in name:
                _, run = name.split('Run', 1)
            else:
                run = name

            ls = listdir(path)
            self.file_list = []

            for file_name in ls:
                if run in file_name:
                    full_name = os.path.join(path, file_name)
                    self.file_list.append(full_name)

        else:
            self.file_list = [self.input_url]

        self.multi_file = MultiFiles(self.file_list)
        self.geometry_version = 4

        self.camera_config = self.multi_file.camera_config
        self.log.info(
            "Read {} input files".format(
                self.multi_file.num_inputs()
            )
        )
        self.tel_id = self.camera_config.telescope_id
        self._subarray = self.create_subarray(self.geometry_version, self.tel_id)
        self.r0_r1_calibrator = LSTR0Corrections(
            subarray=self._subarray, parent=self
        )
        self.time_calculator = EventTimeCalculator(
            subarray=self.subarray,
            run_id=self.camera_config.configuration_id,
            expected_modules_id=self.camera_config.lstcam.expected_modules_id,
            parent=self,
        )
        self.pointing_source = PointingSource(subarray=self.subarray, parent=self)
        self.lst_service = self.fill_lst_service_container(self.tel_id, self.camera_config)

        self.read_pedestal_ids()

    @property
    def subarray(self):
        return self._subarray

    @property
    def is_simulation(self):
        return False

    @property
    def obs_ids(self):
        # currently no obs id is available from the input files
        return [self.camera_config.configuration_id, ]

    @property
    def datalevels(self):
        if self.r0_r1_calibrator.calibration_path is not None:
            return (DataLevel.R0, DataLevel.R1)
        return (DataLevel.R0, )

    def rewind(self):
        self.multi_file.rewind()

    @staticmethod
    def create_subarray(geometry_version, tel_id=1):
        """
        Obtain the subarray from the EventSource
        Returns
        -------
        ctapipe.instrument.SubarrayDescription
        """

        # camera info from LSTCam-[geometry_version].camgeom.fits.gz file
        camera_geom = load_camera_geometry(version=geometry_version)

        # get info on the camera readout:
        daq_time_per_sample, pulse_shape_time_step, pulse_shapes = read_pulse_shapes()

        camera_readout = CameraReadout(
            'LSTCam',
            1 / daq_time_per_sample,
            pulse_shapes,
            pulse_shape_time_step,
        )

        camera = CameraDescription('LSTCam', camera_geom, camera_readout)

        lst_tel_descr = TelescopeDescription(
            name='LST', tel_type='LST', optics=OPTICS, camera=camera
        )

        tel_descriptions = {tel_id: lst_tel_descr}

        # LSTs telescope position taken from MC from the moment
        tel_positions = {tel_id: [50., 50., 16] * u.m}

        subarray = SubarrayDescription(
            name=f"LST-{tel_id} subarray",
            tel_descriptions=tel_descriptions,
            tel_positions=tel_positions,
        )

        return subarray

    def _generator(self):

        # container for LST data
        array_event = LSTArrayEventContainer()
        array_event.meta['input_url'] = self.input_url
        array_event.meta['max_events'] = self.max_events
        array_event.meta['origin'] = 'LSTCAM'

        # also add service container to the event section
        array_event.lst.tel[self.tel_id].svc = self.lst_service

        # initialize general monitoring container
        self.initialize_mon_container(array_event)

        # loop on events
        for count, zfits_event in enumerate(self.multi_file):
            array_event.count = count
            array_event.index.event_id = zfits_event.event_id
            array_event.index.obs_id = self.obs_ids[0]

            # Skip "empty" events that occur at the end of some runs
            if zfits_event.event_id == 0:
                self.log.warning('Event with event_id=0 found, skipping')
                continue

            self.fill_r0r1_container(array_event, zfits_event)
            self.fill_lst_event_container(array_event, zfits_event)
            if self.trigger_information:
                self.fill_trigger_info(array_event)

            self.fill_mon_container(array_event, zfits_event)

            if self.pointing_information:
                self.fill_pointing_info(array_event)

            # apply low level corrections
            if self.apply_drs4_corrections:
                self.r0_r1_calibrator.apply_drs4_corrections(array_event)

                # flat field tagging is performed on r1 data, so can only
                # be done after the drs4 corrections are applied
                if self.use_flatfield_heuristic:
                    self.tag_flatfield_events(array_event)

            if self.pedestal_ids is not None:
                self.check_interleaved_pedestal(array_event)

            # gain select and calibrate to pe
            if self.r0_r1_calibrator.calibration_path is not None:
                # skip flatfield and pedestal events if asked
                if (
                    self.calibrate_flatfields_and_pedestals
                    or array_event.trigger.event_type not in {EventType.FLATFIELD, EventType.SKY_PEDESTAL}
                ):
                    self.r0_r1_calibrator.calibrate(array_event)

            yield array_event

    @staticmethod
    def is_compatible(file_path):
        from astropy.io import fits
        try:
            # The file contains two tables:
            #  1: CameraConfig
            #  2: Events
            h = fits.open(file_path)[2].header
            ttypes = [
                h[x] for x in h.keys() if 'TTYPE' in x
            ]
        except OSError:
            # not even a fits file
            return False

        except IndexError:
            # A fits file of a different format
            return False

        is_protobuf_zfits_file = (
            (h['XTENSION'] == 'BINTABLE') and
            (h['EXTNAME'] == 'Events') and
            (h['ZTABLE'] is True) and
            (h['ORIGIN'] == 'CTA') and
            (h['PBFHEAD'] == 'R1.CameraEvent')
        )

        is_lst_file = 'lstcam_counters' in ttypes
        return is_protobuf_zfits_file & is_lst_file

    @staticmethod
    def fill_lst_service_container(tel_id, camera_config):
        """
        Fill LSTServiceContainer with specific LST service data data
        (from the CameraConfig table of zfit file)

        """
        return LSTServiceContainer(
            telescope_id=tel_id,
            cs_serial=camera_config.cs_serial,
            configuration_id=camera_config.configuration_id,
            date=camera_config.date,
            num_pixels=camera_config.num_pixels,
            num_samples=camera_config.num_samples,
            pixel_ids=camera_config.expected_pixels_id,
            data_model_version=camera_config.data_model_version,
            num_modules=camera_config.lstcam.num_modules,
            module_ids=camera_config.lstcam.expected_modules_id,
            idaq_version=camera_config.lstcam.idaq_version,
            cdhs_version=camera_config.lstcam.cdhs_version,
            algorithms=camera_config.lstcam.algorithms,
            pre_proc_algorithms=camera_config.lstcam.pre_proc_algorithms,
        )

    def fill_lst_event_container(self, array_event, zfits_event):
        """
        Fill LSTEventContainer with specific LST service data
        (from the Event table of zfit file)

        """
        tel_id = self.tel_id

        lst_evt = array_event.lst.tel[tel_id].evt

        lst_evt.configuration_id = zfits_event.configuration_id
        lst_evt.event_id = zfits_event.event_id
        lst_evt.tel_event_id = zfits_event.tel_event_id
        lst_evt.pixel_status = zfits_event.pixel_status
        lst_evt.ped_id = zfits_event.ped_id
        lst_evt.module_status = zfits_event.lstcam.module_status
        lst_evt.extdevices_presence = zfits_event.lstcam.extdevices_presence

        # if TIB data are there
        if lst_evt.extdevices_presence & 1:
            tib = zfits_event.lstcam.tib_data.view(TIB_DTYPE)[0]
            lst_evt.tib_event_counter = tib['event_counter']
            lst_evt.tib_pps_counter = tib['pps_counter']
            lst_evt.tib_tenMHz_counter = tib['tenMHz_counter']
            lst_evt.tib_stereo_pattern = tib['stereo_pattern']
            lst_evt.tib_masked_trigger = tib['masked_trigger']

        # if UCTS data are there
        if lst_evt.extdevices_presence & 2:
            if int(array_event.lst.tel[tel_id].svc.idaq_version) > 37201:
                cdts = zfits_event.lstcam.cdts_data.view(CDTS_AFTER_37201_DTYPE)[0]
                lst_evt.ucts_timestamp = cdts[0]
                lst_evt.ucts_address = cdts[1]        # new
                lst_evt.ucts_event_counter = cdts[2]
                lst_evt.ucts_busy_counter = cdts[3]   # new
                lst_evt.ucts_pps_counter = cdts[4]
                lst_evt.ucts_clock_counter = cdts[5]
                lst_evt.ucts_trigger_type = cdts[6]
                lst_evt.ucts_white_rabbit_status = cdts[7]
                lst_evt.ucts_stereo_pattern = cdts[8] # new
                lst_evt.ucts_num_in_bunch = cdts[9]   # new
                lst_evt.ucts_cdts_version = cdts[10]  # new

            else:
                # unpack UCTS-CDTS data (old version)
                cdts = zfits_event.lstcam.cdts_data.view(CDTS_BEFORE_37201_DTYPE)[0]
                lst_evt.ucts_event_counter = cdts[0]
                lst_evt.ucts_pps_counter = cdts[1]
                lst_evt.ucts_clock_counter = cdts[2]
                lst_evt.ucts_timestamp = cdts[3]
                lst_evt.ucts_camera_timestamp = cdts[4]
                lst_evt.ucts_trigger_type = cdts[5]
                lst_evt.ucts_white_rabbit_status = cdts[6]

        # if SWAT data are there
        if lst_evt.extdevices_presence & 4:
            # unpack SWAT data
            unpacked_swat = zfits_event.lstcam.swat_data.view(SWAT_DTYPE)[0]
            lst_evt.swat_timestamp = unpacked_swat[0]
            lst_evt.swat_counter1 = unpacked_swat[1]
            lst_evt.swat_counter2 = unpacked_swat[2]
            lst_evt.swat_event_type = unpacked_swat[3]
            lst_evt.swat_camera_flag = unpacked_swat[4]
            lst_evt.swat_camera_event_num = unpacked_swat[5]
            lst_evt.swat_array_flag = unpacked_swat[6]
            lst_evt.swat_array_event_num = unpacked_swat[7]

        # unpack Dragon counters
        counters = zfits_event.lstcam.counters.view(DRAGON_COUNTERS_DTYPE)
        lst_evt.pps_counter = counters['pps_counter']
        lst_evt.tenMHz_counter = counters['tenMHz_counter']
        lst_evt.event_counter = counters['event_counter']
        lst_evt.trigger_counter = counters['trigger_counter']
        lst_evt.local_clock_counter = counters['local_clock_counter']

        lst_evt.chips_flags = zfits_event.lstcam.chips_flags
        lst_evt.first_capacitor_id = zfits_event.lstcam.first_capacitor_id
        lst_evt.drs_tag_status = zfits_event.lstcam.drs_tag_status
        lst_evt.drs_tag = zfits_event.lstcam.drs_tag

        lst_evt.ucts_jump = False

    def fill_trigger_info(self, array_event):
        tel_id = self.tel_id

        trigger = array_event.trigger
        trigger.time = self.time_calculator(tel_id, array_event)
        trigger.tels_with_trigger = [tel_id]
        trigger.tel[tel_id].time = trigger.time

        lst = array_event.lst.tel[tel_id]
        tib_available = lst.evt.extdevices_presence & 1
        ucts_available = lst.evt.extdevices_presence & 2

        # decide which source to use, if both are available,
        # the option decides, if not, fallback to the avilable source
        # if no source available, warn and do not fill trigger info
        if tib_available and ucts_available:
            if self.default_trigger_type == 'ucts':
                trigger_bits = lst.evt.ucts_trigger_type
            else:
                trigger_bits = lst.evt.tib_masked_trigger

        elif tib_available:
            trigger_bits = lst.evt.tib_masked_trigger

        elif ucts_available:
            trigger_bits = lst.evt.ucts_trigger_type

        else:
            self.log.warning('No trigger info available.')
            trigger.event_type = EventType.UNKNOWN
            return

        if (
            ucts_available
            and lst.evt.ucts_trigger_type == 42
            and self.default_trigger_type == "ucts"
        ) :
            self.log.warning(
                'Event with UCTS trigger_type 42 found.'
                ' Probably means unreliable or shifted UCTS data.'
                ' Consider switching to TIB using `default_trigger_type="tib"`'
            )

        # first bit mono trigger, second stereo.
        # If *only* those two are set, we assume it's a physics event
        # for all other we only check if the flag is present
        if (trigger_bits & TriggerBits.PHYSICS) and not (trigger_bits & TriggerBits.OTHER):
            trigger.event_type = EventType.SUBARRAY
        elif trigger_bits & TriggerBits.CALIBRATION:
            trigger.event_type = EventType.FLATFIELD
        elif trigger_bits & TriggerBits.PEDESTAL:
            trigger.event_type = EventType.SKY_PEDESTAL
        elif trigger_bits & TriggerBits.SINGLE_PE:
            trigger.event_type = EventType.SINGLE_PE
        else:
            self.log.warning(f'Event {array_event.index.event_id} has unknown event type, trigger: {trigger_bits:08b}')
            trigger.event_type = EventType.UNKNOWN

    def tag_flatfield_events(self, array_event):
        '''
        Use a heuristic based on R1 waveforms to recognize flat field events

        Currently, tagging of flat field events does not work,
        they are reported as physics events, here a heuristic identifies
        those events. Since trigger types might be wrong due to ucts errors,
        we try to identify flat field events in all trigger types.

        DRS4 corrections but not the p.e. calibration must be applied
        '''
        tel_id = self.tel_id
        waveform = array_event.r1.tel[tel_id].waveform

        # needs to work for gain already selected or not
        if waveform.ndim == 3:
            image = waveform[HIGH_GAIN].sum(axis=1)
        else:
            image = waveform.sum(axis=1)

        in_range = (image >= self.min_flatfield_adc) & (image <= self.max_flatfield_adc)
        n_in_range = np.count_nonzero(in_range)

        looks_like_ff = n_in_range >= self.min_flatfield_pixel_fraction * image.size
        if looks_like_ff:
            array_event.trigger.event_type = EventType.FLATFIELD
            self.log.debug(
                'Setting event type of event'
                f' {array_event.index.event_id} to FLATFIELD'
            )
        elif array_event.trigger.event_type == EventType.FLATFIELD:
            self.log.warning(
                'Found FF event that does not fulfill FF criteria: %d',
                array_event.index.event_id,
            )
            array_event.trigger.event_type = EventType.UNKNOWN

    def fill_pointing_info(self, array_event):
        tel_id = self.tel_id
        pointing = self.pointing_source.get_pointing_position_altaz(
            tel_id, array_event.trigger.time,
        )
        array_event.pointing.tel[tel_id] = pointing
        array_event.pointing.array_altitude = pointing.altitude
        array_event.pointing.array_azimuth = pointing.azimuth

        ra, dec = self.pointing_source.get_pointing_position_icrs(
            tel_id, array_event.trigger.time
        )
        array_event.pointing.array_ra = ra
        array_event.pointing.array_dec = dec

    def fill_r0r1_camera_container(self, zfits_event):
        """
        Fill the r0 or r1 container, depending on whether gain
        selection has already happened (r1) or not (r0)

        This will create waveforms of shape (N_GAINS, N_PIXELS, N_SAMPLES),
        or (N_PIXELS, N_SAMPLES) respectively regardless of the n_pixels, n_samples
        in the file.

        Missing or broken pixels are filled using maxval of the waveform dtype.
        """
        n_pixels = self.camera_config.num_pixels
        n_samples = self.camera_config.num_samples
        expected_pixels = self.camera_config.expected_pixels_id

        has_low_gain = (zfits_event.pixel_status & PixelStatus.LOW_GAIN_STORED).astype(bool)
        has_high_gain = (zfits_event.pixel_status & PixelStatus.HIGH_GAIN_STORED).astype(bool)
        not_broken = (has_low_gain | has_high_gain).astype(bool)

        # broken pixels have both false, so gain selected means checking
        # if there are any pixels where exactly one of high or low gain is stored
        gain_selected = np.any(has_low_gain != has_high_gain)

        # fill value for broken pixels
        dtype = zfits_event.waveform.dtype
        fill = np.iinfo(dtype).max
        # we assume that either all pixels are gain selected or none
        # only broken pixels are allowed to be missing completely
        if gain_selected:
            selected_gain = np.where(has_high_gain, 0, 1)
            waveform = np.full((n_pixels, n_samples), fill, dtype=dtype)
            waveform[not_broken] = zfits_event.waveform.reshape((-1, n_samples))

            reordered_waveform = np.full((N_PIXELS, N_SAMPLES), fill, dtype=dtype)
            reordered_waveform[expected_pixels] = waveform

            reordered_selected_gain = np.full(N_PIXELS, -1, dtype=np.int8)
            reordered_selected_gain[expected_pixels] = selected_gain

            r0 = R0CameraContainer()
            r1 = R1CameraContainer(
                waveform=reordered_waveform,
                selected_gain_channel=reordered_selected_gain,
            )
        else:
            reshaped_waveform = zfits_event.waveform.reshape(N_GAINS, n_pixels, n_samples)
            # re-order the waveform following the expected_pixels_id values
            #  could also just do waveform = reshaped_waveform[np.argsort(expected_ids)]
            reordered_waveform = np.full((N_GAINS, N_PIXELS, N_SAMPLES), fill, dtype=dtype)
            reordered_waveform[:, expected_pixels, :] = reshaped_waveform
            r0 = R0CameraContainer(waveform=reordered_waveform)
            r1 = R1CameraContainer()

        return r0, r1

    def fill_r0r1_container(self, array_event, zfits_event):
        """
        Fill with R0Container

        """
        r0, r1 = self.fill_r0r1_camera_container(zfits_event)
        array_event.r0.tel[self.tel_id] = r0
        array_event.r1.tel[self.tel_id] = r1

    def initialize_mon_container(self, array_event):
        """
        Fill with MonitoringContainer.
        For the moment, initialize only the PixelStatusContainer

        """
        container = array_event.mon
        mon_camera_container = container.tel[self.tel_id]

        shape = (N_GAINS, N_PIXELS)
        # all pixels broken by default
        status_container = PixelStatusContainer(
            hardware_failing_pixels=np.ones(shape, dtype=bool),
            pedestal_failing_pixels=np.zeros(shape, dtype=bool),
            flatfield_failing_pixels=np.zeros(shape, dtype=bool),
        )
        mon_camera_container.pixel_status = status_container

    def fill_mon_container(self, array_event, zfits_event):
        """
        Fill with MonitoringContainer.
        For the moment, initialize only the PixelStatusContainer

        """
        status_container = array_event.mon.tel[self.tel_id].pixel_status

        # reorder the array
        expected_pixels_id = self.camera_config.expected_pixels_id

        reordered_pixel_status = np.zeros(N_PIXELS, dtype=zfits_event.pixel_status.dtype)
        reordered_pixel_status[expected_pixels_id] = zfits_event.pixel_status

        channel_info = get_channel_info(reordered_pixel_status)
        status_container.hardware_failing_pixels[:] = channel_info == 0

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __len__(self):
        if self.max_events is not None:
            return min(self.max_events, len(self.multi_file))
        return len(self.multi_file)

    def close(self):
        self.multi_file.close()

    def read_pedestal_ids(self):
        if self.pedestal_ids_path is not None:
            t = read_table(self.pedestal_ids_path, '/interleaved_pedestal_ids')
            Provenance().add_input_file(
                self.pedestal_ids_path, role="InterleavedPedestalIDs"
            )
            self.pedestal_ids = set(t['event_id'])
        else:
            self.pedestal_ids = None


    def check_interleaved_pedestal(self, array_event):
        event_id = array_event.index.event_id

        if event_id in self.pedestal_ids:
            array_event.trigger.event_type = EventType.SKY_PEDESTAL
            self.log.debug("Event %d is an interleaved pedestal", event_id)

        elif array_event.trigger.event_type == EventType.SKY_PEDESTAL:
            # wrongly tagged pedestal event must be cosmic, since it would
            # have been changed to flatfield by the flatfield tagging if ff
            array_event.trigger.event_type = EventType.SUBARRAY
            self.log.debug(
                "Event %d is tagged as pedestal but not a known pedestal event",
                event_id,
            )

