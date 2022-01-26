"""Unittests for the 'ModelFitting' class."""
#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pathlib import Path

import numpy as np
import pytest

import pyxel
from pyxel.calibration import Calibration
from pyxel.calibration.fitting import ModelFitting
from pyxel.calibration.util import CalibrationMode
from pyxel.detectors import CCD
from pyxel.pipelines import DetectionPipeline, Processor
from pyxel.pipelines.processor import ResultType

try:
    import pygmo as pg

    WITH_PYGMO = True
except ImportError:
    WITH_PYGMO = False


def configure(mf: ModelFitting, sim: pyxel.Configuration) -> None:
    """TBW."""
    assert sim.calibration is not None

    pg.set_global_rng_seed(sim.calibration.pygmo_seed)
    np.random.seed(sim.calibration.pygmo_seed)

    mf.configure(
        calibration_mode=sim.calibration.calibration_mode,
        generations=sim.calibration.algorithm.generations,
        population_size=sim.calibration.algorithm.population_size,
        simulation_output=sim.calibration.result_type,
        fitness_func=sim.calibration.fitness_function,
        target_output=sim.calibration.target_data_path,
        target_fit_range=sim.calibration.target_fit_range,
        out_fit_range=sim.calibration.result_fit_range,
        weights_from_file=sim.calibration.weights_from_file,
        weights=sim.calibration.weights,
        file_path=None,
    )


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize("yaml_file", ["tests/data/calibrate.yaml"])
def test_configure_params(yaml_file):
    """Test"""
    cfg = pyxel.load(yaml_file)
    detector = cfg.ccd_detector
    pipeline = cfg.pipeline
    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )

    if not isinstance(mf.processor, Processor):
        raise ValueError

    configure(mf, cfg)

    assert mf.calibration_mode == CalibrationMode.Pipeline
    assert mf.sim_fit_range == (
        slice(None, None, None),
        slice(0, 4, None),
        slice(2, 4, None),
    )
    assert mf.targ_fit_range == (slice(1, 5, None), slice(0, 2, None))
    assert mf.sim_output == ResultType.Image


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize("yaml", ["tests/data/calibrate_fits.yaml"])
def test_configure_fits_target(yaml):
    """Test"""
    cfg = pyxel.load(yaml)
    detector = cfg.ccd_detector
    pipeline = cfg.pipeline
    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )
    configure(mf, cfg)
    assert mf.sim_fit_range == (
        slice(None, None, None),
        slice(0, 4, None),
        slice(2, 4, None),
    )
    assert mf.targ_fit_range == (slice(1, 5, None), slice(0, 2, None))
    assert mf.sim_output == ResultType.Image
    expected = np.array(
        [
            [4173.6434, 4203.6883],
            [4468.6537, 4517.2588],
            [4683.7958, 4594.2287],
            [4520.4915, 4315.9494],
        ]
    )
    np.testing.assert_array_equal(
        np.around(mf.all_target_data[0], decimals=4), np.around(expected, decimals=4)
    )


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml", ["tests/data/calibrate.yaml", "tests/data/calibrate_fits.yaml"]
)
def test_boundaries(yaml):
    """Test"""
    cfg = pyxel.load(yaml)
    detector = cfg.ccd_detector
    pipeline = cfg.pipeline
    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )

    configure(mf, cfg)

    lbd_expected = [1.0, -3.0, -3.0, -2.0, -2.0, 0.0, 10.0]
    ubd_expected = [10.0, 0.3010299956639812, 0.3010299956639812, 1.0, 1.0, 1.0, 200.0]
    assert mf.lbd == lbd_expected
    assert mf.ubd == ubd_expected
    ll, uu = mf.get_bounds()
    assert ll == lbd_expected
    assert uu == ubd_expected


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "simulated_data, target_data, expected_fitness",
    [
        # (231, 231, 0.0),
        # (231, 145, 86.0),
        # (2.31, 1.45, 0.8600000000000001),
        # (2.0, 1, 1.0),
        (np.array([1, 9, 45, 548, 2, 2]), np.array([1, 9, 45, 548, 2, 2]), 0.0),
        (np.array([1, 9, 45, 548, 2, 2]), np.array([1, 3, 56, 21, 235, 11]), 786.0),
        (
            np.array([[1362.0, 1378.0], [1308.0, 1309.0]]),
            np.array([[1362.0, 1378.0], [1308.0, 1309.0]]),
            0.0,
        ),
        (
            np.array([[1362.0, 1378.0], [1308.0, 1309.0]]),
            np.array([[1462.0, 1368.0], [1508.0, 1399.0]]),
            400.0,
        ),
    ],
)
def test_calculate_fitness(simulated_data, target_data, expected_fitness):
    """Test"""
    cfg = pyxel.load("tests/data/calibrate.yaml")
    detector = cfg.ccd_detector
    pipeline = cfg.pipeline
    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )
    configure(mf, cfg)
    fitness = mf.calculate_fitness(simulated_data, target_data)
    assert fitness == expected_fitness
    print("fitness: ", fitness)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml, factor, expected_fitness",
    [
        (Path("tests/data/calibrate_weighting.yaml"), 1, 0.0),
        (Path("tests/data/calibrate_weighting.yaml"), 2, 1287593.3479011902),
        (Path("tests/data/calibrate_weighting.yaml"), 3, 2575186.695802381),
    ],
)
def test_weighting(yaml, factor, expected_fitness):
    """Test"""
    cfg = pyxel.load(yaml)
    detector = cfg.ccd_detector
    pipeline = cfg.pipeline
    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )
    configure(mf, cfg)
    fitness = mf.calculate_fitness(
        mf.all_target_data[0] * factor, mf.all_target_data[0]
    )
    assert fitness == expected_fitness
    print("fitness: ", fitness)


