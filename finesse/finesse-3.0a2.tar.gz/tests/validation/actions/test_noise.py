import finesse
import pytest


@pytest.fixture
def siso_laser_amplitude():
    model = finesse.Model()
    model.parse(
        """
    fsig(1)
    l l1 P=0.1
    bs bs1 R=0.01 T=0.99
    readout_dc pd1
    amplifier G -10M
    butter A 4 lowpass 70
    link(l1, bs1, pd1, pd1.DC, G, A, l1.amp)

    # out of loop witness sensor
    readout_dc witness
    link(bs1, witness)

    noise laser_amp l1.amp.i 1m/&fsig
    noise amplifier G.p2.o &G.gain*(0.2m/&fsig + 0.0001u*&fsig**2)
    noise pd1_dark_noise pd1.DC.o 0.33n

    noise_projection(
        geomspace(1m, 10M, 1000),
        witness.DC
    )

    """
    )

    return model


def test_siso_laser_amplitude(siso_laser_amplitude):
    siso_laser_amplitude.run()


def test_siso_laser_amplitude_plot(siso_laser_amplitude):
    siso_laser_amplitude.run().plot()
    siso_laser_amplitude.run().plot("witness.DC")
