import numpy as np

from finesse.components import Cavity
from finesse.detectors.general import Detector
from finesse.detectors.compute.gaussian import (
    CPDetectorWorkspace,
    CPDetectorABCDWorkspace,
    CPDetectorModeWorkspace,
    CavityProperty,
)


# Map of cavity property keywords to enum fields.
CP_KEYWORDS = {
    "length": CavityProperty.LENGTH,
    "l": CavityProperty.LENGTH,
    "loss": CavityProperty.LOSS,
    "finesse": CavityProperty.FINESSE,
    "fsr": CavityProperty.FSR,
    "fwhm": CavityProperty.FWHM,
    "pole": CavityProperty.POLE,
    "tau": CavityProperty.TAU,
    "abcd": CavityProperty.ABCD,
    "g": CavityProperty.STABILITY,
    "stability": CavityProperty.STABILITY,
    "gouy": CavityProperty.RTGOUY,
    "modesep": CavityProperty.MODESEP,
    "resolution": CavityProperty.RESOLUTION,
    "q": CavityProperty.EIGENMODE,
    "w": CavityProperty.SOURCE_SIZE,
    "w0": CavityProperty.SOURCE_WAISTSIZE,
    "z": CavityProperty.SOURCE_DISTANCE,
    "zr": CavityProperty.SOURCE_RAYLEIGH,
    "div": CavityProperty.SOURCE_DIVERGENCE,
    "rc": CavityProperty.SOURCE_ROC,
    "s": CavityProperty.SOURCE_DEFOCUS,
}


