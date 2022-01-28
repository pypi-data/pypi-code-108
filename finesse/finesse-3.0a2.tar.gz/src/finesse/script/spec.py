"""KatScript specification.

This defines supported KatScript syntax and maps it to Finesse Python classes via
:class:`.ItemAdapter` objects.
"""

import abc
import logging
from collections import ChainMap
from .. import components, detectors, locks, symbols, frequency
from ..config import config_instance
from ..model import Model
from ..components import mechanical, electronics
from ..components.ligo import suspensions as ligo
from ..analysis import actions, noise
from .adapter import (
    Argument,
    ArgumentDump,
    ArgumentType,
    ItemAdapter,
    ItemDumper,
    ItemSetter,
    ElementDumper,
    ElementDump,
    ElementFactory,
    ElementSetter,
    ElementDocumenter,
    CommandMethodSetter,
    CommandMethodDocumenter,
    CommandPropertyDumper,
    CommandPropertySetter,
    CommandPropertyDocumenter,
    AnalysisDumper,
    AnalysisFactory,
    AnalysisSetter,
    AnalysisDocumenter,
    SignatureArgumentMixin,
    CommandDump,
)

LOGGER = logging.getLogger(__name__)


def _make_element(element_type, full_name, build_last=False, ref_args=None, **kwargs):
    """Create a standard element adapter.

    Use this for elements that follow the normal behaviour: they are of type
    :class:`.ModelElement`, their constructor signature defines their attributes, and
    the attributes are available with the same name in the object.
    """
    return ItemAdapter(
        full_name,
        getter=ElementDumper(item_type=element_type, ref_args=ref_args),
        factory=ElementFactory(item_type=element_type, last=build_last),
        setter=ElementSetter(item_type=element_type),
        documenter=ElementDocumenter(item_type=element_type),
        **kwargs,
    )


def _make_analysis(analysis_type, full_name, ref_args=None, **kwargs):
    """Create a standard analysis adapter.

    Use this for analyses that follow the normal behaviour: they are of type
    :class:`.Action`, their constructor signature defines their attributes, and the
    attributes are available with the same name in the object.
    """
    return ItemAdapter(
        full_name,
        getter=AnalysisDumper(item_type=analysis_type, ref_args=ref_args),
        factory=AnalysisFactory(item_type=analysis_type),
        setter=AnalysisSetter(item_type=analysis_type),
        documenter=AnalysisDocumenter(item_type=analysis_type),
        singular=True,
        **kwargs,
    )


class GaussDumper(ItemDumper):
    """Dumper for the :class:`.Gauss` component.

    Gauss components accept many different forms of argument to define the beam
    parameter but only store these internally as q parameters. This dumper therefore
    tries to figure out how the parameters were defined by the user (either via Python
    or KatScript) and generates parameters based on that.
    """

    def __init__(self):
        super().__init__(item_type=components.Gauss)

    def __call__(self, adapter, model):
        for gauss in model.get_elements_of_type(self.item_type):
            parameters = {
                "node": ArgumentDump("node", value=gauss.node, kind=ArgumentType.ANY),
                "priority": ArgumentDump(
                    "priorty", value=gauss.priority, default=0, kind=ArgumentType.ANY
                ),
            }

            # Map of available gauss call parameters to attributes.
            # FIXME: move these to Gauss itself.
            gauss_attr_map = {
                "w0": gauss.qx.w0,
                "z": gauss.qx.z,
                "zr": gauss.qx.zr,
                "w": gauss.qx.w,
                "Rc": gauss.qx.Rc,
                "S": gauss.qx.S,
                "q": gauss.qx.q,
            }

            # Add additional parameters specified by the user.
            for param in gauss._specified_params:
                value = gauss_attr_map[param]
                parameters[param] = ArgumentDump(
                    param,
                    value=value,
                    default=None,
                    kind=ArgumentType.KEYWORD_ONLY,
                )

            yield ElementDump(
                element=gauss,
                adapter=adapter,
                parameters=parameters,
                is_default=all(param.is_default for param in parameters.values()),
            )


class FsigArgumentsMixin(metaclass=abc.ABCMeta):
    def arguments(self, **kwargs):
        # FIXME: these would ideally come from Fsig's constructor, but we can't inspect
        # Cython types.
        return {"f": Argument("f", ArgumentType.ANY)}


