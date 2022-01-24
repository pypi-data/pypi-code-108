"""
=====================================
Orbits Package (:mod:`drama.orbits`)
=====================================
"""
from drama.orbits.orbital_drifts import nodal_regression, omega_per_dot
from drama.orbits.velocity import orbit_to_vel

# import swath_geo to solve the circular dependency issue due to
# SingleSwath in swath_geo inheriting from .keplerian.SingleOrbit
import drama.geo.swath_geo
from drama.orbits.keplerian import KeplerianOrbit, SingleOrbit
# from .rw_XML import write_XMLorbit, read_XMLorbit, write_SV
from drama.orbits.sunsync_orbit import get_sunsync_repeat_orbit, \
    get_sunsync_orbit, get_sunsync_inclination, alt_inc_sunsync
# from formation import clohessy_wiltshire, FormationTimeline
