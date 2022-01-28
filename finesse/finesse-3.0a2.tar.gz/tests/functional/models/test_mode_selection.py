"""Test cases for selecting modes to include in a model."""

import pytest
import numpy as np

HGs_order_2 = [[0, 0], [0, 1], [2, 0], [1, 0], [0, 2], [1, 1]]
HGs_order_1 = [[0, 0], [0, 1], [1, 0]]
HGs_order_4_even = [[0, 0], [2, 0], [0, 2], [4, 0], [2, 2], [0, 4]]
HGs_order_3_odd = [[0, 0], [1, 0], [0, 1], [1, 1], [3, 0], [0, 3]]
HGs_order_5_x = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]
HGs_order_4_y = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]


def test_maxtem_off(model):
    """Test HOMs when maxtem set to off."""
    model.switch_off_homs()
    assert np.all(model.homs == [[0, 0]])


def test_maxtem_zero(model):
    """Test HOMs when maxtem set to 0."""
    model.modes(maxtem=0)
    assert np.all(model.homs == [[0, 0]])


def test_maxtem_on(model):
    """Test HOMs when maxtem set to 2."""
    model.modes(maxtem=2)
    assert HGs_order_2 in model.homs


def test_maxtem_on_increased(model):
    """Test HOMs when maxtem set higher."""
    model.modes(maxtem=1)
    assert HGs_order_1 in model.homs

    model.modes(maxtem=2)
    assert HGs_order_2 in model.homs


def test_maxtem_on_decreased(model):
    """Test HOMs when maxtem set lower."""
    model.modes(maxtem=2)
    assert HGs_order_2 in model.homs

    model.modes(maxtem=1)
    assert HGs_order_1 in model.homs


def test_maxtem_on_to_off(model):
    """Test HOMs when maxtem set to 1 then off."""
    model.modes(maxtem=1)
    assert HGs_order_1 in model.homs

    model.modes("off")
    assert np.all(model.homs == [[0, 0]])


def test_even_modes_specify_maxtem(model):
    """Test HOMs when modes set to even."""
    model.modes("even", 4)

    assert HGs_order_4_even in model.homs


def test_odd_modes_specify_maxtem(model):
    """Test HOMs when modes set to odd."""
    model.modes("odd", 3)

    assert HGs_order_3_odd in model.homs


def test_tangential_modes_specify_maxtem(model):
    """Test HOMs when modes set to 5 for x-direction."""
    model.modes("x", 5)

    assert HGs_order_5_x in model.homs


def test_sagittal_modes_specify_maxtem(model):
    """Test HOMs when modes set to 4 for y-direction."""
    model.modes("y", 4)

    assert HGs_order_4_y in model.homs


def test_insert_single_mode(model):
    """Test HOMs when maxtem set to 3 and modes set to x-direction, with extra mode
    included."""
    model.modes(maxtem=3)
    model.modes("x", 3)
    model.include_modes("11")

    assert [[0, 0], [1, 0], [1, 1], [2, 0], [3, 0]] in model.homs


def test_insert_multiple_modes(model):
    """Test HOMs when maxtem set to even 4 modes, with extra mode included."""
    model.modes("even", 4)
    model.include_modes(["11", "32", "50"])

    assert [
        [0, 0],
        [0, 2],
        [0, 4],
        [1, 1],
        [2, 0],
        [2, 2],
        [3, 2],
        [4, 0],
        [5, 0],
    ] in model.homs


def test_negative_maxtem_is_invalid(model):
    """Test that maxtem cannot be negative."""
    with pytest.raises(ValueError):
        model.modes(maxtem=-2)
    with pytest.raises(ValueError):
        model.modes(maxtem=-314)

    assert np.all(model.homs == [[0, 0]])


def test_non_integer_maxtem_is_invalid(model):
    """Test that maxtem cannot be floats."""
    with pytest.raises(ValueError):
        model.modes(maxtem=3.4)
    with pytest.raises(ValueError):
        model.modes(maxtem=-3.4)

    assert np.all(model.homs == [[0, 0]])


def test_unique_mode_indices(model):
    """Test HOMs when manually selected modes."""

    with pytest.raises(ValueError):
        model.modes(["00", "11", "22", "11", "00"])

    assert np.all(model.homs == [[0, 0]])


@pytest.mark.xfail(reason="See NOTE in Model.modes")
def test_warns_when_enabling(caplog):
    """Test that a warning is emitted when maxtem = 0

    Test that a warning is emitted when
    the model is automatically swicthed
    to modal, but no higher order modes
    are set.

    Also checks that the message is only
    displayed once.
    """
    import finesse
    import logging

    ifo = finesse.Model()
    ifo.parse(
        """

    l LaserIn P=1

    s s0 LaserIn.p1 ITM.p1 L=1

    m ITM R=0.99 T=0.01 Rc=-1
    s sCAV ITM.p2 ETM.p1 L=1.5
    m ETM R=0.99 T=0.01 Rc=1
    """
    )

    assert not ifo.is_modal
    with caplog.at_level(logging.WARNING):
        ifo.parse(
            """
        cavity fab1 ITM.p2 via=ETM.p1.i
        """
        )
        assert "enabled with only HG00" in caplog.text

    assert ifo.is_modal

    # Check that this is only displayed once
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        ifo.parse(
            """
        s s02 ETM.p2 ITM2.p1 L=1
        m ITM2 R=0.99 T=0.01 Rc=-1
        s sCAV2 ITM2.p2 ETM2.p1 L=1.5
        m ETM2 R=0.99 T=0.01 Rc=1
        cavity fab2 ITM2.p2 via=ETM2.p1.i
        """
        )
        assert "enabled with only HG00" not in caplog.text
