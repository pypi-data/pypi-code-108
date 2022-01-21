from pathlib import Path
import json
import os

from ctapipe.io import read_table
from ctapipe.containers import EventType
import numpy as np
from astropy.time import Time
import astropy.units as u


test_data = Path(os.getenv('LSTCHAIN_TEST_DATA', 'test_data'))
test_r0_path = test_data / 'real/R0/20200218/LST-1.1.Run02008.0000_first50.fits.fz'
test_calib_path = test_data / 'real/monitoring/PixelCalibration/LevelA/calibration/20200218/v0.8.2.post2.dev48+gb1343281/calibration_filters_52.Run02006.0000.h5'
test_drs4_pedestal_path = test_data / 'real/monitoring/PixelCalibration/LevelA/drs4_baseline/20200218/v0.8.2.post2.dev48+gb1343281/drs4_pedestal.Run02005.0000.h5'
test_time_calib_path = test_data / 'real/monitoring/PixelCalibration/LevelA/drs4_time_sampling_from_FF/20191124/v0.8.2.post2.dev48+gb1343281/time_calibration.Run01625.0000.h5'
test_drive_report = test_data / 'real/monitoring/DrivePositioning/drive_log_20200218.txt'
test_run_summary = test_data / 'real/monitoring/RunSummary/RunSummary_20200218.ecsv'


def test_stage1(tmp_path):
    """Test the ctapipe stage1 tool can read in LST real data using the event source"""
    from ctapipe.tools.process import ProcessorTool
    from ctapipe.core.tool import run_tool

    config_path = tmp_path / 'config.json'

    config = {
        'LSTEventSource': {
            'LSTR0Corrections': {
                'drs4_pedestal_path': str(test_drs4_pedestal_path),
                'drs4_time_calibration_path': str(test_time_calib_path),
                'calibration_path': str(test_calib_path),
            },
            'PointingSource': {
                'drive_report_path': str(test_drive_report)
            },
            'EventTimeCalculator': {
                'run_summary_path': str(test_run_summary),
            },
        },
        "CameraCalibrator": {
            "image_extractor_type": "LocalPeakWindowSum",
            "LocalPeakWindowSum": {
                "window_shift": 4,
                "window_width": 8,
                "apply_integration_correction": False,
            }
        },
        "TailcutsImageCleaner": {
            "picture_threshold_pe": 6,
            "boundary_threshold_pe": 3,
            "keep_isolated_pixels": False,
            "min_picture_neighbors": 1,
        }
    }
    with config_path.open('w') as f:
        json.dump(config, f)

    tool = ProcessorTool()
    output = tmp_path / "test_dl1.h5"

    ret = run_tool(tool, argv=[
        f'--input={test_r0_path}',
        f'--output={output}',
        f'--config={config_path}',
    ])
    assert ret == 0

    # test our custom default works
    assert tool.event_source.r0_r1_calibrator.gain_selector.threshold == 3500

    parameters = read_table(output, '/dl1/event/telescope/parameters/tel_001')
    assert len(parameters) == 200

    trigger = read_table(output, '/dl1/event/subarray/trigger')

    # test regression of event time calculation
    first_event_time = Time(59101.95035244, format='mjd', scale='tai')
    assert np.all((trigger['time'] - first_event_time).to_value(u.s) < 10)

    event_type_counts = np.bincount(trigger['event_type'])

    # one pedestal and flat field expected each, rest should be physics data
    assert event_type_counts.sum() == 200
    assert event_type_counts[EventType.FLATFIELD.value] == 1
    assert event_type_counts[EventType.SKY_PEDESTAL.value] == 1
    assert event_type_counts[EventType.SUBARRAY.value] == 198


def test_no_ff_tagging(tmp_path):
    """Test the ctapipe stage1 tool can read in LST real data using the event source"""
    from ctapipe.tools.process import ProcessorTool
    from ctapipe.core.tool import run_tool

    config_path = tmp_path / 'config.json'

    config = {
        'LSTEventSource': {
            "use_flatfield_heuristic": False,
            'LSTR0Corrections': {
                'drs4_pedestal_path': str(test_drs4_pedestal_path),
                'drs4_time_calibration_path': str(test_time_calib_path),
                'calibration_path': str(test_calib_path),
            },
            'PointingSource': {
                'drive_report_path': str(test_drive_report)
            },
            'EventTimeCalculator': {
                'run_summary_path': str(test_run_summary),
            },
        },
        "CameraCalibrator": {
            "image_extractor_type": "LocalPeakWindowSum",
            "LocalPeakWindowSum": {
                "window_shift": 4,
                "window_width": 8,
                "apply_integration_correction": False,
            }
        },
        "TailcutsImageCleaner": {
            "picture_threshold_pe": 6,
            "boundary_threshold_pe": 3,
            "keep_isolated_pixels": False,
            "min_picture_neighbors": 1,
        }
    }
    with config_path.open('w') as f:
        json.dump(config, f)

    tool = ProcessorTool()
    output = tmp_path / "test_dl1.h5"

    ret = run_tool(tool, argv=[
        f'--input={test_r0_path}',
        f'--output={output}',
        f'--config={config_path}',
    ])
    assert ret == 0

    # test our custom default works
    assert tool.event_source.r0_r1_calibrator.gain_selector.threshold == 3500

    parameters = read_table(output, '/dl1/event/telescope/parameters/tel_001')
    assert len(parameters) == 200

    trigger = read_table(output, '/dl1/event/subarray/trigger')

    # test regression of event time calculation
    first_event_time = Time(59101.95035244, format='mjd', scale='tai')
    assert np.all((trigger['time'] - first_event_time).to_value(u.s) < 10)

    event_type_counts = np.bincount(trigger['event_type'])

    # one pedestal and flat field expected each, rest should be physics data
    # without ff heuristic, the ff event will have type SUBARRAY
    assert event_type_counts.sum() == 200
    assert event_type_counts[EventType.FLATFIELD.value] == 0
    assert event_type_counts[EventType.SKY_PEDESTAL.value] == 1
    assert event_type_counts[EventType.SUBARRAY.value] == 199
