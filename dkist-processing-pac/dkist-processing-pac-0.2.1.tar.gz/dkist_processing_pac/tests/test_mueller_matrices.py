import numpy as np
from dkist_processing_pac import Data

RTOL=1e-6

def test_linear_retarder():
    np.testing.assert_allclose(Data.linear_retarder(1,0,0), np.diag(np.ones(4)), rtol=RTOL)

def test_rotation():
    np.testing.assert_allclose(Data.rotation(0), np.diag(np.ones(4)), rtol=RTOL)

def test_mirror():
    np.testing.assert_allclose(Data.mirror(1,0), np.diag(np.ones(4)), rtol=RTOL)
