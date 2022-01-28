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
        s s1 L0.p1 ITM.p1

        m ITM R=0.99 T=0.01
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=1 T=0 phi=1

        pd1 REFL_I ITM.p1.o &fsig.f
        fsig 1
        sgen sg ETM.mech.z 1 0

        xaxis fsig.f log 1 100M 10
        """
    )

    return kat.run()


@pytest.mark.xfail(reason="https://chat.ligo.org/ligo/pl/oziz95gj3ino9qz9fs5ax1i57o")
def test_output(detuned_model_out):
    ref = np.array(
        [
            (7.525831460952759e-05 + 2.245580867230892e02j,),
            (3.028899431228638e-03 + 1.416865741059184e03j,),
            (1.205636709928513e-01 + 8.939818473026156e03j,),
            (4.799766514450312e00 + 5.640644574221969e04j,),
            (1.910834566541016e02 + 3.559017434528768e05j,),
            (7.609180054403841e03 + 2.245872388010547e06j,),
            (3.061387282564417e05 + 1.424221875080180e07j,),
            (1.942956484518483e07 + 1.118144891760693e08j,),
            (7.573131370840698e06 - 7.049621890433751e07j,),
            (1.496518263742990e05 - 1.024282869384192e07j,),
            (-1.121538163378247e04 - 3.851185182438274e06j,),
        ],
        dtype=[("REFL_I", "<c16")],
    )

    assert np.allclose(detuned_model_out["REFL_I"], ref["REFL_I"], rtol=1e-10)
