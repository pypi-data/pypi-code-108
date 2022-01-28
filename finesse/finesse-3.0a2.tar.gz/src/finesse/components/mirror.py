"""Dielectric interface type components representing physical mirrors."""

import logging
import types

import numpy as np

from finesse.parameter import float_parameter, bool_parameter
from finesse.utilities import refractive_index

from finesse.components.general import InteractionType, NoiseType, DOFDefinition
from finesse.components.surface import Surface
from finesse.components.node import NodeDirection, NodeType

LOGGER = logging.getLogger(__name__)


@float_parameter("R", "Reflectivity", validate="_check_R", setter="set_RTL")
@float_parameter("T", "Transmission", validate="_check_T", setter="set_RTL")
@float_parameter("L", "Loss", validate="_check_L", setter="set_RTL")
@float_parameter(
    "phi", "Microscopic tuning (360 degrees = 1 default wavelength)", units="degrees"
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
@bool_parameter("misaligned", "Misaligns mirror reflection (R=0 when True)")
class Mirror(Surface):
    """The mirror component represents a thin dielectric surface with associated
    properties such as reflectivity, tuning, and radius of curvature. It has two optical
    ports `p1` and `p2` which decsribe the two beams incident on either side of this
    surface. It also has a mechanical port `mech` which has nodes for longitudinal, yaw,
    and pitch motions. These mechanical nodes are purely for exciting small signal
    oscillations of the mirror. Static offsets in longitudinal displacements are set by
    the `phi` parameter (in units of degrees), yaw by the `xbeta` parameter, and pitch
    the `ybeta` parameter.

    Parameters
    ----------
    name : str
        Name of newly created mirror.

    R : float, optional
        Reflectivity of the mirror; defaults to 0.5.

    T : float, optional
        Transmittance of the mirror; defaults to 0.5.

    L : float, optional
        Loss of the mirror; defaults to 0.0.

    phi : float, optional
        Tuning of the mirror (in degrees); defaults to 0.0.

    Rc : float or container of two floats, optional
        The radius of curvature of the mirror (in metres); defaults to a flat mirror (`Rc=np.inf`).
        Astigmatic mirrors can also be set with `Rc=(Rcx, Rcy)`.

    xbeta, ybeta : float, optional
        Misalignment of the mirror in yaw and pitch in units of radians

    misaligned : bool, optional
        When True the mirror will be significantly misaligned and
        assumes any reflected beam is dumped. Transmissions will
        still occur.

    Attributes
    ----------
    Attributes are set via the Python API and not available via KatScript.

    surface_map : :class:`finesse.knm.Map`
        Decsribes the surface distortion of this mirror component.
        Coordinate system to the map is right-handed with the postive-z
        direction as the surface normal on the port 1 side of the mirror.
    """

    def __init__(
        self,
        name,
        R=None,
        T=None,
        L=None,
        phi=0,
        Rc=np.inf,
        xbeta=0,
        ybeta=0,
        misaligned=False,
    ):
        super().__init__(name, R, T, L, phi, Rc, xbeta, ybeta)
        self.misaligned = misaligned

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p2", NodeType.OPTICAL)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        # Optic to optic couplings
        self._register_node_coupling(
            "P1i_P1o",
            self.p1.i,
            self.p1.o,
            interaction_type=InteractionType.REFLECTION,
            # enabled_check=lambda: self.R > 0 and not self.R.is_changing
        )
        self._register_node_coupling(
            "P2i_P2o",
            self.p2.i,
            self.p2.o,
            interaction_type=InteractionType.REFLECTION,
            # enabled_check=lambda: self.R > 0 and not self.R.is_changing
        )
        self._register_node_coupling(
            "P1i_P2o",
            self.p1.i,
            self.p2.o,
            interaction_type=InteractionType.TRANSMISSION,
            # enabled_check=lambda: self.T > 0 and not self.T.is_changing
        )
        self._register_node_coupling(
            "P2i_P1o",
            self.p2.i,
            self.p1.o,
            interaction_type=InteractionType.TRANSMISSION,
            # enabled_check=lambda: self.T > 0 and not self.T.is_changing
        )

        # Mirror motion couplings
        self._add_port("mech", NodeType.MECHANICAL)
        self.mech._add_node("z", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("yaw", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("pitch", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("F_z", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("F_yaw", NodeDirection.BIDIRECTIONAL)
        self.mech._add_node("F_pitch", NodeDirection.BIDIRECTIONAL)

        # Optic to motion couplings
        self._register_node_coupling("P1i_Fz", self.p1.i, self.mech.F_z)
        self._register_node_coupling("P2i_Fz", self.p2.i, self.mech.F_z)
        self._register_node_coupling("P1o_Fz", self.p1.o, self.mech.F_z)
        self._register_node_coupling("P2o_Fz", self.p2.o, self.mech.F_z)
        self._register_node_coupling("P1i_Fyaw", self.p1.i, self.mech.F_yaw)
        self._register_node_coupling("P2i_Fyaw", self.p2.i, self.mech.F_yaw)
        self._register_node_coupling("P1o_Fyaw", self.p1.o, self.mech.F_yaw)
        self._register_node_coupling("P2o_Fyaw", self.p2.o, self.mech.F_yaw)
        self._register_node_coupling("P1i_Fpitch", self.p1.i, self.mech.F_pitch)
        self._register_node_coupling("P2i_Fpitch", self.p2.i, self.mech.F_pitch)
        self._register_node_coupling("P1o_Fpitch", self.p1.o, self.mech.F_pitch)
        self._register_node_coupling("P2o_Fpitch", self.p2.o, self.mech.F_pitch)

        # motion to optic coupling: phase coupling on reflection
        self._register_node_coupling("Z_P1o", self.mech.z, self.p1.o)
        self._register_node_coupling("Z_P2o", self.mech.z, self.p2.o)
        self._register_node_coupling("yaw_P1o", self.mech.yaw, self.p1.o)
        self._register_node_coupling("yaw_P2o", self.mech.yaw, self.p2.o)
        self._register_node_coupling("pitch_P1o", self.mech.pitch, self.p1.o)
        self._register_node_coupling("pitch_P2o", self.mech.pitch, self.p2.o)

        self.__changing_check = set(
            (self.R, self.T, self.L, self.phi, self.xbeta, self.ybeta)
        )

        self.surface_map = None

        # Define typical degrees of freedom for this component
        self.dofs = types.SimpleNamespace()
        self.dofs.z = DOFDefinition(f"{self.name}.dofs.z", self.phi, self.mech.z, 1)
        self.dofs.yaw = DOFDefinition(
            f"{self.name}.dofs.yaw", self.xbeta, self.mech.yaw, 1
        )
        self.dofs.pitch = DOFDefinition(
            f"{self.name}.dofs.pitch", self.ybeta, self.mech.pitch, 1
        )

    def _resymbolise_ABCDs(self):
        # -> reflections
        self.__symbolise_ABCD(self.p1.i, self.p1.o, "x")
        self.__symbolise_ABCD(self.p1.i, self.p1.o, "y")
        self.__symbolise_ABCD(self.p2.i, self.p2.o, "x")
        self.__symbolise_ABCD(self.p2.i, self.p2.o, "y")
        # -> transmissions
        self.__symbolise_ABCD(self.p1.i, self.p2.o, "x")
        self.__symbolise_ABCD(self.p1.i, self.p2.o, "y")
        self.__symbolise_ABCD(self.p2.i, self.p1.o, "x")
        self.__symbolise_ABCD(self.p2.i, self.p1.o, "y")

    def __symbolise_ABCD(self, from_node, to_node, direction):
        if direction == "x":
            Rc = self.Rcx.ref
        else:
            Rc = self.Rcy.ref

        # reflection
        if self.interaction_type(from_node, to_node) == InteractionType.REFLECTION:
            nr = refractive_index(from_node, symbolic=True)

            C = 2 * nr / Rc
            if from_node.port is self.p1:
                C *= -1

        # transmission
        else:
            nr1 = refractive_index(from_node, symbolic=True)
            nr2 = refractive_index(to_node, symbolic=True)

            C = (nr2 - nr1) / Rc
            if from_node.port is not self.p1:
                C *= -1

        M_sym = np.array([[1.0, 0.0], [C, 1.0]])

        key = (from_node, to_node, direction)
        # For mirrors the symbol nr can change when connected up to spaces
        # in a model so here we update the ABCD matrix entry
        if key in self._abcd_matrices:
            self._abcd_matrices[key] = M_sym, np.array(M_sym, dtype=np.float64)
        # Otherwise just register the new ABCD matrix as usual
        else:
            self.register_abcd_matrix(M_sym, (from_node, to_node, direction))

    @property
    def abcd11x(self):
        """Numeric ABCD matrix from port 1 to port 1 in the tangential plane.

        Equivalent to ``mirror.ABCD(1, 1, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 1, "x")

    @property
    def abcd11y(self):
        """Numeric ABCD matrix from port 1 to port 1 in the sagittal plane.

        Equivalent to ``mirror.ABCD(1, 1, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 1, "y")

    @property
    def abcd22x(self):
        """Numeric ABCD matrix from port 2 to port 2 in the tangential plane.

        Equivalent to ``mirror.ABCD(2, 2, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 2, "x")

    @property
    def abcd22y(self):
        """Numeric ABCD matrix from port 2 to port 2 in the sagittal plane.

        Equivalent to ``mirror.ABCD(2, 2, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 2, "y")

    @property
    def abcd12x(self):
        """Numeric ABCD matrix from port 1 to port 2 in the tangential plane.

        Equivalent to ``mirror.ABCD(1, 2, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 2, "x")

    @property
    def abcd12y(self):
        """Numeric ABCD matrix from port 1 to port 2 in the sagittal plane.

        Equivalent to ``mirror.ABCD(1, 2, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 2, "y")

    @property
    def abcd21x(self):
        """Numeric ABCD matrix from port 2 to port 1 in the tangential plane.

        Equivalent to ``mirror.ABCD(2, 1, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 1, "x")

    @property
    def abcd21y(self):
        """Numeric ABCD matrix from port 2 to port 1 in the sagittal plane.

        Equivalent to ``mirror.ABCD(2, 1, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(2, 1, "y")

    def ABCD(
        self,
        from_node,
        to_node,
        direction="x",
        symbolic=False,
        copy=True,
        retboth=False,
    ):
        r"""Returns the ABCD matrix of the mirror for the specified coupling.

        In both cases below, the sign of the radius is defined such that :math:`R_c`
        is negative if the centre of the sphere is located in the direction of propagation.

        .. rubric:: Transmission

        .. _fig_abcd_mirror_transmission:
        .. figure:: ../images/abcd_mi.*
            :align: center

        For transmission this is given by,

        .. math::
            M_{t} = \begin{pmatrix}
                        1 & 0 \\
                        \frac{n_2 - n_1}{R_c} & 1
                    \end{pmatrix},

        where :math:`n_2` and :math:`n_1` are the indices of refraction of the spaces
        connected to the mirror and :math:`R_c` is the radius of curvature of the mirror.

        The matrix for transmission in the opposite direction of propagation is identical.

        .. rubric:: Reflection

        .. _fig_abcd_mirror_reflection:
        .. figure:: ../images/abcd_mr.*
            :align: center

        In the case of reflection the matrix is,

        .. math::
            M_{r} = \begin{pmatrix}
                        1 & 0 \\
                        -\frac{2n_1}{R_c} & 1
                    \end{pmatrix}.

        Reflection at the back surface can be described by the same type of matrix by setting
        the :math:`C` element to :math:`C = 2n_2/R_c`.

        See :meth:`.Connector.ABCD` for descriptions of parameters, return values and possible
        exceptions.
        """
        return super().ABCD(from_node, to_node, direction, symbolic, copy, retboth)

    def _get_workspace(self, sim):
        """Returns a workspace to use in a simulation."""
        from finesse.simulations.basematrix import CarrierSignalMatrixSimulation

        if isinstance(sim, CarrierSignalMatrixSimulation):
            from finesse.components.modal.mirror import (
                mirror_carrier_fill,
                mirror_signal_opt_fill,
                mirror_signal_mech_fill,
                mirror_fill_qnoise,
                MirrorWorkspace,
            )

            _, is_changing = self._eval_parameters()

            carrier_refill = (
                sim.is_component_in_mismatch_couplings(self)
                or self in sim.trace_forest
                or sim.carrier.any_frequencies_changing
                or len(is_changing)
            )
            ws = MirrorWorkspace(self, sim)
            # This assumes that nr1/nr2 cannot change during a simulation
            ws.nr1 = refractive_index(self.p1)
            ws.nr2 = refractive_index(self.p2)

            ws.carrier.add_fill_function(mirror_carrier_fill, carrier_refill)

            if sim.signal:
                signal_refill = carrier_refill or (
                    sim.model.fsig.f.is_changing
                    and not (self.phi.value == 0 and self.phi.is_changing)
                )
                ws.signal.add_fill_function(mirror_signal_opt_fill, signal_refill)

                signal_refill = carrier_refill or (sim.model.fsig.f.is_changing)
                ws.signal.add_fill_function(mirror_signal_mech_fill, signal_refill)

            # Initialise the ABCD matrix memory-views
            if sim.is_modal:
                ws.abcd_p1p1_x = self.ABCD(self.p1.i, self.p1.o, "x", copy=False)
                ws.abcd_p1p1_y = self.ABCD(self.p1.i, self.p1.o, "y", copy=False)
                ws.abcd_p2p2_x = self.ABCD(self.p2.i, self.p2.o, "x", copy=False)
                ws.abcd_p2p2_y = self.ABCD(self.p2.i, self.p2.o, "y", copy=False)

                ws.abcd_p1p2_x = self.ABCD(self.p1.i, self.p2.o, "x", copy=False)
                ws.abcd_p1p2_y = self.ABCD(self.p1.i, self.p2.o, "y", copy=False)
                ws.abcd_p2p1_x = self.ABCD(self.p2.i, self.p1.o, "x", copy=False)
                ws.abcd_p2p1_y = self.ABCD(self.p2.i, self.p1.o, "y", copy=False)

                ws.set_knm_info(
                    "P1i_P1o",
                    abcd_x=ws.abcd_p1p1_x,
                    abcd_y=ws.abcd_p1p1_y,
                    nr_from=ws.nr1,
                    nr_to=ws.nr1,
                    is_transmission=False,
                    beta_x=self.xbeta,
                    beta_x_factor=2,
                    beta_y=self.ybeta,
                    beta_y_factor=-2,
                    apply_map=self.surface_map,
                    map_phase_factor=-2 * ws.nr1,
                    map_fliplr=False,
                )
                ws.set_knm_info(
                    "P2i_P2o",
                    abcd_x=ws.abcd_p2p2_x,
                    abcd_y=ws.abcd_p2p2_y,
                    nr_from=ws.nr2,
                    nr_to=ws.nr2,
                    is_transmission=False,
                    beta_x=self.xbeta,
                    beta_x_factor=2,
                    beta_y=self.ybeta,
                    beta_y_factor=2,
                    apply_map=self.surface_map,
                    map_phase_factor=2 * ws.nr2,
                    map_fliplr=True,
                )
                ws.set_knm_info(
                    "P1i_P2o",
                    abcd_x=ws.abcd_p1p2_x,
                    abcd_y=ws.abcd_p1p2_y,
                    nr_from=ws.nr1,
                    nr_to=ws.nr2,
                    is_transmission=True,
                    beta_x=self.xbeta,
                    beta_x_factor=-(1 - ws.nr1 / ws.nr2),
                    beta_y=self.ybeta,
                    beta_y_factor=(1 - ws.nr1 / ws.nr2),
                    apply_map=self.surface_map,
                    map_phase_factor=(ws.nr2 - ws.nr1),
                    map_fliplr=False,
                )
                ws.set_knm_info(
                    "P2i_P1o",
                    abcd_x=ws.abcd_p2p1_x,
                    abcd_y=ws.abcd_p2p1_y,
                    nr_from=ws.nr2,
                    nr_to=ws.nr1,
                    is_transmission=True,
                    beta_x=self.xbeta,
                    beta_x_factor=-(1 - ws.nr2 / ws.nr1),
                    beta_y=self.ybeta,
                    beta_y_factor=-(1 - ws.nr2 / ws.nr1),
                    apply_map=self.surface_map,
                    map_phase_factor=-(ws.nr1 - ws.nr2),
                    map_fliplr=True,
                )

            if sim.signal:
                ws.signal.set_fill_noise_function(NoiseType.QUANTUM, mirror_fill_qnoise)
            return ws
