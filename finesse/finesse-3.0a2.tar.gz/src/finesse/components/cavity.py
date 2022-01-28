"""Optical cavities with associated properties."""

import logging
from copy import deepcopy
import math
import cmath

import networkx as nx
import numpy as np

from .node import OpticalNode, Port
from ..config import config_instance
from .. import components
from ..env import warn
from ..tracing.tree import TraceTree
from ..cymath.math import sgn
from ..constants import values as constants
from ..parameter import info_parameter
from ..gaussian import BeamParam
from ..utilities.components import refractive_index

from .trace_dependency import TraceDependency


LOGGER = logging.getLogger(__name__)

# TODO (sjr) Add Cavity.gain property
#            - optical gain eqn? simple for 2 mirror cav, but need general eqn.


@info_parameter("FSR", "FSR", units="Hz")
@info_parameter("loss", "Loss")
@info_parameter("finesse", "Finesse")
@info_parameter("FWHM", "FWHM", units="Hz")
@info_parameter("storage_time", "Storage time", units="s")
@info_parameter("pole", "Pole", units="Hz")
@info_parameter("round_trip_length", "Round trip length", units="m")
@info_parameter("w0", "Waist size", units="m")
@info_parameter("waistpos", "Waist position", units="m")
@info_parameter("m", "Stability (m-factor)")
@info_parameter("g", "Stability (g-factor)")
@info_parameter("gouy", "Round trip gouy phase", units="°")
@info_parameter("mode_separation", "Mode separation", units="Hz")
@info_parameter("S", "Resolution")
@info_parameter("is_stable", "Stable")
@info_parameter("is_critical", "Critically stable")
class Cavity(TraceDependency):
    """Represents a cavity in an interferometer configuration.

    This class stores the shortest path between the start node and end node of the cavity and
    holds symbolic expressions for each physical attribute of the cavity. Numeric values
    corresponding to these attributes are obtained through the relevant properties.

    Adding a Cavity to a :class:`.Model` results in the beam parameters of all nodes in the cavity
    path being set according to the cavity eigenmode (:attr:`Cavity.q`) when a beam trace is
    performed (e.g. at the start of a modal based simulation). The mode of the cavity is then also
    used as a trace starting point when setting beam parameters at nodes outside of the cavity - see
    :ref:`tracing_manual` for details on the beam tracing algorithm.

    Parameters
    ----------
    name : str
        Name of newly created cavity.

    source : :class:`.OpticalNode` or :class:`.Port`
        Node / Port that the cavity path starts from. If no `via` node is specified, then the cavity
        path will be given by the shortest path from source back to the component that owns
        source.

        If a port is given then the *output* optical node of that port will be used as the source.

    via : :class:`.OpticalNode`, optional
        Node that the cavity path must traverse via; defaults to `None`.

        Note that, unlike `source`, this cannot be a :class:`.Port` object as this would be ambiguous
        for beamsplitter type components - i.e. determination of which node to use cannot be
        assumed automatically.

    priority : number, optional; default: 0
        Priority value for beam tracing. Beam tracing dependencies are sorted in descending order
        of priority - i.e. higher priority value dependencies will be traced first. Any dependency
        with a priority value of zero will be traced, after non-zero priority dependencies, in alphabetic
        order of the dependency names.
    """

    def __init__(self, name, source, via=None, priority=0):
        super().__init__(name, priority)

        # If the source is a port then use the output node
        # of this port as the source for the cavity path
        if isinstance(source, Port):
            source = source.o

        if not isinstance(source, OpticalNode):
            raise TypeError("Expected source to be an OpticalNode.")
        else:
            if source.is_input:
                raise ValueError("Source must be an output node.")

            if not isinstance(source.component, components.Surface):
                msg = (
                    "Expected owner of source node to be a Surface, "
                    f"but got a {type(self.source.component)}"
                )
                raise TypeError(msg)

        if via is not None and not isinstance(via, OpticalNode):
            raise TypeError("Expected via to be an OpticalNode.")

        self.__source = source
        self.__via = via
        self.__path = None

    def __deepcopy__(self, memo):
        # TraceTree instances are non-copyable by design so
        # temporarily set __tree field to None to avoid copy
        tmp = self.__tree
        self.__tree = None
        new = super().__deepcopy__(memo)

        memo[id(self)] = new

        new.__dict__.update(deepcopy(self.__dict__, memo))
        new_model = memo.get(id(self._model))
        new._reset_model(new_model)

        def update_later():
            new.initialise()

        new_model.after_deepcopy.append(update_later)

        # Re-build the tree on self due to above - not an
        # expensive operation so no big deal for now
        self.__tree = tmp
        return new

    def _on_add(self, model):
        if model is not self.source._model:
            raise Exception(
                f"Cavity {repr(self)} is using a source node {self.source} from a different model"
            )

    def draw(self):
        """A string representation of the cavity route.

        Returns
        -------
        s : str
            The node path of the cavity as a string.
        """
        return self.__tree.draw()

    @property
    def path(self):
        """The :class:`.OpticalPath` instance of the cavity.

        :getter: Returns the path of the cavity (read-only).

        See Also
        --------
        finesse.model.Model.path : Retrieves an ordered container of the path trace between two
                                   specified nodes.
        """
        return self.__path

    @property
    def source(self):
        """Starting node of the cavity.

        :getter: Returns the cavity starting node (read-only).
        """
        return self.__source

    @property
    def via(self):
        """Via node of the cavity.

        :getter: Returns the cavity via node (read-only).
        """
        return self.__via

    @property
    def is_fabry_perot(self):
        """Flag indicating whether the cavity is a Fabry-Perot cavity.

        :getter: Returns true if the cavity is a Fabry-Perot, false otherwise (read-only).
        """
        if self.path is None:
            return False

        unique_spaces = set(self.path.spaces)
        # cavity is Fabry-Perot if there's only one space in the path
        return len(unique_spaces) == 1

    ### Non-geometric properties ###

    @property
    def FSR(self):
        r"""The free-spectral-range (FSR) of the cavity.

        This quantity is defined as,

        .. math::
            \mathrm{FSR} = \frac{c}{2L},

        where :math:`c` is the speed of light and :math:`L` is the
        length of the cavity.

        :getter: Returns the cavity free-spectral-range (read-only).
        """
        return self._FSR.eval()

    @property
    def loss(self):
        r"""The round-trip loss of the cavity as a fraction of the incoming power.

        This quantity is computed via,

        .. math::
            L = 1 - \prod_{\mathrm{i}}^{N_{\mathrm{refl}}} R_{\mathrm{i}} \times
                \prod_{\mathrm{i}}^{N_{\mathrm{trns}}} T_{\mathrm{i}},

        i.e. one minus the product of all reflections multiplied with the product of all
        transmissions for a round-trip of the cavity.

        :getter: Returns the fractional round-trip cavity loss (read-only).
        """
        return self._loss.eval()

    @property
    def finesse(self):
        r"""The finesse of the cavity.

        This quantity is defined as,

        .. math::
            \mathcal{F} = \frac{\pi}{2\arcsin{\left(
                \frac{1 - \widetilde{l}}{2\sqrt{\widetilde{l}}}
            \right)
            }},

        where :math:`\widetilde{l} = \sqrt{1 - l}` and :math:`l`
        is the cavity loss.

        :getter: Returns the cavity finesse (read-only).
        """
        return self._finesse.eval()

    @property
    def FWHM(self):
        r"""The cavity full-width-half-maximum (FWHM).

        This quantity is defined as,

        .. math::
            \mathrm{FWHM} = \frac{\mathrm{FSR}}{\mathcal{F}},

        where :math:`\mathcal{F}` is the cavity finesse.

        :getter: Returns the FWHM of the cavity (read-only).

        See Also
        --------
        Cavity.FSR : Free-spectral-range of a cavity.
        Cavity.finesse : Finesse of a cavity.
        """
        return self._FWHM.eval()

    @property
    def storage_time(self):
        r"""The cavity storage time (:math:`\tau`).

        This quantity is defined as,

        .. math::
            \tau = \frac{1}{\pi\mathrm{FWHM}},

        where :math:`\mathrm{FWHM}` is the full-width at half-maximum
        of the cavity resonance.

        :getter: Returns the storage time of the cavity (read-only).

        See Also
        --------
        Cavity.FWHM : Full-width at half-maximum (FWHM) of a cavity.
        """
        return self._tau.eval()

    @property
    def pole(self):
        r"""The pole-frequency of the cavity.

        This quantity is defined as,

        .. math::
            f_{\mathrm{pole}} = \frac{\mathrm{FWHM}}{2},

        where :math:`\mathrm{FWHM}` is the full-width at half-maximum
        of the cavity resonance.

        :getter: Returns the cavity pole-frequency (read-only).

        See Also
        --------
        Cavity.FWHM : Full-width at half-maximum (FWHM) of a cavity.
        """
        return self._pole.eval()

    ### Geometric properties ###

    @property
    def round_trip_length(self):
        """The round-trip length of the cavity (in metres).

        :getter: Returns the length of a single round-trip of the cavity (read-only).
        """
        return self._length.eval()

    @property
    def ABCD(self):
        """The round-trip ABCD matrix of the cavity in both plannes.

        :getter: Returns a :class:`numpy.ndarray` with shape ``(2, 2, 2)`` of the cavity
                 round-trip matrices in the tangential and sagittal planes, respectively. (read-only).
        """
        self.__tree.compute_rt_abcd(self._ABCDx, self._ABCDy)
        Ms = np.zeros((2, 2, 2))
        Ms[0][:] = self._ABCDx[:]
        Ms[1][:] = self._ABCDy[:]
        return Ms

    def __get_ABCD(self, direction):
        return getattr(self, f"ABCD{direction}")

    @property
    def ABCDx(self):
        """The tangential round-trip ABCD matrix of the cavity.

        :getter: Returns the cavity round-trip matrix in the
                 tangential plane (read-only).
        """
        self.__tree.compute_rt_abcd(abcdx=self._ABCDx)
        return self._ABCDx

    @property
    def ABCDy(self):
        """The sagittal round-trip ABCD matrix of the cavity.

        :getter: Returns the cavity round-trip matrix in the
                 sagittal plane (read-only).
        """
        self.__tree.compute_rt_abcd(abcdy=self._ABCDy)
        return self._ABCDy

    @property
    def q(self):
        r"""The eigenmode of the cavity in both planes.

        For a single plane, the cavity eigenmode :math:`q_{\mathrm{cav}}` is computed by solving,

        .. math::
            C q_{\mathrm{cav}}^2+(D-A)q_{\mathrm{cav}} - B = 0,

        where :math:`A`, :math:`B`, :math:`C` and :math:`D` are the elements of the
        round-trip ABCD matrix of the cavity for this plane.

        :getter: Returns a :class:`numpy.ndarray` of the cavity eigenmodes in the tangential and
                 sagittal planes, respectively, where both values are :class:`.BeamParam`
                 instances. (read-only).
        """
        return np.array([self.qx, self.qy])

    def __get_lambda0(self):
        if self.has_model:
            lambda0 = self._model.lambda0
        else:
            lambda0 = config_instance()["constants"].getfloat("lambda0")

        return lambda0

    def __compute_eigenmode(self, direction):
        ABCD = self.__get_ABCD(direction)

        C = ABCD[1][0]
        if C == 0.0:  # confocal cavity - g = 0 (critical)
            return None
        half_inv_C = 0.5 / C

        D_minus_A = ABCD[1][1] - ABCD[0][0]
        minus_B = -1 * ABCD[0][1]

        sqrt_term = cmath.sqrt(D_minus_A * D_minus_A - 4 * C * minus_B)
        lower = (-D_minus_A - sqrt_term) * half_inv_C
        upper = (-D_minus_A + sqrt_term) * half_inv_C

        if lower.imag > 0:
            q = lower
        elif upper.imag > 0:
            q = upper
        else:
            return None

        return q

    @property
    def qx(self):
        """The eigenmode of the cavity in the tangential plane.

        :getter: Returns the cavity's tangential plane eigenmode (read-only).

        See Also
        --------
        Cavity.q
        """
        q = self.__compute_eigenmode("x")
        if q is None:
            return None

        nr = refractive_index(self.source)
        return BeamParam(q=q * nr, wavelength=self.__get_lambda0(), nr=nr)

    @property
    def qy(self):
        """The eigenmode of the cavity in the sagittal plane.

        :getter: Returns the cavity's sagittal plane eigenmode (read-only).

        See Also
        --------
        Cavity.q
        """
        q = self.__compute_eigenmode("y")
        if q is None:
            return None

        nr = refractive_index(self.source)
        return BeamParam(q=q * nr, wavelength=self.__get_lambda0(), nr=nr)

    @property
    def w0(self):
        """The waist size of the cavity in both planes.

        :getter: Returns a :class:`numpy.ndarray` of the cavity waist size in the tangential
                 and sagittal planes, respectively. (read-only).
        """
        return np.array([self.w0x, self.w0y])

    @property
    def w0x(self):
        """The waist size of the cavity in the tangential plane.

        Equivalent to ``cavity.qx.w0``.

        :getter: Returns the cavity waist size in the tangential plane (read-only).
        """
        if not self.is_stable_x:
            return np.nan

        return self.qx.w0

    @property
    def w0y(self):
        """The waist size of the cavity in the sagittal plane.

        Equivalent to ``cavity.qy.w0``.

        :getter: Returns the cavity waist size in the sagittal plane (read-only).
        """
        if not self.is_stable_y:
            return np.nan

        return self.qy.w0

    @property
    def waistpos(self):
        """The position of the cavity waist in both planes.

        This distance to the waist is measured using the position of :attr:`Cavity.source`
        node as the origin.

        :getter: Returns a :class:`numpy.ndarray` of the cavity waist position in the tangential
                 and sagittal planes, respectively. (read-only).
        """
        return np.array([self.waistpos_x, self.waistpos_y])

    @property
    def waistpos_x(self):
        """The waist position of the cavity in the tangential plane.

        Equivalent to ``cavity.qx.z``.

        :getter: Returns the cavity waist position in the tangential plane (read-only).
        """
        if not self.is_stable_x:
            return np.nan

        return self.qx.z

    @property
    def waistpos_y(self):
        """The waist position of the cavity in the sagittal plane.

        Equivalent to ``cavity.qy.z``.

        :getter: Returns the cavity waist position in the sagittal plane (read-only).
        """
        if not self.is_stable_y:
            return np.nan

        return self.qy.z

    @property
    def m(self):
        r"""The stability of the cavity, in both planes, given by the :math:`m`-factor:

        .. math::
            m = \frac{A + D}{2},

        where :math:`A` and :math:`D` are the relevant entries of the
        cavity round-trip ABCD matrix. The cavity is stable if the
        following condition is satisfied:

        .. math::
            -1 \leq m \leq 1.

        :getter: Returns a :class:`numpy.ndarray` of the cavity stability in the tangential and
                 sagittal planes, respectively. (read-only).
        """
        return np.array([self.mx, self.my])

    def __compute_m(self, direction):
        ABCD = self.__get_ABCD(direction)

        A = ABCD[0][0]
        D = ABCD[1][1]
        return 0.5 * (A + D)

    @property
    def mx(self):
        """The stability, m, of the cavity in the tangential plane.

        :getter: Returns the tangential plane m-factor (read-only).

        See Also
        --------
        Cavity.m
        Cavity.gx
        """
        return self.__compute_m("x")

    @property
    def my(self):
        """The stability, m, of the cavity in the sagittal plane.

        :getter: Returns the sagittal plane m-factor (read-only).

        See Also
        --------
        Cavity.m
        Cavity.gy
        """
        return self.__compute_m("y")

    @property
    def g(self):
        r"""The stability of the cavity, in both planes, given by the :math:`g`-factor:

        .. math::
            g = \frac{A + D + 2}{4},

        where :math:`A` and :math:`D` are the relevant entries of the
        cavity round-trip ABCD matrix. The cavity is stable if the
        following condition is satisfied:

        .. math::
            0 \leq g \leq 1.

        :getter: Returns a :class:`numpy.ndarray` of the cavity stability in the tangential and
                 sagittal planes, respectively. (read-only).
        """
        return np.array([self.gx, self.gy])

    def __compute_g(self, direction):
        m = self.__compute_m(direction)
        return 0.5 * (1 + m)

    @property
    def gx(self):
        """The stability, g, of the cavity in the tangential plane.

        :getter: Returns the tangential plane g-factor (read-only).

        See Also
        --------
        Cavity.g
        Cavity.mx
        """
        return self.__compute_g("x")

    @property
    def gy(self):
        """The stability, g, of the cavity in the sagittal plane.

        :getter: Returns the sagittal plane g-factor (read-only).

        See Also
        --------
        Cavity.g
        Cavity.my
        """
        return self.__compute_g("y")

    @property
    def gouy(self):
        r"""The accumulated round-trip Gouy phase of the cavity in both planes (in degrees).

        This is given by,

        .. math::
            \psi_{\mathrm{rt}} = 2\,\arccos{\left( \mathrm{sgn}(B) \sqrt{g} \right)},

        where :math:`B` is the corresponding element of the round-trip
        ABCD matrix and :math:`g` is the cavity stability parameter
        returned by :attr:`Cavity.g`.

        :getter: Returns a :class:`numpy.ndarray` of the accumulated round-trip Gouy phase in the
                 tangential and sagittal planes, respectively. (read-only).
        """
        return np.array([self.gouy_x, self.gouy_y])

    def __compute_round_trip_gouy(self, direction, deg=True):
        ABCD = self.__get_ABCD(direction)

        B = ABCD[0][1]
        g = getattr(self, f"g{direction}")

        psi = 2 * math.acos(sgn(B) * math.sqrt(g))

        if deg:
            return math.degrees(psi)
        return psi

    @property
    def gouy_x(self):
        """The round-trip Gouy phase in the tangential plane (in degrees).

        If the cavity is not stable, then ``np.nan`` is returned.

        :getter: Returns the tangential plane round-trip Gouy phase (read-only).

        See Also
        --------
        Cavity.gouy
        """
        if not self.is_stable_x:
            return np.nan

        return self.__compute_round_trip_gouy("x")

    @property
    def gouy_y(self):
        """The round-trip Gouy phase in the sagittal plane (in degrees).

        If the cavity is not stable, then ``np.nan`` is returned.

        :getter: Returns the sagittal plane round-trip Gouy phase (read-only).

        See Also
        --------
        Cavity.gouy
        """
        if not self.is_stable_y:
            return np.nan

        return self.__compute_round_trip_gouy("y")

    @property
    def mode_separation(self):
        r"""The mode separation frequency of the cavity in both planes.

        This is defined by,

        .. math::
            \delta f =
                \begin{cases}
                    \frac{\psi_{\mathrm{rt}}}{2\pi}
                    \Delta f, & \text{if } \psi_{\mathrm{rt}} \leq \pi\\
                    (1 - \frac{\psi_{\mathrm{rt}}}{2\pi}) \Delta f, & \text{if } \psi_{\mathrm{rt}}
                    > \pi,
                \end{cases}

        where :math:`\psi_{\mathrm{rt}}` is the accumulated round-trip Gouy phase
        and :math:`\Delta f` is the FSR of the cavity.

        :getter: Returns a :class:`numpy.ndarray` of the mode separation frequency in the tangential
                 and sagittal planes, respectively. (read-only).
        """
        return np.array([self.mode_separation_x, self.mode_separation_y])

    def __compute_mode_separation(self, direction):
        gouy = self.__compute_round_trip_gouy(direction, deg=False)

        fsr = self.FSR
        df = 0.5 * fsr * gouy / np.pi
        if gouy > np.pi:
            df = fsr - df

        return df

    @property
    def mode_separation_x(self):
        """The mode separation frequency in the tangential plane.

        If the cavity is not stable, then ``np.nan`` is returned.

        :getter: Returns the tangential plane mode separation frequency (read-only).

        See Also
        --------
        Cavity.mode_separation
        """
        if not self.is_stable_x:
            return np.nan

        return self.__compute_mode_separation("x")

    @property
    def mode_separation_y(self):
        """The mode separation frequency in the sagittal plane.

        If the cavity is not stable, then ``np.nan`` is returned.

        :getter: Returns the sagittal plane mode separation frequency (read-only).

        See Also
        --------
        Cavity.mode_separation
        """
        if not self.is_stable_y:
            return np.nan

        return self.__compute_mode_separation("y")

    @property
    def S(self):
        r"""The resolution of the cavity in both planes.

        Cavity resolution, :math:`S`, is defined by,

        .. math::
            S =
                \begin{cases}
                    \frac{\psi_{\mathrm{rt}}}{2\pi}
                    \mathcal{F}, & \text{if } \psi_{\mathrm{rt}} \leq \pi\\
                    (1 - \frac{\psi_{\mathrm{rt}}}{2\pi})
                        \mathcal{F}, & \text{if } \psi_{\mathrm{rt}} > \pi,
                \end{cases}

        where :math:`\psi_{\mathrm{rt}}` is the round-trip Gouy phase and :math:`\mathcal{F}` is the
        cavity finesse.

        :getter: Returns a :class:`numpy.ndarray` of the cavity resolution in the tangential and
                 sagittal planes, respectively. (read-only).
        """
        return np.array([self.Sx, self.Sy])

    def __compute_resolution(self, direction):
        gouy = self.__compute_round_trip_gouy(direction, deg=False)

        f = self.finesse
        s = 0.5 * f * gouy / np.pi
        if gouy > np.pi:
            s = f - s

        return s

    @property
    def Sx(self):
        """The resolution of cavity in the tangential plane.

        If the cavity is not stable, then ``np.nan`` is returned.

        :getter: Returns the tangential plane resolution (read-only).

        See Also
        --------
        Cavity.S
        """
        if not self.is_stable_x:
            return np.nan

        return self.__compute_resolution("x")

    @property
    def Sy(self):
        """The resolution of cavity in the sagittal plane.

        If the cavity is not stable, then ``np.nan`` is returned.

        :getter: Returns the sagittal plane resolution (read-only).

        See Also
        --------
        Cavity.S
        """
        if not self.is_stable_y:
            return np.nan

        return self.__compute_resolution("y")

    ### Stability flags ###

    @property
    def is_stable(self):
        r"""Flag indicating whether the cavity is stable.

        This only returns `True` if *both* planes of the cavity eigenmode
        are stable.

        :getter: Returns `True` if :math:`0 \leq g \leq 1`,
                 `False` otherwise (for both tangential, sagittal planes).

        See Also
        --------
        Cavity.g
        """
        return self.is_stable_x and self.is_stable_y

    @property
    def is_stable_x(self):
        r"""Flag indicating whether cavity is stable in the tangential plane.

        :getter: Returns `True` if :math:`0 \leq g_x \leq 1`, `False` otherwise.

        See Also
        --------
        Cavity.is_stable
        Cavity.gx
        """
        return 0 < self.gx < 1

    @property
    def is_stable_y(self):
        r"""Flag indicating whether cavity is stable in the sagittal plane.

        :getter: Returns `True` if :math:`0 \leq g_y \leq 1`, `False` otherwise.

        See Also
        --------
        Cavity.is_stable
        Cavity.gy
        """
        return 0 < self.gy < 1

    @property
    def is_critical(self):
        r"""Flag indicating whether the cavity is critically stable.

        This only returns `True` if *both* planes of the cavity eigenmode
        are critically stable.

        :getter: Returns `True` if :math:`g = 0` or :math:`g = 1`,
                 `False` otherwise (for both tangential, sagittal planes).

        See Also
        --------
        Cavity.g
        """
        return self.is_critical_x and self.is_critical_y

    @property
    def is_critical_x(self):
        r"""Flag indicating whether the cavity is critically stable in the tangential plane.

        :getter: Returns `True` if :math:`g_x = 0` or :math:`g_x = 1`,
                 `False` otherwise.

        See Also
        --------
        Cavity.is_critical
        Cavity.gx
        """
        gx = self.gx
        return gx == 0 or gx == 1

    @property
    def is_critical_y(self):
        r"""Flag indicating whether the cavity is critically stable in the sagittal plane.

        :getter: Returns `True` if :math:`g_x = 0` or :math:`g_x = 1`,
                 `False` otherwise.

        See Also
        --------
        Cavity.is_critical
        Cavity.gy
        """
        gy = self.gy
        return gy == 0 or gy == 1

    ### Methods for setting up the symbolic equations for each property ###

    def __symbolise_round_trip_length(self):
        self._length = 0.0
        for comp in self.__path.spaces:
            self._length += comp.L.ref

    def __symbolise_FSR(self):
        self._FSR = constants.C_LIGHT / self._length

    def __symbolise_loss(self):
        from finesse.components.general import InteractionType

        power = 1.0
        t = self.__tree
        while t.left is not None:
            if t.node.is_input:
                comp = t.node.component
            else:
                comp = t.node.space

            if isinstance(comp, components.Surface):
                if (
                    comp.interaction_type(t.node, t.left.node)
                    == InteractionType.REFLECTION
                ):
                    power *= comp.R.ref
                else:
                    power *= comp.T.ref

            t = t.left

        # Need to do final reflection from root component
        power *= self.__tree.node.component.R.ref
        self._loss = 1.0 - power

    def __symbolise_finesse(self):
        _loss = np.sqrt(1.0 - self._loss)
        self._finesse = 0.5 * np.pi / np.arcsin(0.5 * (1.0 - _loss) / np.sqrt(_loss))

    def __symbolise_FWHM(self):
        self._FWHM = self._FSR / self._finesse

    def __symbolise_storage_time(self):
        self._tau = 1 / (np.pi * self._FWHM)

    def __symbolise_pole(self):
        self._pole = 0.5 * self._FWHM

    def __initialise_ABCD(self):
        self.__tree = TraceTree.from_cavity(self)

        self._ABCDx = np.eye(2)
        self._ABCDy = np.eye(2)

        self.__tree.compute_rt_abcd(self._ABCDx, self._ABCDy)

    def _get_workspace(self, sim):
        from finesse.components.modal.cavity import CavityWorkspace

        return CavityWorkspace(self, sim)

    def initialise(self):
        """Initialises the symbolic equations of the cavity and calculates the cavity
        path from the associated model."""

        # determine the target node of the cavity path
        if isinstance(self.source.component, components.Mirror):
            target = self.source.opposite
        else:
            bs = self.source.component
            if self.source.port is bs.p1:
                target = bs.p2.i
            elif self.source.port is bs.p2:
                target = bs.p1.i
            elif self.source.port is bs.p3:
                target = bs.p4.i
            else:
                target = bs.p3.i

        self.__path = self._model.path(self.source, target, self.via)

        self.__initialise_ABCD()
        # Set up all the symbolic equations for each property
        self.__symbolise_round_trip_length()
        self.__symbolise_loss()
        self.__symbolise_finesse()
        self.__symbolise_FSR()
        self.__symbolise_FWHM()
        self.__symbolise_storage_time()
        self.__symbolise_pole()

        if self.is_fabry_perot:
            comps = list(
                filter(
                    lambda x: isinstance(x, components.Surface),
                    self.path.components_only,
                )
            )
            M1, M2 = comps[0], comps[-1]

            R1x, R1y = M1.Rcx.value, M1.Rcy.value
            R2x, R2y = M2.Rcx.value, M1.Rcy.value
            if sgn(R1x) == sgn(R2x) and sgn(R1y) == sgn(R2y) and not self.is_stable:
                warn(
                    f"the signs of the radii of curvature of mirrors {repr(M1.name)} "
                    f"and {repr(M2.name)} in the unstable Fabry-Perot cavity "
                    f"{repr(self.name)} are equal"
                )

    def any_changing_params(self, geometric=False):
        """Determines whether any parameter of any component inside the cavity is
        changing.

        If the optional argument `geometric` is True, then this will only
        check that the following parameters are changing:

        - radii of curvature of surfaces,
        - lengths of spaces,
        - refractive indices of spaces,
        - focal lengths of lenses,
        - angles of incidence of beam splitters.

        Parameters
        ----------
        geometric : bool
            If true then only checks parameters which affect ABCD matrices.

        Returns
        -------
        flag : bool
            True if any parameter is changing (subject to the condition outlined
            above), False otherwise.
        """
        geometric_params = ["Rcx", "Rcy", "L", "f", "nr", "alpha"]
        for comp in self.path.components_only:
            for param in comp.parameters:
                if param.is_changing:
                    if geometric and param.name not in geometric_params:
                        continue

                    return True

        return False

    @property
    def is_changing(self):
        """Flag indicating whether any geometric parameter inside the cavity is
        changing.

        A geometric parameter is defined as one of:

        - radii of curvature of surfaces,
        - focal lengths of lenses,
        - angles of incidence of beam splitters,
        - lengths of spaces,
        - refractive indices of spaces,

        i.e. any parameter which can affect the ABCD matrix values.
        """
        return self.any_changing_params(geometric=True)

    def get_exit_nodes(self):
        """Obtains a dictionary of `source: target` mappings where source -> target and
        target is an exit node of the cavity.

        An exit node is defined to be a node that is not internal
        to the cavity, rather it is obtained on propagation from
        an internal node to outside the cavity.

        Returns
        -------
        exit_nodes : dict
            A dictionary of `source: target` mappings.
        """
        source_succ = nx.dfs_successors(
            self._model.optical_network, self.source.full_name
        )

        node_from_name = lambda n: self._model.network.nodes[n]["weakref"]()
        cav_nodes = self.path.nodes_only
        exit_nodes = {}
        for source_name, target_names in source_succ.items():
            source = node_from_name(source_name)
            if source in cav_nodes:
                for target_name in target_names:
                    target = node_from_name(target_name)
                    if target not in cav_nodes:
                        exit_nodes[source] = target

        return exit_nodes

    def trace_beam(self):
        """Traces the cavity eigenmode through the cavity path.

        Returns
        -------
        out : :class:`.BeamTraceSolution`
            An object representing the results of the tracing routine.
        """
        from ..solutions import BeamTraceSolution

        wavelength = self.__get_lambda0()
        trace = self.__tree.trace_beam(wavelength, symmetric=True)

        return BeamTraceSolution(f"{self.name}_trace", trace, [self.__tree])

    def generate_abcd_str(self):
        """Generates a string representation of the cavity round-trip ABCD matrix
        operations.

        This can be useful for debugging purposes as the returned string will
        correspond exactly to the operation performed internally for calculating
        the round-trip matrices.

        The format of each matrix symbol will be ``<comp>__<from_port>_<to_port>``,
        e.g. the reflection at the rear (port two) surface of a mirror named ITM
        would be represented as ``ITM__p2_p2``. The matrix multiplication is denoted
        via the ``@`` symbol.

        Returns
        -------
        abcd_str : str
            A string representing the operation to obtain the cavity round-trip
            ABCD matrix (in either plane).
        """
        from finesse.tracing.cytools import generate_rt_abcd_str

        return generate_rt_abcd_str(self.__tree)

    def plot(self, direction=None, *args, **kwargs):
        """Plots the beam representing the cavity eigenmode over the path of the cavity.

        See :meth:`.PropagationSolution.plot` if specifying `direction` or
        :meth:`.AstigmaticPropagationSolution.plot` otherwise.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        axs : axes
            The axis handles.
        """
        nodes = self.path.nodes_only
        # From node is always first node of cavity path
        fn = nodes[0]
        traversed_ports = set()
        tn = None
        for node in nodes:  # traverse all the nodes
            # If port has already been encountered, stop
            # as we don't want to repeat the same space
            # (this is applicable to linear cavs only)
            if node.port in traversed_ports:
                tn = node
                break

            traversed_ports.add(node.port)

        # If we didn't traverse the same port twice (e.g. this
        # is a ring or bow-tie type cavity) then set to node as
        # final node of the cavity path for the round-trip
        if tn is None:
            tn = nodes[-1]

        if direction is None:
            ps = self._model.propagate_beam_astig(from_node=fn, to_node=tn)
        else:
            ps = self._model.propagate_beam(
                from_node=fn, to_node=tn, direction=direction
            )

        return ps.plot(*args, **kwargs)
