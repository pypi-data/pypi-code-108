# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import pickle
import numpy as np
from numpy.testing import assert_array_equal

from eelbrain import datasets
from eelbrain._stats.spm import LM, LMGroup


def test_lm():
    ds = datasets.get_uts()
    model = ds.eval("A*B*Y")
    coeffs = ds['uts'].ols(model)

    lm = LM('uts', 'A*B*Y', ds, 'effect')
    assert repr(lm) == "<LM: uts ~ A + B + A x B + Y + A x Y + B x Y + A x B x Y>"
    for i, effect in enumerate(model.effects):
        assert_array_equal(lm.coefficient(effect.name).x, coeffs.x[i])


def test_random_lm():
    np.random.seed(0)

    ds = datasets.get_uts()
    lms_dummy = []
    lms_effect = []
    for i in range(5):
        ds['uts'].x += np.random.normal(0, 2, ds['uts'].shape)
        lms_dummy.append(LM('uts', 'A*B*Y', ds))
        lms_effect.append(LM('uts', 'A*B*Y', ds, 'effect'))

    # dummy coding
    rlm = LMGroup(lms_dummy)
    assert repr(rlm) == '<LMGroup: uts ~ A + B + A x B + Y + A x Y + B x Y + A x B x Y, n=5>'
    # coefficients
    ds = rlm.coefficients_dataset(('A', 'A x B'), long=True)
    assert ds['term'].cells == ('A', 'A x B')
    # tests
    res = rlm.column_ttest('A x B', samples=100, pmin=0.05, mintime=0.025)
    assert res.clusters.n_cases == 2

    # effect coding
    rlm = LMGroup(lms_effect)
    res = rlm.column_ttest('A x B', samples=100, pmin=0.05, mintime=0.025)
    assert res.clusters.n_cases == 5
    # persistence
    rlm_p = pickle.loads(pickle.dumps(rlm, pickle.HIGHEST_PROTOCOL))
    assert rlm_p.dims == rlm.dims
