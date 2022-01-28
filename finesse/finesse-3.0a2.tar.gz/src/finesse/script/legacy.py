# flake8: noqa

"""Finesse legacy (Finesse 2) kat-script parser."""

from collections import OrderedDict
import logging
import re

from sly import Lexer, Parser

from .. import Model, analysis, components, constants, detectors, symbols, gaussian
from ..frequency import Frequency
from ..utilities import opened_file
from ..env import warn

LOGGER = logging.getLogger(__name__)

# Mapping of some alternate legacy attribute names to finesse 3 versions
attribute_map = {
    "M": "mass",
    "m": "mass",
    "Mass": "mass",
    "Rx": "Rcx",
    "rx": "Rcx",
    "rcx": "Rcx",
    "rocx": "Rcx",
    "ROCx": "Rcx",
    "Ry": "Rcy",
    "ry": "Rcy",
    "rcy": "Rcy",
    "rocy": "Rcy",
    "ROCy": "Rcy",
}


def select_powerdetector(*args, **kwargs):
    if len(args) + len(kwargs) <= 2:
        return detectors.PowerDetector(*args, **kwargs)
    elif len(args) + len(kwargs) <= 4:
        new_kwargs = {}
        for k, v in kwargs.items():
            if k == "f1" or k == "phase1":
                new_kwargs[k.strip("1")] = v
            else:
                new_kwargs[k] = v
        return detectors.PowerDetectorDemod1(*args, **new_kwargs)
    elif len(args) + len(kwargs) <= 6:
        return detectors.PowerDetectorDemod2(*args, **kwargs)


def select_quantum_noisedetector(*args, **kwargs):
    shot_only = kwargs.pop("shot_only")
    if len(args) + len(kwargs) <= 3:
        if shot_only:
            return detectors.QuantumShotNoiseDetector(*args, **kwargs)
        else:
            return detectors.QuantumNoiseDetector(*args, **kwargs)
    elif len(args) + len(kwargs) <= 5:
        new_kwargs = {}
        for k, v in kwargs.items():
            if k == "f1" or k == "phase1":
                new_kwargs[k.strip("1")] = v
            else:
                new_kwargs[k] = v
        if shot_only:
            return detectors.QuantumShotNoiseDetectorDemod1(*args, **new_kwargs)
        else:
            return detectors.QuantumNoiseDetectorDemod1(*args, **new_kwargs)
    elif len(args) + len(kwargs) <= 7:
        if shot_only:
            return detectors.QuantumShotNoiseDetectorDemod2(*args, **kwargs)
        else:
            return detectors.QuantumNoiseDetectorDemod2(*args, **kwargs)


def get_const(consts, value):
    if type(value) is str and value.strip("+-") in consts:
        ret = consts[value.strip("+-")]
        if value.startswith("-"):
            ret *= -1
    else:
        ret = value
    return ret


def get_model_element(model, element):
    try:
        return model.elements[element]
    except KeyError:
        raise KeyError(f"Element '{element}' not in model.")


