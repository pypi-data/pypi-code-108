"""Laser-type optical components for producing beams."""

import logging
import warnings
import math
import types

import numpy as np

from .general import Connector, FrequencyGenerator, NoiseType, DOFDefinition
from .node import NodeType, NodeDirection

from ..cymath.complex import crotate
from ..parameter import float_parameter, bool_parameter

LOGGER = logging.getLogger(__name__)


@float_parameter("P", "Power", units="W")
@float_parameter("phase", "Phase", units="degrees")
@float_parameter("f", "Frequency", units="Hz")
@bool_parameter("signals_only", "Signals only", changeable_during_simulation=False)
class Laser(Connector, FrequencyGenerator):
    """Represents a laser producing a beam with associated properties such as power and
    frequency.

    Parameters
    ----------
    name : str
        Name of the newly created laser.

    P : float, optional
        Power of the laser (in Watts), defaults to 1 W.

    f : float or :class:`.Frequency`, optional
        Frequency-offset of the laser from the default (in Hz) or :class:`.Frequency`
        object. Defaults to 0 Hz offset.

    phase : float, optional
        Phase-offset of the laser from the default, defaults to zero.

    signals_only : bool, optional
        When True, this laser component will only inject signal sidebands. They will use
        the current carrier value as a scaling terms but the carrier will not be
        injected into the simulation. This allows a user to just inject signal sidebands
        into a model.

    Attributes
    ----------
    add_gouy_phase : bool
        When set to True the gouy phase of the current beam parameters values at the
        laser will be added to the optical field outputs during the simulation. When
        False, it will not. This can be used with :meth:`.set_output_field` to force a
        particular optical field output from a laser.
    """

    DEFAULT_POWER_COEFFS = {(0, 0): (1.0, 0.0)}

    def __init__(self, name, P=1, f=0, phase=0, signals_only=False):
        Connector.__init__(self, name)
        FrequencyGenerator.__init__(self)

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        # Modulation inputs
        self._add_port("amp", NodeType.ELECTRICAL)
        self.amp._add_node("i", NodeDirection.INPUT)
        self._add_port("phs", NodeType.ELECTRICAL)
        self.phs._add_node("i", NodeDirection.INPUT)
        self._add_port("frq", NodeType.ELECTRICAL)
        self.frq._add_node("i", NodeDirection.INPUT)
        self._add_port("dx", NodeType.ELECTRICAL)
        self.dx._add_node("i", NodeDirection.INPUT)
        self._add_port("dy", NodeType.ELECTRICAL)
        self.dy._add_node("i", NodeDirection.INPUT)
        self._add_port("yaw", NodeType.ELECTRICAL)
        self.yaw._add_node("i", NodeDirection.INPUT)
        self._add_port("pitch", NodeType.ELECTRICAL)
        self.pitch._add_node("i", NodeDirection.INPUT)

        self._register_node_coupling("SIGAMP_P1o", self.amp.i, self.p1.o)
        self._register_node_coupling("SIGPHS_P1o", self.phs.i, self.p1.o)
        self._register_node_coupling("SIGFRQ_P1o", self.frq.i, self.p1.o)

        self._add_port("mech", NodeType.MECHANICAL)
        self.mech._add_node("z", NodeDirection.OUTPUT)
        self.mech._add_node("x", NodeDirection.OUTPUT)
        self.mech._add_node("y", NodeDirection.OUTPUT)
        self.mech._add_node("yaw", NodeDirection.OUTPUT)
        self.mech._add_node("pitch", NodeDirection.OUTPUT)

        self._register_node_coupling("dz_P1o", self.mech.z, self.p1.o)
        self._register_node_coupling("dx_P1o", self.mech.x, self.p1.o)
        self._register_node_coupling("dy_P1o", self.mech.y, self.p1.o)
        self._register_node_coupling("xbeta_P1o", self.mech.yaw, self.p1.o)
        self._register_node_coupling("ybeta_P1o", self.mech.pitch, self.p1.o)

        self.f = f
        self.P = P
        self.phase = phase
        self.__power_coeffs = self.DEFAULT_POWER_COEFFS.copy()
        self.add_gouy_phase = True
        self.signals_only = bool(signals_only)

        # Define typical degrees of freedom for this component
        self.dofs = types.SimpleNamespace()
        self.dofs.amp = DOFDefinition(f"{self.name}.dofs.amp", self.P, self.amp.i, 1)
        self.dofs.phs = DOFDefinition(
            f"{self.name}.dofs.phs", self.phase, self.phs.i, 1
        )
        self.dofs.frq = DOFDefinition(f"{self.name}.dofs.frq", self.f, self.frq.i, 1)
        self.dofs.z = DOFDefinition(f"{self.name}.dofs.z", None, self.mech.z, 1)
        self.dofs.x = DOFDefinition(f"{self.name}.dofs.x", None, self.mech.x, 1)
        self.dofs.y = DOFDefinition(f"{self.name}.dofs.y", None, self.mech.y, 1)
        self.dofs.yaw = DOFDefinition(f"{self.name}.dofs.yaw", None, self.mech.yaw, 1)
        self.dofs.pitch = DOFDefinition(
            f"{self.name}.dofs.pitch", None, self.mech.pitch, 1
        )

    def _source_frequencies(self):
        return [self.f.ref]

    @property
    def power_coeffs(self):
        """The relative power factors and phase offsets for each HGnm mode.

        :getter: Returns the mode factors and phase offsets as a dict with the mode
                 indices as keys. Read-only.
        """
        return self.__power_coeffs.copy()

    def tem(self, n, m, factor, phase=0.0):
        """Distributes power into the mode HGnm.

        Parameters
        ----------
        n, m : int
            Mode indices.

        factor : float
            Relative power factor, modes with equal `factor` will
            have equivalent power distributed to them.

        phase : float, optional; default = 0.0
            Phase offset for the field, in degrees.

        Notes
        -----
        This does not change the total power of the laser, rather, it redistributes this
        power into / out of the specified mode.
        """
        self.__power_coeffs[(n, m)] = float(factor), float(phase)

    def __find_src_freq(self, sim):
        # If it's tunable we want to look for the symbol that is just this laser's
        # frequency, as it will be changing.
        for f in sim.optical_frequencies.frequencies:
            if not self.f.is_changing:
                # Don't match changing frequency bins if ours won't match.
                if not f.symbol.is_changing and (
                    f.f == self.f.value  # match potential param refs
                    or f.f == float(self.f.value)  # match numeric values
                ):
                    # If nothing is changing then we can just match freq values.
                    return f
            else:
                # If our frequency is changing then we have to have a frequency bin that
                # matches our symbol.
                if f.symbol == self.f.ref:
                    return f  # Simple case
        return None

    def _get_workspace(self, sim):
        from finesse.components.modal.laser import (
            laser_carrier_fill_rhs,
            laser_fill_signal,
            laser_fill_qnoise,
            LaserWorkspace,
            laser_set_gouy,
        )

        ws = LaserWorkspace(self, sim)
        ws.node_car_id = sim.carrier.node_id(self.p1.o)
        ws.fsrc_car_idx = -1

        ws.add_gouy_phase = bool(self.add_gouy_phase)
        ws.set_gouy_function(laser_set_gouy)
        # Carrier just fills RHS.
        ws.carrier.set_fill_rhs_fn(laser_carrier_fill_rhs)

        fsrc = self.__find_src_freq(sim.carrier)
        # Didn't find a Frequency bin for this laser in carrier simulation.
        if fsrc is None:
            raise Exception(f"Could not find a frequency bin at {self.f} for {self}")
        ws.fsrc_car_idx = fsrc.index

        if sim.is_modal:
            scaling = 0
            ws.power_coeffs = np.zeros(sim.model_settings.num_HOMs, dtype=np.complex128)
            coeffs = self.power_coeffs
            for i in range(sim.model_settings.num_HOMs):
                n = sim.model_settings.homs_view[i][0]
                m = sim.model_settings.homs_view[i][1]

                try:
                    factor, phase = coeffs.pop((n, m))
                except KeyError:
                    factor = phase = 0

                ws.power_coeffs[i] = crotate(
                    complex(math.sqrt(factor), 0), math.radians(phase)
                )
                scaling += abs(ws.power_coeffs[i]) ** 2

            if not scaling:
                raise RuntimeError(
                    f"No power in any modes of {self.name}! At least one mode must "
                    f"have a non-zero power factor applied to it."
                )

            for i in range(sim.model_settings.num_HOMs):
                ws.power_coeffs[i] /= np.sqrt(scaling)

            if coeffs:
                warnings.warn(
                    f"The following modes, included in the coeffs of "
                    f"{repr(self.name)}, are not being modelled and will be ignored: "
                    f"{list(coeffs.keys())}"
                )

        if sim.signal:
            ws.node_sig_id = sim.signal.node_id(self.p1.o)
            # Audio sim requies matrix filling
            # for signal couplings
            ws.signal.add_fill_function(
                laser_fill_signal, True
            )  # TODO sort out refill flag here
            ws.signal.set_fill_noise_function(NoiseType.QUANTUM, laser_fill_qnoise)
            # Find the sideband frequencies
            sb = tuple(
                (
                    f
                    for f in sim.signal.optical_frequencies.frequencies
                    if f.audio_carrier_index == fsrc.index
                )
            )
            if len(sb) != 2:
                raise Exception(
                    f"Only something other than two audio sidebands {sb} for carrier "
                    f"{fsrc}"
                )
            ws.fcar_sig_sb_idx = (sb[0].index, sb[1].index)

        # if sim.is_modal: self._update_tem_gouy_phases(sim)
        return ws

    def _couples_frequency(self, ws, connection, frequency_in, frequency_out):
        # The only connections we have are signal inputs to optical output
        # And all the inputs should generate any output.
        return True

    def set_output_field(self, E, homs):
        """Set optical field outputted using HOM vector.

        This changes the output power and mode content of the laser to match the
        requested ``E`` field.

        Parameters
        ----------
        E : sequence
            The complex optical field amplitude for `homs`.
        homs : sequence
            Sequence of (n, m) higher order modes. Typically this is just the
            ``model.homs`` value. It should match the size of ``E``.

        Notes
        -----
        If you do not want the gouy phase due to the current beam parameter values set
        at the laser to be added to the output, set the ``add_gouy_phase`` attribute of
        the laser element to ``False``.
        """
        E = np.asarray(E, dtype=complex)
        homs = np.array(homs, dtype=int)
        if homs.shape[1] != 2:
            raise ValueError("homs input should be a (N, 2) shape")
        if homs.shape[0] != E.shape[0]:
            raise ValueError("number of homs should match length of E field")
        if E.ndim != 1:
            raise ValueError("E field input is not a 1D array")

        self.power_coeffs.clear()
        self.P = sum(abs(E) ** 2)
        for (n, m), a in zip(homs, E):
            self.tem(n, m, abs(a) ** 2 / self.P.value, np.angle(a, deg=True))

    def get_output_field(self, homs):
        """Get optical field outputted as a HOM vector.

        Returns the complex amplitude of the modes specified in homs. This does not
        respect the `add_gouy_phase`` attribute of the laser element and will always
        return the complex amplitude without the gouy phase. If the gouy phase is
        required then it is recommended to use a FieldDetector at the laser output with
        ``add_gouy_phase`` set to ``True``.

        Parameters
        ----------
        homs : sequence
            Collection of (n, m) higher order modes to retrieve the output field for.
            Typically this is just the ``model.homs`` value. The output ``E`` vector
            will match the ordering of ``homs``.

        Returns
        -------
        sequence
            The output fields for `homs`. If a given (n, m) has no defined coefficients,
            its field defaults to 0.
        """
        E = np.zeros(len(homs), dtype=complex)
        total_power = self.P.value
        for i, (n, m) in enumerate(homs):
            power_frac, phase = self.power_coeffs.get((n, m), (0, 0))
            E[i] = np.sqrt(total_power * power_frac) * np.exp(1j * phase / 180 * np.pi)
        return E
