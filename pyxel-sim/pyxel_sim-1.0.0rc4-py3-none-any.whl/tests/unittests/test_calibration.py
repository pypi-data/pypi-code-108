#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Unittests for the 'Calibration' class."""

from pathlib import Path

import numpy as np
import pytest

from pyxel import Configuration, load
from pyxel.calibration import Calibration
from pyxel.calibration.util import list_to_slice, read_data, read_single_data
from pyxel.detectors import CCD
from pyxel.pipelines import DetectionPipeline, Processor

try:
    import pygmo as pg

    WITH_PYGMO = True
except ImportError:
    WITH_PYGMO = False


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml",
    [
        "tests/data/calibrate.yaml",
        "tests/data/calibrate_sade.yaml",
        "tests/data/calibrate_sga.yaml",
        "tests/data/calibrate_nlopt.yaml",
        "tests/data/calibrate_models.yaml",
        "tests/data/calibrate_custom_fitness.yaml",
        "tests/data/calibrate_fits.yaml",
    ],
)
def test_set_algo(yaml):
    """Test"""
    cfg = load(yaml)
    calibration = cfg.calibration
    obj = calibration.algorithm.get_algorithm()
    if isinstance(obj, pg.sade):
        pass
    elif isinstance(obj, pg.sga):
        pass
    elif isinstance(obj, pg.nlopt):
        pass
    else:
        raise ReferenceError


@pytest.mark.parametrize(
    "input_data",
    [
        [Path("tests/data/calibrate-data.npy")],
        [Path("tests/data/calibrate-data.txt")],
        [Path("tests/data/ascii_input_3.data")],
        [Path("tests/data/ascii_input_4.data")],
        pytest.param(
            Path("tests/data/calibrate-data.npy"),
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        pytest.param(
            Path("tests/data/calibrate-data.txt"),
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        pytest.param(
            Path("tests/data/ascii_input_1.data"),
            marks=pytest.mark.xfail(raises=TypeError),
        ),
        pytest.param(
            Path("tests/data/ascii_input_2.data"),
            marks=pytest.mark.xfail(raises=TypeError),
        ),
    ],
)
def test_read_data(input_data):
    """Test"""
    output = read_data(input_data)
    assert isinstance(output, list)


@pytest.mark.parametrize(
    "input_data",
    [
        # pytest.param(
        #     [Path("tests/data/calibrate-data.npy")],
        #     marks=pytest.mark.xfail(raises=TypeError),
        # ),
        # pytest.param(
        #     [Path("tests/data/calibrate-data.txt")],
        #     marks=pytest.mark.xfail(raises=TypeError),
        # ),
        # pytest.param(
        #     [Path("tests/data/ascii_input_3.data")],
        #     marks=pytest.mark.xfail(raises=TypeError),
        # ),
        # pytest.param(
        #     [Path("tests/data/ascii_input_4.data")],
        #     marks=pytest.mark.xfail(raises=TypeError),
        # ),
        Path("tests/data/calibrate-data.npy"),
        Path("tests/data/calibrate-data.txt"),
        Path("tests/data/ascii_input_1.data"),
        Path("tests/data/ascii_input_2.data"),
    ],
)
def test_read_single_data(input_data):
    output = read_single_data(input_data)

    assert isinstance(output, np.ndarray)


@pytest.mark.parametrize(
    "input_data",
    [
        [1.0, 3.0, 2.0, 5.0],
        [1, 3, 2, 5],
        [0, 0, 0, 0],
        [2, 4, 1, 3, 2, 5],
        [4.0, 8.0, 1.0, 3.0, 2.0, 5.0],
        None,
        # [1],              # TODO
        # [1, 2, 3],
        # [1, 2, 3, 4, 5],
    ],
)
def test_list_to_slice(input_data):
    """Test"""
    output = list_to_slice(input_data)
    if isinstance(output, slice):
        pass
    elif isinstance(output, tuple) and all(isinstance(item, slice) for item in output):
        pass
    else:
        raise TypeError
    print(output)


@pytest.mark.skip(reason="!! FIX THIS TEST !!")
@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize("yaml", ["tests/data/calibrate_models.yaml"])
def test_run_calibration(yaml):
    """Test"""
    cfg = load(yaml)
    assert isinstance(cfg, Configuration)

    detector = cfg.ccd_detector
    assert isinstance(detector, CCD)

    pipeline = cfg.pipeline
    assert isinstance(pipeline, DetectionPipeline)

    processor = Processor(detector, pipeline)
    assert isinstance(processor, Processor)

    calibration = cfg.calibration
    assert isinstance(calibration, Calibration)

    assert calibration is not None
    result = calibration.run_calibration(processor)
    # assert result == 1         # TODO
