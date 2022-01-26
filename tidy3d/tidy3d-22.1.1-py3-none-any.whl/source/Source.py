import numpy as np

from ..utils import inside_box_coords, cs2span, listify, list2str
from ..utils.log import log_and_raise, SourceError
from ..utils.check import check_3D_lists
from ..constants import int_, float_, complex_, fp_eps, xyz_list, xyz_dict, inf


class Source(object):
    """
    Base class for defining spatial profiles of excitation conditions.
    """

    def __init__(self, source_time, span, amplitude=1.0, name="source"):
        """Base constructor. Available subclasses:

        - :class:`.VolumeSource`
        - :class:`.PointDipole`
        - :class:`.ModeSource`
        - :class:`.PlaneWave`
        - :class:`.GaussianBeam`
        """
        self.source_time = source_time
        """ Slightly offset the span such that if the source is zero-size 
        along a certain direction, and is placed exactly on a grid coordinate,
        it will deterministically be placed to the right of the coordinate."""
        self.span = span
        zero_span = self.span[:, 1] - self.span[:, 0] < fp_eps
        self.span[zero_span, :] += fp_eps
        self.amplitude = amplitude
        self.name = None if name is None else str(name)

        # Nonzero components boolean: Ex, Ey, Ez, Hx, Hy, Hz. If 0, the solver
        # automatically skips the component.
        self.components = np.zeros((6,), dtype=np.int8)

    def _inside(self, coords):
        """Get a mask equal to one if a point is inside the source region,
        and zero if outside.

        Parameters
        ----------
        coords : 3-tuple
            Defines the x, y, and z coords.
        """
        mask = np.zeros(tuple(c.size - 1 for c in coords))
        indsx, indsy, indsz = inside_box_coords(self.span, coords)
        mask[indsx[0] : indsx[1], indsy[0] : indsy[1], indsz[0] : indsz[1]] = 1.0

        return mask

    def _inside_inds(self, coords):
        """Get indexes of the points inside the source region.

        Parameters
        ----------
        coords : 3-tuple
            Defines the x, y, and z coords.

        Returns
        -------
        np.ndarray
            An array of shape (Np, 3), where Np is the total number of coords
            points in the source region.
        """
        inds = inside_box_coords(self.span, coords)
        indsm = np.meshgrid(
            np.arange(inds[0][0], inds[0][1]),
            np.arange(inds[1][0], inds[1][1]),
            np.arange(inds[2][0], inds[2][1]),
            indexing="ij",
        )
        if indsm[0].size == 0:
            return np.zeros((0, 3), dtype=int_)

        return np.stack([inds.ravel() for inds in indsm], axis=1).astype(int_)


class VolumeSource(Source):
    """A source specified as an electric or a magnetic current of a fixed
    component (one of ``Ex, Ey, Ez, Hx, Hy, Hz``) with a constant amplitude
    inside a 3D volume region.
    """

    def __init__(self, source_time, center, size, component, amplitude=1.0, name=None):
        """
        Construct.

        Parameters
        ----------
        source_time : SourceTime
            Object describing the time dependence of the source.
        center : array_like
            (micron) 3D vector defining the center of the source region.
        size : array_like
            (micron) 3D vector defining the size of the source region.
        component : str
            One of ``{'Ex', 'Ey', 'Ez', 'Hx', 'Hy', 'Hz'}``, specifying the
            direction and type of current component (e.g. ``Ez`` specifies
            electric current source polarized along the z-axis).
        amplitude : float, optional
            Scaling amplitude of the source.
        name : None, optional
            Custom name of the source.
        """
        check_3D_lists(center=listify(center), size=listify(size))
        self.center = np.array(center)
        self.size = np.array(size)
        span = cs2span(center, size)
        super().__init__(source_time, span, amplitude, name)
        self.component = component
        cinds = ["ex", "ey", "ez", "hx", "hy", "hz"]
        try:
            comp_ind = cinds.index(component.lower())
            self.components[comp_ind] = 1
        except:
            log_and_raise(
                f"Unrecognized component {component}, must be one of {cinds}.", SourceError
            )

    def __repr__(self):
        rep = "Tidy3D VolumeSource: {\n"
        rep += "name         = %s\n" % self.name
        rep += "center       = %s\n" % list2str(self.center, "%1.4f")
        rep += "size         = %s\n" % list2str(self.size, "%1.4f")
        rep += "source_time  = " + repr(self.source_time) + "\n"
        rep += "component    = %s\n" % self.component
        rep += "amplitude    = %1.2e\n" % self.amplitude
        rep += "}\n"

        return rep