class FsigDumper(ItemDumper):
    def __init__(self):
        super().__init__(item_type=frequency.Fsig)

    def __call__(self, adapter, model):
        # FIXME: these would ideally come from Fsig's constructor, but we can't inspect
        # Cython types.
        default = None
        is_default = model.fsig.f.value == default
        parameters = {"f": ArgumentDump("f", value=model.fsig.f, default=default)}

        yield CommandDump(adapter=adapter, parameters=parameters, is_default=is_default)


class FsigSetter(FsigArgumentsMixin, ItemSetter):
    def __init__(self):
        super().__init__(item_type=frequency.Fsig)

    def __call__(self, model, argskwargs):
        args, kwargs = argskwargs
        allargs = list(args) + list(kwargs.values())
        assert len(allargs) == 1
        model.fsig.f = allargs[0]


class FsigDocumenter(FsigArgumentsMixin, CommandMethodDocumenter):
    def __init__(self):
        super().__init__(item_type=frequency.Fsig)


class ModesDumper(SignatureArgumentMixin, ItemDumper):
    def __init__(self):
        super().__init__(item_type=Model.modes)

    def __call__(self, adapter, model):
        # Grab the values from :meth:`.Model.modes_setting` but grab the defaults from
        # the :meth:`.Model.modes` signature.
        sigparams = self.arguments()
        parameters = {
            key: ArgumentDump(
                key,
                value=value,
                default=sigparams[key].default,
                kind=sigparams[key].kind,
            )
            for key, value in model.modes_setting.items()
        }

        # Ensure the "modes" parameter exists so that, if "default valued" commands are
        # requested, a modes command with an "off" parameter is dumped.
        modes_other_defaults = [sigparams["modes"].default]
        if modes := parameters.get("modes"):
            # The `modes` parameter accepts "off" via KatScript as the same meaning as
            # the Python default (`None`).
            modes.default = "off"
            modes.other_defaults = modes_other_defaults
        else:
            # Ensure there is at least an "off".
            parameters["modes"] = ArgumentDump(
                "modes",
                value="off",
                default="off",
                other_defaults=modes_other_defaults,
                kind=sigparams["modes"].kind,
            )

        yield CommandDump(
            adapter=adapter,
            parameters=parameters,
            is_default=all(param.is_default for param in parameters.values()),
        )


class TEMDumper(SignatureArgumentMixin, ItemDumper):
    def __init__(self):
        super().__init__(item_type=components.Laser.tem)

    def __call__(self, adapter, model):
        """(args, kwargs) tuples for each defined TEM mode."""
        sigparams = self.arguments()

        for laser in model.get_elements_of_type(components.Laser):
            for (n, m), (factor, phase) in laser.power_coeffs.items():
                otherkv = {"n": n, "m": m, "factor": factor, "phase": phase}
                other_parameters = {
                    key: ArgumentDump(
                        key,
                        value=value,
                        default=sigparams[key].default,
                        kind=sigparams[key].kind,
                    )
                    for key, value in otherkv.items()
                }

                parameters = {
                    "laser": ArgumentDump("laser", value=laser),
                    **other_parameters,
                }

                current = {(n, m): (factor, phase)}
                yield CommandDump(
                    adapter=adapter,
                    parameters=parameters,
                    is_default=current.items() <= laser.DEFAULT_POWER_COEFFS.items(),
                )


class TEMSetter(CommandMethodSetter):
    def __init__(self):
        super().__init__(item_type=components.Laser.tem)

    def __call__(self, _, argskwargs):
        args, kwargs = argskwargs

        if "laser" in kwargs:
            laser = kwargs.pop("laser")
        else:
            laser, *args = args

        self.item_type(laser, *args, **kwargs)


class TEMDocumenter(CommandMethodDocumenter):
    def __init__(self):
        super().__init__(item_type=components.Laser.tem)

    ##
    # Override some inherited methods to add the laser argument, which is not part of
    # :meth:`.Laser.tem` (well, technically it's `self`, but we want to call it
    # "laser").

    def arguments(self):
        return {
            "laser": Argument(name="laser", kind=ArgumentType.ANY),
            **super().arguments(),
        }

    def argument_descriptions(self):
        return {
            "laser": (":class:`.Laser`", "The laser to set mode power for."),
            **super().argument_descriptions(),
        }


