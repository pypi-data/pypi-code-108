"""Test cases for copying models."""

import copy
import numpy as np
import pytest
from ....util import (
    assert_cavities_equivalent,
    assert_gauss_commands_equivalent,
    assert_model_elements_equivalent,
    assert_detectors_equivalent,
)
from finesse.parameter import ParameterState


@pytest.fixture(scope="module")
def model_reference_expression():
    import finesse

    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s s1 L0.p1 ITM.p1
        m ITM R=1-&ETM.T T=&ETM.T
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=0.99 T=0.01

        xaxis(ETM.phi, lin, 0, 1, 100)
        """
    )
    return kat


def test_get_element(model_reference_expression):
    assert model_reference_expression.get_element("L0").name == "L0"
    assert model_reference_expression.get_element("ITM").name == "ITM"
    copy = model_reference_expression.deepcopy()
    assert copy.get_element("L0").name == "L0"
    assert copy.get_element("L0") is not model_reference_expression.get_element("L0")
    assert copy.get_element("ITM") is not model_reference_expression.get_element("ITM")


def test_deepcopy_ref_expr(model_reference_expression):
    model_reference_expression.deepcopy()


@pytest.fixture(scope="module")
def deep_copied_model(complicated_ifo_for_copying):
    """Deep copied complicated model.

    Tests that use this fixture rely on all of the checked parameters NOT BEING EMPTY.
    That means the model here should have components, cavities and detectors.
    """
    if (
        not complicated_ifo_for_copying.components
        or not complicated_ifo_for_copying.cavities
        or not complicated_ifo_for_copying.detectors
    ):
        raise ValueError(
            "deep_copied_model requires a model with components, cavities and detectors"
        )

    return complicated_ifo_for_copying, copy.deepcopy(complicated_ifo_for_copying)


def test_deep_copied_model_ids_dont_match(deep_copied_model):
    """Check that deep copied model IDs are different."""
    original, copied = deep_copied_model
    assert id(original) != id(copied)


def test_deep_copied_model_element_symbols(deep_copied_model):
    A, B = deep_copied_model
    for a, b in zip(A.elements.values(), B.elements.values()):
        for pa, pb in zip(a.parameters, b.parameters):
            if pa.state == ParameterState.Symbolic:
                # if symbolic make sure refs point to new refs
                for sa, sb in zip(pa.value.parameters(), pb.value.parameters()):
                    assert sa.owner is not sb.owner
            else:
                assert pa.value == pb.value


def test_deep_copied_model_have_same_properties(deep_copied_model):
    """Check that deep copied models have the same properties."""
    original, copied = deep_copied_model
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


def test_deep_copied_model_network_objects_dont_match(deep_copied_model):
    """Check that deep copied model networks are not the same object."""
    original, copied = deep_copied_model
    assert original.network != copied.network


def test_deep_copied_model_networks_have_same_properties(deep_copied_model):
    """Check that deep copied model networks have the same properties."""
    original, copied = deep_copied_model
    assert list(original.network) == list(copied.network)
    assert list(original.network.edges) == list(copied.network.edges)


def test_deep_copied_model_optical_network_objects_match(deep_copied_model):
    """Check that deep copied model optical networks are not the same object."""
    original, copied = deep_copied_model
    assert original.optical_network != copied.optical_network


def test_deep_copied_model_optical_networks_have_same_properties(deep_copied_model):
    """Check that deep copied model optical networks have the same properties."""
    original, copied = deep_copied_model
    assert list(original.optical_network) == list(copied.optical_network)
    assert list(original.optical_network.edges) == list(copied.optical_network.edges)


def test_deep_copied_model_cavities_objects_dont_match(deep_copied_model):
    """Check that deep copied model cavities are not the same object."""
    original, copied = deep_copied_model
    assert original.cavities != copied.cavities


def test_deep_copied_model_cavities_have_same_properties(deep_copied_model):
    """Check that deep copied model cavities have the same properties."""
    original, copied = deep_copied_model
    for original_cavity, copied_cavity in zip(original.cavities, copied.cavities):
        assert_cavities_equivalent(original_cavity, copied_cavity)


def test_deep_copied_model_gauss_commands_objects_dont_match(deep_copied_model):
    """Check that deep copied model gauss commands are not the same object."""
    original, copied = deep_copied_model
    assert original.gausses != copied.gausses


def test_deep_copied_model_gauss_commands_have_same_properties(deep_copied_model):
    """Check that deep copied model gauss commands have the same properties."""
    original, copied = deep_copied_model
    for original_gauss, copied_gauss in zip(original.gausses, copied.gausses):
        assert_gauss_commands_equivalent(
            original.gausses[original_gauss], copied.gausses[copied_gauss]
        )


def test_deep_copied_model_components_objects_dont_match(deep_copied_model):
    """Check that deep copied model components are not the same object."""
    original, copied = deep_copied_model
    assert original.components != copied.components


def test_deep_copied_model_components_have_same_properties(deep_copied_model):
    """Check that deep copied model components have the same properties."""
    original, copied = deep_copied_model
    for original_component, copied_component in zip(
        original.components, copied.components
    ):
        assert_model_elements_equivalent(original_component, copied_component)


def test_deep_copied_model_detectors_objects_dont_match(deep_copied_model):
    """Check that deep copied model detectors are not the same object."""
    original, copied = deep_copied_model
    assert original.detectors != copied.detectors


def test_deep_copied_model_detectors_have_same_properties(deep_copied_model):
    """Check that deep copied model detectors have the same properties."""
    original, copied = deep_copied_model
    for original_detector, copied_detector in zip(original.detectors, copied.detectors):
        assert_detectors_equivalent(original_detector, copied_detector)


def test_deep_copied_model_elements_objects_dont_match(deep_copied_model):
    """Check that deep copied model elements are not the same objects."""
    original, copied = deep_copied_model
    assert original.elements != copied.elements


def test_deep_copied_model_elements_have_same_properties(deep_copied_model):
    """Check that deep copied model elements have the same properties."""
    original, copied = deep_copied_model
    # Check element names are equal.
    for original_element, copied_element in zip(original.elements, copied.elements):
        # FIXME: check objects within the elements dict too.
        assert original_element == copied_element