class PointDipole(VolumeSource):
    """A source specified as an electric or a magnetic current of a fixed
    component (one of ``Ex, Ey, Ez, Hx, Hy, Hz``) at a given point.
    """

    def __init__(self, source_time, center, component, amplitude=1.0, name=None):
        """
        Construct.

        Parameters
        ----------
        source_time : SourceTime
            Object describing the time dependence of the source.
        center : array_like
            (micron) 3D vector defining the center of the source region.
        component : str
            One of ``{'Ex', 'Ey', 'Ez', 'Hx', 'Hy', 'Hz'}``, specifying the
            direction and type of current component (e.g. ``Ez`` specifies
            electric current source polarized along the z-axis).
        amplitude : float, optional
            Scaling amplitude of the source.
        name : None, optional
            Custom name of the source.
        """

        super().__init__(
            source_time,
            center=center,
            size=[0, 0, 0],
            component=component,
            amplitude=amplitude,
            name=name,
        )

        def __repr__(self):
            rep = "Tidy3D PointDipole: {\n"
            rep += "name         = %s\n" % self.name
            rep += "center       = %s\n" % list2str(self.center, "%1.4f")
            rep += "source_time  = " + repr(self.source_time) + "\n"
            rep += "component    = %s\n" % self.component
            rep += "amplitude    = %1.2e\n" % self.amplitude
            rep += "}\n"

            return rep


class Field2DSource(Source):
    """Base class for a source spanning a 2D cross section of a given size
    inside a :class:`.Simulation`.
    """

    def __init__(self, source_time, center, size, direction="forward", amplitude=1.0, name=None):
        """Base class constructor."""

        check_3D_lists(center=listify(center), size=listify(size))
        # Get normal direction from size
        self.norm_ind = np.nonzero(size < fp_eps)[0]
        if self.norm_ind.size != 1:
            log_and_raise("Exactly one element of source 'size' must be zero.", SourceError)
        self.norm_ind = int(self.norm_ind)

        try:
            # Direction index is -/+ 1 for backward/forward
            dir_ind = ["backward", "forward"].index(direction)
            self.dir_ind = int(2 * (dir_ind - 0.5))
        except:
            log_and_raise("'direction' must be one of 'forward', 'backward'.", SourceError)

        self.normal = xyz_list[self.norm_ind]
        self.direction = direction
        self.center = np.array(center)
        self.size = np.array(size)
        span = cs2span(center, size)
        super().__init__(source_time, span, amplitude, name)

        # Angle of injection
        self.angle_theta = 0
        self.angle_phi = 0

        # All tangential components could be non-zero.
        self.components = np.ones((6,), dtype=np.int8)
        # No normal E component
        self.components[self.norm_ind] = 0
        # No normal H component
        self.components[3 + self.norm_ind] = 0


class ModeSource(Field2DSource):
    """Eigenmode source spanning a 2D cross section of a given size inside
    a :class:`.Simulation`. The source needs to be added to a
    :class:`.Simulation` object before the eigenmodes can be computed. They are
    computed using the material parameters defined by the :class:`.Simulation`
    in the 2D cross section, and the central frequency of the ModeSource time
    dependence. Periodic boundary conditions are assumed in the 2D plane.
    The modes are sorted by their effective index (propagation constant in the
    normal direction), in decreasing order. Before the :class:`.Simulation`
    can be run, the index of the eigenmode to be used by the ModeSource has to
    be specified.
    """

    def __init__(
        self,
        source_time,
        center,
        size,
        direction="forward",
        angle_theta=0.0,
        angle_phi=0.0,
        amplitude=1.0,
        name=None,
    ):
        """
        Construct.

        Parameters
        ----------
        source_time : SourceTime
            Object describing the time dependence of the source.
        center : array_like
            (micron) 3D vector defining the center of the 2D plane.
        size : array_like
            (micron) 3D vector defining the size of the 2D plane. Exactly one
            of the values must be ``0``, defining the normal direction.
        direction : {'forward', 'backward'}
            Specifying propagation along the positive or negative direction of
            the normal axis.
        angle_theta : float, optional
            (radian) Polar angle of propagation from the normal axis.
        angle_phi : float, optional
            (radian) Azimuth angle of propagation in the plane orthogonal to the normal axis.
        amplitude : float, optional
            Scaling amplitude of the source.
        name : str or None, optional
            Custom name of the source.
        """

        super().__init__(source_time, center, size, direction, amplitude=amplitude, name=name)

        if angle_theta < 0 or angle_theta >= np.pi / 2:
            log_and_raise("'angle_theta' must be between 0 and pi/2.", SourceError)

        self.angle_theta = angle_theta
        self.angle_phi = angle_phi

    def __repr__(self):
        rep = "Tidy3D ModeSource: {\n"
        rep += "name         = %s\n" % self.name
        rep += "normal       = %s\n" % self.normal
        rep += "direction    = %s\n" % self.direction
        rep += "center       = %s\n" % list2str(self.center, "%1.4f")
        rep += "size         = %s\n" % list2str(self.size, "%1.4f")
        rep += "source_time  = " + repr(self.source_time) + "\n"
        rep += "amplitude    = %1.2e\n" % self.amplitude

        return rep