class BaseSpec(metaclass=abc.ABCMeta):
    """Empty language specification."""

    _SUPPORTED_CONSTANTS = {}
    _SUPPORTED_KEYWORDS = set()
    _SUPPORTED_UNARY_OPERATORS = {}
    _SUPPORTED_BINARY_OPERATORS = {}
    _SUPPORTED_EXPRESSION_FUNCTIONS = {}
    _DEFAULT_ELEMENTS = []
    _DEFAULT_COMMANDS = []
    _DEFAULT_ANALYSES = []

    def __init__(self):
        # Modifiable specifications. These are dynamically supported by the parser.
        self.elements = {}
        self.commands = {}
        self.analyses = {}

        # Fixed specifications. These are not modifiable by the user.
        self.constants = self._SUPPORTED_CONSTANTS
        self.keywords = self._SUPPORTED_KEYWORDS
        self.unary_operators = self._SUPPORTED_UNARY_OPERATORS
        self.binary_operators = self._SUPPORTED_BINARY_OPERATORS
        self.expression_functions = self._SUPPORTED_EXPRESSION_FUNCTIONS

        # Add support for the default directives.
        for adapter in self._DEFAULT_ELEMENTS:
            self.register_element(adapter)
        for adapter in self._DEFAULT_COMMANDS:
            self.register_command(adapter)
        for adapter in self._DEFAULT_ANALYSES:
            self.register_analysis(adapter)

    @property
    def directives(self):
        """All top level parser directives.

        :getter: Returns a mapping of top level parser directive aliases to
                 :class:`adapters <.ItemAdapter>`.
        :type: :class:`~collections.ChainMap`
        """
        # ChainMap yields in LIFO order so key order becomes elements, then commands,
        # then analyses. This order is relied upon by :func:`.syntax`.
        return ChainMap(self.analyses, self.commands, self.elements)

    @property
    def function_directives(self):
        """All top level function-style parser directives.

        :getter: Returns a mapping of top level function parser directive aliases to
                 :class:`adapters <.ItemAdapter>`.
        :type: :class:`~collections.ChainMap`
        """
        return ChainMap(self.analyses, self.commands)

    @property
    def reserved_names(self):
        """All reserved names.

        This is primarily useful for tests.

        :getter: Returns the names reserved in the parser as special production types.
        :type: :class:`list`
        """
        return list(self.keywords) + list(self.constants)

    def _register_adapter(self, mapping, adapter, overwrite=False):
        for alias in adapter.aliases:
            if alias in mapping:
                if overwrite:
                    LOGGER.info(
                        f"overwriting existing {repr(alias)} with {repr(adapter)}"
                    )
                else:
                    raise KeyError(
                        f"{repr(alias)} from {repr(adapter)} already exists (provided "
                        f"by {mapping[alias]}). If you intend to overwrite the "
                        f"existing definition, set overwrite=True."
                    )

            mapping[alias] = adapter

    def register_element(self, adapter, **kwargs):
        """Add parser and generator support for a model element such as a component or
        detector.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The element adapter.

        Other Parameters
        ----------------
        overwrite : bool, optional
            Overwrite elements with the same aliases, if present. If `False` and one of
            `adapter`'s aliases already exists, a :class:`KeyError` is raised.
            Defaults to `False`.
        """
        self._register_adapter(self.elements, adapter, **kwargs)

    def register_command(self, adapter, **kwargs):
        """Add parser and generator support for a command.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The command adapter.

        Other Parameters
        ----------------
        overwrite : bool, optional
            Overwrite commands with the same aliases, if present. If `False` and one of
            `adapter`'s aliases already exists, a :class:`KeyError` is raised.
            Defaults to `False`.
        """
        self._register_adapter(self.commands, adapter, **kwargs)

    def register_analysis(self, adapter, **kwargs):
        """Add parser and generator support for an analysis.

        Parameters
        ----------
        adapter : :class:`.ItemAdapter`
            The analysis adapter.

        Other Parameters
        ----------------
        overwrite : bool, optional
            Overwrite analyses with the same aliases, if present. If `False` and one of
            `adapter`'s aliases already exists, a :class:`KeyError` is raised.
            Defaults to `False`.
        """
        self._register_adapter(self.analyses, adapter, **kwargs)

    def match_fuzzy_directive(self, search, limit=3, cutoff=0.5):
        """Get the directives that most closely match the specified string.

        Parameters
        ----------
        search : str
            The directive to search for.

        limit : int, optional
            The maximum number of matches to return.

        cutoff : float, optional
            The cutoff below which to assume no match. This is the ratio as defined in
            the `Python documentation
            <https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.ratio>`__.

        Returns
        -------
        list
            Up to `limit` closest matches.
        """
        from difflib import get_close_matches

        return get_close_matches(search, self.directives, n=limit, cutoff=cutoff)

    def type_descriptor(self, *args, **kwargs):
        """Get a descriptor for a type that's suitable for use in user feedback.

        This allows something other than Python class names to be displayed to the user
        inside error messages.

        Supports the same parameters as :meth:`dict.get`.
        """
        descriptors = {}
        return descriptors.get(*args, **kwargs)


