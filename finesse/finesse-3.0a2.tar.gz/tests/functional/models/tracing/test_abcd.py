"""ABCD matrix result tests."""

import pytest
import numpy as np
from finesse.components import Beamsplitter, Lens, Mirror, Nothing
from finesse.exceptions import TotalReflectionError


def abcd_space(L, nr):
    """ABCD matrix for a space."""
    return np.array([[1.0, L / nr], [0.0, 1.0]])


def abcd_lens(f):
    """ABCD matrix for a lens."""
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def abcd_mirror_t(nr1, nr2, rc):
    """ABCD matrix for mirror transmission."""
    return np.array([[1.0, 0.0], [(nr2 - nr1) / rc, 1.0]])


def abcd_mirror_r(nr1, rc):
    """ABCD matrix for mirror reflection."""
    return np.array([[1.0, 0.0], [-2 * nr1 / rc, 1.0]])


def abcd_beamsplitter_tt(nr1, nr2, alpha1, alpha2, rc):
    """ABCD matrix for beam splitter tangential transmission."""
    dn = (nr2 * np.cos(alpha2) - nr1 * np.cos(alpha1)) / (
        np.cos(alpha1) * np.cos(alpha2)
    )
    return np.array(
        [
            [np.cos(alpha2) / np.cos(alpha1), 0.0],
            [dn / rc, np.cos(alpha1) / np.cos(alpha2)],
        ]
    )


def abcd_beamsplitter_ts(nr1, nr2, alpha1, alpha2, rc):
    """ABCD matrix for beam splitter transmission."""
    dn = (nr2 * np.cos(alpha2) - nr1 * np.cos(alpha1)) / (
        np.cos(alpha1) * np.cos(alpha2)
    )
    return np.array([[1.0, 0.0], [dn / rc, 1.0]])


def abcd_beamsplitter_rt(nr1, alpha1, rc):
    """ABCD matrix for beam splitter tangential reflection."""
    return np.array([[1.0, 0.0], [-2 * nr1 / (rc * np.cos(alpha1)), 1.0]])


def abcd_beamsplitter_rs(nr1, alpha1, rc):
    """ABCD matrix for beam splitter reflection."""
    return np.array([[1.0, 0.0], [-2 * nr1 * np.cos(alpha1) / rc, 1.0]])


def test_space_abcd_refractive_index_unity_transmit(model):
    """Test space ABCD matrix for refractive index = 1."""
    # length = 1 m, nr = 1.0
    L1 = 1.0
    nr = 1.0

    model.add([Nothing("NULL1"), Nothing("NULL2")])
    model.connect(model.NULL1.p2, model.NULL2.p1, name="S", L=L1, nr=nr)

    result = model.elements["S"].ABCD(model.NULL1.p2.o, model.NULL2.p1.i)
    target = abcd_space(L1, nr)
    assert result.tolist() == target.tolist()

    # Check that reversing propagation direction yields same result.
    result_transmit_reversed = model.elements["S"].ABCD(
        model.NULL2.p1.o, model.NULL1.p2.i
    )
    assert result_transmit_reversed.tolist() == target.tolist()

    # length = 34.5544 m, nr = 1.0
    L2 = 34.5544
    model.elements["S"].L = L2
    result_L2 = model.elements["S"].ABCD(model.NULL1.p2.o, model.NULL2.p1.i)
    target_L2 = abcd_space(L2, nr)
    assert result_L2.tolist() == target_L2.tolist()


def test_space_abcd_refractive_index_non_unity_transmit(model):
    """Test space ABCD matrix for refractive index != 1."""
    # length = 2 m, nr = 1.44
    L = 2.0
    nr = 1.44

    model.add([Nothing("NULL1"), Nothing("NULL2")])
    model.connect(model.NULL1.p2, model.NULL2.p1, name="S", L=L, nr=nr)

    result = model.elements["S"].ABCD(model.NULL1.p2.o, model.NULL2.p1.i)
    target = abcd_space(L, nr)

    assert result.tolist() == target.tolist()

    # Check that reversing propagation direction yields same result.
    result_transmit_reversed = model.elements["S"].ABCD(
        model.NULL2.p1.o, model.NULL1.p2.i
    )
    assert result_transmit_reversed.tolist() == target.tolist()


