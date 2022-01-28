from abc import ABC
from math import isclose
import numpy as np

from ..parameter import float_parameter
from ..symbols import Resolving, Symbol
from ..utilities.misc import calltracker
from .general import Connector


@float_parameter("R", "Reflectivity", validate="_check_R", setter="set_RTL")
@float_parameter("T", "Transmission", validate="_check_T", setter="set_RTL")
@float_parameter("L", "Loss", validate="_check_L", setter="set_RTL")
@float_parameter("phi", "Phase", units="degrees")
@float_parameter(
    "Rcx",
    "Radius of curvature (x)",
    units="m",
    validate="_check_Rc",
    is_geometric=True,
)
@float_parameter(
    "Rcy",
    "Radius of curvature (y)",
    units="m",
    validate="_check_Rc",
    is_geometric=True,
)
@float_parameter("xbeta", "Misalignment (x)", units="radians")
@float_parameter("ybeta", "Misalignment (y)", units="radians")
class Surface(ABC, Connector):
    """Abstract optical surface interface providing an object with common properties for
    :class:`.Mirror` and :class:`.Beamsplitter` to inherit from.

    Parameters
    ----------
    name : str
        Name of newly created surface.

    R : float, optional
        Reflectivity of the surface.

    T : float, optional
        Transmissivity of the surface.

    L : float, optional
        Loss of the surface.

    phi : float, optional
        Microscopic tuning of the surface (in degrees).

    Rc : float, optional
        Radius of curvature (in metres); defaults to ``numpy.inf`` to indicate a planar
        surface. An astigmatic surface can be set with `Rc = (Rcx, Rcy)`.
    """

    def __init__(self, name, R, T, L, phi, Rc, xbeta, ybeta):
        Connector.__init__(self, name)

        # only in constructor allow setting of none of R, T, L
        # -> default to equally reflective and tranmissive with no loss
        if R is None and T is None and L is None:
            # Use some default
            self.set_RTL(0.5, T=0.5, L=0)
        else:
            self.set_RTL(R, T, L)

        self.phi = phi
        self.Rc = Rc
        self.xbeta = xbeta
        self.ybeta = ybeta

    def _check_R(self, value):
        if not 0 <= value <= 1:
            raise ValueError("Reflectivity must satisfy 0 <= R <= 1")

        return value

    def _check_T(self, value):
        if not 0 <= value <= 1:
            raise ValueError("Transmissivity must satisfy 0 <= T <= 1")

        return value

    def _check_L(self, value):
        if not 0 <= value <= 1:
            raise ValueError("Loss must satisfy 0 <= L <= 1")

        return value

    def _check_Rc(self, value):
        if value == 0:
            raise ValueError("Radius of curvature must be non-zero.")

        return value

    @calltracker
    def set_RTL(self, R=None, T=None, L=None):
        """Set the values for the R, T and L properties of the surface.

        One of the following combination must be specified:

            - R and T or,
            - R and L or,
            - T and L or,
            - R and T and L

        In the first three cases, the remaining parameter is set via
        the condition,

        .. math::
            R + T + L = 1

        Parameters
        ----------
        R : scalar
            Value of the reflectivity to set.

        T : scalar
            Value of the transmissivity to set.

        L : scalar
            Value of the loss to set.

        Raises
        ------
        ValueError
            If a combination other than one of the above is specified.

            Or if R, T and L are all given but they sum to anything other than one.
        """
        # Try and cast the input into a float, the datatype of the
        # R/T/L parameters. If it can't just ignore it, as it could be
        # None or some callable, or something else. Need this because
        # the usual datatype casting doesn't happen until much later
        # with this setter, and it is used to R/T/L in the contructor
        # not self.R = R, etc.
        if R is not None and not isinstance(R, Symbol):
            R = self.R.datatype_cast(R)
        if T is not None and not isinstance(T, Symbol):
            T = self.T.datatype_cast(T)
        if L is not None and not isinstance(L, Symbol):
            L = self.L.datatype_cast(L)

        # if any of R, T, L set with parameter refs in kat file
        # syntax then just set each attribute directly here and
        # skip completion of third argument / checking of RTL sum
        if any(isinstance(x, Resolving) for x in (R, T, L)):
            if R is not None:
                self.R = R
            if T is not None:
                self.T = T
            if L is not None:
                self.L = L

            return

        N = sum(x is not None for x in (R, T, L))

        if N < 2:
            msg = f"""Invalid combination passed to {self.name}.set_RTL. One of the
following must be specified:

    - R and T or,
    - R and L or,
    - T and L or,
    - R and T and L
            """
            raise ValueError(msg.strip())

        if N == 2:
            old_R = self.R.value
            old_T = self.T.value
            old_L = self.L.value

            try:
                if R is not None:
                    self.R = R
                else:
                    self.R = 1 - (T + L)

                if T is not None:
                    self.T = T
                else:
                    self.T = 1 - (R + L)

                if L is not None:
                    self.L = L
                else:
                    self.L = 1 - (R + T)
            except ValueError:
                self.R = old_R
                self.T = old_T
                self.L = old_L

                raise

        else:
            RTL_sum = R + T + L

            try:
                # Evaluate symbolics, if necessary.
                RTL_sum = RTL_sum.eval()
            except AttributeError:
                pass

            # FIXME: decide what the necessary tolerance is here.
            if not isclose(RTL_sum, 1):
                msg = (
                    f"Expected R + T + L = 1 in {self.name}.set_RTL but "
                    f"got R + T + L = {RTL_sum}"
                )
                raise ValueError(msg)

            self.R = R
            self.T = T
            self.L = L

    @property
    def Rc(self):
        """The radius of curvature of the mirror in metres, for both the tangential and
        sagittal planes.

        :getter: Returns values of both planes' radii of curvature as a
                 :class:`numpy.ndarray` where the first element is the tangential plane
                 RoC and the second element is the sagittal plane RoC.

        :setter: Sets the radius of curvature.

        Examples
        --------
        The following sets the radii of curvature of an object `m`, which
        is a sub-instance of `Surface`, in both directions to 2.5 m:

        >>> m.Rc = 2.5

        Whilst this would set the radius of curvature in the x-direction (tangential
        plane) to 2.5 m and the radius of curvature in the y-direction (sagittal plane)
        to 2.7 m:

        >>> m.Rc = (2.5, 2.7)
        """
        return np.array([self.Rcx.value, self.Rcy.value])

    @Rc.setter
    def Rc(self, value):
        try:
            self.Rcx = value[0]
            self.Rcy = value[1]
        except (IndexError, TypeError):
            self.Rcx = value
            self.Rcy = value

    def actuate_roc(self, dioptres, direction=("x", "y")):
        r"""Actuate on the radius of curvature (RoC) of the surface with a
        specified dioptre shift.

        Sets the RoC to a new value, :math:`R_2`, via,

        .. math::

            R_2 = \frac{2}{d + \frac{2}{R_1}},

        where :math:`R_1` is the current RoC and :math:`d` is the dioptre shift (i.e.
        the `dioptre` argument).

        By default, both planes of curvature are shifted. To shift, e.g., only the
        tangential plane, specify ``direction="x"``.

        Parameters
        ----------
        dioptres : float
            Shift in surface RoC in dioptres.

        direction : tuple or str, optional; default: ("x", "y")
            RoC plane to shift, defaults to both tangential and sagittal.
        """
        rcnew = lambda x: 2 / (dioptres + 2 / x)
        if "x" in direction:
            self.Rcx = rcnew(self.Rcx.value)
        if "y" in direction:
            self.Rcy = rcnew(self.Rcy.value)

    # NOTE this is a bit hacky but gets around using surface.R = value (etc.)
    #      directly in an axis scan without being warned

    def _on_build(self, sim):
        self.set_RTL.__func__.has_been_called = True

    def _on_unbuild(self, sim):
        self.set_RTL.__func__.has_been_called = False