class KatSpec(BaseSpec):
    """Kat language specification.

    This defines the available instructions for the parser and the adapters that convert
    them to and from Python models. The default instructions, actions and keywords are
    built into public properties which may be modified by users (e.g. to add support for
    custom commands). As such, the internal defaults (fields with names beginning
    `_DEFAULT_`) should not be modified after import.
    """

    _DEFAULT_ELEMENTS = [
        ## Components.
        _make_element(electronics.Amplifier, "amplifier"),
        _make_element(components.Beamsplitter, "beamsplitter", short_name="bs"),
        # The cavity factory's `last` flag is set because cavities implicitly depend on
        # any nodes that appear in paths from their start ports back to themselves, so
        # their dependencies cannot be determined by the time the first set of elements
        # are built into the model. It is moved to the second build pass by this flag.
        _make_element(components.Cavity, "cavity", short_name="cav", build_last=True),
        _make_element(
            components.DegreeOfFreedom, "degree_of_freedom", short_name="dof"
        ),
        _make_element(
            components.DirectionalBeamsplitter,
            "directional_beamsplitter",
            short_name="dbs",
        ),
        _make_element(electronics.ZPKFilter, "filter_zpk", short_name="zpk"),
        _make_element(electronics.ButterFilter, "filter_butter", short_name="butter"),
        _make_element(electronics.Cheby1Filter, "filter_cheby1", short_name="cheby1"),
        _make_element(components.Isolator, "isolator", short_name="isol"),
        _make_element(components.Laser, "laser", short_name="l"),
        _make_element(components.Lens, "lens"),
        _make_element(components.Mirror, "mirror", short_name="m"),
        _make_element(components.Modulator, "modulator", short_name="mod"),
        _make_element(
            components.optical_bandpass.OpticalBandpassFilter,
            "optical_bandpass",
            short_name="obp",
        ),
        _make_element(components.Squeezer, "squeezer", short_name="sq"),
        _make_element(components.ReadoutDC, "readout_dc"),
        _make_element(components.ReadoutRF, "readout_rf"),
        _make_element(components.Variable, "variable", short_name="var"),
        _make_element(
            components.SignalGenerator, "signal_generator", short_name="sgen"
        ),
        ## Detectors.
        _make_element(
            detectors.AmplitudeDetector, "amplitude_detector", short_name="ad"
        ),
        _make_element(detectors.FieldDetector, "field_detector", short_name="fd"),
        _make_element(detectors.AstigmatismDetector, "astigd"),
        _make_element(
            detectors.BeamPropertyDetector, "beam_property_detector", short_name="bp"
        ),
        _make_element(detectors.OptimalQ, "optimal_q_detector", short_name="optbp"),
        _make_element(detectors.CCD, "ccd"),
        _make_element(detectors.CCDScanLine, "ccdline"),
        _make_element(detectors.CCDPixel, "ccdpx"),
        _make_element(
            detectors.CavityPropertyDetector,
            "cavity_property_detector",
            short_name="cp",
        ),
        _make_element(detectors.FieldCamera, "fcam"),
        _make_element(detectors.FieldScanLine, "fline"),
        _make_element(detectors.FieldPixel, "fpx"),
        # The gouy detector factory's `last` flag is set it implicitly depends on any
        # nodes that appear in the path from its start port back to itself, so its
        # dependencies cannot be determined by the time the first set of elements are
        # built into the model. It is moved to the second build pass by this flag.
        _make_element(detectors.Gouy, "gouy", build_last=True),
        _make_element(detectors.KnmDetector, "knmd"),
        _make_element(detectors.ModeMismatchDetector, "mmd"),
        _make_element(detectors.MotionDetector, "motion_detector", short_name="xd"),
        _make_element(detectors.PowerDetector, "power_detector_dc", short_name="pd"),
        _make_element(
            detectors.PowerDetectorDemod1, "power_detector_demod_1", short_name="pd1"
        ),
        _make_element(
            detectors.PowerDetectorDemod2, "power_detector_demod_2", short_name="pd2"
        ),
        _make_element(
            detectors.QuantumNoiseDetector,
            "quantum_noise_detector",
            short_name="qnoised",
        ),
        _make_element(
            detectors.QuantumNoiseDetectorDemod1,
            "quantum_noise_detector_demod_1",
            short_name="qnoised1",
        ),
        _make_element(
            detectors.QuantumNoiseDetectorDemod2,
            "quantum_noise_detector_demod_2",
            short_name="qnoised2",
        ),
        _make_element(
            detectors.QuantumShotNoiseDetector,
            "quantum_shot_noise_detector",
            short_name="qshot",
        ),
        _make_element(
            detectors.QuantumShotNoiseDetectorDemod1,
            "quantum_shot_noise_detector_demod_1",
            short_name="qshot1",
        ),
        _make_element(
            detectors.QuantumShotNoiseDetectorDemod2,
            "quantum_shot_noise_detector_demod_2",
            short_name="qshot2",
        ),
        ## Connectors.
        _make_element(components.Space, "space", short_name="s"),
        _make_element(components.Wire, "wire", short_name="w"),
        _make_element(components.Nothing, "nothing"),
        ## Mechanics.
        _make_element(mechanical.FreeMass, "free_mass"),
        _make_element(mechanical.Pendulum, "pendulum"),
        _make_element(mechanical.SuspensionZPK, "suspension_zpk", short_name="sus_zpk"),
        _make_element(ligo.LIGOTripleSuspension, "ligo_triple"),
        _make_element(ligo.LIGOQuadSuspension, "ligo_quad"),
        ## Lock.
        _make_element(locks.Lock, "lock", ref_args=("feedback",)),
        ## Noise.
        _make_element(noise.ClassicalNoise, "noise"),
        ## Gauss.
        ItemAdapter(
            full_name="gauss",
            getter=GaussDumper(),
            factory=ElementFactory(item_type=components.Gauss),
            setter=ElementSetter(item_type=components.Gauss),
            documenter=ElementDocumenter(item_type=components.Gauss),
        ),
    ]

    _DEFAULT_COMMANDS = [
        ItemAdapter(
            full_name="fsig",
            getter=FsigDumper(),
            setter=FsigSetter(),
            documenter=FsigDocumenter(),
            singular=True,
        ),
        ItemAdapter(
            full_name="lambda",
            getter=CommandPropertyDumper(
                item_type=Model.lambda0,
                default=config_instance()["constants"].getfloat("lambda0"),
            ),
            setter=CommandPropertySetter(item_type=Model.lambda0),
            documenter=CommandPropertyDocumenter(item_type=Model.lambda0),
            singular=True,
        ),
        ItemAdapter(
            full_name="modes",
            getter=ModesDumper(),
            setter=CommandMethodSetter(item_type=Model.modes),
            documenter=CommandMethodDocumenter(item_type=Model.modes),
            singular=True,
        ),
        ItemAdapter(
            full_name="link",
            setter=CommandMethodSetter(item_type=Model.link),
            documenter=CommandMethodDocumenter(item_type=Model.link),
        ),
        # ItemAdapter(full_name="intrix"),
        ItemAdapter(
            full_name="tem",
            getter=TEMDumper(),
            setter=TEMSetter(),
            documenter=TEMDocumenter(),
        ),
    ]

    _DEFAULT_ANALYSES = [
        ## Group actions.
        _make_analysis(actions.Parallel, "parallel"),
        _make_analysis(actions.Series, "series"),
        _make_analysis(actions.For, "for"),
        ## Axes.
        _make_analysis(actions.Noxaxis, "noxaxis"),
        _make_analysis(actions.Xaxis, "xaxis", ref_args=("parameter",)),
        _make_analysis(actions.X2axis, "x2axis", ref_args=("parameter1", "parameter2")),
        _make_analysis(
            actions.X3axis,
            "x3axis",
            ref_args=("parameter1", "parameter2", "parameter3"),
        ),
        _make_analysis(actions.Sweep, "sweep", ref_args=("*args",)),
        _make_analysis(actions.Change, "change"),
        _make_analysis(actions.UpdateMaps, "update_maps"),
        _make_analysis(
            actions.FrequencyResponse, "frequency_response", short_name="freqresp"
        ),
        _make_analysis(actions.OptimiseRFReadoutPhaseDC, "opt_rf_readout_phase"),
        _make_analysis(actions.SensingMatrixDC, "sensing_matrix_dc"),
        ## Model physics.
        _make_analysis(actions.Eigenmodes, "eigenmodes"),
        _make_analysis(actions.Operator, "operator"),
        _make_analysis(actions.ABCD, "abcd"),
        _make_analysis(actions.BeamTrace, "beam_trace"),
        _make_analysis(actions.PropagateBeam, "propagate_beam"),
        _make_analysis(actions.PropagateAstigmaticBeam, "propagate_beam_astig"),
        ## Utilities.
        _make_analysis(actions.Debug, "debug"),
        _make_analysis(actions.debug.SaveMatrix, "save_matrix"),
        _make_analysis(actions.Plot, "plot"),
        _make_analysis(actions.Printer, "print"),
        _make_analysis(actions.RunLocks, "run_locks"),
        _make_analysis(actions.PseudoLockCavity, "pseudo_lock_cavity"),
        _make_analysis(actions.PseudoLockDRFPMI, "pseudo_lock_drfpmi"),
        _make_analysis(actions.NoiseProjection, "noise_projection"),
        _make_analysis(actions.PrintModel, "print_model"),
        _make_analysis(actions.PrintModelAttr, "print_model_attr"),
        _make_analysis(actions.Minimize, "minimize"),
        _make_analysis(actions.Maximize, "maximize"),
    ]

    _SUPPORTED_KEYWORDS = {
        # None.
        "none",
        # HOM collections.
        "even",
        "odd",
        "x",
        "y",
        "off",
        # Axis scales.
        "lin",
        "log",
        # Modulator types.
        "am",
        "pm",
        # Filter types.
        "lowpass",
        "highpass",
        "bandpass",
        "bandstop",
        "single",
        "xsplit",
        "ysplit",
        # Beam properties (see :class:`finesse.detectors.compute.gaussian.BeamProperty`).
        *detectors.bpdetector.BP_KEYWORDS.keys(),
        # Cavity properties (see :class:`finesse.detectors.compute.gaussian.CavityProperty`).
        *detectors.cavity_detector.CP_KEYWORDS.keys(),
    }

    _SUPPORTED_CONSTANTS = symbols.CONSTANTS

    _SUPPORTED_UNARY_OPERATORS = {
        "+": symbols.FUNCTIONS["pos"],
        "-": symbols.FUNCTIONS["neg"],
    }

    _SUPPORTED_BINARY_OPERATORS = {
        "+": symbols.OPERATORS["__add__"],
        "-": symbols.OPERATORS["__sub__"],
        "*": symbols.OPERATORS["__mul__"],
        "**": symbols.OPERATORS["__pow__"],
        "/": symbols.OPERATORS["__truediv__"],
        "//": symbols.OPERATORS["__floordiv__"],
    }

    # Built-in functions.
    _SUPPORTED_EXPRESSION_FUNCTIONS = symbols.FUNCTIONS

    def type_descriptor(self, _type, default=None):
        # This function is typically only needed by error handling code, so import
        # required types on first call.
        from ..components.node import Node, Port

        descriptors = {
            str: "string",
            int: "integer",
            float: "floating point",
            complex: "complex",
            Node: "node",
            Port: "port",
        }

        return descriptors.get(_type, default)
