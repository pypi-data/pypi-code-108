#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


from pathlib import Path

import pytest
from freezegun import freeze_time

import pyxel


@pytest.fixture
def config_no_running_mode(tmp_path: Path) -> Path:
    """Create a configuration file without a valid running mode."""
    content = """
ccd_detector:

  geometry:

    row: 450               # pixel
    col: 450               # pixel
    total_thickness: 40.    # um
    pixel_vert_size: 10.    # um
    pixel_horz_size: 10.    # um

  environment:
    temperature: 300        # K

  characteristics:
    qe:   1.                # -
    eta:  1.                # e/photon
    sv:   3.e-6             # V/e
    amp:  10.               # V/V
    a1:   100.              # V/V
    a2:   3000              # DN/V
    fwc:  2000              # e
    fwc_serial: 10000       # e
    vg:   1.62e-10          # cm^2
    svg:  1.62e-10          # cm^2
    t:    9.4722e-04        # s
    st:   9.4722e-04        # s

pipeline:
  photon_generation:
    - name: illumination
      func: pyxel.models.photon_generation.illumination
      enabled: true
      arguments:
          level: 0
  optics:
  charge_generation:
  charge_collection:
  charge_transfer:
  charge_measurement:
  readout_electronics:
"""

    filename = tmp_path / "no_running_mode.yaml"

    with filename.open(mode="w") as fh:
        fh.write(content)

    return filename


@pytest.fixture
def config_two_running_modes(tmp_path: Path) -> Path:
    """Create a configuration file with two valid running mode."""
    content = """
exposure:

  outputs:
    output_folder: "output"
    save_data_to_file:
      - detector.image.array:   ['fits']
      - detector.pixel.array: ['npy']
      
observation:

  parameters:
    - key: pipeline.photon_generation.illumination.arguments.level
      values: numpy.unique(numpy.logspace(0, 6, 10, dtype=int))

  outputs:
    output_folder:  'outputs'
    # each pipeline run
    save_data_to_file:
      - detector.image.array:   ['npy']
    # once at the end
    save_observation_data:


ccd_detector:

  geometry:

    row: 450               # pixel
    col: 450               # pixel
    total_thickness: 40.    # um
    pixel_vert_size: 10.    # um
    pixel_horz_size: 10.    # um

  environment:
    temperature: 300        # K

  characteristics:
    qe:   1.                # -
    eta:  1.                # e/photon
    sv:   3.e-6             # V/e
    amp:  10.               # V/V
    a1:   100.              # V/V
    a2:   3000              # DN/V
    fwc:  2000              # e
    fwc_serial: 10000       # e
    vg:   1.62e-10          # cm^2
    svg:  1.62e-10          # cm^2
    t:    9.4722e-04        # s
    st:   9.4722e-04        # s

pipeline:
  photon_generation:
    - name: illumination
      func: pyxel.models.photon_generation.illumination
      enabled: true
      arguments:
          level: 0
  optics:
  charge_generation:
  charge_collection:
  charge_transfer:
  charge_measurement:
  readout_electronics:
"""

    filename = tmp_path / "no_running_mode.yaml"

    with filename.open(mode="w") as fh:
        fh.write(content)

    return filename


@pytest.fixture
def config_no_detector(tmp_path: Path) -> Path:
    """Create a configuration file without detector."""
    content = """
exposure:

  outputs:
    output_folder: "output"
    save_data_to_file:
      - detector.image.array:   ['fits']
      - detector.pixel.array: ['npy']

pipeline:
  photon_generation:
    - name: illumination
      func: pyxel.models.photon_generation.illumination
      enabled: true
      arguments:
          level: 0
  optics:
  charge_generation:
  charge_collection:
  charge_transfer:
  charge_measurement:
  readout_electronics:
"""

    filename = tmp_path / "no_running_mode.yaml"

    with filename.open(mode="w") as fh:
        fh.write(content)

    return filename


