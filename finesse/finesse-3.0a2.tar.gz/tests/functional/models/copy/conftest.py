"""Model copy unit test fixtures."""

import pytest
from finesse import Model
from finesse.components import Laser, Beamsplitter, Mirror, Cavity, Gauss
from finesse.detectors import PowerDetector
from finesse.analysis.actions import Xaxis


# FIXME: this fixture should provide a very complicated model, ideally one with every type of
# component.
@pytest.fixture(scope="module")
def complicated_ifo_for_copying():
    """Fixture for constructing a complicated model for testing copy operations."""
    model = Model()

    model.add(
        [
            Laser("L0"),
            Beamsplitter("BS"),
            Mirror("IMX", R=0.99, L=0, Rc=-10),
            Mirror("IMY", R=0.99, L=0, Rc=-10),
            Mirror("EMX", T=10e-6, L=0, Rc=10),
            Mirror("EMY", T=10e-6, L=0, Rc=10),
        ]
    )
    model.connect(model.L0.p1, model.BS.p1)
    model.connect(model.BS.p2, model.IMY.p1, L=1)
    model.connect(model.IMY.p2, model.EMY.p1, L=1)
    model.connect(model.BS.p3, model.IMX.p1, L=1)
    model.connect(model.IMX.p2, model.EMX.p1, L=1)

    model.add(PowerDetector("refl", model.IMX.p1.o))
    model.add(PowerDetector("circ", model.EMX.p1.i))
    model.add(PowerDetector("trns", model.EMX.p2.o))

    model.add(Cavity("cav_y", model.IMY.p2.o, model.IMY.p2.i))
    model.add(Cavity("cav_x", model.IMX.p2.o, model.IMX.p2.i))
    model.add(Gauss("g_L0", model.L0.p1.o, q=(-0.2 + 2.5j)))

    # model.modes(modes="even", maxtem=4)

    model.run(Xaxis("EMX.phi", "lin", -180, 180, 400))

    return model