class KatParser:
    """Kat file lexer, parser and builder."""

    def parse(self, text, model=None, **kwargs):
        """Parse kat code into a model.

        Parameters
        ----------
        text : str
            String containing the kat code to be parsed.

        model : :class:`.Model`, optional
            Model object to add components to. If not specified, a new model will be
            created.

        ignored_blocks : list, optional
            A list of names of ``FTBLOCK`` sections in the kat code to leave out of the
            model; defaults to empty list.

        Returns
        -------
        :class:`.Model`
            The constructed model.

        Raises
        ------
        :class:`.KatParserError`
            If an error occurs during parsing or building.
        """
        if model is not None:
            LOGGER.info(f"Parsing into existing model {model!r}.")
        else:
            model = Model()

        return self._build(self._parse(text), model, **kwargs)

    def parse_file(self, path, model=None, **kwargs):
        """Parse kat code from a file into a model.

        Parameters
        ----------
        path : str or :py:class:`io.FileIO`
            The path or file object to read kat script from. If an open file object is
            passed, it will be read from and left open. If a path is passed, it will be
            opened, read from, then closed.

        model : :class:`.Model`, optional
            Model object to add components to. If not specified, a new model will be
            created.

        Other Parameters
        ----------------
        **kwargs
            Keyword parameters supported by :meth:`.parse`.

        Raises
        ------
        :class:`.KatParserError`
            If an error occurs during parsing or building.
        """
        with opened_file(path, "r") as fobj:
            LOGGER.info(f"Parsing kat script from {fobj.name}")
            return self.parse(fobj.read(), model=model, **kwargs)

    def _parse(self, text):
        """Parses kat code into a model.

        Parameters
        ----------
        text : str
            String containing the kat code to be parsed.

        Returns
        -------
        parser : :class:`.sly.Parser`
            The parser object containing the parsed blocks.

        Raises
        ------
        KatParserError
            If an error occurs during parsing.
        """
        lexer = _KatLEX()
        parser = _KatYACC()

        # As we have no way of detecting EOF and calling pop_state() from
        # within the component lexer, we must ensure that all files end in a
        # newline
        text = f"{text}\n"

        # Trim any whitespace within $$ strings
        matches = re.findall(r"\$\$[^$]+\$\$", text)
        for match in matches:
            text = text.replace(match, re.sub(r"\s+", "", match))

        tokens = lexer.tokenize(text)
        parser.parse(tokens)

        errors = sorted(lexer.errors + parser.errors, key=lambda tup: tup[1])
        if len(errors) > 0:
            raise KatParserError(errors, text)

        for warning in lexer.warnings:
            warn(f"{warning[1]}:{find_column(text, warning[2])}: {warning[0]}")

        return parser

    def _build(self, parser, model=None, ignored_blocks=None):
        """Constructs a new model or appends to an existing model using the parsed kat
        code.

        Parameters
        ----------
        parser : :class:`.sly.Parser`
            The parser object containing the parsed blocks.

        model : :class:`.Model`
            Model object to update.

        ignored_blocks : list, optional
            A list of names of ``FTBLOCK`` sections in the kat code to leave out of the model;
            defaults to empty list.

        Returns
        -------
        :class:`.Model`
            The constructed model.
        """

        blocks = parser.blocks

        if ignored_blocks is None:
            ignored_blocks = []

        def parse_parameter(param):
            if type(param) is not str or "$" not in param:
                return param
            local = dict(map(lambda f: (f.name, f), model.frequencies))
            local.update(model.alternate_name_map)
            local = {**local, **model.elements}
            if param.endswith("$"):
                p = re.sub("([a-zA-Z_][a-zA-Z0-9_:.]*)", r"\1.ref", param)
            else:
                p = param
            return eval(f"{p}".replace("$", ""), local)

        LOGGER.info("Building model")

        component_constructors = {
            "lasers": components.Laser,
            "squeezers": components.Squeezer,
            "mirrors": components.Mirror,
            "beamsplitters": components.Beamsplitter,
            "directional_beamsplitters": components.DirectionalBeamsplitter,
            "isolators": components.Isolator,
            "modulators": components.Modulator,
            "lenses": components.Lens,
        }

        detector_constructors = {
            "amplitude_detectors": detectors.AmplitudeDetector,
            "beam_detectors": (detectors.CCDPixel, detectors.FieldPixel),
            "beam_property_detectors": detectors.BeamPropertyDetector,
            "power_detectors": select_powerdetector,
            "quantum_noise_detectors": select_quantum_noisedetector,
        }
        model = model or Model()
        node_names = ["node", "node1", "node2", "node3", "node4"]
        nodes = {}
        consts = {}

        ignored_blocks = set(ignored_blocks)

        if ignored_blocks:
            ignored_block_list = ", ".join(ignored_blocks)
            LOGGER.debug(f"Ignoring blocks {ignored_block_list}.")

        for key in ignored_blocks:
            # TODO: make KatParserError behave like the kat3 parser's, i.e. it can be instantiated
            # with a single message and not just a list of errors, then if a KeyError is thrown
            # here, rethrow a KatParserError with a message about the ignored block not existing.
            blocks.pop(key)

        # First pass, just grab constants
        for block, d in blocks.items():
            for k, v in d["constants"].items():
                consts[k] = v

        def apply_constants(comp):
            if isinstance(comp, list):
                for k, v in enumerate(comp):
                    if isinstance(v, dict) or isinstance(v, list):
                        apply_constants(v)
                    else:
                        comp[k] = get_const(consts, v)
            if isinstance(comp, dict):
                for k, v in comp.items():
                    if isinstance(v, dict) or isinstance(v, list):
                        apply_constants(v)
                    else:
                        comp[k] = get_const(consts, v)

        # And apply any constant renaming
        for block, d in blocks.items():
            for name, comp_type in d.items():
                if name == "constants":
                    continue
                apply_constants(comp_type)

        # Variables
        for block, d in blocks.items():
            for k, v in d["variables"].items():
                model.add(components.Variable(k, v))

        # Next grab source frequencies
        for block, d in blocks.items():
            for f in d["frequencies"]:
                model.add_frequency(
                    Frequency(f["name"], model, symbols.Constant(f["f"]))
                )

        # Next construct all frequencies & normal components,
        # and get node names
        for block, d in blocks.items():
            for name, constructor in component_constructors.items():
                for comp in d[name]:
                    args = []
                    ns = []
                    lineno = None
                    for k, v in comp.items():
                        if k == "lineno":
                            lineno = v
                        elif k in node_names:
                            ns.append(v)
                        else:
                            args.append(v)
                    el = constructor(*args)
                    if lineno:
                        el._legacy_script_line_number = lineno
                    model.add(el)
                    for i, n in enumerate(ns):
                        if n in nodes and n != "dump":
                            raise ValueError(
                                f"In block '{block}': {args[0]}: "
                                f"Node '{n}' already assigned to "
                                f"'{nodes[n][0]}'."
                            )
                        else:
                            nodes[n] = (args[0], ns.index(n) + 1)
                            # get the output node object corresponding to
                            # this node and tag it
                            _ni = getattr(
                                getattr(
                                    get_model_element(model, comp["name"]), f"p{i + 1}"
                                ),
                                "o",
                            )
                            try:
                                model.tag_node(_ni, n)
                            except:
                                pass

        # Connect all of the components up with spaces
        for block, d in blocks.items():
            for space in d["spaces"]:
                try:
                    comp1 = nodes[space["node1"]]
                    node1 = getattr(get_model_element(model, comp1[0]), f"p{comp1[1]}")
                except KeyError:
                    name = space["name"] + "_" + space["node1"]
                    comp1 = components.Nothing(name)
                    model.add(comp1)
                    node1 = comp1.p1
                    nodes[space["node1"]] = (name, 1)
                try:
                    comp2 = nodes[space["node2"]]
                    node2 = getattr(get_model_element(model, comp2[0]), f"p{comp2[1]}")
                except KeyError:
                    name = space["name"] + "_" + space["node2"]
                    comp2 = components.Nothing(name)
                    model.add(comp2)
                    node2 = comp2.p1
                    nodes[space["node2"]] = (name, 1)
                kwargs = {}
                lineno = None
                for k, v in space.items():
                    if k == "lineno":
                        lineno = v
                    elif k not in node_names:
                        kwargs[k] = v

                el = components.Space(**kwargs, portA=node1, portB=node2)
                model.add(el)
                if lineno:
                    el._legacy_script_line_number = lineno

        # Create fsigs
        for block, d in blocks.items():
            for fsig in d["fsigs"]:
                if model.fsig.f.value is None:
                    model.fsig.f = parse_parameter(fsig["f"])
                    model.alternate_name_map["fs"] = model.fsig.f.ref
                    model.alternate_name_map["mfs"] = model.fsig.f.ref
                elif model.fsig.f.value != parse_parameter(fsig["f"]):
                    raise ValueError("Cannot have more than one signal frequency.")

                # fsig command is specifying an input not just a frequency
                if len(fsig.keys()) == 2:
                    # Need to make some dummy object here to reference
                    # the model fsig value legacy issues of dealing with
                    # a single parameter that can have multiple names
                    model.fsig.f = fsig["f"]
                    model.alternate_name_map[fsig["name"]] = model.fsig
                else:
                    comp = get_model_element(model, fsig["component"])
                    mod_type = fsig["mod_type"]
                    scaling = 1
                    if isinstance(comp, components.Mirror) or isinstance(
                        comp, components.Beamsplitter
                    ):
                        node = comp.mech.z
                        if mod_type is None or mod_type == "phase":
                            scaling = model.lambda0 / (2 * constants.PI)
                        else:
                            raise ValueError(
                                f"Unsupported signal type '{mod_type}' at a mirror."
                            )
                    else:
                        if mod_type == "amp":
                            node = comp.amp.i
                        elif mod_type == "phase":
                            node = comp.phs.i
                        elif mod_type == "freq":
                            node = comp.frq.i
                        elif mod_type is None:
                            if isinstance(comp, components.Laser):
                                node = comp.frq.i
                            elif isinstance(comp, components.Space):
                                node = comp.h.i
                            else:
                                node = comp.phs.i
                        else:
                            raise ValueError(f"Unknown signal type '{mod_type}'.")
                    signal = components.SignalGenerator(
                        fsig["name"], node, fsig["amp"] * scaling, fsig["phase"]
                    )
                    model.add(signal)

        # Create detectors
        for block, d in blocks.items():
            for name, constructor in detector_constructors.items():
                for det in d[name]:
                    args = {}
                    lineno = None
                    for k, v in det.items():
                        if k == "lineno":
                            lineno = v
                        elif k not in node_names:
                            if isinstance(v, list):
                                args[k] = [parse_parameter(x) for x in v]
                            else:
                                args[k] = parse_parameter(v)
                        else:
                            direction = "o"
                            if v.endswith("*"):
                                v = v.strip("*")
                                direction = "i"
                            comp = get_model_element(model, nodes[v][0])
                            if isinstance(comp, components.Nothing) or isinstance(
                                comp, components.Laser
                            ):
                                if direction == "i":
                                    direction = "o"
                                else:
                                    direction = "i"
                            node = f"p{nodes[v][1]}.{direction}"
                            n = comp
                            for attr in node.split("."):
                                n = getattr(n, attr)
                            args["node"] = n

                    if name == "beam_detectors":
                        if args["f"] is None:  # CCDPixel
                            del args["f"]
                            constructor = constructor[0]
                        else:  # FieldPixel
                            constructor = constructor[1]

                    comp = constructor(**args)
                    comp._legacy_script_line_number = lineno
                    model.add(comp)

        # Gouy detector
        for block, d in blocks.items():
            for det in d["gouy"]:
                args = [det["name"]]
                for space in det["space_list"]:
                    args.append(get_model_element(model, space))
                el = detectors.Gouy(*args, direction=det["direction"])
                el._legacy_script_line_number = det["lineno"]
                model.add(el)

        # Motion detector
        for block, d in blocks.items():
            for det in d["motion_detectors"]:
                name = det["name"]
                node = getattr(
                    get_model_element(model, det["component"]).mech, det["motion"]
                )
                el = detectors.MotionDetector(name, node)
                el._legacy_script_line_number = det["lineno"]
                model.add(el)

        # Apply attributes
        for block, d in blocks.items():
            for k, v in d["attributes"].items():
                component = get_model_element(model, k)
                for attr, val in v:
                    if attr in attribute_map:
                        attr = attribute_map[attr]
                    if attr == "mass":
                        name = component.name + "_free_mass"
                        model.add(
                            components.mechanical.FreeMass(name, component.mech, val)
                        )
                    else:
                        setattr(component, attr, val)

        cavities = []
        # Create cavities
        for block, d in blocks.items():
            for cav in d["cavities"]:
                try:
                    comp1 = nodes[cav["node1"]]
                except KeyError:
                    raise KeyError(f"Node '{cav['node11']}' not in model.")
                try:
                    comp2 = nodes[cav["node2"]]
                except KeyError:
                    raise KeyError(f"Node '{cav['node2']}' not in model.")
                node1 = getattr(get_model_element(model, comp1[0]), f"p{comp1[1]}")
                node2 = getattr(get_model_element(model, comp2[0]), f"p{comp2[1]}")

                if comp1[0] != comp2[0]:
                    el = components.Cavity(cav["name"], node1.o, node2.i)
                else:
                    el = components.Cavity(cav["name"], node1.o)

                el._legacy_script_line_number = cav["lineno"]
                model.add(el)
                cavities.append(el)

        gausses = []
        # Gauss commands
        for block, d in blocks.items():
            for gauss in d["gauss"]:
                try:
                    comp = nodes[gauss["node"]]
                except KeyError:
                    raise KeyError(f"Node '{gauss['node']}' not in model.")
                node = getattr(get_model_element(model, comp[0]), f"p{comp[1]}").o
                if gauss["component"] != comp[0]:
                    el = get_model_element(model, gauss["component"])
                    if isinstance(el, components.Space):
                        if node.port.space != el:
                            raise KeyError(
                                f"Invalid node '{gauss['node']}' for component '{gauss['component']}'."
                            )
                        # If a space was specified, flip the direction around
                        node = node.port.i
                    else:
                        raise KeyError(
                            f"Invalid node '{gauss['node']}' for component '{gauss['component']}'."
                        )

                gauss_kwargs = {}
                if "qy_re" in gauss:
                    gauss_kwargs["qx"] = gauss["qx_re"] + 1j * gauss["qx_im"]
                    gauss_kwargs["qy"] = gauss["qy_re"] + 1j * gauss["qy_im"]
                elif "qx_re" in gauss:
                    gauss_kwargs["q"] = gauss["qx_re"] + 1j * gauss["qx_im"]
                elif "w0y" in gauss:
                    gauss_kwargs["w0x"] = gauss["w0x"]
                    gauss_kwargs["zx"] = gauss["zx"]
                    gauss_kwargs["w0y"] = gauss["w0y"]
                    gauss_kwargs["zy"] = gauss["zy"]
                else:
                    gauss_kwargs["w0"] = gauss["w0x"]
                    gauss_kwargs["z"] = gauss["zx"]

                gauss_obj = components.Gauss(gauss["name"], node, **gauss_kwargs)
                model.add(gauss_obj)
                gausses.append(gauss_obj)

        # Want to keep Finesse 2 behaviour as much as possible in legacy parsing, so
        # here we set the priority values of the dependencies based on the order in
        # which the cavities and gausses were parsed to be consistent with Finesse 2
        Ndeps = len(cavities) + len(gausses)
        for i, dep in enumerate(cavities + gausses):
            dep.priority = Ndeps - i

        # Max TEM
        for block, d in blocks.items():
            maxtem = parse_parameter(d["maxtem"])
            if maxtem == "off" or maxtem is None:
                model.switch_off_homs()
            else:
                model.modes(maxtem=maxtem)

        # Phase command
        for block, d in blocks.items():
            model.phase_level = parse_parameter(d["phase"])

        # Lambda command
        for block, d in blocks.items():
            if d["lambda"] is not None:
                model.lambda0 = d["lambda"]

        # Retrace command
        for block, d in blocks.items():
            if d["retrace"] is None or d["retrace"] == "":
                continue
            elif d["retrace"] == "off":
                model.sim_trace_config["retrace"] = False
            else:
                warn(f"Unknown retrace argument '{d['retrace']}'; ignoring")

        # Startnode command
        for block, d in blocks.items():
            if d["startnode"] is not None:
                comp = nodes[d["startnode"]]
                node = getattr(get_model_element(model, comp[0]), f"p{comp[1]}").o
                associated_gauss = model.gausses.get(node)
                if associated_gauss is None:
                    LOGGER.error(
                        "startnode %s does not correspond to any Gauss command.",
                        node.full_name,
                    )

                # Get the current maximum priority (guaranteed to be first dependency)
                max_priority = model.trace_order[0].priority
                # Set the startnode Gauss as the new highest priority
                associated_gauss.priority = max_priority + 1

        # Input TEMs
        for block, d in blocks.items():
            for tem in d["tems"]:
                args = dict(tem)
                component = get_model_element(model, args.pop("component"))
                component.tem(**args)

        # Photo-detector types
        for block, d in blocks.items():
            for pdtype in d["pdtypes"]:
                raise NotImplementedError("This needs fixing to not rely on SplitPD")
                args = dict(pdtype)
                detector = get_model_element(model, args.pop("detector"))

                if not isinstance(detector, detectors.PowerDetector):
                    raise ValueError("Cannot apply pdtype to a non pd detector.")

                name = detector.name
                node = detector.node
                # just getting the first letter of type now (either 'x' or 'y')
                # to create a SplitPD with x-split or y-split beats
                direction = args["type"][0]

                # get the demodulation frequencies and phases
                max_demodulations = 10
                freqs = []
                phases = []
                for i in range(max_demodulations):
                    f = getattr(detector, f"f{i}", None)
                    p = getattr(detector, f"phase{i}", None)

                    if f is not None and f.value is not None:
                        freqs.append(f)
                    if p is not None and p.value is not None:
                        phases.append(p)

                model.remove(detector)
                model.add(
                    detectors.SplitPD(name, node, direction, freqs=freqs, phases=phases)
                )

        # Detector masks
        for block, d in blocks.items():
            for mask in d["masks"]:
                args = dict(mask)
                detector = get_model_element(model, args.pop("detector"))
                detector.add_to_mask(**args)

        analyses = []

        # Xaxis
        camera_replacement = None
        for block, d in blocks.items():
            xaxis = d["xaxis"]
            x2axis = d["x2axis"]
            x3axis = d["x3axis"]
            if xaxis is None:
                continue

            xaxis["steps"] = int(xaxis["steps"])

            if xaxis["component"] in model.alternate_name_map:
                comp = model.alternate_name_map[xaxis["component"]]
            else:
                comp = get_model_element(model, f"{xaxis['component']}")

            # store this before converting with attribute getter below
            # as we want to use this for camera axis sweep checking
            xax_param = xaxis["parameter"]

            # phase1 & f1 for a pd1 have had the 1 removed, so rename them here
            if isinstance(comp, detectors.PowerDetectorDemod1) and xax_param[-1] == "1":
                xax_param = xax_param[:-1]

            xaxis["parameter"] = getattr(comp, xax_param)
            # cannot scan axes of Pixel, this is now done via ScanLine or Image type
            # cameras so we begin the process of transforming to one of these here
            if not (
                isinstance(comp, detectors.camera.Pixel) and xax_param in ("x", "y")
            ):
                model.alternate_name_map["x1"] = xaxis["parameter"].ref
                model.alternate_name_map["mx1"] = -xaxis["parameter"].ref

            del xaxis["component"]

            if xaxis["starred"]:
                xaxis["offset"] = xaxis["parameter"].value
            else:
                xaxis["offset"] = 0

            if isinstance(comp, detectors.camera.Pixel) and xax_param in ("x", "y"):
                LOGGER.info(
                    "Found an xaxis scan over the %s parameter of the "
                    "Pixel detector %s --> Replacing this detector and axis "
                    "sweep with a ScanLine detector.",
                    xax_param,
                    comp.name,
                )

                node = comp.node
                lim = [xaxis["min"], xaxis["max"]]
                npts = xaxis["steps"] + 1
                direction = xax_param

                if hasattr(comp, "f"):
                    f = comp.f.value
                else:
                    f = None

                # remove the Pixel detectors and add a ScanLine detector
                # in replacement of the axis sweep
                model.remove(comp)

                if f is None:
                    camera_replacement = detectors.CCDScanLine(
                        comp.name,
                        node,
                        npts,
                        xlim=lim if direction == "x" else None,
                        ylim=lim if direction == "y" else None,
                    )
                else:
                    camera_replacement = detectors.FieldScanLine(
                        comp.name,
                        node,
                        npts,
                        xlim=lim if direction == "x" else None,
                        ylim=lim if direction == "y" else None,
                        f=f,
                    )
                model.add(camera_replacement)

            if x2axis is None:
                if camera_replacement is None:
                    analyses.append(
                        analysis.actions.Xaxis(
                            xaxis["parameter"],
                            xaxis["scale"],
                            xaxis["min"],
                            xaxis["max"],
                            xaxis["steps"],
                            relative=xaxis["offset"],
                        )
                    )
            else:
                x2axis["steps"] = int(x2axis["steps"])

                if x2axis["component"] in model.alternate_name_map:
                    comp = model.alternate_name_map[x2axis["component"]]
                else:
                    comp = get_model_element(model, f"{x2axis['component']}")

                if isinstance(comp, detectors.camera.ScanLine):
                    if xax_param in ("x", "y") and x2axis["parameter"] in ("x", "y"):
                        LOGGER.info(
                            "Found an x2axis scan over the %s parameter of the previous "
                            "Pixel detector %s --> Replacing the ScanLine detector "
                            "added previously with a ComplexCamera.",
                            xax_param,
                            comp.name,
                        )

                        node = comp.node
                        x1ax_dir = xax_param
                        x2ax_dir = x2axis["parameter"]

                        if x1ax_dir == x2ax_dir:
                            raise ValueError(
                                "Cannot scan the same axis of the beam analyser twice."
                            )

                        if x1ax_dir == "x":
                            xlim = [xaxis["min"], xaxis["max"]]
                            ylim = [x2axis["min"], x2axis["max"]]
                        else:
                            xlim = [x2axis["min"], x2axis["max"]]
                            ylim = [xaxis["min"], xaxis["max"]]

                        npts = xaxis["steps"] + 1

                        if hasattr(comp, "f"):
                            f = comp.f.value
                        else:
                            f = None

                        # remove the ScanLine detector and add a ComplexCamera
                        # in replacement of axes sweeps
                        model.remove(comp)

                        if f is None:
                            camera_replacement = detectors.CCD(
                                comp.name,
                                node,
                                xlim,
                                ylim,
                                npts,
                            )
                        else:
                            camera_replacement = detectors.FieldCamera(
                                comp.name, node, xlim, ylim, npts, f
                            )
                        model.add(camera_replacement)

                else:
                    x2axis["parameter"] = getattr(comp, f"{x2axis['parameter']}")
                    model.alternate_name_map["x2"] = x2axis["parameter"].ref
                    model.alternate_name_map["mx2"] = -x2axis["parameter"].ref

                del x2axis["component"]

                if x2axis["starred"]:
                    x2axis["offset"] = x2axis["parameter"].value
                else:
                    x2axis["offset"] = 0
                if x3axis is None:
                    if camera_replacement is None:
                        analyses.append(
                            analysis.actions.X2axis(
                                xaxis["parameter"],
                                xaxis["scale"],
                                xaxis["min"],
                                xaxis["max"],
                                xaxis["steps"],
                                x2axis["parameter"],
                                x2axis["scale"],
                                x2axis["min"],
                                x2axis["max"],
                                x2axis["steps"],
                            )
                        )
                    elif isinstance(camera_replacement, detectors.camera.ScanLine):
                        analyses.append(
                            analysis.actions.Xaxis(
                                x2axis["parameter"],
                                x2axis["scale"],
                                x2axis["min"],
                                x2axis["max"],
                                x2axis["steps"],
                                relative=x2axis["offset"],
                            )
                        )
                else:
                    x3axis["steps"] = int(x3axis["steps"])

                    if x3axis["component"] in model.alternate_name_map:
                        comp = model.alternate_name_map[x3axis["component"]]
                    else:
                        comp = get_model_element(model, f"{x3axis['component']}")

                    x3axis["parameter"] = getattr(comp, f"{x3axis['parameter']}")
                    model.alternate_name_map["x3"] = x3axis["parameter"].ref
                    model.alternate_name_map["mx3"] = -x3axis["parameter"].ref

                    del x3axis["component"]

                    if x3axis["starred"]:
                        x3axis["offset"] = x3axis["parameter"].value
                    else:
                        x3axis["offset"] = 0

                    if camera_replacement is None:
                        analyses.append(
                            analysis.actions.X3axis(
                                xaxis["parameter"],
                                xaxis["scale"],
                                xaxis["min"],
                                xaxis["max"],
                                xaxis["steps"],
                                x2axis["parameter"],
                                x2axis["scale"],
                                x2axis["min"],
                                x2axis["max"],
                                x2axis["steps"],
                                x3axis["parameter"],
                                x3axis["scale"],
                                x3axis["min"],
                                x3axis["max"],
                                x3axis["steps"],
                            )
                        )
                    elif isinstance(camera_replacement, detectors.camera.ScanLine):
                        analyses.append(
                            analysis.actions.X2axis(
                                x2axis["parameter"],
                                x2axis["scale"],
                                x2axis["min"],
                                x2axis["max"],
                                x2axis["steps"],
                                x3axis["parameter"],
                                x3axis["scale"],
                                x3axis["min"],
                                x3axis["max"],
                                x3axis["steps"],
                            )
                        )
                    elif isinstance(camera_replacement, detectors.camera.Image):
                        analyses.append(
                            analysis.actions.Xaxis(
                                x3axis["parameter"],
                                x3axis["scale"],
                                x3axis["min"],
                                x3axis["max"],
                                x3axis["steps"],
                                relative=x3axis["offset"],
                            )
                        )

        # Yaxis
        for block, d in blocks.items():
            for yaxis in d["yaxis"]:
                if model.yaxis is not None:
                    raise ValueError("Cannot have more than one yaxis command.")
                model.yaxis = yaxis

        # Sets
        for block, d in blocks.items():
            for name, cmd in d["sets"].items():
                comp = get_model_element(model, cmd["component"])
                if isinstance(comp, detectors.Detector):
                    raise ValueError(
                        "Finesse 3 does not support using 'set' with the output of a detector. If "
                        "you are using this in combination with a 'lock' command, please switch "
                        "to the new syntax and use the 'lock' command as defined there."
                    )
                model.alternate_name_map[name] = getattr(
                    get_model_element(model, cmd["component"]), cmd["parameter"]
                )

        # Funcs
        for block, d in blocks.items():
            for name, func in d["functions"].items():
                model.alternate_name_map[name] = parse_parameter(func)

        # Puts
        scanning_im_ax = None
        for block, d in blocks.items():
            for put in d["puts"]:
                value = parse_parameter(put["variable"])
                if put["add"]:
                    component = get_model_element(model, put["component"])
                    param = getattr(component, put["parameter"])
                    setattr(component, put["parameter"], param + value)
                else:
                    component = get_model_element(model, put["component"])

                    if isinstance(component, components.SignalGenerator):
                        setattr(model.fsig, put["parameter"], value)
                    elif isinstance(component, detectors.camera.Pixel):
                        if isinstance(
                            camera_replacement, detectors.camera.ScanLine
                        ) and put["parameter"] in ("x", "y"):
                            model.remove(component)

                            if camera_replacement.direction == "x":
                                npts = camera_replacement.x.shape[0]
                            else:
                                npts = camera_replacement.y.shape[0]

                            if hasattr(component, "f"):
                                model.add(
                                    detectors.FieldScanLine(
                                        component.name,
                                        component.node,
                                        npts,
                                        camera_replacement.x,
                                        camera_replacement.y,
                                        camera_replacement.xlim,
                                        camera_replacement.ylim,
                                        component.f.value,
                                    )
                                )
                            else:
                                model.add(
                                    detectors.CCDScanLine(
                                        component.name,
                                        component.node,
                                        npts,
                                        camera_replacement.x,
                                        camera_replacement.y,
                                        camera_replacement.xlim,
                                        camera_replacement.ylim,
                                    )
                                )

                        elif isinstance(camera_replacement, detectors.camera.Image):
                            if scanning_im_ax is None:
                                scanning_im_ax = put["parameter"]
                                continue
                            elif (
                                scanning_im_ax == "x"
                                and put["parameter"] == "y"
                                or scanning_im_ax == "y"
                                and put["parameter"] == "x"
                            ):
                                model.remove(component)

                                if hasattr(component, "f"):
                                    model.add(
                                        detectors.FieldCamera(
                                            component.name,
                                            component.node,
                                            camera_replacement.x,
                                            camera_replacement.y,
                                            camera_replacement.x.shape[0],
                                            component.f.value,
                                        )
                                    )
                                else:
                                    model.add(
                                        detectors.CCD(
                                            component.name,
                                            component.node,
                                            camera_replacement.x,
                                            camera_replacement.y,
                                            camera_replacement.x.shape[0],
                                        )
                                    )
                            else:
                                setattr(component, put["parameter"], value)
                    else:
                        setattr(component, put["parameter"], value)

        scales = {}
        for block, d in blocks.items():
            for scale in d["scales"]:
                v = scale["value"]
                if isinstance(v, str):
                    import numpy as np

                    s = v.lower()
                    if s == "deg":
                        scale["value"] = 180 / np.pi
                    elif s == "rad":
                        scale["value"] = np.pi / 180
                    elif s == "meter":
                        scale["value"] = 2 * np.pi / model.lambda0
                    else:
                        LOGGER.error(
                            f"Scale type '{v}' not recognised, not performing scaling."
                        )
                        scale["value"] = 1
                comp = scale["component"]
                if comp is not None:
                    if comp in scales:
                        scales[comp] *= scale["value"]
                    else:
                        scales[comp] = scale["value"]
                else:
                    for det in model.detectors:
                        if det.name in scales:
                            scales[det.name] *= scale["value"]
                        else:
                            scales[det.name] = scale["value"]
        if len(scales) > 0:
            analyses[0] = analysis.actions.Serial(
                analyses[0], analysis.actions.Scale("Scale", scales)
            )

        if len(analyses) > 1:
            raise NotImplementedError(
                "Handling multiple analyses for legacy parsing not implemented yet"
            )

        if not analyses:
            analyses.append(analysis.actions.Noxaxis())

        model.analysis = analyses[0]

        def sort(item):
            has = hasattr(item[1], "_legacy_script_line_number")
            return (not has, item[1]._legacy_script_line_number if has else None)

        model.sort_elements(key=sort)

        for el in model.elements.values():
            if hasattr(el, "_legacy_script_line_number"):
                del el._legacy_script_line_number
        return model


