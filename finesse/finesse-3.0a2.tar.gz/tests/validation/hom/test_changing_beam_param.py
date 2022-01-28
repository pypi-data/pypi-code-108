import pytest
import numpy as np


@pytest.mark.parametrize("initial_z0", (+1200, -1200))
def test_initial_beam_param(initial_z0):
    """Test that an initial beam parameter is overwritten by xaxis.

    This test is based on the discussion in
    https://chat.ligo.org/ligo/pl/rzm4ews487dzuyqmsrzwj5jfqa
    where a beam parameter initially set
    was not being overwitten by the xaxis.

    This test failed in 86bea1a4
    and was fixed in 10af113c.
    """
    import finesse

    out = []
    for z0 in 0, initial_z0:
        script = f"""
        laser l1 P=1.5

        gauss g1 l1.p1.o w0=10e-3 z={z0}
        modes(maxtem=7)

        space s1 l1.p1 bs1.p1 L=1000
        beamsplitter bs1 R=1 T=0 alpha=30 xbeta=1e-5
        space s2 bs1.p2 bs2.p1 L=400
        beamsplitter bs2 R=1 T=0 alpha=30 xbeta=&bs1.xbeta
        space s3 bs2.p2 n1.p1 L=600
        nothing n1

        power_detector_dc pd1 node=n1.p1.i pdtype=none

        xaxis(g1.zx, lin, 0, -2000, 60)
        """
        kat = finesse.Model()
        kat.parse(script)
        kat.g1.zy = kat.g1.zx.ref
        out.append(kat.run())

    assert np.all(out[0]["pd1"] == out[1]["pd1"])
