import os
from pathlib import Path
import tempfile

import numpy as np
import astropy.units as u
from traitlets.config import Config
import pytest
import tables

from ctapipe.containers import EventType
from ctapipe.calib.camera.gainselection import ThresholdGainSelector

from ctapipe_io_lst.constants import N_GAINS, N_PIXELS_MODULE, N_SAMPLES, N_PIXELS

test_data = Path(os.getenv('LSTCHAIN_TEST_DATA', 'test_data')).absolute()
test_r0_dir = test_data / 'real/R0/20200218'
test_r0_path = test_r0_dir / 'LST-1.1.Run02006.0004.fits.fz'
test_r0_path_all_streams = test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz'

test_missing_module_path = test_data / 'real/R0/20210215/LST-1.1.Run03669.0000_first50.fits.fz'

test_drive_report = test_data / 'real/monitoring/DrivePositioning/drive_log_20200218.txt'

# ADC_SAMPLES_SHAPE = (2, 14, 40)


config = Config()
config.LSTEventSouce.EventTimeCalculator.extract_reference = True


def test_loop_over_events():
    from ctapipe_io_lst import LSTEventSource

    n_events = 10
    source = LSTEventSource(
        input_url=test_r0_path,
        max_events=n_events,
        apply_drs4_corrections=False,
        pointing_information=False,
    )

    for i, event in enumerate(source):
        assert event.count == i
        for telid in event.r0.tel.keys():
            n_gains = 2
            n_pixels = source.subarray.tels[telid].camera.geometry.n_pixels
            n_samples = event.lst.tel[telid].svc.num_samples
            waveform_shape = (n_gains, n_pixels, n_samples)
            assert event.r0.tel[telid].waveform.shape == waveform_shape
            assert event.mon.tel[telid].pixel_status.hardware_failing_pixels.shape == (n_gains, n_pixels)

    # make sure max_events works
    assert (i + 1) == n_events


def test_multifile():
    from ctapipe_io_lst import LSTEventSource

    event_count = 0

    with LSTEventSource(
        input_url=test_r0_path_all_streams,
        apply_drs4_corrections=False,
        pointing_information=False,
    ) as source:
        assert len(set(source.file_list)) == 4
        assert len(source) == 200

        for event in source:
            event_count += 1
            # make sure all events are present and in the correct order
            assert event.index.event_id == event_count

    # make sure we get all events from all streams (50 per stream)
    assert event_count == 200


def test_is_compatible():
    from ctapipe_io_lst import LSTEventSource
    assert LSTEventSource.is_compatible(test_r0_path)


def test_event_source_for_lst_file():
    from ctapipe.io import EventSource

    reader = EventSource(test_r0_path)

    # import here to see if ctapipe detects plugin
    from ctapipe_io_lst import LSTEventSource

    assert isinstance(reader, LSTEventSource)
    assert reader.input_url == test_r0_path


def test_subarray():
    from ctapipe_io_lst import LSTEventSource

    source = LSTEventSource(test_r0_path)
    subarray = source.subarray
    subarray.info()
    subarray.to_table()

    assert source.lst_service.telescope_id == 1
    assert source.lst_service.num_modules == 265

    with tempfile.NamedTemporaryFile(suffix='.h5') as f:
        subarray.to_hdf(f.name)


def test_missing_modules():
    from ctapipe_io_lst import LSTEventSource
    source = LSTEventSource(
        test_missing_module_path,
        apply_drs4_corrections=False,
        pointing_information=False,
    )

    assert source.lst_service.telescope_id == 1
    assert source.lst_service.num_modules == 264

    fill = np.iinfo(np.uint16).max
    for event in source:
        # one module missing, so 7 pixels
        assert np.count_nonzero(event.mon.tel[1].pixel_status.hardware_failing_pixels) == N_PIXELS_MODULE * N_GAINS
        assert np.count_nonzero(event.r0.tel[1].waveform == fill) == N_PIXELS_MODULE * N_SAMPLES * N_GAINS

        # 514 is one of the missing pixels
        assert np.all(event.r0.tel[1].waveform[:, 514] == fill)


