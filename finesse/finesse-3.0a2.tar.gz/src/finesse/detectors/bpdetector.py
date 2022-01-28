import numpy as np

from finesse.detectors.general import Detector
from finesse.detectors.compute.gaussian import BPDetectorWorkspace, BeamProperty


# Map of beam property keywords to enum fields.
BP_KEYWORDS = {
    "w": BeamProperty.SIZE,
    "w0": BeamProperty.WAISTSIZE,
    "z": BeamProperty.DISTANCE,
    "zr": BeamProperty.RAYLEIGH,
    "gouy": BeamProperty.GOUY,
    "div": BeamProperty.DIVERGENCE,
    "rc": BeamProperty.ROC,
    "s": BeamProperty.DEFOCUS,
    "q": BeamProperty.Q,
}

property_to_label = {
    BeamProperty.SIZE: "Beam size",
    BeamProperty.WAISTSIZE: "Beam waist-size",
    BeamProperty.DISTANCE: "Distance to beam waist",
    BeamProperty.RAYLEIGH: "Rayleigh range",
    BeamProperty.GOUY: "Gouy phase",
    BeamProperty.DIVERGENCE: "Divergence angle",
    BeamProperty.ROC: "Beam radius of curvature",
    BeamProperty.DEFOCUS: "Beam defocus",
    BeamProperty.Q: "Beam parameter",
}


class BeamPropertyDetector(Detector):
    r"""Probe for detecting the properties of a beam at a given node.

    The valid values for `prop` are:

      * ``"w"``: beam size at `node` [metres],
      * ``"w0"``: waist size as measured at `node` [metres],
      * ``"z"``: distance to the waist from `node` [metres],
      * ``"zr"``: the Rayleigh range [metres],
      * ``"gouy"``: the Gouy phase of the beam at `node` [radians],
      * ``"div"``: divergence angle of the beam at `node`  [radians],
      * ``"rc"``: radius of curvature of wavefront at `node` [metres],
      * ``"s"``: curvature of wavefront at `node` [1 / metres],
      * ``"q"``: beam parameter at `node`.

    .. note::

        The ``"gouy"`` target property here detects the Gouy phase as derived
        from the beam parameter :math:`q` at the specified node, i.e:

        .. math::

            \psi = \arctan{\left(\frac{\myRe{q}}{\myIm{q}}\right)}.

        It does **not** compute any Gouy phase accumulation. Use :class:`.Gouy`
        to detect the accumulated Gouy phase over a path.

    Parameters
    ----------
    name : str
        Name of newly created detector.

    node : :class:`.OpticalNode`
        Node to read output from.

    prop : str or :class:`.BeamProperty`
        The property of the beam to detect. See above for options.

    direction : str, optional; default: 'x'
        Plane to detect in - 'x' for tangential, 'y' for sagittal.

    q_as_bp : bool, optional; default: False
        If detecting q, should the detector output return :class:`.BeamParam`
        object instead of just a complex number.
    """

    def __init__(self, name, node, prop, direction="x", q_as_bp=False):
        if isinstance(prop, str):
            if prop.casefold() not in BP_KEYWORDS:
                raise ValueError(
                    f"Unrecognised property: {prop}, expected "
                    f"one of: {list(BP_KEYWORDS.keys())}"
                )
            prop = BP_KEYWORDS[prop.casefold()]

        if prop == BeamProperty.Q:
            if q_as_bp:
                dtype = object
            else:
                dtype = np.complex128
            units = ""
        else:
            dtype = np.float64
            if prop == BeamProperty.GOUY or prop == BeamProperty.DIVERGENCE:
                units = "radians"
            elif prop == BeamProperty.DEFOCUS:
                units = "1/m"
            else:
                units = "m"

        Detector.__init__(
            self, name, node, dtype=dtype, unit=units, label=property_to_label[prop]
        )
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
        return True

    @property
    def detecting(self):
        """The property of the beam which is being detected.

        :getter: Returns the detected property (read-only).
        """
        return self.__prop

    def _get_workspace(self, sim):
        ws = BPDetectorWorkspace(self, sim)
        ws.q_as_bp = self.q_as_bp
        return ws

    def _set_plotting_variables(self, trace_info):
        # Can't pickle enum so cast to int, which works the same
        trace_info["detecting"] = int(self.detecting)
