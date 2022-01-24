import numpy as np
import scipy.signal

def correct_spikes(image, threshold):
    """
    Perform a conditional median filtering
    The filtering is done in-place, meaning that the array content is modified.

    Parameters
    ----------
    image: numpy.ndarray
        Image to filter
    threshold: float
        Median filter threshold
    """
    m_im = scipy.signal.medfilt2d(image)
    fixed_part = np.array(image[[0, 0, -1, -1], [0, -1, 0, -1]])

    where = abs(image - m_im) > threshold
    image[where] = m_im[where]
    image[[0, 0, -1, -1], [0, -1, 0, -1]] = fixed_part

    return image