def custom_fitness_func(simulated, target, weighting=None):
    """Custom fitness func for testing"""
    return np.sum(target * 2 - simulated / 2 + 1.0)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml, simulated, target, weighting",
    [
        (
            "tests/data/calibrate_custom_fitness.yaml",
            np.array([1.0]),
            np.array([2.0]),
            np.array([4.5]),
        ),
        (
            "tests/data/calibrate_custom_fitness.yaml",
            np.array([1.0, 2.0, 3.0]),
            np.array([2.0, 5.0, 6.0]),
            np.array([26.0]),
        ),
        (
            "tests/data/calibrate_least_squares.yaml",
            np.array([2.0]),
            np.array([4.0]),
            np.array([4.0]),
        ),
    ],
)
def test_custom_fitness(yaml, simulated, target, weighting):
    """Test"""
    cfg = pyxel.load(yaml)
    assert isinstance(cfg, pyxel.Configuration)

    detector = cfg.ccd_detector
    assert isinstance(detector, CCD)

    pipeline = cfg.pipeline
    assert isinstance(pipeline, DetectionPipeline)

    processor = Processor(detector, pipeline)
    assert isinstance(processor, Processor)

    calibration = cfg.calibration
    assert isinstance(calibration, Calibration)

    assert cfg.calibration is not None

    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )
    configure(mf=mf, sim=cfg)

    fitness = mf.calculate_fitness(simulated, target)
    assert fitness == weighting
    print("fitness: ", fitness)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml, parameter, expected_fitness",
    [
        (
            "tests/data/calibrate_models.yaml",
            np.array(
                [
                    1.0,
                    0.5,
                    1.5,
                    -2.0,
                    -3.0,
                    4.5,
                    -4.0,
                    1.0,
                    0.5,
                    -3.5,
                    2.0,
                    -3.0,
                    -4.0,
                    0.5,
                    1.0,
                    100.0,
                ]
            ),
            24521750.21462584,
        )
    ],
)
def test_fitness(yaml, parameter, expected_fitness):
    """Test"""
    cfg = pyxel.load(yaml)

    detector = cfg.ccd_detector
    pipeline = cfg.pipeline

    processor = Processor(detector, pipeline)
    calibration = cfg.calibration

    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )

    configure(mf, cfg)

    overall_fitness = mf.fitness(parameter)
    assert overall_fitness[0] == expected_fitness

    print("fitness: ", overall_fitness[0])


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml, parameter, expected_array",
    [
        (
            "tests/data/calibrate_models.yaml",
            np.arange(16.0),
            np.array(
                [
                    0.0,
                    10.0,
                    100.0,
                    1000.0,
                    10000.0,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    1.0e09,
                    1.0e10,
                    1.0e11,
                    1.0e12,
                    13.0,
                    1.0e14,
                    15.0,
                ]
            ),
        )
    ],
)
def test_split_and_update(yaml, parameter, expected_array):
    """Test"""
    cfg = pyxel.load(yaml)
    detector = cfg.ccd_detector
    pipeline = cfg.pipeline
    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )
    configure(mf, cfg)
    array = mf.convert_to_parameters(parameter)
    np.testing.assert_array_equal(array, expected_array)


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml, param_array",
    [
        (
            "tests/data/calibrate_models.yaml",
            np.array(
                [
                    1.0,
                    10.0,
                    100.0,
                    1000.0,
                    10000.0,
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                    1.0e09,
                    1.0e10,
                    1.0e11,
                    1.0e12,
                    13.0,
                    1.0e14,
                    150,
                ]
            ),
        )
    ],
)
def test_detector_and_model_update(yaml: str, param_array: np.ndarray):
    """Test"""
    cfg = pyxel.load(yaml)

    detector = cfg.ccd_detector
    pipeline = cfg.pipeline

    processor = Processor(detector, pipeline)
    calibration = cfg.calibration
    mf = ModelFitting(
        processor=processor,
        variables=calibration.parameters,
        readout=calibration.readout,
    )
    configure(mf=mf, sim=cfg)
    mf.processor = mf.update_processor(param_array, processor)

    assert mf.processor.pipeline.charge_transfer is not None
    assert mf.processor.pipeline.charge_measurement is not None

    attributes = [
        mf.processor.detector.characteristics.pre_amplification,
        mf.processor.pipeline.charge_transfer.models[0].arguments["trap_release_times"],
        mf.processor.pipeline.charge_transfer.models[0].arguments["trap_densities"],
        mf.processor.pipeline.charge_transfer.models[0].arguments["sigma"],
        mf.processor.pipeline.charge_transfer.models[0].arguments["beta"],
        mf.processor.pipeline.charge_measurement.models[1].arguments["std_deviation"],
        mf.processor.detector.environment.temperature,
    ]
    a = 0
    for idx, attr in enumerate(attributes):
        if isinstance(attr, np.ndarray):
            b = len(attr)
            np.testing.assert_array_equal(attr, param_array[a : a + b])
        else:
            b = 1
            assert attr == param_array[a]
        a += b
