"""Test cases for shallow copying models."""

import copy
import numpy as np
import pytest


@pytest.fixture(scope="module")
def shallow_copied_model(complicated_ifo_for_copying):
    """Shallow copied complicated model.

    Tests that use this fixture rely on all of the checked parameters NOT BEING EMPTY.
    That means the model here should have components, cavities and detectors.
    """
    if (
        not complicated_ifo_for_copying.components
        or not complicated_ifo_for_copying.cavities
        or not complicated_ifo_for_copying.detectors
    ):
        raise ValueError(
            "shallow_copied_model requires a model with components, cavities and detectors"
        )

    return complicated_ifo_for_copying, copy.copy(complicated_ifo_for_copying)


def test_shallow_copied_model_ids_dont_match(shallow_copied_model):
    """Check that shallow copied model IDs are different."""
    original, copied = shallow_copied_model
    assert id(original) != id(copied)


def test_deep_copied_model_have_same_properties(shallow_copied_model):
    """Check that shallow copied models have the same properties."""
    original, copied = shallow_copied_model
    assert np.all(original.homs == copied.homs)
    assert original._settings.fsig == copied._settings.fsig
    assert original._settings.EPSILON0_C == copied._settings.EPSILON0_C
    assert original._settings.UNIT_VACUUM == copied._settings.UNIT_VACUUM
    assert original._settings.lambda0 == copied._settings.lambda0
    assert original._settings.f0 == copied._settings.f0
    assert original._settings.k0 == copied._settings.k0
    assert original._settings.is_modal == copied._settings.is_modal
    assert original._settings.num_HOMs == copied._settings.num_HOMs
    assert original._settings.max_n == copied._settings.max_n
    assert original._settings.max_m == copied._settings.max_m
    assert original._settings.x_scale == copied._settings.x_scale
    assert original.lambda0 == copied.lambda0


def test_shallow_copied_model_networks_match(shallow_copied_model):
    """Check that shallow copied model networks are the same."""
    original, copied = shallow_copied_model
    assert original.network == copied.network


def test_shallow_copied_model_optical_networks_match(shallow_copied_model):
    """Check that shallow copied model optical networks are the same."""
    original, copied = shallow_copied_model
    assert original.optical_network == copied.optical_network


def test_shallow_copied_model_cavities_match(shallow_copied_model):
    """Check that shallow copied model cavities are the same."""
    original, copied = shallow_copied_model
    assert original.cavities == copied.cavities


def test_shallow_copied_model_gauss_commands_match(shallow_copied_model):
    """Check that shallow copied model gauss commands are the same."""
    original, copied = shallow_copied_model
    assert original.gausses == copied.gausses


def test_shallow_copied_model_components_match(shallow_copied_model):
    """Check that shallow copied model components are the same."""
    original, copied = shallow_copied_model
    assert original.components == copied.components


def test_shallow_copied_model_detectors_match(shallow_copied_model):
    """Check that shallow copied model detectors are the same."""
    original, copied = shallow_copied_model
    assert original.detectors == copied.detectors


def test_shallow_copied_model_elements_match(shallow_copied_model):
    """Check that shallow copied model elements are the same."""
    original, copied = shallow_copied_model
    assert original.elements == copied.elements