@pytest.fixture
def config_two_detectors(tmp_path: Path) -> Path:
    """Create a configuration file with two detectors."""
    content = """
ccd_detector:

  geometry:

    row: 450               # pixel
    col: 450               # pixel
    total_thickness: 40.    # um
    pixel_vert_size: 10.    # um
    pixel_horz_size: 10.    # um

  environment:
    temperature: 300        # K

  characteristics:
    qe:   1.                # -
    eta:  1.                # e/photon
    sv:   3.e-6             # V/e
    amp:  10.               # V/V
    a1:   100.              # V/V
    a2:   3000              # DN/V
    fwc:  2000              # e
    fwc_serial: 10000       # e
    vg:   1.62e-10          # cm^2
    svg:  1.62e-10          # cm^2
    t:    9.4722e-04        # s
    st:   9.4722e-04        # s

cmos_detector:

  geometry:

    row: 100               # pixel
    col: 100               # pixel
    total_thickness: 40.    # um
    pixel_vert_size: 10.    # um
    pixel_horz_size: 10.    # um
    n_output: 1
    n_row_overhead: 0
    n_frame_overhead: 0
    reverse_scan_direction: False
    reference_pixel_border_width: 4

  environment:
    temperature: 300

  characteristics:
    qe: 0.5               # -
    eta: 1                # e/photon
    sv: 1.0e-6            # V/e
    amp: 0.8              # V/V
    a1: 100               # V/V
    a2: 50000             # DN/V
    #a2: 65536             # DN/V
    fwc: 100000            # e
    dsub: 0.5

exposure:

  outputs:
    output_folder: "output"
    save_data_to_file:
      - detector.image.array:   ['fits']
      - detector.pixel.array: ['npy']

pipeline:
  photon_generation:
    - name: illumination
      func: pyxel.models.photon_generation.illumination
      enabled: true
      arguments:
          level: 0
  optics:
  charge_generation:
  charge_collection:
  charge_transfer:
  charge_measurement:
  readout_electronics:
"""

    filename = tmp_path / "no_running_mode.yaml"

    with filename.open(mode="w") as fh:
        fh.write(content)

    return filename


def test_load_2_times():
    """Test function 'pyxel.load' called two times."""
    filename = "tests/data/dummy_simple.yaml"

    # Get full filename
    full_filename = Path(filename)  # type: Path
    assert full_filename.exists()

    # Load the configuration file for the first time
    with freeze_time("2021-06-15 14:11"):
        _ = pyxel.load(full_filename)

    # Load the configuration file for the second time
    with freeze_time("2021-06-15 14:11"):
        _ = pyxel.load(full_filename)


def test_load_no_running_mode(config_no_running_mode: Path):
    """test function 'pyxel.load' without a running mode."""
    filename = config_no_running_mode

    with pytest.raises(
        ValueError,
        match=r"Expecting only one running mode: 'exposure', 'observation', 'calibration'",
    ):
        _ = pyxel.load(filename)


def test_load_two_running_modes(config_two_running_modes: Path):
    """test function 'pyxel.load' without two running modes."""
    filename = config_two_running_modes

    with pytest.raises(
        ValueError,
        match=r"Expecting only one running mode: 'exposure', 'observation', 'calibration'",
    ):
        _ = pyxel.load(filename)


def test_load_no_detector(config_no_detector: Path):
    """test function 'pyxel.load' without detector."""
    filename = config_no_detector

    with pytest.raises(
        ValueError,
        match=r"Expecting only one detector: 'ccd_detector', 'cmos_detector', 'mkid_detector'",
    ):
        _ = pyxel.load(filename)


def test_load_two_detectors(config_two_detectors: Path):
    """test function 'pyxel.load' with two detectors."""
    filename = config_two_detectors

    with pytest.raises(
        ValueError,
        match=r"Expecting only one detector: 'ccd_detector', 'cmos_detector', 'mkid_detector'",
    ):
        _ = pyxel.load(filename)
