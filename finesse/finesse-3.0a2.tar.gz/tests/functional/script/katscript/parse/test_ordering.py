"""Tests for making sure that order in katscript doesn't matter."""

from finesse.script import parse


def test_space_instruction_order_doesnt_matter():
    """Test that the order in which a space is defined in kat script does not matter."""
    # Shouldn't throw an error.
    parse(
        """
        l L0 P=1

        s s0 L0.p1 ITM.p1

        s CAV ITM.p2 ETM.p1 L=1  # Defined before the ITM and ETM components.

        m ITM R=0.99 T=0.01 Rc=-10
        m ETM R=0.99 T=0.01 Rc=10

        modes(even, 4)
        """
    )


def test_cavity_property_detector():
    """Cavity property detector should parse after cavity.

    The cavity property detector takes a cavity as a parameter, but cavities are `build_last`
    components so get built after everything that isn't. Cavity property detectors therefore have
    to be built after cavities.
    """
    # Shouldn't throw an error.
    parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1

        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2

        cav FP ITM.p2
        cp gx FP g x

        modes(maxtem=2)

        xaxis(ITM.phi, lin, 0, 180, 100)
        """
    )


def test_gouy_detector():
    """Gouy detector should parse in the second build step.

    The gouy detector has implicit dependencies like `cavity`, in that it requires for there to
    exist a path between its start and end nodes by the time it itself gets built. It therefore is
    set to `build_last` in the :class:`.KatSpec`. This test checks that the gouy detector still
    parses correctly.
    """
    # Shouldn't throw an error.
    parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1

        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2

        cav FP ITM.p2
        gouy gFP from_node=ITM.p2 to_node=ETM.p1

        modes(maxtem=2)
        xaxis(ITM.phi, lin, 0, 180, 100)
        """
    )
