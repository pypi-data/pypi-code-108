"""Model component network unit test fixtures."""

import pytest
from finesse import Model
from finesse.components import Laser, Beamsplitter, Mirror, Cavity
from finesse.detectors import PowerDetector


@pytest.fixture(scope="module")
def network_model_michelson():
    """Fixture with a Michelson model to test component network generation."""
    model = Model()

    model.add(
        [
            Laser("L0"),
            Beamsplitter("BS"),
            Mirror("IMX", Rc=-0.6),
            Mirror("IMY", Rc=-0.6),
            Mirror("EMX", Rc=0.6),
            Mirror("EMY", Rc=0.6),
        ]
    )
    model.connect(model.L0.p1, model.BS.p1, L=1)
    model.connect(model.BS.p2, model.IMY.p1, L=1)
    model.connect(model.IMY.p2, model.EMY.p1, L=1)
    model.connect(model.BS.p3, model.IMX.p1, L=1)
    model.connect(model.IMX.p2, model.EMX.p1, L=1)

    model.add(PowerDetector("refl", model.IMX.p1.o))
    model.add(Cavity("cav_x", model.IMX.p2.o, model.IMX.p2.i))
    model.add(Cavity("cav_y", model.IMY.p2.o, model.IMY.p2.i))

    return model, model.to_component_network()


@pytest.fixture(scope="module")
def network_model_sagnac():
    """Fixture with a Sagnac model to test component network generation."""
    model = Model()

    model.add(
        [
            Laser("L0"),
            Beamsplitter("BS"),
            Mirror("M1", Rc=-1.7),
            Mirror("M2"),
            Mirror("M3", Rc=1.7),
        ]
    )
    model.connect(model.L0.p1, model.BS.p1, L=1)
    model.connect(model.BS.p2, model.M1.p1, L=1)
    model.connect(model.M1.p2, model.M2.p1, L=1)
    model.connect(model.M2.p2, model.M3.p1, L=1)
    model.connect(model.M3.p2, model.BS.p3, L=1)

    model.add(PowerDetector("trns", model.BS.p4.o))

    return model, model.to_component_network()