class PlaneWave(Field2DSource):
    """Plane-wave source with a specified direction and polarization, spanning
    the whole 2D simulation cross-section at a given position normal to a
    given injection axis.
    """

    def __init__(
        self, source_time, injection_axis, position, polarization, amplitude=1.0, name=None
    ):
        """Construct.

        Parameters
        ----------
        source_time : SourceTime
            Object describing the time dependence of the source.
        injection_axis : {'+x', '-x', '+y', '-y', '+z', '-z'}
            Defines the axis normal to the plane of the source, and the
            direction of propagation of the plane wave.
        position : float
            (micron) Position of the plane along the nomral axis.
        polarization : {'x', 'y', 'z'}
            Electric field polarization of the plane wave. Cannot be the same
            as the ``injection_axis``.
        amplitude : float, optional
            Scaling amplitude of the source.
        name : str or None, optional
            Custom name of the source.
        """

        inj_axes = ["+x", "-x", "+y", "-y", "+z", "-z"]
        if injection_axis not in inj_axes:
            log_and_raise(f"'injection_axis' must be one of {inj_axes}.", SourceError)
        norm_ind = xyz_dict[injection_axis[1]]
        direction = {"-": "backward", "+": "forward"}[injection_axis[0]]

        try:
            self.position = float(position)
        except:
            log_and_raise(
                "'position' is a single float defining the plane position along the 'normal' axis.",
                SourceError,
            )
        try:
            self.epol_ind = xyz_dict[polarization]
        except:
            log_and_raise("'polarization' must be one of 'x', 'y', or 'z'.", SourceError)

        if norm_ind == self.epol_ind:
            log_and_raise(
                "'polarization' orientation cannot be the same as 'injection_axis'.", SourceError
            )

        self.polarization = polarization
        self.injection_axis = injection_axis

        center = np.zeros((3,))
        center[norm_ind] = position
        size = inf * np.ones((3,))
        size[norm_ind] = 0
        super().__init__(source_time, center, size, direction, amplitude=amplitude, name=name)

        # Re-initialize components
        self.components = np.zeros((6,), dtype=np.int8)
        self.components[self.epol_ind] = 1
        # H-field polarization index (orthogonal to E and normal)
        self.hpol_ind = [0, 1, 2]
        self.hpol_ind.remove(self.epol_ind)
        self.hpol_ind.remove(self.norm_ind)
        self.hpol_ind = self.hpol_ind[0]
        # Magnetic field component (boolean)
        self.components[3 + self.hpol_ind] = 1

    def __repr__(self):
        rep = "Tidy3D PlaneWave:\n"
        rep += "name            = %s\n" % self.name
        rep += "injection_axis  = %s\n" % self.injection_axis
        rep += "position        = %1.2f\n" % self.position
        rep += "source_time     = " + repr(self.source_time) + "\n"
        rep += "polarization    = %s\n" % self.polarization
        rep += "amplitude       = %1.2e\n" % self.amplitude

        return rep


