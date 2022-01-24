import numpy as np


WHITE = np.array([1., 1., 1.])
BRIGHTNESS = 0.5


def abc_to_rgb(abc):
    """Conversion from candidates to RGB color

    Parameters
    ----------
    abc : tuple, list or numpy.ndarray
        Array of size 3. Each coefficient is associated to a candidate a, b, c. Typically the coefficients sum to 1
        or less than 1.

    Returns
    -------
    numpy.ndarray
        Array of size 3. RGB color. Roughly speaking, candidate `a` is associated to red, `b` to green and `c` to blue,
        but we try to mix colors more reasonably than just an average in RGB space.

    Examples
    --------
        >>> abc_to_rgb([1, 0, 0])
        array([1. , 0.5, 0.5])
        >>> abc_to_rgb([.5, .5, 0])
        array([1. , 1. , 0.5])
        >>> abc_to_rgb([0., 0., 0])
        array([0.5, 0.5, 0.5])
    """
    norm_inf = np.max(abc)
    if norm_inf == 0:
        rgb = np.zeros(3)
    else:
        norm_1 = np.sum(abc)
        rgb = np.array(abc) * np.min([norm_1, 1]) / norm_inf
    return rgb * (1 - BRIGHTNESS) + WHITE * BRIGHTNESS


COLOR_NO_ONE = abc_to_rgb([0, 0, 0])
COLOR_A = abc_to_rgb([1, 0, 0])
COLOR_B = abc_to_rgb([0, 1, 0])
COLOR_C = abc_to_rgb([0, 0, 1])
COLOR_AB = abc_to_rgb([1, 1, 0])
COLOR_AC = abc_to_rgb([1, 0, 1])
COLOR_BC = abc_to_rgb([0, 1, 1])
COLOR_ABC = abc_to_rgb([1, 1, 1])


def _uni_mix(color_1, color_2, weight_1, weight_2):
    """Mix two colors, with a fade that emphasizes the two base colors.

    Parameters
    ----------
    color_1, color_2 : tuple, list or numpy.ndarray
        Arrays of size 3 in format RGB.
    weight_1, weight_2 : Number
        Respective weights of the two colors.

    Returns
    -------
    numpy.ndarray
        Array of size 3 in format RGB. The mix is not linear. Currently, the resulting color is a barycenter
        with respective weights ``weight_1**n`` and ``weight_2**n``, with ``n = 2.5``. This makes a "sharper"
        transition, so that we see more of the base colors and less of the mixes.

    Examples
    --------
        >>> import numpy as np
        >>> _uni_mix(color_1=[1, 0, 0], color_2=[0, 1, 0], weight_1=1, weight_2=0)
        array([1., 0., 0.])
        >>> _uni_mix(color_1=[1, 0, 0], color_2=[0, 1, 0], weight_1=.5, weight_2=.5)
        array([0.5, 0.5, 0. ])
        >>> _uni_mix(color_1=[1, 0, 0], color_2=[0, 1, 0], weight_1=0, weight_2=1)
        array([0., 1., 0.])
    """
    n = 2.5
    return (np.array(color_1) * weight_1 ** n + np.array(color_2) * weight_2 ** n) / (weight_1 ** n + weight_2 ** n)


def _palette(x, y):
    """Compute the data for a nice color palette.

    Parameters
    ----------
    x, y : Number
        Cartesian coordinates of the point.

    Returns
    -------
    numpy.ndarray
        Array of size 3 in format RGB. The resulting figure consists of:

        * A nice color palette in the unit disk,
        * A black circle on the unit circle,
        * White background outside.

    Examples
    --------
        >>> _palette(x=0, y=1.5)
        array([1., 1., 1.])
        >>> _palette(x=0, y=0.99)
        array([0., 0., 0.])
        >>> color_almost_a = _palette(x=0, y=0.95)
        >>> np.all(np.isclose(color_almost_a, [1, .5, .5], atol=1E-2))
        True
    """
    z = x + 1j * y
    r = np.abs(z)
    if r > 1:
        return np.array([1., 1., 1.])
    if r > 0.96:
        return np.array([0., 0., 0.])
    theta = (np.angle(z, 'deg') + 30) % 360 - 30
    for theta_sup, color_inf, color_sup in zip([30, 90, 150, 210, 270, 330],
                                               [COLOR_C, COLOR_AC, COLOR_A, COLOR_AB, COLOR_B, COLOR_BC],
                                               [COLOR_AC, COLOR_A, COLOR_AB, COLOR_B, COLOR_BC, COLOR_C]):
        if theta <= theta_sup:
            weight_inf = (theta_sup - theta) / 60
            color = _uni_mix(color_sup, color_inf, 1 - weight_inf, weight_inf)
            return _uni_mix(color, COLOR_ABC, r ** .8, 1 - r ** .8)


DATA_PALETTE = np.array([[_palette(x / 100, y / 100) for x in range(-100, 100)] for y in range(-100, 100)])
