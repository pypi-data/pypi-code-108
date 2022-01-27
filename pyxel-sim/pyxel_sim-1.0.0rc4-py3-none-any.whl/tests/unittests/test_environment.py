"""Unittests for class `Environment`."""
#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

from pyxel.detectors import Environment


@pytest.mark.parametrize(
    "list_in, list_out",
    [
        # (None, None, None, None, None, None),
        # (1, None, None, 1.0, None, None),
        # (None, 2, None, None, 2.0, None),
        # (None, None, 3, None, None, 3.0),
        ([1], [1.0]),
        ([4.0], [4.0]),
        ([7], [7.0]),
    ],
)
def test_init(list_in, list_out):
    """Test Environment.__init__ with valid entries."""

    # Create the object
    obj = Environment(
        temperature=list_in[0],
    )

    # Test getters
    assert obj.temperature == list_out[0]


# @pytest.mark.parametrize("temperature, total_inonising_dose, total_non_ionising_dose, exp_exception, exp_msg", [
#     ('foo', 2.0, 3.0, TypeError, "Unsupported type for 'temperature"),
#     (1.0 * u.K, 2.0, 3.0, TypeError, "Unsupported type for 'temperature"),
#     (1.0 * u.C, 2.0, 3.0, TypeError, "Unsupported type for 'temperature"),
#     (1.0 * u.m, 2.0, 3.0, TypeError, "Unsupported type for 'temperature"),
#
#     (1.0, 'foo', 3.0, TypeError, "Unsupported type for 'total_ionising_dose"),
#     (1.0, 2.0, 'foo', TypeError, "Unsupported type for 'total_non_ionising_dose"),
#
#     (0, 2.0, 3.0, ValueError, "'temperature' must be > 0"),
#     (0.0, 2.0, 3.0, ValueError, "'temperature' must be > 0"),
#     (-0.1, 2.0, 3.0, ValueError, "'temperature' must be > 0"),
#     (-1, 2.0, 3.0, ValueError, "'temperature' must be > 0"),
#
#     (1.0, -0.1, 3.0, ValueError, "'total_ionising_dose' must be >= 0"),
#     (1.0, -1, 3.0, ValueError, "'total_ionising_dose' must be >= 0"),
#
#     (1.0, 2.0, -0.1, ValueError, "'total_non_ionising_dose' must be >= 0"),
#     (1.0, 2.0, -1, ValueError, "'total_non_ionising_dose' must be >= 0"),
# ])
# def test_failed_init(temperature, total_inonising_dose, total_non_ionising_dose, exp_exception, exp_msg):
#     """Test Environment.__init__ with wrong inputs."""
#     with pytest.raises(exp_exception) as exc_info:
#         _ = Environment(temperature=temperature,
#                         total_ionising_dose=total_inonising_dose,
#                         total_non_ionising_dose=total_non_ionising_dose)
#     assert exc_info.match(exp_msg)
#
#
# @pytest.mark.parametrize("obj, other_obj", [
#     (Environment(), Environment()),
#     (Environment(1.0), Environment(1.0)),
#     (Environment(1.0, total_ionising_dose=2.0), Environment(temperature=1, total_ionising_dose=2)),
#     (Environment(1.0, 2.0, total_non_ionising_dose=3.0), Environment(1.0, 2.0, 3.0)),
#     (Environment(temperature=1.0, total_ionising_dose=2.0, total_non_ionising_dose=3.0), Environment(1, 2, 3)),
# ])
# def test_eq(obj, other_obj):
#     """Test Environment.__eq__."""
#     assert type(obj) is Environment
#
#     assert obj == other_obj
#
#
# @pytest.mark.parametrize("obj, other_obj", [
#     (Environment(), None),
#     (Environment(), Environment(1, 2, 3)),
#     (Environment(1, 2, 3), Environment(4, 2, 3)),
#     (Environment(1, 2, 3), Environment(1, 4, 3)),
#     (Environment(1, 2, 3), Environment(1, 2, 4)),
# ])
# def test_neq(obj, other_obj):
#     """Test Environment.__neq__."""
#     assert type(obj) is Environment
#
#     assert obj != other_obj
#
#
# @pytest.mark.parametrize("obj", [
#     Environment(),
#     Environment(temperature=1.0),
#     Environment(temperature=1.0, total_ionising_dose=2.0),
#     Environment(temperature=1.0, total_ionising_dose=2.0, total_non_ionising_dose=3.0),
# ])
# def test_copy(obj):
#     """Test Environment.copy."""
#     assert type(obj) is Environment
#     id_obj = id(obj)
#
#     new_obj = obj.copy()
#     assert id_obj == id(obj)
#     assert obj is not new_obj
#
#     assert obj == new_obj
#
#
# @pytest.mark.parametrize("obj, exp_state", [
#     (Environment(), {'temperature': None,
#                      'total_ionising_dose': None,
#                      'total_non_ionising_dose': None}),
#     (Environment(1, 2, 3), {'temperature': 1.0,
#                             'total_ionising_dose': 2.0,
#                             'total_non_ionising_dose': 3.0}),
#     (Environment(temperature=1), {'temperature': 1.0,
#                                   'total_ionising_dose': None,
#                                   'total_non_ionising_dose': None}),
#     (Environment(total_ionising_dose=2.0), {'temperature': None,
#                                             'total_ionising_dose': 2.0,
#                                             'total_non_ionising_dose': None}),
#     (Environment(total_non_ionising_dose=3.0), {'temperature': None,
#                                                 'total_ionising_dose': None,
#                                                 'total_non_ionising_dose': 3.0}),
# ])
# def test_getstate(obj, exp_state):
#     """Test Environment.__getstate__."""
#     assert type(obj) is Environment
#
#     state = obj.__getstate__()
#     assert state == exp_state
#
#
# @pytest.mark.parametrize("state, exp_obj", [
#     ({'temperature': None,
#       'total_ionising_dose': None,
#       'total_non_ionising_dose': None}, Environment()),
#     ({'temperature': 1.0,
#       'total_ionising_dose': 2.0,
#       'total_non_ionising_dose': 3.0}, Environment(1.0, 2.0, 3.0)),
#     ({'temperature': 1.0,
#       'total_ionising_dose': None,
#       'total_non_ionising_dose': None}, Environment(temperature=1.0)),
#     ({'temperature': None,
#       'total_ionising_dose': 2.0,
#       'total_non_ionising_dose': None}, Environment(total_ionising_dose=2.0)),
#     ({'temperature': None,
#       'total_ionising_dose': None,
#       'total_non_ionising_dose': 3.0}, Environment(total_non_ionising_dose=3.0)),
#
# ])
# def test_setstate(state, exp_obj):
#     """Test Environment.__setstate__."""
#     assert isinstance(state, dict)
#
#     new_obj = Environment()
#     new_obj.__setstate__(state)
#
#     assert new_obj is not exp_obj
#     assert new_obj == exp_obj
#
#
# @pytest.mark.parametrize("obj, exp_repr", [
#     (Environment(), "Environment(temperature=None, total_ionising_dose=None, total_non_ionising_dose=None)"),
#     (Environment(1.0, 2.0, 3.0), "Environment(temperature=1.0,
#     total_ionising_dose=2.0, total_non_ionising_dose=3.0)"),
#
# ])
# def test_repr(obj, exp_repr):
#     """Test Environment.__repr__."""
#     assert type(obj) is Environment
#
#     assert repr(obj) == exp_repr