class CavityPropertyDetector(Detector):
    """Probe for detecting the properties of a cavity.

    The valid values for `prop` are:

      * ``"length"`` or ``"l"``: round-trip cavity length [metres],
      * ``"loss"``: round-trip loss as a fraction,
      * ``"finesse"``: the cavity finesse,
      * ``"fsr"``: free spectral range [Hz],
      * ``"fwhm"``: full-width at half-maximum (i.e. linewidth) [Hz],
      * ``"pole"``: cavity pole frequency [Hz],
      * ``"tau"``: photon storage time [s],
      * ``"abcd"``: round-trip ABCD matrix,
      * ``"g"`` or ``"stability"``: stability as g-factor,
      * ``"gouy"``: round-trip Gouy phase [deg],
      * ``"modesep"``: mode-separation frequency [Hz],
      * ``"resolution"``: cavity resolution [Hz],
      * ``"q"``: eigenmode,
      * ``"w"``: beam size at the cavity source node [metres],
      * ``"w0"``: waist size [metres],
      * ``"z"``: distance to the waist from the cavity source node [metres],
      * ``"zr"``: the Rayleigh range of the eigenmode [metres],
      * ``"div"``: divergence angle of cavity mode [radians],
      * ``"rc"``: radius of curvature of wavefront at cavity source node [metres],
      * ``"s"``: curvature of wavefront at cavity source node [1 / metres].

    Parameters
    ----------
    name : str
        Name of newly created cavity property detector.

    cavity : str or :class:`.Cavity`
        The cavity to probe. If the name is provided then the
        :attr:`.CavityPropertyDetector.cavity` attribute will point
        to the corresponding :class:`.Cavity` object when adding
        this detector to a :class:`.Model` instance.

    prop : str or :class:`.CavityProperty`
        Property of the cavity to probe. See above for options.

    direction : str, optional; default: 'x'
        Plane to detect in.

    q_as_bp : bool, optional; default: False
        If detecting q, should the detector output return :class:`.BeamParam`
        object instead of just a complex number.
    """

    def __init__(self, name, cavity, prop, direction="x", q_as_bp=False):
        if isinstance(prop, str):
            if prop.casefold() not in CP_KEYWORDS:
                raise ValueError(
                    f"Unrecognised property: {prop}, expected "
                    f"one of: {list(CP_KEYWORDS.keys())}"
                )
            prop = CP_KEYWORDS[prop.casefold()]

        units = ""
        if prop == CavityProperty.EIGENMODE:
            if q_as_bp:
                dtype = object
            else:
                dtype = np.complex128
        else:
            dtype = np.float64
            if prop == CavityProperty.RTGOUY:
                units = "degrees"
            elif prop == CavityProperty.SOURCE_DIVERGENCE:
                units = "radians"
            elif prop == CavityProperty.SOURCE_DEFOCUS:
                units = "1/m"
            elif prop == CavityProperty.TAU:
                units = "s"
            elif prop in (
                CavityProperty.FSR,
                CavityProperty.FWHM,
                CavityProperty.POLE,
                CavityProperty.MODESEP,
            ):
                units = "Hz"
            elif prop in (
                CavityProperty.LENGTH,
                CavityProperty.SOURCE_SIZE,
                CavityProperty.SOURCE_WAISTSIZE,
                CavityProperty.SOURCE_DISTANCE,
                CavityProperty.SOURCE_RAYLEIGH,
                CavityProperty.SOURCE_ROC,
            ):
                units = "m"

        if prop == CavityProperty.ABCD:
            shape = (2, 2)
        else:
            shape = None

        property_to_label = {
            CavityProperty.LENGTH: "Cavity round-trip length",
            CavityProperty.LOSS: "Cavity loss",
            CavityProperty.FINESSE: "Cavity finesse",
            CavityProperty.FSR: "Cavity FSR",
            CavityProperty.FWHM: "Cavity FWHM",
            CavityProperty.POLE: "Cavity pole frequency",
            CavityProperty.TAU: "Cavity storage time",
            CavityProperty.ABCD: "Round-trip ABCD matrix",
            CavityProperty.STABILITY: "Stability of cavity",
            CavityProperty.RTGOUY: "Cavity round-trip Gouy phase",
            CavityProperty.MODESEP: "Cavity mode separation frequency",
            CavityProperty.RESOLUTION: "Cavity resolution",
            CavityProperty.EIGENMODE: "Cavity eigenmode",
            CavityProperty.SOURCE_SIZE: "Beam radius of eigenmode",
            CavityProperty.SOURCE_WAISTSIZE: "Waist radius of eigenmode",
            CavityProperty.SOURCE_DISTANCE: "Distance to waist of eigenmode",
            CavityProperty.SOURCE_RAYLEIGH: "Rayleigh range of eigenmode",
            CavityProperty.SOURCE_DIVERGENCE: "Divergence angle of eigenmode",
            CavityProperty.SOURCE_ROC: "Wavefront RoC of eigenmode",
            CavityProperty.SOURCE_DEFOCUS: "Wavefront defocus of eigenmode",
        }
        label = property_to_label[prop]

        Detector.__init__(self, name, dtype=dtype, shape=shape, unit=units, label=label)
        self.__cavity = cavity
        self.__prop = prop
        self.direction = direction

        self.q_as_bp = q_as_bp

    @property
    def prop(self):
        return self.__prop

    @property
    def needs_fields(self):
        return False

    @property
    def needs_trace(self):
        return self.detecting in (
            CavityProperty.EIGENMODE,
            CavityProperty.SOURCE_SIZE,
            CavityProperty.SOURCE_WAISTSIZE,
            CavityProperty.SOURCE_DISTANCE,
            CavityProperty.SOURCE_RAYLEIGH,
            CavityProperty.SOURCE_DIVERGENCE,
            CavityProperty.SOURCE_ROC,
            CavityProperty.SOURCE_DEFOCUS,
        )

    @property
    def detecting(self):
        """The property of the cavity which is being detected.

        :getter: Returns the detected property (read-only).
        """
        return self.__prop

    @property
    def cavity(self):
        """The cavity instance being probed."""
        return self.__cavity

    def _set_cavity(self):
        if not self.has_model:
            raise RuntimeError(f"Bug encountered! No model associated with {self.name}")

        if not isinstance(self.cavity, Cavity):
            cavity = self._model.elements.get(self.cavity, None)
            if cavity is None or not isinstance(cavity, Cavity):
                raise ValueError(f"No cavity of name {self.cavity} in model.")

            self.__cavity = cavity

    def _get_workspace(self, sim):
        if self.needs_trace:
            ws = CPDetectorModeWorkspace(self, sim)
            ws.q_as_bp = self.q_as_bp
        else:
            if self.detecting == CavityProperty.ABCD:
                ws = CPDetectorABCDWorkspace(self, sim)
            else:
                ws = CPDetectorWorkspace(self, sim)

        return ws

    def _set_plotting_variables(self, trace_info):
        # Can't pickle enum so cast to int, which works the same
        trace_info["detecting"] = self.detecting
