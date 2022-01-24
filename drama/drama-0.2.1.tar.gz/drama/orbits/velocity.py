"""velocity.py includes functions that are related to the speed of the
orbit.
"""
import numpy as np

from drama import constants as const


def orbit_to_vel(
    orbit_alt, ground=False, r_planet=const.r_earth, m_planet=const.m_earth
):
    """Calculates orbital/ground velocity assuming circular orbit

    Parameters
    ----------
    orbit_alt :
        Satellite orbit altitude
    ground :
        If true, returned value will be ground velocity (Default value = False)
    r_planet :
         (Default value = const.r_earth)
    m_planet :
         (Default value = const.m_earth)

    Returns
    -------
    type
        Orbital or Ground velocity

    """
    v = np.sqrt(const.G * m_planet / (r_planet + orbit_alt))

    # Convert to ground velocity if needed
    if ground:
        v = r_planet / (r_planet + orbit_alt) * v
    return v
