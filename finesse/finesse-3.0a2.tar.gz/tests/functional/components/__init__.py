# pylint: disable=no-member

"""Component unit tests."""

import abc
import pytest
import numpy as np
from ... import Faker
from finesse.exceptions import ContextualValueError

FAKE = Faker()

# Invalid component names, i.e. ones containing non-ASCII characters.
NON_ASCII_INVALID = [
    FAKE.lexify("?" * 10, letters=[str(chr(x)) for x in range(1000, 2000)])
    for _ in range(10)
]


class TestComponent(metaclass=abc.ABCMeta):
    """Tests shared by all components.

    Not to be instantiated directly, rather subclassed.
    """

    def test_name__empty_invalid(self, component):
        """Test that empty strings as names are invalid."""
        with pytest.raises(ContextualValueError):
            component(name="")

    @pytest.mark.parametrize("invalid_name", NON_ASCII_INVALID)
    def test_name__non_ascii_invalid(self, component, invalid_name):
        """Test that non-ASCII characters are invalid."""
        with pytest.raises(ContextualValueError):
            component(name=invalid_name)


class TestSurface(TestComponent, metaclass=abc.ABCMeta):
    """Tests shared by all surfaces.

    Not to be instantiated directly, rather subclassed.
    """

    @pytest.mark.parametrize(
        "R,T,L",
        (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (0.5, 0.5, 0),
            (0.5, 0, 0.5),
            (0, 0.5, 0.5),
            (0.1, 0.1, 0.8),
            (0.9, 0.09, 0.01),
        ),
    )
    def test_rtl(self, component, R, T, L):
        """Test that a surface's R, T and L are correctly set by the constructor."""
        obj = component("cmp1", R=R, T=T, L=L)
        assert float(obj.R) == R
        assert float(obj.T) == T
        assert float(obj.L) == L

    @pytest.mark.skip(
        reason="May need to be moved to integration test on BaseAnaylsis - see #34"
    )
    def test_rtl__two_from_three(self, component):
        """Test that a surface's constructor correctly forces R+T+L = 1 from provided pairs."""

        def _do_two_from_three_test(specified_params, other_param_name):
            obj = component("cmp1", **specified_params)
            assert float(getattr(obj, other_param_name)) == rtl_data[other_param_name]

        rtl_data = dict(R=0.9, T=0.09, L=0.01)
        keys = list(rtl_data)

        data1 = dict(rtl_data)
        del data1[keys[0]]
        _do_two_from_three_test(data1, keys[0])

        data1 = dict(rtl_data)
        del data1[keys[1]]
        _do_two_from_three_test(data1, keys[1])

        data1 = dict(rtl_data)
        del data1[keys[2]]
        _do_two_from_three_test(data1, keys[2])

    @pytest.mark.skip(
        reason="May need to be moved to integration test on BaseAnaylsis - see #34"
    )
    def test_rtl__negative_invalid(self, component):
        """Test that a surface's R, T and L cannot be negative."""
        with pytest.raises(ValueError):
            component("cmp1", R=-1, T=0.5, L=0.5)
        with pytest.raises(ValueError):
            component("cmp1", R=0.5, T=-0.5, L=1)
        with pytest.raises(ValueError):
            component("cmp1", R=0.5, T=0.7, L=-0.2)
        with pytest.raises(ValueError):
            component("cmp1", R=-1, T=-1, L=-1)

    @pytest.mark.skip(
        reason="May need to be moved to integration test on BaseAnaylsis - see #34"
    )
    def test_rc__zero_invalid(self, component):
        """Test that a surface's radius of curvature cannot be 0."""
        with pytest.raises(ValueError):
            component(name="cmp1", R=0.5, T=0.5, Rc=0)

    def test_rc_sets_rcx_and_rcy__single(self, component):
        """Test that setting a surface's Rc to a single value sets Rcx and Rcy to that
        value."""
        obj = component(name="cmp1")
        obj.Rc = 3.141
        assert np.all(obj.Rc == 3.141)
        assert float(obj.Rcx) == 3.141
        assert float(obj.Rcy) == 3.141

    def test_rc_sets_rcx_and_rcy__separate(self, component):
        """Test that setting a surface's Rc to a two-valued sequence sets Rcx and Rcy to
        those respective values."""
        obj = component(name="cmp1")
        obj.Rc = (3.141, 6.282)
        part_a, part_b = obj.Rc
        assert (float(part_a), float(part_b)) == (3.141, 6.282)
        assert float(obj.Rcx) == 3.141
        assert float(obj.Rcy) == 6.282
