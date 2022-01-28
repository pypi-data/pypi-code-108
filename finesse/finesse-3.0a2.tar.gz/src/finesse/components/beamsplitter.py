"""Optical components representing physical beamsplitters."""

import logging
import types
import numpy as np

from finesse.exceptions import TotalReflectionError
from finesse.parameter import float_parameter
from finesse.utilities import refractive_index

from finesse.components.general import InteractionType, DOFDefinition, NoiseType
from finesse.components.surface import Surface
from finesse.components.node import NodeDirection, NodeType, Node

LOGGER = logging.getLogger(__name__)


@float_parameter("R", "Reflectivity", validate="_check_R", setter="set_RTL")
@float_parameter("T", "Transmission", validate="_check_T", setter="set_RTL")
@float_parameter("L", "Loss", validate="_check_L", setter="set_RTL")
@float_parameter("phi", "Phase", units="degrees")
@float_parameter(
    "alpha",
    "Angle of incidence (-90 <= alpha <= 90)",
    units="degrees",
    is_geometric=True,
    changeable_during_simulation=False,
)
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
@float_parameter("xbeta", "Yaw misalignment", units="radians")
@float_parameter("ybeta", "Pitch misalignment", units="radians")
class Beamsplitter(Surface):
    """The beamsplitter component represents a thin dielectric surface with associated
    properties such as reflectivity, tuning, and radius of curvature. It has four
    optical ports p1, p2, p3, and p4 which describe the four beams incident on either
    side of this surface. p1 and p2 are on side 1 and p3 and p4 are on side 2. A 100%
    transmissive beamsplitter will transmit all of the light incident at p1 to p3.

    It also has a mechanical port `mech` which has nodes for longitudinal, yaw, and pitch motions.
    These mechanical nodes are purely for exciting small signal oscillations of the mirror.
    Static offsets in longitudinal displacements are set by the `phi` parameter (in units of degrees),
    misalignments in yaw by the `xbeta` parameter, and pitch the `ybeta` parameter. Macroscopic angle
    of incidence of the beamsplitter is set by the ``alpha`` parameter.

    Beamsplitters physically operate the same as mirror components, except for the non-normal angle of incidence
    option.

    Parameters
    ----------
    name : str
        Name of newly created beamsplitter.

    R : float, optional
        Reflectivity of the beamsplitter.

    T : float, optional
        Transmissivity of the beamsplitter.

    L : float, optional
        Loss of the beamsplitter.

    phi : float, optional
        Microscopic tuning of the beamsplitter (in degrees).

    alpha : float, optional
        Angle of incidence (in degrees)

    Rc : float, optional
        Radius of curvature (in metres); defaults to ``numpy.inf``
        to indicate a planar surface.

    xbeta, ybeta : float, optional
        Angle of misalignment in the yaw plane (xbeta) and pitch
        (ybeta), respectively (in radians); defaults to `0`.
    """

    def __init__(
        self, name, R=None, T=None, L=None, phi=0, alpha=0, Rc=np.inf, xbeta=0, ybeta=0
    ):
        super().__init__(name, R, T, L, phi, Rc, xbeta, ybeta)
        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p2", NodeType.OPTICAL)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p3", NodeType.OPTICAL)
        self.p3._add_node("i", NodeDirection.INPUT)
        self.p3._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p4", NodeType.OPTICAL)
        self.p4._add_node("i", NodeDirection.INPUT)
        self.p4._add_node("o", NodeDirection.OUTPUT)

        # optic to optic couplings => reflections
        self._register_node_coupling(
            "P1i_P2o", self.p1.i, self.p2.o, interaction_type=InteractionType.REFLECTION
        )
        self._register_node_coupling(
            "P2i_P1o", self.p2.i, self.p1.o, interaction_type=InteractionType.REFLECTION
        )
        self._register_node_coupling(
            "P3i_P4o", self.p3.i, self.p4.o, interaction_type=InteractionType.REFLECTION
        )
        self._register_node_coupling(
            "P4i_P3o", self.p4.i, self.p3.o, interaction_type=InteractionType.REFLECTION
        )

        # optic to optic couplings => transmissions
        self._register_node_coupling(
            "P1i_P3o",
            self.p1.i,
            self.p3.o,
            interaction_type=InteractionType.TRANSMISSION,
        )
        self._register_node_coupling(
            "P2i_P4o",
            self.p2.i,
            self.p4.o,
            interaction_type=InteractionType.TRANSMISSION,
        )
        self._register_node_coupling(
            "P3i_P1o",
            self.p3.i,
            self.p1.o,
            interaction_type=InteractionType.TRANSMISSION,
        )
        self._register_node_coupling(
            "P4i_P2o",
            self.p4.i,
            self.p2.o,
            interaction_type=InteractionType.TRANSMISSION,
        )

        # mirror motion couplings
        self._add_port("mech", NodeType.MECHANICAL)
        self.mech._add_node("z", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("yaw", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("pitch", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("F_z", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("F_yaw", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("F_pitch", NodeDirection.BIDIRECTIONAL)

        # optic to motion couplings
        self._register_node_coupling("P1i_Fz", self.p1.i, self.mech.F_z)
        self._register_node_coupling("P2i_Fz", self.p2.i, self.mech.F_z)
        self._register_node_coupling("P3i_Fz", self.p3.i, self.mech.F_z)
        self._register_node_coupling("P4i_Fz", self.p4.i, self.mech.F_z)
        self._register_node_coupling("P1o_Fz", self.p1.o, self.mech.F_z)
        self._register_node_coupling("P2o_Fz", self.p2.o, self.mech.F_z)
        self._register_node_coupling("P3o_Fz", self.p3.o, self.mech.F_z)
        self._register_node_coupling("P4o_Fz", self.p4.o, self.mech.F_z)
        self._register_node_coupling("P1i_Fyaw", self.p1.i, self.mech.F_yaw)
        self._register_node_coupling("P2i_Fyaw", self.p2.i, self.mech.F_yaw)
        self._register_node_coupling("P3i_Fyaw", self.p3.i, self.mech.F_yaw)
        self._register_node_coupling("P4i_Fyaw", self.p4.i, self.mech.F_yaw)
        self._register_node_coupling("P1o_Fyaw", self.p1.o, self.mech.F_yaw)
        self._register_node_coupling("P2o_Fyaw", self.p2.o, self.mech.F_yaw)
        self._register_node_coupling("P3o_Fyaw", self.p3.o, self.mech.F_yaw)
        self._register_node_coupling("P4o_Fyaw", self.p4.o, self.mech.F_yaw)
        self._register_node_coupling("P1i_Fpitch", self.p1.i, self.mech.F_pitch)
        self._register_node_coupling("P2i_Fpitch", self.p2.i, self.mech.F_pitch)
        self._register_node_coupling("P3i_Fpitch", self.p3.i, self.mech.F_pitch)
        self._register_node_coupling("P4i_Fpitch", self.p4.i, self.mech.F_pitch)
        self._register_node_coupling("P1o_Fpitch", self.p1.o, self.mech.F_pitch)
        self._register_node_coupling("P2o_Fpitch", self.p2.o, self.mech.F_pitch)
        self._register_node_coupling("P3o_Fpitch", self.p3.o, self.mech.F_pitch)
        self._register_node_coupling("P4o_Fpitch", self.p4.o, self.mech.F_pitch)
        # motion to optic couplings: phase coupling on reflection
        self._register_node_coupling("Z_P1o", self.mech.z, self.p1.o)
        self._register_node_coupling("Z_P2o", self.mech.z, self.p2.o)
        self._register_node_coupling("Z_P3o", self.mech.z, self.p3.o)
        self._register_node_coupling("Z_P4o", self.mech.z, self.p4.o)
        self._register_node_coupling("yaw_P1o", self.mech.yaw, self.p1.o)
        self._register_node_coupling("yaw_P2o", self.mech.yaw, self.p2.o)
        self._register_node_coupling("yaw_P3o", self.mech.yaw, self.p3.o)
        self._register_node_coupling("yaw_P4o", self.mech.yaw, self.p4.o)
        self._register_node_coupling("pitch_P1o", self.mech.pitch, self.p1.o)
        self._register_node_coupling("pitch_P2o", self.mech.pitch, self.p2.o)
        self._register_node_coupling("pitch_P3o", self.mech.pitch, self.p3.o)
        self._register_node_coupling("pitch_P4o", self.mech.pitch, self.p4.o)

        # NOTE (pjj) temporarily moved after add_port, as validator depends on ports
        #            being present. Same fix as below.
        self.alpha = alpha

        self.__changing_check = set(
            (self.R, self.T, self.L, self.phi, self.alpha, self.xbeta, self.ybeta)
        )

        # Define typical degrees of freedom for this component
        self.dofs = types.SimpleNamespace()
        self.dofs.z = DOFDefinition(f"{self.name}.dofs.z", self.phi, self.mech.z, 1)
        self.dofs.yaw = DOFDefinition(
            f"{self.name}.dofs.yaw", self.xbeta, self.mech.yaw, 1
        )
        self.dofs.pitch = DOFDefinition(
            f"{self.name}.dofs.pitch", self.ybeta, self.mech.pitch, 1
        )

    def get_adjacent_port(self, p):
        """Get the port adjacent (on the same side of the surface) as `p`."""
        if isinstance(p, Node):
            p = p.port

        adj_dict = {
            self.p1: self.p2,
            self.p2: self.p1,
            self.p3: self.p4,
            self.p4: self.p3,
        }
        if p not in adj_dict:
            raise ValueError(f"Port {p} does not belong to Beamsplitter {self.name}")

        return adj_dict[p]

    def _resymbolise_ABCDs(self):
        # -> reflections
        self.__symbolise_ABCD(self.p1.i, self.p2.o, "x")
        self.__symbolise_ABCD(self.p1.i, self.p2.o, "y")
        self.__symbolise_ABCD(self.p2.i, self.p1.o, "x")
        self.__symbolise_ABCD(self.p2.i, self.p1.o, "y")
        self.__symbolise_ABCD(self.p3.i, self.p4.o, "x")
        self.__symbolise_ABCD(self.p3.i, self.p4.o, "y")
        self.__symbolise_ABCD(self.p4.i, self.p3.o, "x")
        self.__symbolise_ABCD(self.p4.i, self.p3.o, "y")
        # -> transmissions
        self.__symbolise_ABCD(self.p1.i, self.p3.o, "x")
        self.__symbolise_ABCD(self.p1.i, self.p3.o, "y")
        self.__symbolise_ABCD(self.p3.i, self.p1.o, "x")
        self.__symbolise_ABCD(self.p3.i, self.p1.o, "y")
        self.__symbolise_ABCD(self.p2.i, self.p4.o, "x")
        self.__symbolise_ABCD(self.p2.i, self.p4.o, "y")
        self.__symbolise_ABCD(self.p4.i, self.p2.o, "x")
        self.__symbolise_ABCD(self.p4.i, self.p2.o, "y")

    def __symbolise_ABCD(self, from_node, to_node, direction):
        if direction == "x":
            Rc = self.Rcx.ref
        else:
            Rc = self.Rcy.ref

        alpha = self.alpha.ref

        nr1 = refractive_index(from_node, symbolic=True)
        nr2 = refractive_index(to_node, symbolic=True)

        alpha1 = np.radians(alpha)
        # we get alpha2 from Snell's law
        if from_node.port is self.p3 or from_node.port is self.p4:
            sin_alpha2 = (nr2 / nr1) * np.sin(alpha1)
        else:
            sin_alpha2 = (nr1 / nr2) * np.sin(alpha1)

        if abs(float(sin_alpha2)) > 1:
            msg = (
                f"Total reflection in beam splitter {self.name} for "
                f"{from_node.full_name} -> {to_node.full_name} in plane {direction}."
            )
            tr = TotalReflectionError(msg, from_node, to_node)
            self._abcd_matrices[(from_node, to_node, direction)] = None, tr
            return

        alpha2 = np.arcsin(sin_alpha2)

        A = 1.0
        D = 1.0
        # reflection
        if self.interaction_type(from_node, to_node) == InteractionType.REFLECTION:
            if from_node.port is self.p1 or from_node.port is self.p2:
                if direction == "x":
                    C = -2 * nr1 / (Rc * np.cos(alpha1))
                else:
                    C = -2 * nr1 * np.cos(alpha1) / Rc
            else:
                if direction == "x":
                    C = 2 * nr2 / (Rc * np.cos(alpha2))
                else:
                    C = 2 * nr2 * np.cos(alpha2) / Rc

        # transmission
        else:
            cos_alpha1 = np.cos(alpha1)
            cos_alpha2 = np.cos(alpha2)
            delta_n = (nr2 * cos_alpha2 - nr1 * cos_alpha1) / (cos_alpha1 * cos_alpha2)
            C = delta_n / Rc

            if direction == "x":
                A = cos_alpha2 / cos_alpha1
                D = cos_alpha1 / cos_alpha2
                if from_node.port is self.p3 or from_node.port is self.p4:
                    A = 1 / A
                    D = 1 / D

        M_sym = np.array([[A, 0.0], [C, D]])

        key = (from_node, to_node, direction)
        # For beamsplitters the symbol nr can change when connected up to spaces
        # in a model so here we update the ABCD matrix entry
        if key in self._abcd_matrices:
            self._abcd_matrices[key] = M_sym, np.array(M_sym, dtype=np.float64)
        # Otherwise just register the new ABCD matrix as usual
        else:
            self.register_abcd_matrix(M_sym, (from_node, to_node, direction))

    @property
    def abcd12x(self):
        """Numeric ABCD matrix from port 1 to port 2 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(1, 2, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 2, "x")

    @property
    def abcd12y(self):
        """Numeric ABCD matrix from port 1 to port 2 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(1, 2, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 2, "y")

    @property
    def abcd21x(self):
        """Numeric ABCD matrix from port 2 to port 1 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(2, 1, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 1, "x")

    @property
    def abcd21y(self):
        """Numeric ABCD matrix from port 2 to port 1 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(2, 1, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 1, "y")

    @property
    def abcd34x(self):
        """Numeric ABCD matrix from port 3 to port 4 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(3, 4, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(3, 4, "x")

    @property
    def abcd34y(self):
        """Numeric ABCD matrix from port 3 to port 4 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(3, 4, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(3, 4, "y")

    @property
    def abcd43x(self):
        """Numeric ABCD matrix from port 4 to port 3 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(4, 3, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(4, 3, "x")

    @property
    def abcd43y(self):
        """Numeric ABCD matrix from port 4 to port 3 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(4, 3, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(4, 3, "y")

    @property
    def abcd13x(self):
        """Numeric ABCD matrix from port 1 to port 3 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(1, 3, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 3, "x")

    @property
    def abcd13y(self):
        """Numeric ABCD matrix from port 1 to port 3 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(1, 3, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 3, "y")

    @property
    def abcd31x(self):
        """Numeric ABCD matrix from port 3 to port 1 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(3, 1, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(3, 1, "x")

    @property
    def abcd31y(self):
        """Numeric ABCD matrix from port 3 to port 1 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(3, 1, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(3, 1, "y")

    @property
    def abcd24x(self):
        """Numeric ABCD matrix from port 2 to port 4 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(2, 4, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 4, "x")

    @property
    def abcd24y(self):
        """Numeric ABCD matrix from port 2 to port 4 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(2, 4, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 4, "y")

    @property
    def abcd42x(self):
        """Numeric ABCD matrix from port 4 to port 2 in the tangential plane.

        Equivalent to ``beamsplitter.ABCD(4, 2, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(4, 2, "x")

    @property
    def abcd42y(self):
        """Numeric ABCD matrix from port 4 to port 2 in the sagittal plane.

        Equivalent to ``beamsplitter.ABCD(4, 2, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(4, 2, "y")

    def ABCD(
        self,
        from_node,
        to_node,
        direction="x",
        symbolic=False,
        copy=True,
        retboth=False,
    ):
        r"""Returns the ABCD matrix of the beam splitter for the specified coupling.

        The matrices for transmission and reflection are different for
        the sagittal and tangential planes (:math:`M_s` and :math:`M_t`),
        as shown below.

        .. rubric:: Transmission

        .. _fig_abcd_bs_transmission:
        .. figure:: ../images/abcd_bst.*
            :align: center

        For the tangential plane (`direction = 'x'`),

        .. math::
            M_t = \begin{pmatrix}
                        \frac{\cos{\alpha_2}}{\cos{\alpha_1}} & 0 \\
                        \frac{\Delta n}{R_c} & \frac{\cos{\alpha_1}}{\cos{\alpha_2}}
                    \end{pmatrix},

        and for the sagittal plane (`direction = 'y'`),

        .. math::
            M_s = \begin{pmatrix}
                        1 & 0 \\
                        \frac{\Delta n}{R_c} & 1
                    \end{pmatrix},

        where :math:`\alpha_1` is the angle of incidence of the beam splitter and
        :math:`\alpha_2` is given by Snell's law (:math:`n_1\sin{\alpha_1} =
        n_2\sin{\alpha_2}`). The quantity :math:`\Delta n` is given by,

        .. math::
            \Delta_n = \frac{n_2 \cos{\alpha_2} - n_1 \cos{\alpha_1}}{
                \cos{\alpha_1} \cos{\alpha_2}
                }.

        If the direction of propagation is reversed such that the radius of curvature
        of the beam splitter is in this direction, then the elements :math:`A` and
        :math:`D` of the tangential matrix (:math:`M_t`) are swapped.

        .. rubric:: Reflection

        .. _fig_abcd_bs_reflection:
        .. figure:: ../images/abcd_bsr.*
            :align: center

        The reflection at the front surface of the beam splitter is given by,

        .. math::
            M_t = \begin{pmatrix}
                        1 & 0 \\
                        -\frac{2n_1}{R_c \cos{\alpha_1}} & 1
                    \end{pmatrix},

        for the tangential plane, and,

        .. math::
            M_s = \begin{pmatrix}
                        1 & 0 \\
                        -\frac{2n_1 \cos{\alpha_2}}{R_c} & 1
                    \end{pmatrix},

        for the sagittal plane.

        At the back surface :math:`R_c \rightarrow - R_c` and
        :math:`\alpha_1 \rightarrow - \alpha_2`.

        See :meth:`.Connector.ABCD` for descriptions of parameters, return values and possible
        exceptions.

        Raises
        ------
        tre : :class:`.TotalReflectionError`
            If total reflection occurs for the specified coupling - i.e. if :math:`\sin{\alpha_2} > 1.0`.
        """
        return super().ABCD(from_node, to_node, direction, symbolic, copy, retboth)

    def _get_workspace(self, sim):
        from finesse.components.modal.beamsplitter import (
            beamsplitter_carrier_fill,
            beamsplitter_signal_fill,
            beamsplitter_fill_qnoise,
            BeamsplitterWorkspace,
        )

        _, is_changing = self._eval_parameters()

        carrier_refill = (
            sim.is_component_in_mismatch_couplings(self)
            or self in sim.trace_forest
            or sim.carrier.any_frequencies_changing
            or (len(is_changing) and is_changing.issubset(self.__changing_check))
        )

        ws = BeamsplitterWorkspace(self, sim)
        ws.carrier.add_fill_function(beamsplitter_carrier_fill, carrier_refill)

        if sim.signal:
            signal_refill = sim.model.fsig.f.is_changing
            ws.signal.add_fill_function(
                beamsplitter_signal_fill, carrier_refill or signal_refill
            )

        # Initialise the ABCD matrix memory-views
        if sim.is_modal:
            try:
                ws.abcd_p1p2_x = self.ABCD(self.p1.i, self.p2.o, "x", copy=False)
                ws.abcd_p1p2_y = self.ABCD(self.p1.i, self.p2.o, "y", copy=False)
            except TotalReflectionError:
                raise

            try:
                ws.abcd_p2p1_x = self.ABCD(self.p2.i, self.p1.o, "x", copy=False)
                ws.abcd_p2p1_y = self.ABCD(self.p2.i, self.p1.o, "y", copy=False)
            except TotalReflectionError:
                raise

            try:
                ws.abcd_p3p4_x = self.ABCD(self.p3.i, self.p4.o, "x", copy=False)
                ws.abcd_p3p4_y = self.ABCD(self.p3.i, self.p4.o, "y", copy=False)
            except TotalReflectionError:
                raise

            try:
                ws.abcd_p4p3_x = self.ABCD(self.p4.i, self.p3.o, "x", copy=False)
                ws.abcd_p4p3_y = self.ABCD(self.p4.i, self.p3.o, "y", copy=False)
            except TotalReflectionError:
                raise

            ws.abcd_p1p3_x = self.ABCD(self.p1.i, self.p3.o, "x", copy=False)
            ws.abcd_p1p3_y = self.ABCD(self.p1.i, self.p3.o, "y", copy=False)
            ws.abcd_p3p1_x = self.ABCD(self.p3.i, self.p1.o, "x", copy=False)
            ws.abcd_p3p1_y = self.ABCD(self.p3.i, self.p1.o, "y", copy=False)
            ws.abcd_p2p4_x = self.ABCD(self.p2.i, self.p4.o, "x", copy=False)
            ws.abcd_p2p4_y = self.ABCD(self.p2.i, self.p4.o, "y", copy=False)
            ws.abcd_p4p2_x = self.ABCD(self.p4.i, self.p2.o, "x", copy=False)
            ws.abcd_p4p2_y = self.ABCD(self.p4.i, self.p2.o, "y", copy=False)

            alpha2 = np.arcsin((ws.nr1 / ws.nr2) * np.sin(np.deg2rad(self.alpha.value)))
            cos_alpha = np.cos(np.deg2rad(self.alpha.value))
            cos_alpha2 = np.cos(alpha2)

            ws.set_knm_info(
                "P1i_P2o",
                alpha=self.alpha,
                is_transmission=False,
                nr_from=ws.nr1,
                nr_to=ws.nr1,
                beta_x=self.xbeta,
                beta_x_factor=2,
                beta_y=self.ybeta,
                beta_y_factor=-2 * cos_alpha,
                abcd_x=ws.abcd_p1p2_x,
                abcd_y=ws.abcd_p1p2_y,
            )
            ws.set_knm_info(
                "P2i_P1o",
                alpha=self.alpha,
                is_transmission=False,
                nr_from=ws.nr1,
                nr_to=ws.nr1,
                beta_x=self.xbeta,
                beta_x_factor=2,
                beta_y=self.ybeta,
                beta_y_factor=-2 * cos_alpha,
                abcd_x=ws.abcd_p2p1_x,
                abcd_y=ws.abcd_p2p1_y,
            )
            ws.set_knm_info(
                "P3i_P4o",
                alpha=self.alpha,
                is_transmission=False,
                nr_from=ws.nr2,
                nr_to=ws.nr2,
                beta_x=self.xbeta,
                beta_x_factor=2,
                beta_y=self.ybeta,
                beta_y_factor=2 * cos_alpha2,
                abcd_x=ws.abcd_p3p4_x,
                abcd_y=ws.abcd_p3p4_y,
            )
            ws.set_knm_info(
                "P4i_P3o",
                alpha=self.alpha,
                is_transmission=False,
                nr_from=ws.nr2,
                nr_to=ws.nr2,
                beta_x=self.xbeta,
                beta_x_factor=2,
                beta_y=self.ybeta,
                beta_y_factor=2 * cos_alpha2,
                abcd_x=ws.abcd_p4p3_x,
                abcd_y=ws.abcd_p4p3_y,
            )
            ws.set_knm_info(
                "P1i_P3o",
                alpha=self.alpha,
                is_transmission=True,
                nr_from=ws.nr1,
                nr_to=ws.nr2,
                beta_x=self.xbeta,
                beta_x_factor=-(1 - ws.nr1 / ws.nr2),
                beta_y=self.ybeta,
                beta_y_factor=(1 - ws.nr1 / ws.nr2),
                abcd_x=ws.abcd_p1p3_x,
                abcd_y=ws.abcd_p1p3_y,
            )
            ws.set_knm_info(
                "P3i_P1o",
                alpha=self.alpha,
                is_transmission=True,
                nr_from=ws.nr2,
                nr_to=ws.nr1,
                beta_x=self.xbeta,
                beta_x_factor=-(1 - ws.nr2 / ws.nr1),
                beta_y=self.ybeta,
                beta_y_factor=-(1 - ws.nr2 / ws.nr1),
                abcd_x=ws.abcd_p3p1_x,
                abcd_y=ws.abcd_p3p1_y,
            )
            ws.set_knm_info(
                "P2i_P4o",
                alpha=self.alpha,
                is_transmission=True,
                nr_from=ws.nr1,
                nr_to=ws.nr2,
                beta_x=self.xbeta,
                beta_x_factor=-(1 - ws.nr1 / ws.nr2),
                beta_y=self.ybeta,
                beta_y_factor=(1 - ws.nr1 / ws.nr2),
                abcd_x=ws.abcd_p2p4_x,
                abcd_y=ws.abcd_p2p4_y,
            )
            ws.set_knm_info(
                "P4i_P2o",
                alpha=self.alpha,
                is_transmission=True,
                nr_from=ws.nr2,
                nr_to=ws.nr1,
                beta_x=self.xbeta,
                beta_x_factor=-(1 - ws.nr2 / ws.nr1),
                beta_y=self.ybeta,
                beta_y_factor=-(1 - ws.nr2 / ws.nr1),
                abcd_x=ws.abcd_p4p2_x,
                abcd_y=ws.abcd_p4p2_y,
            )

        if sim.signal:
            ws.signal.set_fill_noise_function(
                NoiseType.QUANTUM, beamsplitter_fill_qnoise
            )
        return ws
