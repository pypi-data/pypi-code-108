"""TraceDependency ordering unit tests."""

import pytest
from finesse import Model
import finesse.components as components


@pytest.fixture
def michelson_model():
    model = Model()
    model.parse(
        """
        l L0 P=1
        s s0 L0.p1 BS.p1 L=10

        bs BS

        s sY BS.p2 ITMY.p1 L=100

        m ITMY R=0.99 T=0.01 Rc=-5580
        s LY ITMY.p2 ETMY.p1 L=10k
        m ETMY R=0.99 T=0.01 Rc=5580

        s sX BS.p3 ITMX.p1 L=100

        m ITMX R=0.99 T=0.01 Rc=-5580
        s LX ITMX.p2 ETMX.p1 L=10k
        m ETMX R=0.99 T=0.01 Rc=5580
        """
    )
    return model


### Only cavities ###


def test_implicit_arm_cavity_ordering__1(michelson_model):
    """Test that cavXARM comes before cavYARM via alphabetic ordering."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    assert michelson_model.trace_order == [FPX, FPY]


def test_implicit_arm_cavity_ordering__2(michelson_model):
    """Test that adding cavYARM cavity before cavXARM makes no difference to order."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2)
    michelson_model.add(FPY)
    michelson_model.add(FPX)

    assert michelson_model.trace_order == [FPX, FPY]


def test_explicit_arm_cavity_ordering__x_priority(michelson_model):
    """Test that giving cavXARM priority arg puts it first."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=1)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    assert michelson_model.trace_order == [FPX, FPY]


def test_explicit_arm_cavity_ordering__y_priority(michelson_model):
    """Test that giving cavYARM priority arg puts it first."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=1)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    assert michelson_model.trace_order == [FPY, FPX]


def test_explicit_arm_cavity_ordering__x_priority_last(michelson_model):
    """Test that giving cavXARM priority arg puts it first."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=-1)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    assert michelson_model.trace_order == [FPY, FPX]


def test_explicit_arm_cavity_ordering__xy_priority(michelson_model):
    """Test that giving cavXARM and cavYARM priority args with X having higher
    priority puts it first."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=2)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=1)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    assert michelson_model.trace_order == [FPX, FPY]


def test_explicit_arm_cavity_ordering__xy_priority_last(michelson_model):
    """Test that giving cavXARM and cavYARM negative priority args with X having higher
    priority puts it first."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=-1)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=-2)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    assert michelson_model.trace_order == [FPX, FPY]


def test_explicit_arm_cavity_ordering__change_priority(michelson_model):
    """Test that changing cavYARM priority to highest, after adding the cavs
    to the model, results in it being first in the trace order."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=2)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=1)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    FPY.priority = 3

    assert michelson_model.trace_order == [FPY, FPX]


def test_explicit_arm_cavity_ordering__change_priority_first_to_last(michelson_model):
    """Test that changing cavYARM priority to highest, after adding the cavs
    to the model, results in it being first in the trace order."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=1)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=2)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    FPY.priority = -3

    assert michelson_model.trace_order == [FPX, FPY]


def test_explicit_arm_cavity_ordering__change_priority_last_to_first(michelson_model):
    """Test that changing cavYARM priority to highest, after adding the cavs
    to the model, results in it being first in the trace order."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=1)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=-5)
    michelson_model.add(FPX)
    michelson_model.add(FPY)

    FPY.priority = 2

    assert michelson_model.trace_order == [FPY, FPX]


def test_explicit_arm_cavity_ordering__xy_equal_priority(michelson_model):
    """Test that giving cavXARM and cavYARM equal priority args puts X first."""
    FPX = components.Cavity("cavXARM", michelson_model.ITMX.p2, priority=1)
    FPY = components.Cavity("cavYARM", michelson_model.ITMY.p2, priority=1)
    michelson_model.add(FPY)
    michelson_model.add(FPX)

    assert michelson_model.trace_order == [FPX, FPY]


### Only gausses ###


def test_implicit_gauss_ordering__1(michelson_model):
    """Test that gAS comes before gL0 via alphabetic ordering."""
    gL0 = components.Gauss("gL0", michelson_model.L0.p1.o, q=-10 + 0.1j)
    gAS = components.Gauss("gAS", michelson_model.BS.p4.o, q=0 + 0.15j)
    michelson_model.add(gAS)
    michelson_model.add(gL0)

    assert michelson_model.trace_order == [gAS, gL0]


def test_implicit_gauss_ordering__2(michelson_model):
    """Test that adding gL0 before gAS makes no difference to order."""
    gL0 = components.Gauss("gL0", michelson_model.L0.p1.o, q=-10 + 0.1j)
    gAS = components.Gauss("gAS", michelson_model.BS.p4.o, q=0 + 0.15j)
    michelson_model.add(gL0)
    michelson_model.add(gAS)

    assert michelson_model.trace_order == [gAS, gL0]


def test_explicit_gauss_ordering__L0_priority(michelson_model):
    """Test that giving gL0 priority arg puts it first."""
    gL0 = components.Gauss("gL0", michelson_model.L0.p1.o, q=-10 + 0.1j, priority=1)
    gAS = components.Gauss("gAS", michelson_model.BS.p4.o, q=0 + 0.15j)
    michelson_model.add(gAS)
    michelson_model.add(gL0)

    assert michelson_model.trace_order == [gL0, gAS]


def test_explicit_gauss_ordering__both_priority(michelson_model):
    """Test that giving gL0 and gAS priority args with gL0 having higher
    priority puts it first."""
    gL0 = components.Gauss("gL0", michelson_model.L0.p1.o, q=-10 + 0.1j, priority=1)
    gAS = components.Gauss("gAS", michelson_model.BS.p4.o, q=0 + 0.15j, priority=0.5)
    michelson_model.add(gAS)
    michelson_model.add(gL0)

    assert michelson_model.trace_order == [gL0, gAS]


def test_explicit_gauss_ordering__change_priority(michelson_model):
    """Test that changing gL0 priority to lowest, after adding the gausses
    to the model, results in it being last in the trace order."""
    gL0 = components.Gauss("gL0", michelson_model.L0.p1.o, q=-10 + 0.1j, priority=2)
    gAS = components.Gauss("gAS", michelson_model.BS.p4.o, q=0 + 0.15j, priority=1)
    michelson_model.add(gL0)
    michelson_model.add(gAS)

    gL0.priority = 0.5

    assert michelson_model.trace_order == [gAS, gL0]


def test_explicit_gauss_ordering__both_equal_priority(michelson_model):
    """Test that giving gL0 and gAS equal priority args puts gAS first."""
    gL0 = components.Gauss("gL0", michelson_model.L0.p1.o, q=-10 + 0.1j, priority=2.5)
    gAS = components.Gauss("gAS", michelson_model.BS.p4.o, q=0 + 0.15j, priority=2.5)
    michelson_model.add(gL0)
    michelson_model.add(gAS)

    assert michelson_model.trace_order == [gAS, gL0]


# TODO (sjr) Write some tests with multiple mixed dependencies
