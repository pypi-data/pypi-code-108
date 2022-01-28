import numpy as np
import finesse
from finesse.utilities.maps import circular_aperture, surface_point_absorber
from finesse.knm.maps import (
    Map,
    map_scattering_coefficients,
    scattering_coefficients_to_KnmMatrix,
)
from finesse.knm.tools import make_bayerhelms_matrix


def test_changing_map():
    """Tests that changing maps just run, not comparing any outputs at the moment."""
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 L=40e-6 T=0.014 Rc=-1945
    m m2 L=40e-6 T=0 Rc=2245
    link(l1, m1, 3994, m2)
    cav c m2.p1.o

    pd P m1.p2.i

    modes(maxtem=7)

    var offset 0 # point absorber position
    """
    )

    R_ap = 0.4 / 2  # test mass radius
    x = y = np.linspace(-R_ap, R_ap, 400)

    def pabs_map(_map, model):
        h = 200e-3
        w = 20e-6
        power_absorbed = 20e-3

        return surface_point_absorber(
            _map.x - float(model.offset.value), _map.y, w, h, power_absorbed
        )

    itm_map = Map(x, y, amplitude=circular_aperture(x, y, R_ap))
    etm_map = Map(x, y, amplitude=itm_map.amplitude, opd=pabs_map)
    # changing maps aren't picked up by refill checks
    # need to force m2 to refill at the moment
    model.m2.phi.is_tunable = True
    model.m2.surface_map = etm_map
    model.run("xaxis(offset, lin, 0, 0.08, 2, pre_step=update_maps())")


def test_remove_tilts():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 L=0e-6 T=0 Rc=1945
    link(l1, m1)
    gauss g1 l1.p1.o w0=0.012044800081073403 z=-1833.9474927802573

    ad a m1.p1.o n=0 m=1 f=0
    ad b m1.p1.o n=1 m=0 f=0

    modes(maxtem=2)
    var tilt 0
    """
    )

    R_ap = 0.4 / 2  # test mass radius
    x = y = np.linspace(-R_ap, R_ap, 100)

    def tilt_map(_map, model):
        return _map.X * float(model.tilt.value) + _map.Y * float(
            -model.tilt.value * 0.033
        )

    # changing maps aren't picked up by refill checks
    # need to force m2 to refill at the moment
    model.m1.phi.is_tunable = True
    model.m1.surface_map = Map(x, y, opd=tilt_map, auto_remove_tilts=True)

    out = model.run("xaxis(tilt, log, 1e-12, 1e-6, 10, pre_step=update_maps())")
    # roughly limit to make sure all the tilt is removed
    assert np.all(abs(out["a"]) < 1e-13)
    assert np.all(abs(out["b"]) < 1e-13)


def test_remove_astigmatism():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 L=0e-6 T=0
    link(l1, m1)
    gauss g1 l1.p1.o w0=0.05 z=0

    ad a m1.p1.o n=0 m=2 f=0
    ad b m1.p1.o n=2 m=0 f=0

    modes(maxtem=2)
    var tilt 0
    """
    )

    R_ap = 0.4 / 2  # test mass radius
    x = y = np.linspace(-R_ap, R_ap, 100)

    def tilt_map(_map, model):
        return _map.X ** 2 * float(model.tilt.value) + _map.Y ** 2 * float(
            -model.tilt.value * 0.033
        )

    # changing maps aren't picked up by refill checks
    # need to force m2 to refill at the moment
    model.m1.phi.is_tunable = True
    model.m1.surface_map = Map(x, y, opd=tilt_map, auto_remove_astigmatism=True)

    out = model.run("xaxis(tilt, log, 1e-12, 1e-6, 10, pre_step=update_maps())")
    # roughly limit to make sure all the tilt is removed
    assert np.all(abs(out["a"]) < 1e-13)
    assert np.all(abs(out["b"]) < 1e-13)


def test_remove_curvatures():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 L=0e-6 T=0
    link(l1, m1)
    gauss g1 l1.p1.o w0=0.05 z=0

    ad a m1.p1.o n=0 m=2 f=0
    ad b m1.p1.o n=2 m=0 f=0

    modes(maxtem=2)
    var tilt 0
    """
    )

    R_ap = 0.4 / 2  # test mass radius
    x = y = np.linspace(-R_ap, R_ap, 100)

    def tilt_map(_map, model):
        return _map.X ** 2 * float(model.tilt.value) + _map.Y ** 2 * float(
            model.tilt.value
        )

    # changing maps aren't picked up by refill checks
    # need to force m2 to refill at the moment
    model.m1.phi.is_tunable = True
    model.m1.surface_map = Map(x, y, opd=tilt_map, auto_remove_curvatures=True)

    out = model.run("xaxis(tilt, log, 1e-12, 1e-6, 10, pre_step=update_maps())")
    # roughly limit to make sure all the tilt is removed
    assert np.all(abs(out["a"]) < 1e-13)
    assert np.all(abs(out["b"]) < 1e-13)


def test_reverse_gouy():
    """curved beam reflected from a flat tilted mirror, check that BH and maps calculate
    same output with reverse gouy."""
    model = finesse.Model()
    model.parse(
        """
    l l1
    m m1 R=1 T=0
    link(l1, m1)
    fd Er m1.p1.o 0

    modes(maxtem=1)
    gauss g1 m1.p1.i w=10e-3 Rc=3000
    """
    )
    model.beam_trace()
    qx1, qy1 = model.m1.p1.i.q
    qx2, qy2 = -np.conj(model.m1.p1.i.q)
    Kbh = make_bayerhelms_matrix(
        qx1, qx2, qy1, qy2, 2e-6, 0, select=model.homs, reverse_gouy=True
    )

    x = np.linspace(-0.04, 0.04, 201)
    y = np.linspace(-0.04, 0.04, 201)
    X, Y = np.meshgrid(x, y)
    Z = -1e-6 * X
    smap = Map(x, y, opd=Z)

    K = map_scattering_coefficients(
        (qx1, qy1, qx2, qy2),
        model.modes_setting["maxtem"],
        smap.x.copy(),
        smap.y.copy(),
        smap.get_z(2 * np.pi / 1064e-9, -2, model),
        reverse_gouy=True,
    )

    K_map = scattering_coefficients_to_KnmMatrix(model.homs, K)

    assert abs(Kbh.data - K_map.data).max() < 1e-13
