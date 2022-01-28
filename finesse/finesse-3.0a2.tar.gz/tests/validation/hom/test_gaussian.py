import finesse
import numpy as np
from finesse.gaussian import optimise_HG00_q
from finesse.knm.tools import make_scatter_matrix


def test_optimise_HG00_q():
    for i in range(100):
        model = finesse.Model()
        model.modes("even", maxtem=20)
        q1x = finesse.BeamParam(w0=1 * np.random.random(), z=4000 * np.random.random())
        q1y = finesse.BeamParam(w0=1 * np.random.random(), z=4000 * np.random.random())
        q2x = finesse.BeamParam(
            w0=q1x.w0 * (1 + np.random.random() / 4),
            z=q1x.z * (1 + np.random.random() / 4),
        )
        q2y = finesse.BeamParam(
            w0=q1y.w0 * (1 + np.random.random() / 4),
            z=q1y.z * (1 + np.random.random() / 4),
        )
        # can't have too large a mismatch otherwise you need way too many modes
        if (
            finesse.BeamParam.mismatch(q1y, q2y) < 0.3
            and finesse.BeamParam.mismatch(q1x, q2x) < 0.3
        ):
            kmat = make_scatter_matrix(
                "bayerhelms", q1x, q2x, q1y, q2y, 0, 0, select=model.homs
            )
            E = np.zeros(len(model.homs), dtype=complex)
            E[0] = 1
            E = kmat.data @ E  # new mode vector
            q3x, q3y = optimise_HG00_q(
                E, (q2x, q2y), model.homs, accuracy=1e-10, max_iterations=100
            )
            assert abs(q3x.w0 - q1x.w0) / abs(q1x.w0) < 0.001
            assert abs(q3x.z - q1x.z) / abs(q1x.z) < 0.001
            assert abs(q3y.w0 - q1y.w0) / abs(q1y.w0) < 0.001
            assert abs(q3y.z - q1y.z) / abs(q1y.z) < 0.001
