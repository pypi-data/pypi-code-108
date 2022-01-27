"""Unit tests for class `Detector`."""

#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from copy import deepcopy

import pytest

from pyxel.detectors import (
    CCD,
    CMOS,
    CCDCharacteristics,
    CCDGeometry,
    Characteristics,
    CMOSCharacteristics,
    CMOSGeometry,
    Detector,
    Environment,
)

# from pyxel.data_structure.photon import Photon


@pytest.mark.parametrize(
    "cls, geometry, environment, characteristics",
    [
        # (Geometry(), Environment(), Characteristics(), Material()),
        # (Geometry(), Environment(), CCDCharacteristics(), Material()),
        # (Geometry(), Environment(), CMOSCharacteristics(), Material()),
        (CCD, CCDGeometry(row=1, col=1), Environment(), Characteristics()),
        (CCD, CCDGeometry(row=1, col=1), Environment(), CCDCharacteristics()),
        (CCD, CCDGeometry(row=1, col=1), Environment(), CMOSCharacteristics()),
        (CMOS, CMOSGeometry(row=1, col=1), Environment(), Characteristics()),
        (CMOS, CMOSGeometry(row=1, col=1), Environment(), CCDCharacteristics()),
        (CMOS, CMOSGeometry(row=1, col=1), Environment(), CMOSCharacteristics()),
    ],
)
def test_init(cls, geometry, environment, characteristics):
    """Test Detector.__init__ with valid entries."""

    # Create a `Detector`
    obj = cls(
        geometry=geometry,
        environment=environment,
        characteristics=characteristics,
    )

    # Test getters
    assert obj.geometry is geometry
    assert obj.environment is environment
    assert obj.characteristics is characteristics

    assert obj.photon is not None
    assert obj.charge is not None
    assert obj.pixel is not None
    assert obj.signal is not None
    assert obj.image is not None


#
# @pytest.mark.parametrize("obj, other_obj", [
#     (Detector(Geometry(), Material(), Environment(), Characteristics()),        # TODO
#      Detector(Geometry(), Material(), Environment(), Characteristics())),
#     (Detector(CCDGeometry(), Material(), Environment(), Characteristics()),
#      Detector(CCDGeometry(), Material(), Environment(), Characteristics())),
#     (Detector(CMOSGeometry(), Material(), Environment(), Characteristics()),
#      Detector(CMOSGeometry(), Material(), Environment(), Characteristics())),
#
#     (Detector(Geometry(), Material(), Environment(), CCDCharacteristics()),
#      Detector(Geometry(), Material(), Environment(), CCDCharacteristics())),        # TODO
#     (Detector(CCDGeometry(), Material(), Environment(), CCDCharacteristics()),
#      Detector(CCDGeometry(), Material(), Environment(), CCDCharacteristics())),
#     (Detector(CMOSGeometry(), Material(), Environment(), CCDCharacteristics()),
#      Detector(CMOSGeometry(), Material(), Environment(), CCDCharacteristics())),
#
#     (Detector(Geometry(), Material(), Environment(), CMOSCharacteristics()),               # TODO
#      Detector(Geometry(), Material(), Environment(), CMOSCharacteristics())),
#     (Detector(CCDGeometry(), Material(), Environment(), CMOSCharacteristics()),
#      Detector(CCDGeometry(), Material(), Environment(), CMOSCharacteristics())),
#     (Detector(CMOSGeometry(), Material(), Environment(), CMOSCharacteristics()),
#      Detector(CMOSGeometry(), Material(), Environment(), CMOSCharacteristics())),
# ])
# def test_eq(obj, other_obj):
#     """Test Detector.__eq__."""
#     assert isinstance(obj, Detector)


@pytest.mark.parametrize(
    "obj", [CCD(CCDGeometry(row=1, col=1), Environment(), CCDCharacteristics())]
)
def test_copy(obj):
    """Test Detector.copy."""
    assert isinstance(obj, Detector)
    id_obj = id(obj)
    new_obj = deepcopy(obj)
    assert id_obj == id(obj)
    assert new_obj is not obj
