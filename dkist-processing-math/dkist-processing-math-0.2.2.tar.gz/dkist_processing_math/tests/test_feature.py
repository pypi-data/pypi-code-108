import numpy as np

from dkist_processing_math.feature import find_px_angles


def test_find_px_angles():
    """
    Given: a single numpy array
    When: finding the most significant angles in a hough transform
    Then: return the correct peak angle
    """

    theta = np.linspace(-np.pi / 4, np.pi / 4, 1500)

    def Gaussian(x, mu, sig):
        return np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))

    mu = 0.1
    sigma = 0.2
    gaussian = Gaussian(theta, mu, sigma)

    H = np.zeros((20, 1500)) + gaussian[None, :]
    desired_peaktheta = np.array(mu)

    result_peaktheta = find_px_angles(H, theta)
    assert isinstance(result_peaktheta, np.ndarray)

    np.testing.assert_array_almost_equal(result_peaktheta, desired_peaktheta)
