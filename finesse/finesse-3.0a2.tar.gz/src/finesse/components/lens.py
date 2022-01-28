"""Transmissive optical components which focus or disperse light beams."""

import logging

import numpy as np

from finesse.components.general import Connector, InteractionType
from finesse.components.node import NodeDirection, NodeType
from finesse.parameter import float_parameter
from finesse.utilities import refractive_index

LOGGER = logging.getLogger(__name__)


@float_parameter(
    "f",
    "Focal length",
    validate="_check_f",
    units="m",
    is_geometric=True,
)
class Lens(Connector):
    """Represents a thin lens optical component with an associated focal length.

    Notes
    -----
    The specified focal length `f` is only accurate when the lens is attached to spaces with index
    of refraction close to 1. This component exists so that one can use the intuitive focal length
    parameter instead of having to set radii of curvature as with e.g. :class:`.Mirror`.

    Parameters
    ----------
    name : str
        Name of newly created lens.

    f : float, optional
        Focal length of the lens in metres; defaults to infinity.

    Attributes
    ----------
    OPD_map : :class:`finesse.knm.Map`
        A map that is used to describe the transverse spatial amplitude and phase
        variations beyond a simple lensing. Typically the map applied is describing
        the dnr/dT temperature effects in some substrate.
    """

    def __init__(self, name, f=np.inf):
        super().__init__(name)

        self.f = f
        self.OPD_map = None

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p2", NodeType.OPTICAL)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        # optic to optic couplings
        self._register_node_coupling(
            "P1i_P2o",
            self.p1.i,
            self.p2.o,
            interaction_type=InteractionType.TRANSMISSION,
        )
        self._register_node_coupling(
            "P2i_P1o",
            self.p2.i,
            self.p1.o,
            interaction_type=InteractionType.TRANSMISSION,
        )

    def _check_f(self, value):
        if value == 0:
            raise ValueError("Focal length of lens must be non-zero.")

        return value

    def _resymbolise_ABCDs(self):
        self.__symbolise_ABCDs("x")
        self.__symbolise_ABCDs("y")

    def __symbolise_ABCDs(self, direction):
        # TODO (sjr) Not using direction currently but will split
        #            into fx, fy soon to support astigmatic lenses
        M_sym = np.array([[1.0, 0.0], [-1.0 / self.f.ref, 1.0]])

        # Matrices same for both node couplings
        self.register_abcd_matrix(
            M_sym,
            (self.p1.i, self.p2.o, direction),
            (self.p2.i, self.p1.o, direction),
        )

    @property
    def abcdx(self):
        """Numeric ABCD matrix in the tangential plane.

        Equivalent to ``lens.ABCD(1, 2, "x")`` and ``lens.ABCD(2, 1, "x")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 2, "x")

    @property
    def abcdy(self):
        """Numeric ABCD matrix in the sagittal plane.

        Equivalent to ``lens.ABCD(2, 1, "y")`` and ``lens.ABCD(2, 1, "y")``.

        :getter: Returns a copy of the (numeric) ABCD matrix for this coupling (read-only).
        """
        return self.ABCD(1, 2, "y")

    def ABCD(
        self,
        from_node,
        to_node,
        direction="x",
        symbolic=False,
        copy=True,
        retboth=False,
    ):
        r"""Returns the ABCD matrix of the lens for the specified coupling.

        .. _fig_abcd_lens_transmission:
        .. figure:: ../images/abcd_lenst.*
            :align: center

        This is given by,

        .. math::
            M = \begin{pmatrix}
                    1 & 0 \\
                    -\frac{1}{f} & 1
                \end{pmatrix},

        where :math:`f` is the focal length of the lens.

        See :meth:`.Connector.ABCD` for descriptions of parameters, return values and possible
        exceptions.
        """
        return super().ABCD(from_node, to_node, direction, symbolic, copy, retboth)

    def actuate_f(self, dioptres, direction=("x", "y")):
        r"""Actuate on the focal length of the lens with a
        specified dioptre shift.

        Sets the focal length to a new value, :math:`f_2`, via,

        .. math::

            f_2 = \frac{1}{d + \frac{1}{f_1}},

        where :math:`f_1` is the current focal length and :math:`d` is the dioptre shift (i.e.
        the `dioptre` argument).

        By default, both focal planes are shifted. To shift, e.g., only the
        tangential plane, specify ``direction="x"``.

        Parameters
        ----------
        dioptres : float
            Shift in lens focal length in dioptres.

        direction : tuple or str, optional; default: ("x", "y")
            Focal plane to shift, defaults to both tangential and sagittal.
        """
        fnew = lambda x: 1 / (dioptres + 1 / x)
        if "x" in direction:  # TODO (sjr) Change to fx
            self.f = fnew(self.f.value)
        if "y" in direction:  # TODO (sjr) Change to fy
            self.f = fnew(self.f.value)

    def _fill_optical_matrix(self, ws, matrix, connections):
        for freq in matrix.optical_frequencies.frequencies:
            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P1i_P2o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.K12.data

            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P2i_P1o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.K21.data

    def _fill_carrier(self, ws):
        self._fill_optical_matrix(ws, ws.sim.carrier, ws.carrier.connections)

    def _fill_signal(self, ws):
        self._fill_optical_matrix(ws, ws.sim.signal, ws.signal.connections)

    def _get_workspace(self, sim):
        from finesse.simulations.basematrix import CarrierSignalMatrixSimulation

        if isinstance(sim, CarrierSignalMatrixSimulation):
            from finesse.components.modal.lens import LensWorkspace

            _, is_changing = self._eval_parameters()
            refill = sim.is_component_in_mismatch_couplings(self) or len(is_changing)

            ws = LensWorkspace(self, sim)
            # This assumes that nr1/nr2 cannot change during a simulation
            ws.nr1 = refractive_index(self.p1)
            ws.nr2 = refractive_index(self.p2)
            # TODO ddb refractive index should be equal on
            # both sides of the lens as we are using the thin
            # lens approximation
            assert ws.nr1 == ws.nr2

            ws.carrier.add_fill_function(self._fill_carrier, refill)
            ws.signal.add_fill_function(self._fill_signal, refill)

            if sim.is_modal:
                ws.abcd_x = self.ABCD(self.p1.i, self.p2.o, "x", copy=False)
                ws.abcd_y = self.ABCD(self.p1.i, self.p2.o, "y", copy=False)

                # Set the coupling matrix information
                # ABCDs are same in each direction
                ws.set_knm_info(
                    "P1i_P2o",
                    abcd_x=ws.abcd_x,
                    abcd_y=ws.abcd_y,
                    nr_from=ws.nr1,
                    nr_to=ws.nr2,
                    is_transmission=True,
                    apply_map=self.OPD_map,
                    map_phase_factor=1,
                    map_fliplr=False,
                )
                # TODO nr reversed here for now until it's forced to be same on both sides
                ws.set_knm_info(
                    "P2i_P1o",
                    abcd_x=ws.abcd_x,
                    abcd_y=ws.abcd_y,
                    nr_from=ws.nr2,
                    nr_to=ws.nr1,
                    is_transmission=True,
                    apply_map=self.OPD_map,
                    map_phase_factor=1,
                    map_fliplr=False,
                )

            return ws
        else:
            raise Exception(f"Lens does not handle a simulation of type {sim}")