class PlaneSource(Field2DSource):
    """Plane-wave source with a specified direction and polarization, spanning
    the whole simulation cross-section at a given position and axis normal.
    """

    def __init__(
        self,
        source_time,
        position,
        normal,
        direction="forward",
        diff_order=[0, 0],
        pol_angle=0,
        polarization=None,
        amplitude=1.0,
        name=None,
    ):
        """Construct.

        Parameters
        ----------
        source_time : SourceTime
            A SourceTime object describing the time dependence of the source.
        normal : {'x', 'y', 'z'}
            Axis normal to the plane of the source.
        position : float
            (micron) Position of the plane along the normal axis.
        direction : {'forward', 'backward'}
            Specifying propagation along the positive or negative direction of
            the normal axis.
        diff_order : array_like
            Two integers specifying the diffraction order of the plane wave
            Periodic (not Bloch) boundary conditions are currently always
            assumed in the cross-sectional plane in which the source is placed.
        pol_angle : float
            (radian) Specifies the angle between the electric field
            polarization of the plane wave and the plane defined by the normal
            axis and the propagation direction. ``pol_angle=0`` (default)
            specifies P polarization, while ``pol_angle=np.pi/2`` specifies S
            polarization.
        polarization : array_like or None
            If provided, this overrides ``pol_angle``. A vector with three
            elements specifically defining the E-field polarization vector.
            If the polarization vector is not orthogonal to the k-vector,
            only the Gram-Schmidt orthogonal part is used.
        name : str or None, optional
            Custom name of the source.
        """

        try:
            self.norm_ind = xyz_dict[normal]
        except:
            log_and_raise("'normal' must be one of 'x', 'y', or 'z'.", SourceError)

        try:
            self.position = float(position)
        except:
            log_and_raise(
                "'position' is a single float defining the plane "
                "position along the 'normal' axis.",
                SourceError,
            )

        self.diff_order = listify(diff_order)
        self.pol_angle = pol_angle
        if polarization is None:
            self.polarization = np.array([0, 0, 0])
        else:
            check_3D_lists(polarization=polarization)
            self.polarization = np.array(polarization, dtype=float_)

        center = np.zeros((3,))
        center[self.norm_ind] = position
        size = inf * np.ones((3,))
        size[self.norm_ind] = 0
        super().__init__(source_time, center, size, direction, amplitude=amplitude, name=name)

    def __repr__(self):
        rep = "Tidy3D PlaneSource: {\n"
        rep += "name         = %s\n" % self.name
        rep += "position     = %1.2f\n" % self.position
        rep += "normal       = %s\n" % self.normal
        rep += "direction    = %s\n" % self.direction
        rep += "diff_order   = %s\n" % list2str(self.diff_order, "%d")
        if np.linalg.norm(self.polarization) < fp_eps:
            rep += "pol_angle    = %1.4f\n" % self.pol_angle
        else:
            rep += "polarization = %s\n" % list2str(self.polarization, "%1.2f")

        rep += "source_time  = " + repr(self.source_time) + "\n"
        rep += "amplitude    = %1.2e\n" % self.amplitude
        rep += "}\n"

        return rep


class GaussianBeam(Field2DSource):
    """Plane-wave source with a specified direction and polarization, spanning
    the whole simulation cross-section at a given position and axis normal.
    """

    def __init__(
        self,
        source_time,
        center,
        normal,
        direction="forward",
        angle_theta=0.0,
        angle_phi=0.0,
        pol_angle=0.0,
        waist_radius=1.0,
        waist_distance=0.0,
        amplitude=1.0,
        name=None,
    ):
        """Construct.

        Parameters
        ----------
        source_time : SourceTime
            A SourceTime object describing the time dependence of the source.
        center : array_like
            (micron) 3D vector defining the center of the source.
        normal : {'x', 'y', 'z'}
            Axis normal to the plane of the source.
        direction : {'forward', 'backward'}
            Specifying propagation along the positive or negative direction of
            the normal axis.
        angle_theta : float, optional
            (radian) Polar angle from the normal axis.
        angle_phi : float, optional
            (radian) Azimuth angle in the plane orthogonal to the normal axis.
        pol_angle : float, optional
            (radian) Specifies the angle between the electric field
            polarization of the source and the plane defined by the normal
            axis and the propagation axis. ``pol_angle=0`` (default)
            specifies P polarization, while ``pol_angle=np.pi/2`` specifies S
            polarization.
        waist_radius : float, optional
            Radius of the Gaussian beam at the waist location, defined as
            field decaying to 1/e of its maximum value.
        waist_distance : float, optional
            Distance from the beam waist along the propagation direction.
        amplitude : float, optional
            Scaling amplitude of the source.
        name : str or None, optional
            Custom name of the source.
        """

        try:
            self.norm_ind = xyz_dict[normal]
        except:
            log_and_raise("'normal' must be one of 'x', 'y', or 'z'.", SourceError)

        if angle_theta < 0 or angle_theta >= np.pi / 2:
            log_and_raise("'angle_theta' must be between 0 and pi/2.", SourceError)

        size = inf * np.ones((3,))
        size[self.norm_ind] = 0
        super().__init__(source_time, center, size, direction, amplitude=amplitude, name=name)

        self.angle_theta = angle_theta
        self.angle_phi = angle_phi
        self.pol_angle = pol_angle
        self.waist_radius = waist_radius
        self.waist_distance = waist_distance

    def __repr__(self):
        rep = "Tidy3D GaussianBeam: {\n"
        rep += "name         = %s\n" % self.name
        rep += "position     = %1.2f\n" % self.position
        rep += "normal       = %s\n" % self.normal
        rep += "direction    = %s\n" % self.direction
        rep += "angle_theta  = %1.4f\n" % self.angle_theta
        rep += "angle_phi    = %1.4f\n" % self.angle_phi
        rep += "pol_angle    = %1.4f\n" % self.pol_angle
        rep += "source_time  = " + repr(self.source_time) + "\n"
        rep += "amplitude    = %1.2e\n" % self.amplitude
        rep += "}\n"

        return rep
