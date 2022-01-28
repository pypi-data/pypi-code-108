"""Test the amplitude of light transmitted through a phase modulator at various
frequencies."""

import numpy as np
from scipy.special import jv
import pytest
from finesse import Model
from finesse.components import Laser, Modulator
from finesse.detectors import AmplitudeDetector
from finesse.analysis.actions import Xaxis


MAX_MODULATION_ORDER = 5


@pytest.fixture(scope="module")
def modulator_model_out():
    """Fixture with the results of a model with a modulator with changing modulation
    index.

    See Also
    --------
    3.8.1 in Living Rev Relativ (2016).
    """
    model = Model()
    model.chain(
        Laser("l1", P=1), Modulator("eom1", midx=0, f=40e3, order=5, mod_type="pm")
    )

    for order in range(1, MAX_MODULATION_ORDER + 1):
        f = 40e3 * order
        model.add(AmplitudeDetector(f"bessel{order}", model.eom1.p2.o, f=f))

    return model.run(Xaxis("eom1.midx", "lin", 0, 10, 100))


def test_bessel(modulator_model_out):
    """Test that the transmitted amplitude as a function of modulation index follows a
    Bessel function."""
    # maxdiff = 0
    # print('')
    for order in range(1, MAX_MODULATION_ORDER + 1):
        mod_data = np.abs(modulator_model_out[f"bessel{order}"])
        bessel_fcn = np.abs(jv(order, modulator_model_out.x1))
        # diff = np.max(np.abs(mod_data - bessel_fcn) / np.abs(bessel_fcn))
        # maxdiff = max(maxdiff, diff)
        # print(f'Order: {order}, Relative Difference: {maxdiff}')
        assert np.allclose(mod_data, bessel_fcn)

    # print('Max relative difference: '+str(maxdiff))


# if __name__ == '__main__':
#    pytest.main(args=['-v', '-s'])