class _KatLEX(Lexer):
    """Kat file lexer, default state."""

    tokens = {
        "AMPLITUDE_DETECTOR",
        "ATTRIBUTE",
        "BEAM_DETECTOR",
        "BEAM_PROPERTY_DETECTOR",
        "BEAM_SPLITTER",
        "CAVITY",
        "COMMENT_START",
        "CONSTANT",
        "DIRECTIONAL_BEAM_SPLITTER",
        "SOURCE_FREQUENCY",
        "FTBLOCK_END",
        "FTBLOCK_START",
        "FUNCTION",
        "FSIG",
        "GAUSS",
        "GNUPLOT_START",
        "GOUY",
        "ISOLATOR",
        "LAMBDA",
        "LASER",
        "LENS",
        "LOCK",
        "MASK",
        "MAXTEM",
        "MIRROR",
        "MODULATOR",
        "MOTION_DETECTOR",
        "NOXAXIS",
        "PDTYPE",
        "PHASE",
        "POWER_DETECTOR",
        "PUT",
        "QUANTUM_NOISE_DETECTOR",
        "QUANTUM_SHOT_NOISE_DETECTOR",
        "RETRACE",
        "SCALE",
        "SET",
        "SPACE",
        "SQUEEZER",
        "STARTNODE",
        "TEM",
        "VARIABLE",
        "XAXIS",
        "X2AXIS",
        "X3AXIS",
        "YAXIS",
    }

    @_(
        "color",
        "conf",
        "debug",
        "frequency",
        "gnuterm",
        "noplot",
        "pause",
        "printmatrix",
        "pyterm",
        "showiterate",
        "time",
        "trace",
        "width",
    )
    def obsolete(self, t):
        self.warnings.append(
            (f"Command '{t.value}' is obsolete, ignoring.", self.lineno, 1)
        )
        line = self.text.split("\n")[self.lineno - 1]
        self.index += len(line) - len(t.value)

    @_(
        "multi",
        "pdS",
        "pdN",
        "hd",
        "qd",
        "sd",
        "qhd",
        "qhdS",
        "qhdN",
        "pgaind",
        "fadd",
        "map",
        "knm",
        "smotion",
        "vacuum",
        "tf",
        "tf2",
        "func",
        "diff",
        "deriv_h",
    )
    def not_implemented(self, t):
        self.warnings.append(
            (f"Command '{t.value}' not yet implemented.", self.lineno, 1)
        )
        line = self.text.split("\n")[self.lineno - 1]
        self.index += len(line) - len(t.value)

    # In order to allow components which are substrings of other components
    # (e.g. 'l' and 'lens'), these should be sorted alphabetically and then in
    # length order, such that no string is a substring of one that comes later
    # in the list.
    AMPLITUDE_DETECTOR = r"ad\s"
    ATTRIBUTE = r"attr\s"
    BEAM_SPLITTER = r"(beamsplitter|bs)[1-2]?\s"
    BEAM_DETECTOR = r"beam\s"
    BEAM_PROPERTY_DETECTOR = r"bp\s"
    CAVITY = r"cav(ity)?\s"
    COMMENT_START = r"/\*"
    CONSTANT = r"const\s"
    DIRECTIONAL_BEAM_SPLITTER = r"dbs\s"
    SOURCE_FREQUENCY = r"freq\s"
    FSIG = r"fsig\s"
    FTBLOCK_END = r"FTend"
    FTBLOCK_START = r"FTblock"
    FUNCTION = r"func\s"
    GAUSS = r"gauss\*?\s"
    GNUPLOT_START = r"(?i)GNUPLOT"
    GOUY = r"gouy\s"
    ISOLATOR = r"(isol|diode)\s"
    LAMBDA = r"lambda0?\s"
    LENS = r"lens\s"
    LOCK = r"lock\*?\s"
    LASER = r"(laser|light|l)\s"
    MASK = r"mask\s"
    MAXTEM = r"maxtem\s"
    MODULATOR = r"mod\s"
    MIRROR = r"(mirror|m[1-2]?)\s"
    NOXAXIS = r"noxaxis"
    PDTYPE = r"pdtype\s"
    PHASE = r"phase\s"
    POWER_DETECTOR = r"pd[0-9]*\s"
    PUT = r"put\*?\s"
    QUANTUM_NOISE_DETECTOR = r"qnoisedS?\s"
    QUANTUM_SHOT_NOISE_DETECTOR = r"qshotS?\s"
    RETRACE = r"retrace"
    STARTNODE = r"startnode\s"
    SCALE = r"scale\s"
    SET = r"set\s"
    SQUEEZER = r"sq\s"
    SPACE = r"s\s"
    TEM = r"tem\s"
    VARIABLE = r"variable\s"
    X3AXIS = r"x3axis\*?\s"
    X2AXIS = r"x2axis\*?\s"
    XAXIS = r"xaxis\*?\s"
    MOTION_DETECTOR = r"xd\s"
    YAXIS = r"yaxis\s"

    # Ignored patterns.
    ignore = "[ \t]"
    ignore_comment = "#.*"
    ignore_comment2 = "%((?!FT).)*"

    def __init__(self):
        self.reset()

    def reset(self):
        self.errors = []
        self.warnings = []

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        line = t.value.split("\n")[0]
        command = line.split(" ")[0]
        self.errors.append(
            (f"Command '{command}' unrecognised", self.lineno, self.index)
        )
        self.index += len(line)
        return t

    def eof(self, t):
        print("EOF")

    # Command type tokens.
    def AMPLITUDE_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def ATTRIBUTE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def BEAM_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def BEAM_PROPERTY_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def BEAM_SPLITTER(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def CAVITY(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def COMMENT_START(self, t):
        self.push_state(_KatCommentLEX)

    def CONSTANT(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def DIRECTIONAL_BEAM_SPLITTER(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def SOURCE_FREQUENCY(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def FTBLOCK_START(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def FTBLOCK_END(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def FUNCTION(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def FSIG(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def GAUSS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def GNUPLOT_START(self, t):
        self.push_state(_KatGnuplotLEX)

    def GOUY(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def ISOLATOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def LAMBDA(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def LASER(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def LENS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def LOCK(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def MASK(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def MAXTEM(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def MIRROR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def MODULATOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def MOTION_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def NOXAXIS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def PDTYPE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def PHASE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def POWER_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def PUT(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def QUANTUM_NOISE_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def QUANTUM_SHOT_NOISE_DETECTOR(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def RETRACE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def SCALE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def SET(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def SPACE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def SQUEEZER(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def STARTNODE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def TEM(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def VARIABLE(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def XAXIS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def X2AXIS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def X3AXIS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t

    def YAXIS(self, t):
        self.push_state(_KatComponentLEX)
        t.value = t.value.strip()
        return t


class _KatCommentLEX(Lexer):
    """Kat file lexer, comment state."""

    tokens = {"END"}

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        self.index += 1
        return

    @_(r"\*/")
    def END(self, t):
        self.pop_state()


class _KatGnuplotLEX(_KatCommentLEX):
    """Kat file lexer, gnuplot state."""

    tokens = {"END"}

    @_("END")
    def END(self, t):
        self.pop_state()


class _KatComponentLEX(Lexer):
    """Kat file lexer, component state."""

    tokens = {"FUNCTIONSTRING", "NUMBER", "STRING"}
    # Top level tokens.
    FUNCTIONSTRING = r"=[^=\n#]+"

    ignore = " \t"
    ignore_comment = r"\#.*"
    ignore_comment2 = "%.*"

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")
        self.pop_state()

    @_(r"[$0-9\-+*(][a-zA-Z0-9_\-+*$().]+")
    def NUM_PARAM(self, t):
        if "$" not in t.value:
            # This is a number
            t.type = "NUMBER"
            return self.NUMBER(t)
        t.type = "NUMBER"
        return t

    # Number token including scientific notation, float,
    # or +/- inf (all states). Alternatively, any string starting with $
    @_(
        r"[+-]?inf",
        r"[+-]?(\d+\.\d*|\d*\.\d+|\d+)([eE]-?\d*\.?\d*)?([pnumkMGT])?",
        r"\$[.\s]+",
    )
    def NUMBER(self, t):
        if t.value.startswith("$"):
            return t
        if re.match(".*[pnumkMGT]$", t.value):
            t.value = t.value.replace("p", "e-12")
            t.value = t.value.replace("n", "e-9")
            t.value = t.value.replace("u", "e-6")
            t.value = t.value.replace("m", "e-3")
            t.value = t.value.replace("k", "e3")
            t.value = t.value.replace("M", "e6")
            t.value = t.value.replace("G", "e9")
            t.value = t.value.replace("T", "e12")

        # Check for numbers ending in "e", like "1e", which Python's float cannot handle.
        if t.value.endswith("e"):
            t.value += "0"

        if "j" in t.value:
            t.value = complex(t.value)
        else:
            t.value = float(t.value)
            if t.value.is_integer():
                t.value = int(t.value)
        return t

    @_(r"[a-zA-Z_][a-zA-Z0-9_:+-]*\*?", "inf")
    def STRING(self, t):
        if t.value == "inf":
            t.type = "NUMBER"
            return self.NUMBER(t)
        return t

    def error(self, t):
        line = t.value.split("\n")[0].split(" ")[0]
        self.errors.append(
            (f"Illegal character '{t.value[0]}'", self.lineno, self.index)
        )
        self.index += len(line)
        return t


class _KatYACC(Parser):
    """Kat file parser."""

    tokens = set.union(_KatLEX.tokens, _KatComponentLEX.tokens)
    tokens.remove("COMMENT_START")
    tokens.remove("GNUPLOT_START")

    # Setting STRING and NUMBER to have the same precedence and be right-associative solves the
    # shift/reduce conflict caused by the frequency_list rule in favour of shifting. We must then
    # be careful to extract the final string, as for e.g. the powerdetector, this is actually a
    # node name, not a phase.
    precedence = (("right", "STRING", "NUMBER"),)

    def __init__(self):
        self.reset()

    def reset(self):
        """Delete all parsed code, resetting the parser to a newly constructed state."""
        self.noxaxis = False
        self.block = None
        self.blocks = OrderedDict()
        self.blocks[self.block] = self._default_components()
        self.errors = []

    def _default_components(self):
        return {
            # Default simulation components.
            "lasers": [],
            "spaces": [],
            "mirrors": [],
            "beamsplitters": [],
            "directional_beamsplitters": [],
            "isolators": [],
            "modulators": [],
            "lenses": [],
            "amplitude_detectors": [],
            "beam_detectors": [],
            "beam_property_detectors": [],
            "gouy": [],
            "motion_detectors": [],
            "power_detectors": [],
            "quantum_noise_detectors": [],
            "cavities": [],
            "squeezers": [],
            # Non-component commands
            "frequencies": [],
            "constants": {},
            "attributes": {},
            "variables": {},
            "functions": {},
            "sets": {},
            "fsigs": [],
            "gauss": [],
            "locks": [],
            "puts": [],
            "pdtypes": [],
            "maxtem": None,
            "phase": 3,
            "retrace": None,
            "startnode": None,
            "scales": [],
            "tems": [],
            "masks": [],
            "xaxis": None,
            "x2axis": None,
            "x3axis": None,
            "yaxis": [],
            "lambda": None,
        }

    @_("instruction", "statement instruction")
    def statement(self, p):
        pass

    # List of one or more numbers
    @_("NUMBER", "number_list NUMBER")
    def number_list(self, p):
        if len(p) == 1:
            return [p.NUMBER]
        else:
            p.number_list.append(p.NUMBER)
            return p.number_list

    # List of one or more strings
    @_("STRING", "string_list STRING")
    def string_list(self, p):
        if len(p) == 1:
            return [p.STRING]
        else:
            p.string_list.append(p.STRING)
            return p.string_list

    # List of frequency-phase pairs
    @_(
        "NUMBER STRING",
        "NUMBER NUMBER",
        "frequency_list NUMBER STRING",
        "frequency_list NUMBER NUMBER",
    )
    def frequency_list(self, p):
        if len(p) == 2:
            return [[p[0], p[1]]]
        else:
            p.frequency_list.append([p[1], p[2]])
            return p.frequency_list

    # List of attribute-value pairs
    @_("STRING NUMBER", "attribute_list STRING NUMBER")
    def attribute_list(self, p):
        if len(p) == 2:
            return [[p.STRING, p.NUMBER]]
        else:
            p.attribute_list.append([p.STRING, p.NUMBER])
            return p.attribute_list

    # Frequencies can either be a number or a combination of source frequencies
    @_("NUMBER")
    def freq_num(self, p):
        return p[0]

    @_("FTBLOCK_START STRING")
    def instruction(self, p):
        if self.block is not None:
            warn(f"Already in FTblock {self.block}")
        if p.STRING in self.blocks:
            warn(f"Duplicate FTblock {p.STRING}")
        self.block = p.STRING
        self.blocks[self.block] = self._default_components()

    @_("FTBLOCK_END STRING")
    def instruction(self, p):
        if self.block != p.STRING:
            message = (
                f"Invalid command 'FTend {p.STRING}': currently in "
                f"FTblock '{self.block}'"
            )
            self.errors.append((message, p.lineno, p.index))
        self.block = None

    @_("SOURCE_FREQUENCY STRING NUMBER")
    def instruction(self, p):
        params = ["name", "f"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["frequencies"].append(dict(zip(params, values)))

    @_("LASER STRING NUMBER freq_num optnum STRING")
    def instruction(self, p):
        # Phase not specified.
        if p[4] is None:
            p[4] = 0

        params = ["name", "P", "f", "phase", "node"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["lasers"].append(dict(zip(params, values)))
        self.blocks[block]["lasers"][-1]["lineno"] = p.lineno

    @_("SQUEEZER STRING freq_num NUMBER NUMBER STRING")
    def instruction(self, p):
        params = ["name", "f", "db", "angle", "node"]
        values = [p[i] for i in range(1, len(p))]

        # Some minor rearranging required here to match the component constructor
        params.insert(2, params.pop(1))
        values.insert(2, values.pop(1))

        block = self.block
        self.blocks[block]["squeezers"].append(dict(zip(params, values)))
        self.blocks[block]["squeezers"][-1]["lineno"] = p.lineno

    @_("SPACE STRING NUMBER optnum STRING STRING")
    def instruction(self, p):
        params = ["name", "L", "nr", "node1", "node2"]
        values = [p[i] for i in range(1, len(p))]

        if values[2] is None:
            # Index of refraction not specified.
            # TODO:phil: should we be specifying 1 as the default here, or
            # checking for None in the space constructor later?
            values[2] = 1

        block = self.block
        self.blocks[block]["spaces"].append(dict(zip(params, values)))
        self.blocks[block]["spaces"][-1]["lineno"] = p.lineno

    @_("MIRROR STRING NUMBER NUMBER NUMBER STRING STRING")
    def instruction(self, p):
        params = ["name", "R", "T", "L", "phi", "node1", "node2"]
        values = [p[i] for i in range(1, len(p))]

        if p[0] == "m":
            # R / T
            values.insert(3, None)
        elif p[0] == "m1":
            # T / Loss.
            values.insert(1, None)
        elif p[0] == "m2":
            # R / Loss.
            values.insert(2, None)

        block = self.block
        self.blocks[block]["mirrors"].append(dict(zip(params, values)))
        self.blocks[block]["mirrors"][-1]["lineno"] = p.lineno

    @_("BEAM_SPLITTER STRING NUMBER NUMBER NUMBER NUMBER STRING STRING STRING STRING")
    def instruction(self, p):
        params = [
            "name",
            "R",
            "T",
            "L",
            "phi",
            "alpha",
            "node1",
            "node2",
            "node3",
            "node4",
        ]
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("2"):
            # R / Loss.
            values.insert(2, None)
        elif p[0].endswith("1"):
            # T / Loss.
            values.insert(1, None)
        else:
            # R / T
            values.insert(3, None)

        block = self.block
        self.blocks[block]["beamsplitters"].append(dict(zip(params, values)))
        self.blocks[block]["beamsplitters"][-1]["lineno"] = p.lineno

    @_("DIRECTIONAL_BEAM_SPLITTER STRING STRING STRING STRING STRING")
    def instruction(self, p):
        params = ["name", "node1", "node2", "node3", "node4"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["directional_beamsplitters"].append(
            dict(zip(params, values))
        )
        self.blocks[block]["directional_beamsplitters"][-1]["lineno"] = p.lineno

    @_("ISOLATOR STRING NUMBER STRING STRING")
    def instruction(self, p):
        params = ["name", "S", "node1", "node2"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["isolators"].append(dict(zip(params, values)))
        self.blocks[block]["isolators"][-1]["lineno"] = p.lineno

    @_(
        "MODULATOR STRING freq_num NUMBER NUMBER STRING optnum STRING STRING",
        "MODULATOR STRING freq_num NUMBER STRING STRING optnum STRING STRING",
    )
    def instruction(self, p):
        params = ["name", "f", "midx", "order", "type", "phase", "node1", "node2"]
        values = [p[i] for i in range(1, len(p))]

        # TODO:phil: is no phase actually the same as 0 phase?
        if values[5] is None:
            values[5] = 0

        if values[3] == "s":
            values[3] = 1
            params.append("positive_only")
            values.append(True)

        block = self.block
        self.blocks[block]["modulators"].append(dict(zip(params, values)))
        self.blocks[block]["modulators"][-1]["lineno"] = p.lineno

    @_("LENS STRING NUMBER STRING STRING")
    def instruction(self, p):
        params = ["name", "f", "node1", "node2"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["lenses"].append(dict(zip(params, values)))
        self.blocks[block]["lenses"][-1]["lineno"] = p.lineno

    @_(
        "AMPLITUDE_DETECTOR STRING NUMBER NUMBER freq_num STRING",
        "AMPLITUDE_DETECTOR STRING freq_num STRING",
    )
    def instruction(self, p):
        params = ["name", "n", "m", "f", "node"]
        values = [p[i] for i in range(1, len(p))]

        if len(values) == 3:
            # Mode numbers not specified.
            values.insert(1, None)
            values.insert(2, None)

        block = self.block
        self.blocks[block]["amplitude_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["amplitude_detectors"][-1]["lineno"] = p.lineno

    @_("BEAM_DETECTOR STRING optnum STRING")
    def instruction(self, p):
        params = ["name", "f", "node"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["beam_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["beam_detectors"][-1]["lineno"] = p.lineno

    @_("BEAM_PROPERTY_DETECTOR STRING STRING STRING STRING")
    def instruction(self, p):
        params = ["name", "direction", "prop", "node"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["beam_property_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["beam_property_detectors"][-1]["lineno"] = p.lineno

    @_("GOUY STRING STRING string_list")
    def instruction(self, p):
        params = ["name", "direction", "space_list"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["gouy"].append(dict(zip(params, values)))
        self.blocks[block]["gouy"][-1]["lineno"] = p.lineno

    @_("MOTION_DETECTOR STRING STRING STRING")
    def instruction(self, p):
        params = ["name", "component", "motion"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["motion_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["motion_detectors"][-1]["lineno"] = p.lineno

    @_(
        "POWER_DETECTOR STRING STRING",
        "POWER_DETECTOR STRING frequency_list optstr",
        "POWER_DETECTOR STRING number_list STRING",
    )
    def instruction(self, p):
        # Parameters shared by all photodetectors.
        params = ["name", "node"]
        values = [p[i] for i in range(1, len(p))]

        ps = ["f{}", "phase{}"]
        if len(values) == 3:
            try:
                p.number_list
                for n in range(len(values[1])):
                    params.insert(n + 1, ps[n % 2].format(n // 2 + 1))
                values = [values[0], *values[1], values[2]]
            except AttributeError:
                if p.optstr is None:
                    # We've grabbed the node as part of the frequency list, so put it back in the
                    # right place
                    values[2] = values[1][-1].pop()
                for n in range(len(values[1])):
                    for m in range(len(values[1][n])):
                        params.insert(2 * n + m + 1, ps[m].format(n + 1))
                values = [
                    values[0],
                    *[param for pair in values[1] for param in pair],
                    values[2],
                ]

        block = self.block
        self.blocks[block]["power_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["power_detectors"][-1]["lineno"] = p.lineno

    @_(
        "QUANTUM_NOISE_DETECTOR STRING number_list STRING",
    )
    def instruction(self, p):
        # Parameters shared by all quantum noise detectors.
        params = ["name", "node"]
        values = [p[i] for i in range(1, len(p))]

        ps = ["f{}", "phase{}"]
        # Strip last demodulation, as this should always be at the signal frequency
        nf = len(values[1]) // 2 - 1
        for n in range(2 * nf):
            params.insert(n + 1, ps[n % 2].format(n // 2 + 1))
        values = [values[0], *values[1][1 : 2 * nf + 1], values[2]]

        params.insert(-1, "shot_only")
        values.insert(-1, False)

        params.insert(-1, "nsr")
        values.insert(-1, p[0].endswith("S"))

        block = self.block
        self.blocks[block]["quantum_noise_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["quantum_noise_detectors"][-1]["lineno"] = p.lineno

    @_(
        "QUANTUM_SHOT_NOISE_DETECTOR STRING number_list STRING",
    )
    def instruction(self, p):
        # Parameters shared by all quantum noise detectors.
        params = ["name", "node"]
        values = [p[i] for i in range(1, len(p))]

        ps = ["f{}", "phase{}"]
        # Strip last demodulation, as this should always be at the signal frequency
        nf = len(values[1]) // 2 - 1
        for n in range(2 * nf):
            params.insert(n + 1, ps[n % 2].format(n // 2 + 1))
        values = [values[0], *values[1][1 : 2 * nf + 1], values[2]]

        params.insert(-1, "shot_only")
        values.insert(-1, True)

        params.insert(-1, "nsr")
        values.insert(-1, p[0].endswith("S"))

        block = self.block
        self.blocks[block]["quantum_noise_detectors"].append(dict(zip(params, values)))
        self.blocks[block]["quantum_noise_detectors"][-1]["lineno"] = p.lineno

    @_("CAVITY STRING STRING STRING STRING STRING")
    def instruction(self, p):
        params = ["name", "component1", "node1", "component2", "node2"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["cavities"].append(dict(zip(params, values)))
        self.blocks[block]["cavities"][-1]["lineno"] = p.lineno

    @_("CONSTANT STRING NUMBER", "CONSTANT STRING STRING")
    def instruction(self, p):
        name = p[1]
        val = p[2]

        block = self.block
        self.blocks[block]["constants"]["$" + name] = val

    @_("ATTRIBUTE STRING attribute_list")
    def instruction(self, p):
        comp = p[1]
        attrs = p[2]

        block = self.block
        if comp in self.blocks[block]["attributes"]:
            self.blocks[block]["attributes"][comp].extend(attrs)
        else:
            self.blocks[block]["attributes"][comp] = attrs

    @_("VARIABLE STRING NUMBER", "VARIABLE STRING STRING")
    def instruction(self, p):
        name = p[1]
        value = p[2]

        block = self.block
        self.blocks[block]["variables"][name] = value

    @_("FUNCTION STRING FUNCTIONSTRING")
    def instruction(self, p):
        name = p[1]
        function_string = p[2]

        # Trim the starting "=" from the function string, and any whitespace
        block = self.block
        self.blocks[block]["functions"][name] = function_string[1:].strip()

    @_("FSIG STRING STRING optstr freq_num NUMBER optnum", "FSIG STRING NUMBER")
    def instruction(self, p):
        if len(p) == 3:
            params = ["name", "f"]
            values = [p[i] for i in range(1, len(p))]

            block = self.block
            self.blocks[block]["fsigs"].append(dict(zip(params, values)))
        else:
            if p.optnum is None:
                # Set default amplitude to 1
                p[-1] = 1
            params = ["name", "component", "mod_type", "f", "phase", "amp"]
            values = [p[i] for i in range(1, len(p))]

            block = self.block
            self.blocks[block]["fsigs"].append(dict(zip(params, values)))

    @_("LOCK STRING NUMBER NUMBER NUMBER")
    def instruction(self, p):
        params = ["name", "variable", "gain", "accuracy", "starred"]
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("*"):
            values.append(True)
        else:
            values.append(False)
        block = self.block
        self.blocks[block]["locks"].append(dict(zip(params, values)))

    @_(
        "GAUSS STRING STRING STRING NUMBER NUMBER",
        "GAUSS STRING STRING STRING NUMBER NUMBER NUMBER NUMBER",
    )
    def instruction(self, p):
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("*"):
            params = ["name", "component", "node", "qx_re", "qx_im", "qy_re", "qy_im"]
        else:
            params = ["name", "component", "node", "w0x", "zx", "w0y", "zy"]

        block = self.block
        self.blocks[block]["gauss"].append(dict(zip(params, values)))

    @_("PUT STRING STRING NUMBER")
    def instruction(self, p):
        params = ["component", "parameter", "variable", "add"]
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("*"):
            values.append(True)
        else:
            values.append(False)
        block = self.block
        self.blocks[block]["puts"].append(dict(zip(params, values)))

    @_("SCALE NUMBER optstr", "SCALE STRING optstr")
    def instruction(self, p):
        params = ["value", "component"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["scales"].append(dict(zip(params, values)))

    @_("SET STRING STRING STRING")
    def instruction(self, p):
        name = p[1]
        params = ["component", "parameter"]
        values = [p[i] for i in range(2, len(p))]

        block = self.block
        self.blocks[block]["sets"][name] = dict(zip(params, values))

    @_("PDTYPE STRING STRING")
    def instruction(self, p):
        params = ["detector", "type"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["pdtypes"].append(dict(zip(params, values)))

    @_("MAXTEM NUMBER", "MAXTEM STRING")
    def instruction(self, p):
        block = self.block
        self.blocks[block]["maxtem"] = p[1]

    @_("PHASE NUMBER")
    def instruction(self, p):
        block = self.block
        self.blocks[block]["phase"] = p[1]

    @_("RETRACE optstr")
    def instruction(self, p):
        block = self.block
        self.blocks[block]["retrace"] = p[1] or ""

    @_("STARTNODE STRING")
    def instruction(self, p):
        block = self.block
        self.blocks[block]["startnode"] = p[1]

    @_("TEM STRING NUMBER NUMBER NUMBER NUMBER")
    def instruction(self, p):
        params = ["component", "n", "m", "factor", "phase"]
        values = [p[i] for i in range(1, len(p))]

        block = self.block
        self.blocks[block]["tems"].append(dict(zip(params, values)))

    @_("MASK STRING NUMBER NUMBER NUMBER")
    def instruction(self, p):
        params = ["detector", "modes", "factor"]
        values = [p[1], (p[2], p[3]), p[4]]

        block = self.block
        # ignoring factor as masks in Finesse 3 just zero the given field
        self.blocks[block]["masks"].append(dict(zip(params[:-1], values[:-1])))

    @_("LAMBDA NUMBER")
    def instruction(self, p):
        block = self.block
        self.blocks[block]["lambda"] = p.NUMBER

    @_("NOXAXIS")
    def instruction(self, p):
        self.noxaxis = True

    @_("XAXIS STRING STRING STRING NUMBER NUMBER NUMBER")
    def instruction(self, p):
        params = ["component", "parameter", "scale", "min", "max", "steps", "starred"]
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("*"):
            values.append(True)
        else:
            values.append(False)

        block = self.block
        self.blocks[block]["xaxis"] = dict(zip(params, values))

    @_("X2AXIS STRING STRING STRING NUMBER NUMBER NUMBER")
    def instruction(self, p):
        params = ["component", "parameter", "scale", "min", "max", "steps", "starred"]
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("*"):
            values.append(True)
        else:
            values.append(False)

        block = self.block
        self.blocks[block]["x2axis"] = dict(zip(params, values))

    @_("X3AXIS STRING STRING STRING NUMBER NUMBER NUMBER")
    def instruction(self, p):
        params = ["component", "parameter", "scale", "min", "max", "steps", "starred"]
        values = [p[i] for i in range(1, len(p))]

        if p[0].endswith("*"):
            values.append(True)
        else:
            values.append(False)

        block = self.block
        self.blocks[block]["x3axis"] = dict(zip(params, values))

    # TODO: placing the optstr before the STRING like in Finesse 2 causes a
    # shift/reduce conflict - can we solve this?
    @_("YAXIS STRING optstr")
    def instruction(self, p):
        params = ["scale", "axes"]
        values = [p[i] for i in range(1, len(p))]

        if values[1] is None:
            values.insert(0, "lin")

        block = self.block
        self.blocks[block]["yaxis"].append(dict(zip(params, values)))

    def error(self, p):
        if p is None:
            msg = "Unexpected end of file"
            self.errors.append((msg, None, None))
            return
        elif p.type == "ERROR":
            return
        msg = f"got unexpected token {p.value} of type {p.type}"
        self.errors.append((msg, p.lineno, p.index))

    @_("")
    def empty(self, p):
        pass

    @_("STRING")
    def optstr(self, p):
        return p.STRING

    @_("empty")
    def optstr(self, p):
        pass

    @_("NUMBER")
    def optnum(self, p):
        return p.NUMBER

    @_("empty")
    def optnum(self, p):
        pass


class KatParserError(ValueError):  # __NODOC__
    """Kat file parser error."""

    def __init__(self, errors, text, **kwargs):
        message = "\n"
        for error in errors:
            lineno = error[1]
            idx = error[2]
            if lineno is None:
                # There is no lineno, as this was an end-of-file error,
                # so assume error was on last non-empty lin
                line = re.findall(r"[^\s]", text)[-1]
                pos = len(text) - 1
            else:
                line = text.split("\n")[lineno - 1]
                pos = find_column(text, idx)
            expected = ""
            for pattern, exp in self.expected.items():
                if exp is not None and re.match(pattern, line) is not None:
                    expected = f", expected '{exp}'"
                    break
            message += f"{lineno}:{pos}: " + error[0] + expected + "\n"
            message += line + "\n"
            message += " " * (pos - 1) + "^\n"

        super().__init__(message.rstrip("\n"), **kwargs)

    expected = {
        r"ad\s": "ad name [n m] f node[*]",
        r"attr\s": "attr component parameter value",
        r"beam\s": "beam name [f] node[*]",
        r"bp\s": "bp name x/y parameter node",
        r"bs2\s": "bs2 name R L phi alpha node1 node2 node3 node4",
        r"bs1\s": "bs1 name T L phi alpha node1 node2 node3 node4",
        r"bs\s": "bs name R T phi alpha node1 node2 node3 node4",
        r"cav\s": "cav name component1 node component2 node",
        r"const\s": "const name value",
        r"dbs\s": "dbs name node1 node2 node3 node4",
        r"freq\s": None,
        r"FTblock": "FTblock name",
        r"FTend": "FTend name",
        r"func\s": "func name = function-string",
        r"fsig\s": ("fsig name component [type] f phase [amp]", "fsig name f"),
        r"gauss*\s": "gauss* name component node q [qy]",
        r"gauss\s": "gauss name component node w0 z [wy0 zy]",
        r"gouy\s": "gouy name x/y space-list",
        r"isol\s": "isol name S [Loss] node1 node2 [node3]",
        r"lambda\s": "lambda wavelength",
        r"lock\s": "lock name function/set gain accuracy [offset]",
        r"lens\s": "lens name f node1 node2",
        r"l\s": "l name I f [phase] node",
        r"maxtem\s": "maxtem order",
        r"mod\s": "mod name f midx order am/pm/yaw/pitch node1 node2",
        r"m2\s": "m2 name R L phi node1 node2",
        r"m1\s": "m1 name T L phi node1 node2",
        r"m\s": "m name R T phi node1 node2",
        r"noxaxis": None,
        r"pd\s": "pd[n] name [f1 [phase1 [f2 [phase2 [...] ] ] ] ] node[*]",
        r"phase\s": "phase 0-7",
        r"put\s": "put component parameter function/set/axis",
        r"qnoised\s": "qnoised name num_demods f1 phase1 [f2 phase2 [...]] node[*]",
        r"qshot\s": "qshot name num_demods f1 phase1 [f2 phase2 [...]] node[*]",
        r"retrace": "retrace [off|force]",
        r"s\s": "s name L [n] node1 node2",
        r"tem\s": "tem input n m factor phase",
        r"variable\s": "variable name value",
        r"xaxis\s": "xaxis component parameter lin/log min max steps",
        r"x2axis\s": "x2axis component parameter lin/log min max steps",
        r"yaxis\s": "yaxis [lin/log] abs:deg/db:deg/re:im/abs/db/deg",
    }


def find_column(text, index):  # __NODOC__
    last_cr = text.rfind("\n", 0, index)
    if last_cr < 0:
        last_cr = 0
    column = index - last_cr
    return column
