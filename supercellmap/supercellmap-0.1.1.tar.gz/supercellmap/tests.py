from supercell import SupercellMaker
import numpy as np


def test_phase_factor():
    scmaker = SupercellMaker(sc_matrix=[2, 2, 2])
    factor = scmaker.phase_factor(qpoint=(0, 0, 0.5), phase=0)
    assert ((factor == np.array([1., -1., 1., -1., 1., -1., 1., -1.])).all())
    xsc = scmaker.sc_trans_kvector(x=[1, 2, 3], qpoint=[0, 0, 0.5])
    xsc_ref = [
        1.,
        2.,
        3.,
        -1.,
        -2.,
        -3.,
        1.,
        2.,
        3.,
        -1.,
        -2.,
        -3.,
        1.,
        2.,
        3.,
        -1.,
        -2.,
        -3.,
        1.,
        2.,
        3.,
        -1.,
        -2.,
        -3.,
    ]

    assert ((xsc == xsc_ref).all())

    Rvecs = scmaker.Rvector_for_each_element(n_ind=2)
    print(Rvecs)


def test():
    test_phase_factor()


test()