def test_space_abcd_reflect(model):
    """Test space ABCD matrix reflection."""
    model.add([Nothing("NULL1"), Nothing("NULL2")])
    model.connect(model.NULL1.p2, model.NULL2.p1, name="S", L=1.0, nr=1.0)

    with pytest.raises(ValueError):
        model.elements["S"].ABCD(model.NULL1.p2.o, model.NULL1.p2.i)


def test_lens_abcd_transmit():
    """Test lens ABCD matrix on transmission."""
    # focal length = 11 m
    f1 = 11.0
    lens = Lens("lens", f1)
    result = lens.ABCD(lens.p1.i, lens.p2.o)
    target = abcd_lens(f1)
    assert result.tolist() == target.tolist()

    # Check that reversing propagation direction yields same result.
    result_transmit_reversed = lens.ABCD(lens.p2.i, lens.p1.o)
    assert result_transmit_reversed.tolist() == target.tolist()

    # focal length = 34.5km
    f2 = 34.5e3
    lens.f = f2
    result_f2 = lens.ABCD(lens.p1.i, lens.p2.o)
    target_f2 = abcd_lens(f2)
    assert result_f2.tolist() == target_f2.tolist()


def test_lens_abcd_reflect():
    """Test lens ABCD matrix on reflection."""
    lens = Lens("lens", 1.0)
    with pytest.raises(ValueError):
        lens.ABCD(lens.p1.i, lens.p1.o)


def test_mirror_abcd_transmission_no_spaces():
    """Test mirror ABCD matrix on transmission with no attached spaces."""
    # radius of curvature = 2.5m, nr1 = nr2 = 1.0
    RoC = 2.5
    mirror = Mirror("M", Rc=RoC)
    result = mirror.ABCD(mirror.p1.i, mirror.p2.o)
    target = abcd_mirror_t(1.0, 1.0, RoC)
    assert result.tolist() == target.tolist()

    # Check reversed propagation.
    result_transmit_reversed = mirror.ABCD(mirror.p2.i, mirror.p1.o)
    target_transmit_reversed = abcd_mirror_t(1.0, 1.0, -RoC)
    assert result_transmit_reversed.tolist() == target_transmit_reversed.tolist()

    # radius of curvature = -12.6m, nr1 = nr2 = 1.0
    RoC = -12.6
    mirror.Rc = RoC
    result_neg_roc = mirror.ABCD(mirror.p1.i, mirror.p2.o)
    target_neg_roc = abcd_mirror_t(1.0, 1.0, RoC)
    assert result_neg_roc.tolist() == target_neg_roc.tolist()


