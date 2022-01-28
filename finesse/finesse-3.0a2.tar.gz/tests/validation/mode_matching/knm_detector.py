""""""
import finesse
import pytest


@pytest.fixture
def model():
    IFO = finesse.Model()
    IFO.parse(
        """
    # Radii of curvature of arm cavity mirrors
    var XROC1 -1934
    var XROC2 2245
    var YROC1 -1934
    var YROC2 2245

    l L0 P=1
    link(L0, BS)
    bs BS

    s sy BS.p2 ITMY.p1 L=10
    m ITMY R=0.99 T=0.01 Rc=[&YROC1, &YROC1]
    s LY ITMY.p2 ETMY.p1 L=4k
    m ETMY R=0.99 T=0.01 Rc=[&YROC2, &YROC2]

    s sx BS.p3 ITMX.p1 L=10
    m ITMX R=0.99 T=0.01 Rc=[&XROC1, &XROC1]
    s LX ITMX.p2 ETMX.p1 L=4k
    m ETMX R=0.99 T=0.01 Rc=[&XROC2, &XROC2]

    cav cavXARM ITMX.p2
    cav cavYARM ITMY.p2

    modes(maxtem=2)

    knmd K22_itmx ITMX 22

    # This will detect mode mismatch from BS.p2.i -> BS.p4.o
    mmd mm_bs_x BS.p2.i BS.p4.o direction=x
    mmd mm_bs_y BS.p2.i BS.p4.o direction=y
    """
    )
    return IFO


def test_xaxis(model):
    model.parse("xaxis(XROC1, lin, -1900, -2000, 1)")
    model.run()


def test_noxaxis(model):
    model.run()
