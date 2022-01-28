"""Functions for generating thermal models for LIGO."""

import numpy as np
import finesse

from ..materials import FusedSilica
from ..utilities.maps import circular_aperture
from . import ring_heater as rh
from . import hello_vinet as hv
from ..knm import Map


def get_name(obj):
    """Helper function to convert input object from str or Variable to a string."""
    try:
        return obj.name
    except AttributeError:
        return str(obj)


def get_thermal_test_mass_params(N_samples):
    R_ap = 0.17  # substrate radius
    h = 0.2  # substrate thickness
    x = y = np.linspace(-R_ap, R_ap, N_samples)
    r = np.linspace(0, R_ap, N_samples)
    X, Y = np.meshgrid(x, y)
    material = FusedSilica
    b = 60e-3  # Ring heater start position [m]
    c = 80e-3  # Ring heater end position [m]
    aperture = circular_aperture(x, y, 0.163)
    return R_ap, h, x, y, r, X, Y, material, b, c, aperture


def make_LIGO_thermal_surface_map(
    N_samples: int,
    HR_port: finesse.components.Port,
    static_surface_offset: callable,
    P_coat_abs: str,
    P_RH: str,
    include_Rc=False,
):
    """This returns a :class:`finesse.knm.maps.Map` object that simulates the thermal
    effects on the surface of a mirror. This is hardcoded for LIGO test masses and uses
    analytic equations from Hello-Vinet :cite:`vinet_liv_rev` and for the ring heater
    :cite:`Ramette:16`".

    Parameters
    ----------
    N_samples : int
        Size of map to be computed over the radius of the test mass
    HR_port : :class:`finesse.components.Port`
        Port of mirror which the HR surface is on
    static_surface_offset: callable(x,y)
        A 2D function of x and y which returns a static surface
        profile of the mirror. To be used for non-spherial
        polishes or other such effects.
    P_coat_abs : [str|model.components.Variable]
        Name of :class:`finesse.components.Variable` element in the model
        that states how much power is absorbed in the coating
    P_RH : [str|model.components.Variable]
        Name of :class:`finesse.components.Variable` element in the model
        that states how much power ring heater power is applied.
    include_Rc : bool, optional
        If True the RoC of the targetted mirror will be included into
        the maps displacement and the :class:`finesse.knm.maps.Map` is
        flagged as a "focusing element". This can be required if the
        surface distortions from the map add large focusing terms to
        the map. Setting to True can reduce the number of modes needed
        to model the system.

    Returns
    -------
    map : :class:`finesse.knm.maps.Map`
        Map with a functional displacement controlled via the two
        Variables provided. Spot sizes are deduced at runtime from
        the current beam tracing in the model.

    Notes
    -----
    The calculated map uses analytics from both [1] and [2]. Although
    an explicit calculation for the thermo-elastic deformation from the
    ring heater is not presented in [2] it can be well approximated with

    .. math::

        Z(r) = \\alpha \\int T(r, z) \\mathrm{d}z.

    This was compared with finite element modelling and for the LIGO test
    mass and ring heater at least very close.

    .. rubric:: Aperture

    The aperture of the mirror is 0.17m but includes the flat sides
    of the LIGO test masses at 0.163m. Beause of this the aperture
    is set to 0.163m assuming that the optic is not coated beyond this.

    .. rubric:: Variables

    The way to interact with this map is by setting the value of the
    two Variable elements given. No error will be raised if the wrong
    names are given when the map is created. The Variables are only queried
    when the simulation is run or the map is calculated. If the name is
    incorrect a ModelAttrException will be raised.
    """
    assert isinstance(HR_port.component, finesse.components.Mirror)
    mirror = HR_port.component
    # determined overall scaling depending on which port is the "HR side"
    scale = -1 if mirror.ports[0] == HR_port else 1
    R_ap, h, x, y, r, X, Y, material, b, c, aperture = get_thermal_test_mass_params(
        N_samples
    )

    # Assumes static Rc parameters
    if include_Rc:
        R_static = X ** 2 / 2 / float(mirror.Rcx) + Y ** 2 / 2 / float(mirror.Rcy)
    else:
        R_static = np.zeros_like(X)
    if static_surface_offset is not None:
        static = static_surface_offset(X, Y)
        R_static += static

    aperture = circular_aperture(x, y, 0.163)
    aperture[abs(X) > 0.163] = 0  # flat sides of test mass

    # Ring heater deformation, only needs to be computed once
    W_z_ring_per_W = rh.thermal_lens(r, R_ap, b, c, h, material)
    # Approximated Thermo-elastic deformation, roughly matches FEA
    # wrong slightly towards the edges but seems fine in the central area
    U_z_ring_per_W = W_z_ring_per_W / material.dndT * material.alpha

    P_coat_abs_name = get_name(P_coat_abs)
    # P_bulk_abs_name = get_name(P_bulk_abs)
    P_RH_name = get_name(P_RH)

    # Make function that update_map will call to recompute itself
    def surface_model(smap, model):
        # get current floating point values for powers
        P_abs = float(model.get(P_coat_abs_name))
        P_rh = float(model.get(P_RH_name))
        spot_size = (HR_port.i.qx.w + HR_port.i.qy.w) / 2  # average spot size
        # Inter polate axisymmetric thermal equations to 2D grid
        thermal = np.interp(
            smap.R,
            r,
            # minus for surface normal change
            scale
            * (
                -P_abs
                * -hv.surface_deformation_coating_heating_HG00(
                    r, R_ap, h, spot_size, material, s_max=10, root_accuracy=1e-6
                )
                - U_z_ring_per_W * P_rh
            ),
        )
        return R_static + thermal

    return Map(
        x,
        y,
        amplitude=aperture,
        opd=surface_model,
        # RoC of mirror is inclued in the map
        is_focusing_element=include_Rc,
    )