def test_mirror_abcd_reflection_no_spaces():
    """Test mirror ABCD matrix on reflection with no attached spaces."""
    # radius of curvature = 7.7m, nr1 = nr2 = 1.0
    RoC = 7.7
    mirror = Mirror("M", Rc=RoC)
    result = mirror.ABCD(mirror.p1.i, mirror.p1.o)
    target = abcd_mirror_r(1.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_refl_reversed = mirror.ABCD(mirror.p2.i, mirror.p2.o)
    target_refl_reversed = abcd_mirror_r(1.0, -RoC)
    assert result_refl_reversed.tolist() == target_refl_reversed.tolist()

    # radius of curvature = -5.5m, nr1 = nr2 = 1.0
    RoC = -5.5
    mirror.Rc = RoC
    result_neg_roc = mirror.ABCD(mirror.p1.i, mirror.p1.o)
    target_neg_roc = abcd_mirror_r(1.0, RoC)
    assert result_neg_roc.tolist() == target_neg_roc.tolist()


def test_mirror_abcd_transmission_space_nr_unity_at_port1(model):
    """Test mirror ABCD matrix on transmission with attached space (nr = 1) at first port."""
    # radius of curvature = 3.4m, nr1 = nr2 = 1.0
    RoC = 3.4
    model.chain(Nothing("NULL"), 1, Mirror("M", Rc=RoC))
    result = model.M.ABCD(model.M.p1.i, model.M.p2.o)
    target = abcd_mirror_t(1.0, 1.0, RoC)
    assert result.tolist() == target.tolist()


def test_mirror_abcd_transmission_space_nr_nonunity_at_port1(model):
    """Test mirror ABCD matrix on transmission with attached space (nr != 1) at first port."""
    # radius of curvature = -37.99m, nr1 = 1.08, nr2 = 1.0
    RoC = -37.99
    nr1 = 1.08
    model.chain(Nothing("NULL"), {"L": 1, "nr": nr1}, Mirror("M", Rc=RoC))
    result = model.M.ABCD(model.M.p1.i, model.M.p2.o)
    target = abcd_mirror_t(1.08, 1.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = model.M.ABCD(model.M.p2.i, model.M.p1.o)
    target_trns_reversed = abcd_mirror_t(1.0, nr1, -RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_mirror_abcd_reflection_space_nr_unity_at_port1(model):
    """Test mirror ABCD matrix on reflection with attached space (nr = 1) at first port."""
    # radius of curvature = 4.2m, nr1 = nr2 = 1.0
    RoC = 4.2
    model.chain(Nothing("NULL"), 1, Mirror("M", Rc=RoC))
    result = model.M.ABCD(model.M.p1.i, model.M.p1.o)
    target = abcd_mirror_r(1.0, RoC)
    assert result.tolist() == target.tolist()


def test_mirror_abcd_reflection_space_nr_nonunity_at_port1(model):
    """Test mirror ABCD matrix on reflection with attached space (nr != 1) at first port."""
    # radius of curvature = -14.7m, nr1 = 1.3, nr2 = 1.0
    RoC = -14.7
    nr1 = 1.3
    model.chain(Nothing("NULL"), {"L": 1, "nr": nr1}, Mirror("M", Rc=RoC))
    result = model.M.ABCD(model.M.p1.i, model.M.p1.o)
    target = abcd_mirror_r(nr1, RoC)
    assert result.tolist() == target.tolist()

    # Check reversed propagation.
    result_refl_reversed = model.M.ABCD(model.M.p2.i, model.M.p2.o)
    target_refl_reversed = abcd_mirror_r(1.0, -RoC)
    assert result_refl_reversed.tolist() == target_refl_reversed.tolist()


def test_mirror_abcd_transmission_spaces_nr_nonunity(model):
    """Test mirror ABCD matrix on transmission - attached spaces at both ports with (nr!=1)."""
    # radius of curvature = 17.67m, nr1 = 1.04, nr2 = 1.45
    RoC = 17.67
    nr1 = 1.04
    nr2 = 1.45
    model.chain(
        Nothing("NULL1"),
        {"L": 1, "nr": nr1},
        Mirror("M", Rc=RoC),
        {"L": 1, "nr": nr2},
        Nothing("NULL2"),
    )
    result = model.M.ABCD(model.M.p1.i, model.M.p2.o)
    target = abcd_mirror_t(nr1, nr2, RoC)
    assert result.tolist() == target.tolist()

    # Check reversed propagation.
    result_trns_reversed = model.M.ABCD(model.M.p2.i, model.M.p1.o)
    target_trns_reversed = abcd_mirror_t(nr2, nr1, -RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_mirror_abcd_reflection_spaces_nr_nonunity(model):
    """Test mirror ABCD matrix on reflection - attached spaces at both ports with (nr!=1)."""
    # radius of curvature = -0.51m, nr1 = 1.11, nr2 = 1.55
    RoC = -0.51
    nr1 = 1.11
    nr2 = 1.55
    model.chain(
        Nothing("NULL1"),
        {"L": 1, "nr": nr1},
        Mirror("M", Rc=RoC),
        {"L": 1, "nr": nr2},
        Nothing("NULL2"),
    )
    result = model.M.ABCD(model.M.p1.i, model.M.p1.o)
    target = abcd_mirror_r(nr1, RoC)
    assert result.tolist() == target.tolist()

    # Check reversed propagation.
    result_refl_reversed = model.M.ABCD(model.M.p2.i, model.M.p2.o)
    target_refl_reversed = abcd_mirror_r(nr2, -RoC)
    assert result_refl_reversed.tolist() == target_refl_reversed.tolist()


def test_bs_abcd_no_coupling():
    """Test that beam splitter ABCD method raises an exception when calling with nodes that have \
    no coupling."""
    bs = Beamsplitter("BS")

    with pytest.raises(ValueError):
        bs.ABCD(bs.p1.i, bs.p4.o)
    with pytest.raises(ValueError):
        bs.ABCD(bs.p2.i, bs.p3.o)
    with pytest.raises(ValueError):
        bs.ABCD(bs.p3.i, bs.p2.o)
    with pytest.raises(ValueError):
        bs.ABCD(bs.p4.i, bs.p1.o)


def test_flat_bs_abcd_transmission():
    """Test flat beam splitter ABCD matrix on transmission."""
    # radius of curvature = inf, nr1 = nr2 = 1.0
    bs = Beamsplitter("BS")
    result_t = bs.ABCD(bs.p1.i, bs.p3.o)
    target_t = abcd_beamsplitter_tt(1.0, 1.0, 0.0, 0.0, np.inf)
    assert result_t.tolist() == target_t.tolist()

    result_s = bs.ABCD(bs.p1.i, bs.p3.o)
    target_s = abcd_beamsplitter_ts(1.0, 1.0, 0.0, 0.0, np.inf)
    assert result_s.tolist() == target_s.tolist()


def test_flat_bs_abcd_reflection():
    """Test flat beam splitter ABCD matrix on transmission."""
    # radius of curvature = inf, nr1 = nr2 = 1.0
    bs = Beamsplitter("BS")
    result_t = bs.ABCD(bs.p1.i, bs.p2.o)
    target_t = abcd_beamsplitter_rt(1.0, 0.0, np.inf)
    assert result_t.tolist() == target_t.tolist()

    result_s = bs.ABCD(bs.p1.i, bs.p3.o)
    target_s = abcd_beamsplitter_rs(1.0, 0.0, np.inf)
    assert result_s.tolist() == target_s.tolist()


def test_bs_abcd_transmission_tangential_no_spaces():
    """Test beam splitter ABCD matrix on transmission for the tangential plane with no attached \
    spaces."""
    # radius of curvature = 2.5m, nr1 = nr2 = 1.0
    RoC = 2.5
    bs = Beamsplitter("BS", Rc=RoC)
    result = bs.ABCD(bs.p1.i, bs.p3.o)
    target = abcd_beamsplitter_tt(1.0, 1.0, 0.0, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = bs.ABCD(bs.p3.i, bs.p1.o)
    target_trns_reversed = abcd_beamsplitter_tt(1.0, 1.0, 0.0, 0.0, -RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_bs_abcd_transmission_sagittal_no_spaces():
    """Test beam splitter ABCD matrix on transmission for the sagittal plane with no attached \
    spaces."""
    # radius of curvature = 13.8m, nr1 = nr2 = 1.0
    RoC = 13.8
    bs = Beamsplitter("BS", Rc=RoC)
    result = bs.ABCD(bs.p1.i, bs.p3.o, direction="y")
    target = abcd_beamsplitter_ts(1.0, 1.0, 0.0, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = bs.ABCD(bs.p3.i, bs.p1.o, direction="y")
    target_trns_reversed = abcd_beamsplitter_ts(1.0, 1.0, 0.0, 0.0, -RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_bs_abcd_reflection_tangential_no_spaces():
    """Test beam splitter ABCD matrix on reflection for the tangential plane with no attached \
    spaces."""
    # radius of curvature = -18.9m, nr1 = nr2 = 1.0
    RoC = -18.9
    bs = Beamsplitter("BS", Rc=RoC)
    result = bs.ABCD(bs.p1.i, bs.p2.o)
    target = abcd_beamsplitter_rt(1.0, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_refl_reversed = bs.ABCD(bs.p2.i, bs.p1.o)
    target_refl_reversed = abcd_beamsplitter_rt(1.0, 0.0, RoC)
    assert result_refl_reversed.tolist() == target_refl_reversed.tolist()


def test_bs_abcd_reflection_sagittal_no_spaces():
    """Test beam splitter ABCD matrix on reflection for the sagittal plane with no attached \
    spaces."""
    # radius of curvature = 1.6m, nr1 = nr2 = 1.0
    RoC = 1.6
    bs = Beamsplitter("BS", Rc=RoC)
    result = bs.ABCD(bs.p1.i, bs.p2.o, direction="y")
    target = abcd_beamsplitter_rs(1.0, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_refl_reversed = bs.ABCD(bs.p2.i, bs.p1.o, direction="y")
    target_refl_reversed = abcd_beamsplitter_rs(1.0, 0.0, RoC)
    assert result_refl_reversed.tolist() == target_refl_reversed.tolist()


def test_bs_abcd_transmission_tangential_spaces(model):
    """Test beam splitter ABCD matrix on transmission for the tangential plane with attached \
    spaces."""
    # radius of curvature = 19.94m, nr1 = 1.04, nr2 = 1.45
    RoC = 19.94
    nr1 = 1.04
    nr2 = 1.45
    model.chain(Nothing("NULL1"), {"L": 1, "nr": nr1}, Beamsplitter("BS", Rc=RoC))
    model.add(Nothing("NULL2"))
    model.connect(model.BS.p3, model.NULL2.p1, L=1, nr=nr2)
    result = model.BS.ABCD(model.BS.p1.i, model.BS.p3.o)
    target = abcd_beamsplitter_tt(nr1, nr2, 0.0, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = model.BS.ABCD(model.BS.p3.i, model.BS.p1.o)
    target_trns_reversed = abcd_beamsplitter_tt(nr1, nr2, 0.0, 0.0, -RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_bs_abcd_transmission_sagittal_spaces(model):
    """Test beam splitter ABCD matrix on transmission for the sagittal plane with attached \
    spaces."""
    # radius of curvature = -9m, nr1 = 1.33, nr2 = 1.044
    RoC = -9.0
    nr1 = 1.33
    nr2 = 1.044
    model.chain(Nothing("NULL1"), {"L": 1, "nr": nr1}, Beamsplitter("BS", Rc=RoC))
    model.add(Nothing("NULL2"))
    model.connect(model.BS.p3, model.NULL2.p1, L=1, nr=nr2)
    result = model.BS.ABCD(model.BS.p1.i, model.BS.p3.o, direction="y")
    target = abcd_beamsplitter_ts(nr1, nr2, 0.0, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = model.BS.ABCD(model.BS.p3.i, model.BS.p1.o, direction="y")
    target_trns_reversed = abcd_beamsplitter_tt(nr1, nr2, 0.0, 0.0, -RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_bs_abcd_reflection_tangential_spaces(model):
    """Test beam splitter ABCD matrix on reflection for the tangential plane with attached \
    spaces."""
    # radius of curvature = 10.66m, nr1 = 1.07, nr2 = 1.70
    RoC = 10.66
    nr1 = 1.07
    nr2 = 1.70
    model.chain(Nothing("NULL1"), {"L": 1, "nr": nr1}, Beamsplitter("BS", Rc=RoC))
    model.add(Nothing("NULL2"))
    model.connect(model.BS.p2, model.NULL2.p1, L=1, nr=nr2)
    result = model.BS.ABCD(model.BS.p1.i, model.BS.p2.o)
    target = abcd_beamsplitter_rt(nr1, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = model.BS.ABCD(model.BS.p2.i, model.BS.p1.o)
    target_trns_reversed = abcd_beamsplitter_rt(nr2, 0.0, RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_bs_abcd_reflection_sagittal_spaces(model):
    """Test beam splitter ABCD matrix on reflection for the sagittal plane
    with attached spaces."""
    # radius of curvature = 10.66m, nr1 = 1.07, nr2 = 1.70
    RoC = 10.66
    nr1 = 1.07
    nr2 = 1.70
    model.chain(Nothing("NULL1"), {"L": 1, "nr": nr1}, Beamsplitter("BS", Rc=RoC))
    model.add(Nothing("NULL2"))
    model.connect(model.BS.p2, model.NULL2.p1, L=1, nr=nr2)
    result = model.BS.ABCD(model.BS.p1.i, model.BS.p2.o, direction="y")
    target = abcd_beamsplitter_rs(nr1, 0.0, RoC)
    assert result.tolist() == target.tolist()

    # check reversed propagation
    result_trns_reversed = model.BS.ABCD(model.BS.p2.i, model.BS.p1.o)
    target_trns_reversed = abcd_beamsplitter_rs(nr2, 0.0, RoC)
    assert result_trns_reversed.tolist() == target_trns_reversed.tolist()


def test_bs_abcd_total_reflection(model):
    """Test beam splitter ABCD matrix with angles and refractive indices configured for total \
    reflection."""
    nr1 = 1.45
    nr2 = 1.0
    alpha1 = 45.0
    model.chain(Nothing("NULL1"), {"L": 1, "nr": nr1}, Beamsplitter("BS", alpha=alpha1))
    model.add(Nothing("NULL2"))
    model.connect(model.BS.p2, model.NULL2.p1, L=1, nr=nr2)

    with pytest.raises(TotalReflectionError):
        model.BS.ABCD(model.BS.p1.i, model.BS.p2.o)