def test_gain_selected():
    from ctapipe_io_lst import LSTEventSource

    config = Config(dict(
        LSTEventSource=dict(
            default_trigger_type='tib',  # ucts unreliable in this run
            apply_drs4_corrections=True,
            pointing_information=False,
            LSTR0Corrections=dict(
                apply_drs4_pedestal_correction=False,
                apply_spike_correction=False,
                apply_timelapse_correction=False,
                offset=400,
            )
        )
    ))

    source = LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50_gainselected.fits.fz',
        config=config,
    )
    original_source = LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
        config=config,
    )
    gain_selector = ThresholdGainSelector(threshold=3500)
    for event, original_event in zip(source, original_source):
        if event.trigger.event_type in {EventType.FLATFIELD, EventType.SKY_PEDESTAL}:
            assert event.r0.tel[1].waveform is not None
            assert event.r0.tel[1].waveform.shape == (N_GAINS, N_PIXELS, N_SAMPLES)
            assert event.r1.tel[1].waveform is not None
            assert event.r1.tel[1].waveform.shape == (N_GAINS, N_PIXELS, N_SAMPLES - 4)
        else:
            if event.r0.tel[1].waveform is not None:
                assert event.r0.tel[1].waveform.shape == (N_GAINS, N_PIXELS, N_SAMPLES)

            assert event.r1.tel[1].waveform.shape == (N_PIXELS, N_SAMPLES - 4)

            # compare to original file
            selected_gain = gain_selector(original_event.r1.tel[1].waveform)
            pixel_idx = np.arange(N_PIXELS)
            waveform = original_event.r1.tel[1].waveform[selected_gain, pixel_idx]
            assert np.allclose(event.r1.tel[1].waveform, waveform)

    assert event.count == 199


def test_pointing_info():

    from ctapipe_io_lst import LSTEventSource

    # test source works when not requesting pointing info
    with LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
        apply_drs4_corrections=False,
        pointing_information=False,
        max_events=1
    ) as source:
        for e in source:
            assert np.isnan(e.pointing.tel[1].azimuth)

    # test we get an error when requesting pointing info but nor drive report given
    with pytest.raises(ValueError):
        with LSTEventSource(
            test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
            apply_drs4_corrections=False,
            max_events=1
        ) as source:
            next(iter(source))


    config = {
        'LSTEventSource': {
            'apply_drs4_corrections': False,
            'max_events': 1,
            'PointingSource': {
                'drive_report_path': str(test_drive_report)
            },
        },
    }

    with LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
        config=Config(config),
    ) as source:
        for e in source:
            # Tue Feb 18 21:03:09 2020 1582059789 Az 197.318 197.287 197.349 0 El 7.03487 7.03357 7.03618 0.0079844 RA 83.6296 Dec 22.0144
            assert u.isclose(e.pointing.array_ra, 83.6296 * u.deg)
            assert u.isclose(e.pointing.array_dec, 22.0144 * u.deg)

            expected_alt = (90 - 7.03487) * u.deg
            assert u.isclose(e.pointing.tel[1].altitude.to(u.deg), expected_alt, rtol=1e-2)

            expected_az = 197.318 * u.deg
            assert u.isclose(e.pointing.tel[1].azimuth.to(u.deg), expected_az, rtol=1e-2)



def test_len():
    from ctapipe_io_lst import LSTEventSource

    with LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
        apply_drs4_corrections=False,
        pointing_information=False,
    ) as source:
        assert len(source) == 200

    with LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
        pointing_information=False,
        apply_drs4_corrections=False,
        max_events=10,
    ) as source:
        assert len(source) == 10


def test_pedestal_events(tmp_path):
    from ctapipe_io_lst import LSTEventSource

    path = tmp_path / 'pedestal_events.h5'
    with tables.open_file(path, 'w') as f:
        data = np.array([(2008, 5), (2008, 11)], dtype=[('obs_id', int), ('event_id', int)])
        f.create_table('/', 'interleaved_pedestal_ids', obj=data)

    with LSTEventSource(
        test_r0_dir / 'LST-1.1.Run02008.0000_first50.fits.fz',
        pedestal_ids_path=path,
        apply_drs4_corrections=False,
        pointing_information=False,
    ) as source:
        for event in source:
            if event.index.event_id in {5, 11}:
                assert event.trigger.event_type == EventType.SKY_PEDESTAL
            else:
                assert event.trigger.event_type != EventType.SKY_PEDESTAL