def make_LIGO_thermal_substrate_map(
    N_samples: int,
    port: finesse.components.Port,
    P_coat_abs: str,
    P_bulk_abs: str,
    P_RH: str,
):
    """This returns a :class:`finesse.knm.maps.Map` object that simulates the substrate
    thermal effects in a LIGO test mass. The equations used are the analytic equations
    from Hello-Vinet :cite:`vinet_liv_rev` and for the ring heater :cite:`Ramette:16`.

    Parameters
    ----------
    N_samples : int
        Size of map to be computed over the radius of the
        test mass
    port : :class:`finesse.components.Port`
        Port of mirror which the HR surface is on
    P_coat_abs : [str|model.components.Variable]
        Name of :class:`finesse.components.Variable` element
        in the model that states how much power is absorbed
        in the coating
    P_bulk_abs : [str|model.components.Variable]
        Name of :class:`finesse.components.Variable` element
        in the model that states how much power is absorbed
        through the entire substrate
    P_RH : [str|model.components.Variable]
        Name of :class:`finesse.components.Variable` element
        in the model that states how much power ring heater
        power is applied.

    Returns
    -------
    map : :class:`finesse.knm.maps.Map`
        Map with a functional displacement controlled via the two
        Variables provided. Spot sizes are deduced at runtime from
        the current beam tracing in the model.

    Notes
    -----
    The calculated map uses analytics from both [1] and [2]. Although
    an explicit calculation for the thermo-elastic deformation from the
    ring heater is not presented in [2] it can be well approximated with

    .. math::

        Z(r) = \\alpha \\int T(r, z) \\mathrm{d}z.

    This was compared with finite element modelling and for the LIGO test
    mass and ring heater at least very close.

    .. rubric:: Aperture

    The aperture of the mirror is 0.17m but includes the flat sides
    of the LIGO test masses at 0.163m. Beause of this the aperture
    is set to 0.163m assuming that the optic is not coated beyond this.

    .. rubric:: Variables

    The way to interact with this map is by setting the value of the
    two Variable elements given. No error will be raised if the wrong
    names are given when the map is created. The Variables are only queried
    when the simulation is run or the map is calculated. If the name is
    incorrect a ModelAttrException will be raised.
    """
    R_ap, h, x, y, r, X, Y, material, b, c, aperture = get_thermal_test_mass_params(
        N_samples
    )

    # Ring heater deformation, only needs to be computed once
    W_z_ring_per_W = rh.thermal_lens(r, R_ap, b, c, h, material)

    P_coat_abs_name = get_name(P_coat_abs)
    P_bulk_abs_name = get_name(P_bulk_abs)
    P_RH_name = get_name(P_RH)

    # Make function that update_map will call to recompute itself
    def surface_model(smap, model):
        # get current floating point values for powers
        P_abs_coat = float(model.get(P_coat_abs_name))
        P_abs_bulk = float(model.get(P_bulk_abs_name))
        P_rh = float(model.get(P_RH_name))
        spot_size = port.i.qx.w
        W_z_coat_per_W, W_z_bulk_per_W = hv.thermal_lenses_HG00(
            r, R_ap, h, spot_size, material
        )
        # Zero thermal lens piston offsets
        W_z_coat_per_W -= abs(W_z_coat_per_W).max()
        W_z_bulk_per_W -= abs(W_z_bulk_per_W).max()
        # Interpolate axisymmetric thermal equations to 2D grid
        thermal = np.interp(
            smap.R,
            r,
            W_z_coat_per_W * P_abs_coat
            + W_z_bulk_per_W * P_abs_bulk
            + W_z_ring_per_W * P_rh,
        )
        return thermal

    return Map(
        x,
        y,
        amplitude=aperture,
        opd=surface_model,
        # RoC of mirror is inclued in the map
        is_focusing_element=True,
    )
