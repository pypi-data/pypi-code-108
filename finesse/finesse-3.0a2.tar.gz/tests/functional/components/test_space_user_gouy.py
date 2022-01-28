import pytest
import finesse
import numpy as np


@pytest.fixture
def simple_cavity_model():
    def getmodel(user_gouy=""):
        model = finesse.Model()
        model.parse(
            f"""
            l l1
            s s0 l1.p1 m1.p1
            m m1 Rc=-0.5
            s cav m1.p2 m2.p1 L=0.25 {user_gouy}
            m m2 Rc=0.5
            cav cavity m1.p2.o
            """
        )

        return model

    return getmodel


def test_getter_returns_default_gouy_without_user(simple_cavity_model):
    model = simple_cavity_model()

    assert model.spaces.s0.gouy_x == 0.0
    assert model.spaces.s0.gouy_y == 0.0
    assert model.spaces.cav.gouy_x == 0.0
    assert model.spaces.cav.gouy_y == 0.0


def test_getter_returns_user_gouy_with_user(simple_cavity_model):
    model = simple_cavity_model("user_gouy_x=1 user_gouy_y=2")

    assert model.spaces.s0.gouy_x == 0.0
    assert model.spaces.s0.gouy_y == 0.0
    assert model.spaces.cav.gouy_x == 1.0
    assert model.spaces.cav.gouy_y == 2.0


def test_user_gouy_is_none_without_user(simple_cavity_model):
    model = simple_cavity_model()

    assert model.spaces.s0.user_gouy_x.value is None
    assert model.spaces.s0.user_gouy_y.value is None
    assert model.spaces.cav.user_gouy_x.value is None
    assert model.spaces.cav.user_gouy_y.value is None


def test_user_gouy_is_none_with_user(simple_cavity_model):
    model = simple_cavity_model("user_gouy_x=1 user_gouy_y=2")

    assert model.spaces.s0.user_gouy_x.value is None
    assert model.spaces.s0.user_gouy_y.value is None
    assert model.spaces.cav.user_gouy_x.value == 1.0
    assert model.spaces.cav.user_gouy_y.value == 2.0


def test_gouy_is_being_set_during_run(simple_cavity_model):
    model = simple_cavity_model()
    model.run()

    assert np.isclose(model.spaces.cav.gouy_x, 60.0)
    assert np.isclose(model.spaces.cav.gouy_y, 60.0)


def test_user_gouy_is_being_set_during_run(simple_cavity_model):
    model = simple_cavity_model("user_gouy_x=1 user_gouy_y=2")
    model.run()

    assert np.isclose(model.spaces.cav.gouy_x, 1.0)
    assert np.isclose(model.spaces.cav.gouy_y, 2.0)
