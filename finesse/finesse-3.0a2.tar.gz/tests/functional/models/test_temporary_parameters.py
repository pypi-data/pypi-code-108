import pytest
import finesse


@pytest.fixture
def model():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 R=0.99 T=0.01 Rc=-1934
    m m2 R=1 T=0 Rc=2245
    m m3 R=1 T=0 Rc=10000
    """
    )
    return model.deepcopy()


def test_simple(model):
    with model.temporary_parameters():
        model.m1.Rc = 123.4
        model.m2.phi = 3141
        model.l1.P = 13

    assert model.m1.Rc[0] != 123.4
    assert model.m1.Rc[1] != 123.4
    assert model.m2.phi != 3141
    assert model.l1.P != 13


def test_wildcard_include(model):
    # Only reset m2 parameters
    with model.temporary_parameters(include="m2.*"):
        model.m1.phi = 10
        model.m2.phi = 12
        model.m2.misaligned = True

    assert model.m1.phi == 10
    assert model.m2.phi != 12
    assert model.m2.misaligned is not True


def test_list_include(model):
    # Only reset m2.phi and m1.phi parameters
    with model.temporary_parameters(include=("m2.phi", "m1.phi")):
        model.m1.phi = 10
        model.m2.phi = 12
        model.m2.misaligned = True

    assert model.m1.phi != 10
    assert model.m2.phi != 12
    assert model.m2.misaligned is not True


def test_wildcard_exclude(model):
    # Reset everything apart from all phi parameters
    with model.temporary_parameters(exclude="*.phi"):
        model.m1.phi = 10
        model.m2.phi = 12
        model.m3.phi = 14
        model.m2.misaligned = True

    assert model.m1.phi == 10
    assert model.m2.phi == 12
    assert model.m3.phi == 14
    assert model.m2.misaligned is not True


def test_symbolic():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    l l2 P=&l1.P
    """
    )
    with model.temporary_parameters():
        model.l1.P = 10
        model.l2.P = 20
    assert model.l1.P.value == 1
    assert model.l2.P.value == model.l1.P


def test_symbolic_increment():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    l l2 P=&l1.P
    """
    )
    with model.temporary_parameters():
        model.l1.P = 10
        model.l2.P += 1
    assert model.l1.P.value == 1
    assert model.l2.P.value == model.l1.P
