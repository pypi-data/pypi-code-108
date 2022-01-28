import pytest
import finesse
import numpy as np
from scipy.special import jv


@pytest.fixture(scope="module")
def modulator_model_out():
    base = finesse.Model()
    base.parse(
        """
        l L0 P=1

        s s0 L0.p1 EOM1.p1

        mod EOM1 f=9M midx=0.1 order=1 mod_type=pm

        pd2 PD2 EOM1.p2.o 9M 0 10
        fsig(10)
        sgen sig L0.amp.i 1 0

        ad icu  EOM1.p1.i &fsig.f
        ad ic   EOM1.p1.i 0
        ad icl  EOM1.p1.i -&fsig.f

        ad am9u EOM1.p2.o -&EOM1.f+&fsig.f
        ad am9  EOM1.p2.o -&EOM1.f
        ad am9l EOM1.p2.o -&EOM1.f-&fsig.f

        ad ap9u EOM1.p2.o &EOM1.f+&fsig.f
        ad ap9  EOM1.p2.o &EOM1.f
        ad ap9l EOM1.p2.o &EOM1.f-&fsig.f

        ad acu  EOM1.p2.o &fsig.f
        ad ac   EOM1.p2.o 0
        ad acl  EOM1.p2.o -&fsig.f
        """
    )

    return base.run()


def test_carrier_signal_coupling(modulator_model_out):
    sol = modulator_model_out
    fmod = lambda k: ((1j) ** k * jv(k, 0.1))

    assert np.allclose(sol["ac"], fmod(0) * sol["ic"])
    assert np.allclose(sol["acl"], fmod(0) * sol["icl"])
    assert np.allclose(sol["acu"], fmod(0) * sol["icu"])

    assert np.allclose(sol["ap9"], fmod(1) * sol["ic"])
    assert np.allclose(sol["ap9l"], fmod(1) * sol["icl"])
    assert np.allclose(sol["ap9u"], fmod(1) * sol["icu"])

    assert np.allclose(sol["am9"], fmod(-1) * sol["ic"])
    assert np.allclose(sol["am9l"], fmod(-1) * sol["icl"])
    assert np.allclose(sol["am9u"], fmod(-1) * sol["icu"])
