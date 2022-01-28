import pytest
import finesse
import numpy as np


def FT_GW_sidebands(Lambda, h0, fsig, L, n, sb_sign, P0):
    """Reference for strain signal in a space.

    Interferometer responses to gravitational waves: Comparing Finesse simulations and
    analytical solutions Charlotte Bond, Daniel Brown and Andreas Freise LIGO DCC:
    T1300190 https://arxiv.org/pdf/1306.6752.pdf
    """
    # Carrier light parameters
    c = 299792458
    f0 = c / Lambda
    w0 = 2 * np.pi * f0
    # Signal anglar frequency
    wsig = 2 * np.pi * fsig
    # Sideband amplitude
    Asb = -np.sqrt(P0) * (w0 * h0 / (2 * wsig)) * np.sin(wsig * L * n / (2 * c))
    # Phase
    phi_sb = np.pi / 2 - sb_sign * wsig * L * n / (2 * c)
    # Final sideband
    return Asb * np.exp(1j * phi_sb)


@pytest.mark.parametrize(
    "L,P",
    ((1, 1), (2, 10), (100, 4), (3, 1000)),
)
def test_space_strain_signal(L, P):
    IFO = finesse.Model()

    IFO.parse(
        f"""
        fsig(10)
        l l1 P={P}
        s s1 l1.p1 n1.p1 L={L}
        nothing n1
        ad upper n1.p1.i &fsig.f
        ad lower n1.p1.i -&fsig.f
        sgen sig s1.h
        xaxis(fsig.f, lin, 1, 100k, 1000)
        """
    )

    out = IFO.run()

    upper_err = abs(
        out["upper"]
        - FT_GW_sidebands(
            IFO.lambda0,
            1,
            out.x1,
            IFO.spaces.s1.L.value,
            IFO.spaces.s1.nr.value,
            +1,
            IFO.l1.P.value,
        )
    )
    lower_err = abs(
        out["lower"]
        - FT_GW_sidebands(
            IFO.lambda0,
            1,
            out.x1,
            IFO.spaces.s1.L.value,
            IFO.spaces.s1.nr.value,
            -1,
            IFO.l1.P.value,
        )
    )

    assert max(upper_err) < 1e-6
    assert max(lower_err) < 1e-6
