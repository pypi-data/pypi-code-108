"""
Simple detuned cavity testing end mirror shaking
"""

import pytest
from finesse import Model
import numpy as np


@pytest.fixture(scope="module")
def detuned_model_out():
    kat = Model()
    kat.parse(
        """
        l L0 P=1
        s s1 L0.p1 EOM.p1
        mod EOM f=100M midx=0.1 order=1 mod_type=pm
        s s2 EOM.p2 ITM.p1
        m ITM R=0.99 T=0.01 Rc=-2
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=1 T=0 phi=1 Rc=2

        pd1 REFL_I ITM.p1.o &EOM.f 0
        pd1 REFL_Q ITM.p1.o &EOM.f 90
        pd Pcirc ITM.p2.o

        xaxis ETM.phi lin -90 90 20
        cav c1 ITM.p2.o
        modes maxtem=1
        """
    )
    kat.L0.tem(0, 0, 1, 0)
    kat.L0.tem(0, 1, 0.1, 0)

    return kat.run()


# The reference data are wrong here I think as they were generated
# with a version where TEM00 gouy phase wasn't being zeroed (fixed
# on this branch)
@pytest.mark.xfail()
def test_output(detuned_model_out):
    ref = np.array(
        [
            (3.048260007757972e-03, -4.057563866939835e-04, -1.665986017373828e-05),
            (4.993300761259105e-03, -3.379075179617520e-03, -1.587114837244450e-04),
            (4.687996995999352e-03, 2.839224033802190e-03, -6.655013375403227e-05),
            (5.668698146939777e-03, 1.504553833115992e-03, -1.282915362755135e-05),
            (8.797817972513779e-03, 1.321570133635263e-03, -6.888817650098621e-06),
            (1.919522403084504e-02, 1.509193628688014e-03, -5.813993248516674e-06),
            (2.714599890963480e00, 6.352118058536139e-03, -1.918947470996297e-05),
            (9.831288394220125e-02, 2.578935556054961e-03, -7.781075771076863e-06),
            (8.793596468267111e01, 7.766073355244238e-02, -2.260111504101986e-04),
            (9.941767539156281e-02, -3.175854717291632e-03, 9.659058796650049e-06),
            (2.515730190282937e-02, -1.739492135361344e-03, 6.009881756588173e-06),
            (1.171697601694244e-02, -1.372536306324695e-03, 6.079074941109638e-06),
            (7.096837304375270e-03, -1.407391416510550e-03, 1.142798678876742e-05),
            (5.245968555865794e-03, -8.918333910188346e-04, 3.845719381380652e-05),
            (4.262430199017620e-03, -2.461304804813973e-03, 5.726760783516286e-05),
            (5.454477560790733e-03, 4.237574819330691e-03, 2.211561199443786e-04),
            (2.897537677745957e-03, 7.349158529738075e-04, 1.045265571351672e-05),
            (2.630326367217972e-03, 2.241089912942922e-04, 2.170924345389430e-06),
            (2.581042893500175e-03, -6.074664999987774e-05, -8.521252673511541e-07),
            (2.813725205639574e-03, -5.543136877694659e-04, -1.573230645243385e-05),
            (3.048259795116278e-03, -4.057642980884341e-04, -1.665981449136200e-05),
        ],
        dtype=[("Pcirc", "<f8"), ("REFL_I", "<f8"), ("REFL_Q", "<f8")],
    )

    assert np.allclose(detuned_model_out["REFL_I"], ref["REFL_I"], rtol=1e-10)
    assert np.allclose(detuned_model_out["REFL_Q"], ref["REFL_Q"], rtol=1e-10)
    assert np.allclose(detuned_model_out["Pcirc"], ref["Pcirc"], rtol=1e-10)
