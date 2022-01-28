"""Squeezer-type optical components for producing squeezed light inputs."""
from finesse.parameter import float_parameter

from finesse.components.general import (
    Connector,
    FrequencyGenerator,
    NoiseGenerator,
    NoiseType,
)
from finesse.components.node import NodeType, NodeDirection


@float_parameter(
    "db",
    "Squeezing in amplitude dB (6dB is factor of 2 reduction in noise)",
    units="dB",
)
@float_parameter("f", "Frequency to squeeze at", units="Hz")
@float_parameter("angle", "Squeezing angle", units="degrees")
class Squeezer(Connector, FrequencyGenerator, NoiseGenerator):
    """Represents a squeezer producing a squeezed-light beam with a given squeezing in
    decibels and angle.

    Parameters
    ----------
    name : str
        Name of the newly created squeezer.

    db : float
        Squeezing factor (in amplitude decibels). 6dB gives a factor of 2 reduction
        in noise.

    f : float or :class:`.Frequency`, optional
        Frequency-offset of the squeezer from the default (in Hz) or
        :class:`.Frequency` object. Defaults to 0 Hz offset.

    angle : float, optional
        Squeezing angle (in degrees). Defaults to zero.
    """

    def __init__(self, name, db, f=0, angle=0):
        Connector.__init__(self, name)
        FrequencyGenerator.__init__(self)
        NoiseGenerator.__init__(self)

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)
        # Two drives to excite an upper and lower sideband
        # individually used for generating squeezing info
        self._add_port("upper", NodeType.ELECTRICAL)
        self.upper._add_node("i", NodeDirection.INPUT)
        self._add_port("lower", NodeType.ELECTRICAL)
        self.lower._add_node("i", NodeDirection.INPUT)

        self.db = db
        self.f = f
        self.angle = angle

        self._register_noise_output("P1o", self.p1.o, NoiseType.QUANTUM)
        self._register_node_coupling("UPPER_P1o", self.upper.i, self.p1.o)
        self._register_node_coupling("LOWER_P1o", self.lower.i, self.p1.o)

    def _source_frequencies(self):
        return [self.f.ref]

    def _couples_noise(self, ws, node, noise_type, frequency_in, frequency_out):
        return (frequency_in.index == frequency_out.index) or (
            (frequency_in.audio_carrier_index == frequency_out.audio_carrier_index)
            and (frequency_in.audio_carrier_index == ws.fsrc_car_idx)
        )

    def _get_workspace(self, sim):
        from finesse.components.modal.squeezer import (
            squeezer_fill_qnoise,
            squeezer_fill_signal,
            SqueezerWorkspace,
        )

        ws = SqueezerWorkspace(self, sim)
        ws.fsrc_car_idx = -1

        if sim.signal:
            ws.node_id = sim.signal.node_id(self.p1.o)
            ws.signal.add_fill_function(
                squeezer_fill_signal, True
            )  # TODO sort out refill flag here
            ws.signal.set_fill_noise_function(NoiseType.QUANTUM, squeezer_fill_qnoise)
            fsrc = self.__find_src_freq(sim.carrier)
            # Didn't find a Frequency bin for this squeezer in carrier simulation
            if fsrc is None:
                raise Exception(
                    f"Could not find a frequency bin in carrier sim at {self.f} for {self}"
                )
            ws.fsrc_car_idx = fsrc.index
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

    def __find_src_freq(self, sim):
        # if it's tunable we want to look for the symbol that is just this
        # lasers frequency, as it will be changing
        for f in sim.optical_frequencies.frequencies:
            if not self.f.is_changing:
                # Don't match changing frequency bins if ours won't match
                if not f.symbol.is_changing and (
                    f.f == self.f.value  # match potential param refs
                    or f.f == float(self.f.value)  # match numeric values
                ):
                    # If nothing is changing then we can just match freq values
                    return f
            else:
                # If our frequency is changing then we have to have a frequency bin that
                # matches our symbol
                if f.symbol == self.f.ref:
                    return f  # Simple case
        return None
