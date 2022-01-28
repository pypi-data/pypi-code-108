"""A sub-module containing the configuration container class :class:`.Model` which is
used for building and manipulating interferometer systems."""

from collections import OrderedDict, defaultdict
from copy import copy, deepcopy
import inspect
import math
from numbers import Number
import weakref
import logging
from contextlib import contextmanager
from functools import wraps
import warnings

import numpy as np
import networkx as nx
from deprecated import deprecated

from .config import config_instance
from .components import (
    Port,
    NodeDirection,
    Connector,
    Space,
    Surface,
    FrequencyGenerator,
    Cavity,
    Wire,
    Gauss,
)
from .components.general import InteractionType
from .components.readout import _Readout
from .components.dof import DegreeOfFreedom
from .components.general import CouplingType
from .components.node import NodeType, OpticalNode, Node, SignalNode
from .components.trace_dependency import TraceDependency
from . import detectors
from .element import ModelElement
from .env import warn
from .exceptions import (
    FinesseException,
    NodeException,
    ComponentNotConnected,
    BeamTraceException,
    ModelAttributeError,
    ContextualValueError,
)
from .freeze import canFreeze, Freezable
from .frequency import Fsig
from .gaussian import BeamParam, transform_beam_param
from .locks import Lock
from .paths import OpticalPath
from .tree import TreeNode
from .solutions import BaseSolution, BeamTraceSolution
from .tracing.forest import TraceForest
from .tracing import tools as tracetools
from .utilities import valid_name, pairwise, ngettext, is_iterable
from .utilities.components import refractive_index
from .utilities.homs import make_modes, insert_modes, remove_modes
from .warnings import ModelParameterSettingWarning, CavityUnstableWarning
from .simulations.base import ModelSettings


def locked_when_built(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.is_built:
            raise Exception(
                f"Model has been built for a simulation, cannot use {func} here"
            )
        return func(self, *args, **kwargs)

    return wrapper


LOGGER = logging.getLogger(__name__)


class IOMatrix:
    def __init__(self, model):
        self._model = model
        self._terms = {}

    def clear(self):
        self._terms.clear()

    def _check_key(a, b):
        raise NotImplementedError()

    def __getitem__(self, key):
        if type(key) is tuple:
            if key[0] in self._terms:
                return self._terms[key[0]][key[1]]
            else:
                raise KeyError(f"{key[0]} not in Matrix")
        else:
            if key in self._terms:
                return self._terms[key]
            else:
                raise KeyError(f"{key} not in Matrix")

    def __setitem__(self, key, value):
        if len(key) != 2:
            raise Exception("Expected pair of string names as key")

        a, b = key
        if key[0] not in self._terms:
            self._terms[key[0]] = {}
        self._terms[key[0]][key[1]] = value

    def __bool__(self):
        return bool(self._terms)


class OutputMatrix(IOMatrix):
    def _check_key(self, a, b):
        if not isinstance(a, _Readout):
            raise Exception(f"First index should be a Readout element name not `{a}`")
        if not isinstance(b, DegreeOfFreedom):
            raise Exception(
                f"Second index should be a DegreeOfFreedom element name not `{a}`"
            )


class InputMatrix(IOMatrix):
    def _check_key(self, a, b):
        if not isinstance(a, DegreeOfFreedom):
            raise Exception(
                f"First index should be a DegreeOfFreedom element name not `{a}`"
            )
        if not isinstance(b, _Readout):
            raise Exception(f"Second index should be a Readout element name not `{a}`")


class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x
    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()
    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)

    Notes
    -----
    Code from https://stackoverflow.com/questions/1092531/event-system-in-python
    """

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)


@canFreeze
class Model:
    """Optical configuration class for handling models of interferometers.

    This class stores the interferometer configuration as a directed graph and contains
    methods to interface with this data structure.
    """

    def __init__(self):
        # The model graph.
        self.__network = nx.DiGraph()
        # The optical graph. We need to store optical network separately for tracing
        # correct paths through optical-optical couplings only.
        self.__opt_net_view = nx.subgraph_view(
            self.__network,
            filter_edge=lambda i, o: self.__network[i][o]["coupling_type"]
            == CouplingType.OPTICAL_TO_OPTICAL,
        )
        # The syntax used to build the model, if parsed from KatScript.
        self.syntax_graph = None
        self.__is_built = False
        # Some simple events that occur within the model that elements can register
        # themselves with.
        self._on_pre_build = Event()  # Called just before a simulation is built.
        self._on_unbuild = Event()  # Called after unbuild() has been completed.

        # Components and detectors.
        self.__cavities = OrderedDict()
        self.__components = OrderedDict()
        self.__detectors = OrderedDict()
        self.__locks = OrderedDict()
        self.__lock_model_change = False
        self.__not_removable = set()

        # Frequency storage.
        self.__frequencies = set()
        self.__frequency_change_callbacks = []
        self.__freq_map = None
        self._frequency_generators = []
        # internal dict to store mode() call args for unparsing
        self.__mode_setting = {}
        self.alternate_name_map = {}

        # Storage class for all the model settings that affects the output of a
        # simulation.
        self._settings = ModelSettings()

        # Higher order mode related attributes.
        self._settings.homs = np.zeros(1, dtype=(np.intc, 2))  # [(0, 0)]
        self._settings.is_modal = False
        self._settings.phase_config.zero_k00 = True
        self._settings.phase_config.zero_tem00_gouy = True
        self._settings.phase_config.v2_transmission_phase = True

        # Constants.
        config_consts = config_instance()["constants"]
        self._settings.set_lambda0(config_consts.getfloat("lambda0"))
        # Ratio of epsilon_0/c, used in converting between power and optical fields.
        # Typically use just renormalise and use 1, putting optical fields in units of
        # sqrt{W}.
        self._settings.EPSILON0_C = 1
        self._settings.UNIT_VACUUM = 1
        self._settings.x_scale = config_consts.getfloat("x_scale")

        # Beam tracing attributes.
        self.__gausses = {}
        self.__last_trace = None
        self.__trace_order = []  # Order of TraceDependency objects for beam tracing
        # Get argument names and values from beam_trace method and set the default
        # simulation tracing config dict with these
        self.__default_sim_trace_config = {
            arg: value.default
            for arg, value in inspect.signature(self.beam_trace).parameters.items()
        }
        self.__default_sim_trace_config["retrace"] = True
        self.__default_sim_trace_config["unstable_handling"] = "auto"
        self.__sim_trace_config = self.__default_sim_trace_config.copy()
        self.__trace_forest = TraceForest(self, self.sim_trace_config["symmetric"])
        self._rebuild_trace_forest = True

        # The root action.
        self.__analysis = None
        self.__inmtx_dc = InputMatrix(self)
        self.yaxis = None

        self.force_refill = False

        # List of all model elements.
        self.__elements = OrderedDict()

        # Models always have a signal element.
        self.add(Fsig("fsig", None), unremovable=True)

        self._freeze()

    def info(
        self,
        modes=True,
        components=True,
        detectors=True,
        cavities=True,
        locks=True,
    ):
        """Get string containing information about this model.

        Parameters
        ----------
        modes, components, detectors, cavities, locks : bool, optional
            Show model component information.

        Returns
        -------
        str
            The model information.
        """
        from .utilities import format_section, format_bullet_list

        pieces = []

        if modes:
            pieces.append(
                format_section(
                    ngettext(len(self.homs), "{n} optical mode", "{n} optical modes"),
                    format_bullet_list(self.homs),
                )
            )

        if components:
            pieces.append(
                format_section(
                    ngettext(len(self.components), "{n} component", "{n} components"),
                    format_bullet_list(self.components),
                )
            )

        if detectors:
            pieces.append(
                format_section(
                    ngettext(len(self.detectors), "{n} detector", "{n} detectors"),
                    format_bullet_list(self.detectors),
                )
            )

        if cavities:
            pieces.append(
                format_section(
                    ngettext(len(self.cavities), "{n} cavity", "{n} cavities"),
                    format_bullet_list(self.cavities),
                )
            )

        if locks:
            pieces.append(
                format_section(
                    ngettext(len(self.locks), "{n} locking loop", "{n} locking loops"),
                    format_bullet_list(self.locks),
                )
            )

        text = str(self) + "\n\n" + "\n".join(pieces)

        return text

    def deepcopy(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        new = object.__new__(type(self))
        memo[id(self)] = new
        new.after_deepcopy = []

        # fields to exclude from copying straight away
        # -> see below for cavities
        # -> TraceForest instances are non-copyable by design so
        #    new model must rebuild its trace_forest by itself
        exclude = [
            "_Model__cavities",
            "_Model__trace_forest",
        ]
        sdict = {}
        for k, v in self.__dict__.items():
            if k in exclude:
                sdict[k] = None
            else:
                sdict[k] = v

        # need to ensure cavities are copied after everything else otherwise
        # the copy operations on the source and target nodes may result in
        # key errors on the memo as the new nodes haven't been created yet
        cdict = {"_Model__cavities": self.__dict__["_Model__cavities"]}

        new.__dict__.update(deepcopy(sdict, memo))
        new.__dict__.update(deepcopy(cdict, memo))

        # update all the weakrefs we have in the network
        for n in new.network.nodes:
            new.network.nodes[n]["weakref"] = weakref.ref(
                memo[id(self.network.nodes[n]["weakref"]())]
            )
            new.network.nodes[n]["owner"] = weakref.ref(
                memo[id(self.network.nodes[n]["owner"]())]
            )

        for e in new.network.edges:
            new.network.edges[e]["in_ref"] = weakref.ref(
                memo[id(self.network.edges[e]["in_ref"]())]
            )
            new.network.edges[e]["out_ref"] = weakref.ref(
                memo[id(self.network.edges[e]["out_ref"]())]
            )
            new.network.edges[e]["owner"] = weakref.ref(
                memo[id(self.network.edges[e]["owner"]())]
            )

        new.__opt_net_view = nx.subgraph_view(
            new.network,
            filter_edge=lambda i, o: new.network[i][o]["coupling_type"]
            == CouplingType.OPTICAL_TO_OPTICAL,
        )
        new.__trace_forest = TraceForest(new, self.sim_trace_config["symmetric"])
        new._rebuild_trace_forest = True
        new.__last_trace = None
        if self.is_built:
            # If we deepcopy from a built state then make sure we clean up the model
            # state to get rid of any old data stored
            new.unbuild()

        # Final run of any later updates
        for _ in new.after_deepcopy:
            _()
        del new.after_deepcopy  # cleanup as this shouldn't be kept

        return new

    @property
    def all_parameters(self):
        """Returns a generator of all the Model parameters."""
        return (p for el in self.elements.values() for p in el.parameters)

    def sort_elements(self, key):
        """Sort the display order of the elements in the model.

        This order is used for determining the order of plot traces and other listings.

        Element sorting is useful for example when parsing KatScript into a model, where
        adding of elements to the model may not be performed in the same order as the
        corresponding definitions in the script. To ensure consistency to the user, this
        method can be used to sort the parsed elements back into their original script
        order.

        Notes
        -----
        The sort performed by this method is stable.

        Parameters
        ----------
        key : callable
            Specifies a function that takes a single argument - a tuple containing the
            element name and object - and returns a comparison key.
        """
        LOGGER.debug("sorting model elements (redefining __elements dict)")
        self.__elements = dict(sorted(self.__elements.items(), key=key))

    def element_order(self, element):
        """Get the order in which `element` was added to the model."""
        return list(self.elements).index(element.name)

    @property
    def input_matrix_dc(self):
        """The DC input matrix is used to relate degrees of freedoms and readouts within
        a model. This information is used to generate DC locks to put the model at an
        operating point defined by the error signals used.

        :getter: Returns an InputMatrix object.
        """
        return self.__inmtx_dc

    @property
    def analysis(self):
        """The root action to apply to the model when :meth:`Model.run` is called.

        :getter: Returns the root analysis attached to this model.
        :setter: Sets the model's root analysis.
        """
        return self.__analysis

    @analysis.setter
    @locked_when_built
    def analysis(self, action):
        self.__analysis = action

    @property
    def elements(self):
        """Dictionary of all the model elements with the keys as their names."""
        return self.__elements.copy()

    @property
    def network(self):
        """The directed graph object containing the optical configuration as a
        :class:`networkx.DiGraph` instance.

        The `network` stores :class:`.Node` instances as nodes and :class:`.Space`
        instances as edges, where the former has access to its associated component via
        :attr:`.Node.component`.

        See the NetworkX documentation for further details and a reference to the data
        structures and algorithms within this module.

        :getter: Returns the directed graph object containing the configuration
                 (read-only).
        """
        return self.__network

    @property
    def optical_network(self):
        """A read-only view of the directed graph object stored by :attr:`Model.network`
        but only containing nodes of type :class:`.OpticalNode` and only with edges that
        have couplings to optical nodes.

        :getter: Returns the optical-only directed graph-view (read-only).
        """
        return self.__opt_net_view

    def to_component_network(self):
        """Generate an undirected graph containing components as the nodes of the graph
        and connections (spaces, wires) between component nodes as the edges of the
        graph.

        Returns
        -------
        :class:`networkx.Graph`
            The component network.
        """

        cnetwork = nx.Graph()

        # Add components as nodes.
        for component in self.components:
            cnetwork.add_node(component.name)

        # Add spaces, wires as edges.
        for u, v, data in self.network.edges(data=True):
            # Resolve the owning object.
            owner = data["owner"]()

            if not isinstance(owner, (Space, Wire)):
                continue

            # Resolve the connected objects.
            in_ref = data["in_ref"]()
            out_ref = data["out_ref"]()

            u = in_ref.component.name
            v = out_ref.component.name

            if u not in cnetwork.nodes or v not in cnetwork.nodes:
                # Only add edges between components (not e.g. connections between components and
                # spaces, like phase couplings).
                continue

            # Since the network is a graph, not a digraph, we only need to add one direction.
            if (u, v) not in cnetwork.edges:
                cnetwork.add_edge(u, v, connection=data["owner"])

        return cnetwork

    def __nodes_of(self, *node_types):
        return [
            attr["weakref"]()
            for _, attr in self.__network.nodes(data=True)
            if attr["weakref"]().type in node_types
        ]

    @property
    def optical_nodes(self):
        """The optical nodes stored in the model.

        :getter: Returns a list of all the optical nodes in the model (read-only).
        """
        return self.__nodes_of(NodeType.OPTICAL)

    @property
    def signal_nodes(self):
        """The signal nodes stored in the model.

        :getter: Returns a list of all the signal nodes in the model (read-only).
        """
        return self.__nodes_of(NodeType.ELECTRICAL, NodeType.MECHANICAL)

    @property
    def gausses(self):
        """A dictionary of optical node to :class:`.Gauss` instance mappings.

        :getter: Returns the dictionary of user defined beam parameter nodes (read-only).
        """
        return self.__gausses

    @property
    def lambda0(self):
        """The default wavelength to use for the model.

        :getter: Returns wavelength in meters
        :setter: Sets the wavelength in meters
        """
        return self._settings.lambda0

    @lambda0.setter
    @locked_when_built
    def lambda0(self, value):
        self._settings.set_lambda0(float(value))

        # Update the wavelengths of Gauss object beam parameters
        for gauss in self.__gausses.values():
            gauss.qx.wavelength = self._settings.lambda0
            gauss.qy.wavelength = self._settings.lambda0

    @property
    def f0(self):
        """The default frequency to use for the model. This is determinde by the value
        of lambda0.

        :getter: Returns frequency in Hertz
        """
        return self._settings.f0

    @property
    def is_modal(self):
        """Flag indicating whether the model is modal or plane-wave.

        :getter: `True` if the modal is modal, `False` if it is plane-wave.
        """
        return self._settings.is_modal

    @property
    def hom_labels(self):
        """Labels for the HOMs present in this model."""
        return tuple(f"{n},{m}" for n, m in self.homs)

    @property
    def homs(self):
        """An array of higher-order modes (HOMs) included in the model.

        :getter: Returns a copy of the array of the HOMs in the model.
        :setter: Sets the HOMs to be included in the model. See :meth:`Model.modes`
                 for the options available.
        """
        return self._settings.homs

    @homs.setter
    @locked_when_built
    def homs(self, value):
        self.modes(value)

    @property
    def modes_setting(self):
        return self.__mode_setting

    @property
    def mode_index_map(self):
        """An ordered dictionary where the key type is the modes in the model and the
        mapped type is the index of the mode.

        :getter: Returns the map of modes to indices (read-only).
        """
        return {(n, m): i for i, (n, m) in enumerate(self._settings.homs)}

    @locked_when_built
    def include_modes(self, modes):
        """Inserts the mode indices in `modes` into the :attr:`.Model.homs` array at the
        correct (sorted) position(s).

        Parameters
        ----------
        modes : sequence, str
            A single mode index pair or an iterable of mode indices. Each
            element must unpack to two integer convertible values.
        """
        self._settings.homs = insert_modes(self._settings.homs, modes)

        if not self._settings.is_modal:
            self._settings.is_modal = True
            LOGGER.info(f"Turning on HOMs --> switching model: {self!r} to modal.")

        self.__mode_setting["include"] = modes

    @locked_when_built
    def remove_modes(self, modes):
        """Removes the mode indices in `modes` from the :attr:`.Model.homs` array.

        Parameters
        ----------
        modes : sequence, str
            A single mode index pair or an iterable of mode indices. Each
            element must unpack to two integer convertible values.
        """
        self._settings.homs = remove_modes(self._settings.homs, modes)
        self.__mode_setting["remove"] = modes

    @locked_when_built
    def switch_off_homs(self):
        """Turns off HOMs, switching the model to a plane wave basis."""
        LOGGER.info("Turning off HOMs --> switching model to plane wave.")
        self._settings.homs = np.zeros(1, dtype=(np.intc, 2))
        self._settings.is_modal = False

    @locked_when_built
    def modes(self, modes=None, maxtem=None, include=None, remove=None):
        """Select the HOM indices to include in the model.

        See :ref:`selecting_modes` for examples on using this method.

        Parameters
        ----------
        modes : sequence, str, optional; default: None
            Identifier for the mode indices to generate. This can be:

            - An iterable of mode indices, where each element in the iterable must
              unpack to two integer convertible values.

            - A string identifying the type of modes to include, must be one of "off",
              "even", "odd", "tangential" (or "x") or "sagittal" (or "y").

        maxtem : int, optional; default: None
            Optional maximum mode order.

        include : sequence, str, optional
            A single mode index pair, or an iterable of mode indices, to include. Each
            element must unpack to two integer convertible values.

        remove : sequence, str, optional
            A single mode index pair, or an iterable of mode indices, to remove. Each
            element must unpack to two integer convertible values.

        See Also
        --------
        Model.include_modes : Insert mode indices into :attr:`Model.homs` at the
                              correct (sorted) positions.

        Model.remove_modes : Remove mode index pairs from the model.

        Examples
        --------
        See :ref:`selecting_modes`.
        """
        if (
            (modes is None)
            and (maxtem is None)
            and (include is None)
            and (remove is None)
        ):
            if self._settings.is_modal:
                return self.homs
            else:
                return None

        if not self._settings.is_modal:
            self._settings.is_modal = True
            LOGGER.info("Turning on HOMs --> switching model to modal.")

            # NOTE (sjr) Commenting this out for now as it can cause confusion when
            #            parsing a file - e.g. adding a cavity, gauss object before
            #            maxtem is set will trigger this statement and erroneously lead
            #            the user to believe that only the 00 mode is present
            # if modes is None and maxtem == 0 and include is None and remove is None:
            # warn(
            #    "Modal model enabled with only HG00. Call Model.modes to add modes."
            # )

        def do_make_modes(*args, **kwargs):
            try:
                return make_modes(*args, **kwargs)
            except ContextualValueError as e:
                # make_modes uses different parameters to this method so we need to
                # rewrite the parameters.
                if "select" in e.params:
                    # Note: ensure the signature order is retained!
                    params = {"modes": e.params["select"], **e.params}
                    params.pop("select")
                    e.params = params
                raise e

        if modes is None:  # maxtem
            if maxtem is None:
                self.switch_off_homs()
            else:
                self._settings.homs = do_make_modes(maxtem=maxtem)

        elif isinstance(modes, str):  # identifier
            if modes.casefold() == "off":
                self.switch_off_homs()
            else:
                if maxtem is None:
                    raise ValueError(
                        f"Argument maxtem must be specified for modes argument of "
                        f"{modes}"
                    )

                self._settings.homs = do_make_modes(modes, maxtem)
        else:  # iterable of mode indices
            self._settings.homs = do_make_modes(modes)

        if include is not None:
            self.include_modes(include)

        if remove is not None:
            self.remove_modes(remove)

        # remember the modes setting for use in the unparser
        self.__mode_setting["modes"] = modes
        self.__mode_setting["maxtem"] = maxtem
        self.__mode_setting["include"] = include
        self.__mode_setting["remove"] = remove

    @locked_when_built
    def add_all_ad(self, node, f=0):
        """Adds amplitude detectors at the specified `node` and frequency `f` for all
        Higher Order Modes in the model.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            Node to add the detectors at.

        f : scalar, :class:`.Parameter` or :class:`.ParameterRef`
            Frequency of the field to detect.

        Returns
        -------
        dets : list
            A list of all the amplitude detector instances added to the model.
        """
        node_name = node.tag
        if node_name is None or not valid_name(node_name):
            node_name = node.full_name.replace(".", "_")

        ads = []
        for n, m in self._settings.homs:
            ad = detectors.AmplitudeDetector(f"ad_{n}_{m}_{node_name}", node, f, n, m)
            self.add(ad)
            ads.append(ad)

        return ads

    @locked_when_built
    def add_fd_to_every_node(self, freq=0):
        """Adds a FieldDetector at every optical node in model at a given frequency
        The name of each FieldDetector is automatically generated using the following
        pattern: ``E_<component>_<port>_<node>``

        Parameters
        ----------
        f : scalar, :class:`.Parameter` or :class:`.ParameterRef`
            Frequency of the field to detect.

        Returns
        -------
        dets : list
            A list of all the field detector instances added to the model.
        """

        nodes = self.optical_nodes

        fds = []
        for node in nodes:
            fd_name = f"E_{node.full_name.replace('.','_')}"
            fd = detectors.FieldDetector(fd_name, node, freq)
            self.add(fd)
            fds.append(fd)

        return fds

    @property
    def phase_level(self):
        """An integer corresponding to the phase level given to the phase command of a
        Finesse 2 kat script.

        :getter: Returns the phase level.
        :setter: Sets the phase level - turns on/off specific flags
                 for the scaling of coupling coefficient and Gouy phases.
        """
        lvl = 0
        if self._settings.phase_config.zero_k00:
            lvl += 1
        if self._settings.phase_config.zero_tem00_gouy:
            lvl += 2
        return lvl

    @locked_when_built
    @phase_level.setter
    def phase_level(self, value):
        if value == 0:
            self._settings.phase_config.zero_k00 = False
            self._settings.phase_config.zero_tem00_gouy = False
        elif value == 1:
            self._settings.phase_config.zero_k00 = True
            self._settings.phase_config.zero_tem00_gouy = False
        elif value == 2:
            self._settings.phase_config.zero_k00 = False
            self._settings.phase_config.zero_tem00_gouy = True
        elif value == 3:
            self._settings.phase_config.zero_k00 = True
            self._settings.phase_config.zero_tem00_gouy = True
        else:
            raise ValueError(f"Value is not valid {value}")

    @property
    def Nhoms(self):
        """Number of higher-order modes (HOMs) included in the model.

        :getter: Returns the number of HOMs in the model (read-only).
        """
        return self._settings.num_HOMs

    @property
    def frequencies(self):
        """The frequencies stored in the model as a :py:class:`list` instance.

        :getter: Returns a list of the model frequencies (read-only).
        """
        return tuple(self.__frequencies)

    @property
    def source_frequencies(self):
        """The source frequencies stored in the model as a :py:class:`dict` instance.

        The frequencies are the keys, and the values are list of components that depend on the given
        frequency.

        :getter: Returns a dict of the model source frequencies (read-only).
        """
        return tuple(self.__source_frequencies.keys())

    @property
    def components(self):
        """The components stored in the model as a tuple object.

        :getter: Returns a tuple of the components in the model (read-only).
        """
        return tuple(self.__components.keys())

    @property
    def detectors(self):
        """The detectors stored in the model as a tuple object.

        :getter: Returns a tuple of the detectors in the model (read-only).
        """
        return tuple(self.__detectors.keys())

    @property
    def cavities(self):
        """The cavities stored in the model as a tuple object.

        :getter: Returns a tuple of the cavities in the model (read-only).
        """
        return tuple(self.__cavities.keys())

    @property
    def locks(self):
        return tuple(self.__locks.keys())

    @property
    def is_built(self):
        """Flag indicating whether the model has been built.

        When this evaluates to `True`, the structure of the underlying matrix
        should not be changed.

        :getter: `True` if the model has been built, `False` otherwise.
        """
        return self.__is_built

    @property
    def trace_order(self):
        """A list of beam tracing dependencies, ordered by their tracing priority.

        Dependency (i.e. :class:`.Cavity` and :class:`.Gauss`) objects are ordered
        in this list according to the priority in which they will be traced during
        the beam tracing routine.

        This ordering is strictly defined as follows:

        Dependencies will be sorted in order of *descending* :attr:`.TraceDependency.priority`
        value. Any dependencies which have equal :attr:`.TraceDependency.priority` value are
        sorted *alphabetically* according to their names.

        Please be aware that this means if no priority values have been given to any
        :class:`.TraceDependency` instance in the model, as is the default when creating
        these objects, then this trace order list is simply sorted alphabetically by the
        dependency names.

        .. note::

            Regardless of their positions in this list, the *internal* traces of
            :class:`.Cavity` objects will always be performed first. Internal cavity
            traces are defined as the traces which propagate the cavity eigenmode
            through all the nodes of the cavity path.

            Importantly, however, the order in which :class:`.Cavity` objects appear
            in this trace order list *will* also determine the order in which their internal
            traces are performed. This is relevant only for when there are overlapping
            cavities in the model - recycling cavities in dual-recycled Michelson interferometer
            configurations are a typical case of this.

            As always see :meth:`.Model.beam_trace` and :ref:`tracing_manual` for more details
            on the inner workings of the beam tracing routines.

        Temporary overriding of this order for a given :meth:`.Model.beam_trace` call
        can be performed by specifying the ``order`` argument for this method call.

        To override this ordering for a simulation, one should use the ``"order"`` keyword
        argument of :meth:`.Model.sim_trace_config_manager` to temporarily use any arbitrary
        dependency order within a context.

        :getter: Returns a list giving the order in which dependencies will be traced. Read-only.
        """
        return self.__trace_order.copy()

    @property
    def trace_order_names(self):
        """A convenience property to retrieve a list of the names of each
        :class:`.TraceDependency` instance in :attr:`.Model.trace_order`.

        :getter: Returns a list of the names of the dependencies in the order
                 they will be traced. Read-only.
        """
        return [d.name for d in self.trace_order]

    def __insert_trace_dependency(self, dep):
        self.__trace_order.append(dep)
        self._resort_trace_dependencies()

    def _resort_trace_dependencies(self):
        # Sort in order of descending priority and ensure dependencies
        # with equal priority are sorted alphabetically by name
        self.__trace_order.sort(key=lambda x: (-x.priority, x.name))

    @property
    def trace_forest(self):
        """The :class:`.TraceForest` instance held by the model.

        This is a representation of the beam tracing paths from each dependency which takes
        on a form corresponding to the last call to :meth:`.Model.beam_trace`. See the
        documentation for :class:`.TraceForest` itself for details on what exactly this
        object is, and the various methods and properties it exposes.

        .. hint::

            Most of the time users will not need to touch this property as it is generally
            just used internally. Beam tracing functionality should instead be used via
            the carefully designed interfaces, i.e: :meth:`.Model.beam_trace` for full model
            beam traces, :meth:`.Model.propagate_beam` for propagating an arbitrary beam
            through a path etc. See :mod:`.tracing.tools` for details on various beam tracing
            tools.

            Despite the above, it *can* sometimes be useful to query this property to get a visual
            representation of how the beam tracing paths look in your model. To do this one
            can simply print the return of this property, i.e.::

                print(model.trace_forest)

            to get a forest-like structure of all the beam tracing trees which represent the
            current state (as of the last :meth:`.Model.beam_trace` call) of the model.

        :getter: The :class:`.TraceForest` object associated with this model. Read-only.
        """
        return self.__trace_forest

    @contextmanager
    def sim_trace_config_manager(self, **kwargs):
        """Change the :attr:`.Model.sim_trace_config` within a context.

        This provides a convenient pattern through which one can temporarily
        set the simulation beam tracing behaviour in a ``with`` block. The
        method :meth:`.Model.reset_sim_trace_config` is called on exit.

        Parameters
        ----------
        kwargs : keyword arguments
            See :attr:`.Model.sim_trace_config`.

        Examples
        --------

        Temporarily change the tracing order::

            with model.sim_trace_config_manager(order=["cavXARM", "gaussBS", "cavYARM"]):
                out = model.run()

        Disable certain dependencies in a context::

            with model.sim_trace_config_manager(disable="cavIMC"):
                out = model.run()

        Switch off re-tracing and enable only two specific trace dependencies::

            with model.sim_trace_config_manager(
                retrace=False, enable_only=["cavXARM", "cavYARM"]
            ):
                out = model.run()

        Use asymmetric tracing and mask all data points where any unstable cavity
        is encountered::

            with model.sim_trace_config_manager(symmetric=False, unstable_handling="mask"):
                out = model.run()
        """
        diff = set(kwargs) - set(self.sim_trace_config)
        if diff:
            raise KeyError(
                "The following arguments are not sim_trace_config "
                f"options: {', '.join(diff)}"
            )

        self.sim_trace_config.update(kwargs)

        try:
            yield
        finally:
            self.reset_sim_trace_config()

    @property
    def sim_trace_config(self):
        """Dictionary corresponding to beam tracing configuration options for
        simulations.

        The (string) keys of this dict are:

         * The arguments of :meth:`.Model.beam_trace`, see the linked docs for descriptions
           of each of these. These config values are passed to the initial beam trace
           call when building a modal simulation, thereby determining the structure of
           both the :attr:`.Model.trace_forest` used for computing the initial beam
           parameters, as well as the trace forest of changing beam paths as stored by
           the simulation itself.

         * "retrace" --- flag determining whether beam tracing is re-executed, during a
           simulation, whenever some dependent parameter changes. This is ``True`` by
           default, meaning that any paths in the model with changing geometric parameters
           will automatically be retraced during the simulation. Setting this to ``False``
           means that the initial beam parameters (from the beam trace executed at the
           start of the simulation) are used for all data points, regardless of whether
           any geometric parameter is changing or not.

         * "unstable_handling" --- the strategy to use when encountering unstable optical
           cavities during a simulation (as a potential result of scanning geometric
           parameters). The accepted values for this config option are:

           * "auto" --- (default) contingency :class:`.TraceForest` instances are created when
             entering unstable cavity regions; or, if there are no stable :class:`.TraceDependency`
             objects, detector outputs are masked appropriately in these regions.
           * "mask" --- detector outputs masked appropriately whenever an unstable cavity
             is encountered; i.e. nothing else (scatter matrices, gouy phases, refills etc.)
             is computed for such data points.
           * "abort" --- immediately aborts the simulation, if an unstable cavity is encountered,
                         by raising a :class:`.BeamTraceException`.

        .. hint::

            Most of the time it is better to use :meth:`.Model.sim_trace_config_manager` to
            temporarily set simulation beam tracing configuration options, rather than modifying
            the entries here directly (which then requires manual re-setting as outlined below).

        :getter: Beam tracing configuration options for simulations.

        Examples
        --------

        One can use this property to change the behaviour of beam tracing for a simulation. For
        example, this::

            model.sim_trace_config["disable"] = "cav1"

        would switch off tracing from the trace-dependency named `"cav1"` during a simulation.

        It can also be used to temporarily override the trace order used, without modifying
        :attr:`.TraceDependency.priority` values and, thus, without modifying the actual
        :attr:`.Model.trace_order`. For example::

            model.sim_trace_config["order"] = ["gL0", "cav2", "cav1"]

        would set the trace ordering for the next simulation using this model to the order given.

        To reset the `sim_trace_config` dict entries to the default values,
        call :meth:`.Model.reset_sim_trace_config`.
        """
        return self.__sim_trace_config

    @property
    def sim_initial_trace_args(self):
        """Filtered dictionary of :attr:`.Model.sim_trace_config` corresponding to only
        those options which match the arguments of :meth:`.Model.beam_trace`.

        The arguments of :meth:`.Model.beam_trace`, see the linked docs for descriptions
        of each of these. These config values are passed to the initial beam trace
        call when building a modal simulation, thereby determining the structure of
        both the :attr:`.Model.trace_forest` used for computing the initial beam
        parameters, as well as the trace forest of changing beam paths as stored by
        the simulation itself.

        .. note::
            The return value is a new filtered dict, not a sub-view of :attr:`.Model.sim_trace_config`,
            thus modifying this dict does not affect the entries in :attr:`.Model.sim_trace_config`.
        """
        return {
            k: self.sim_trace_config[k]
            for k in inspect.signature(self.beam_trace).parameters.keys()
        }

    def reset_sim_trace_config(self):
        """Resets the simulation beam tracing configuration dict, given by
        :attr:`.Model.sim_trace_config`, to the default values."""
        self.__sim_trace_config = self.__default_sim_trace_config.copy()

    @property
    def is_traced(self):
        """Flag indicating whether the model has been traced.

        .. warning::

            This flag only indicates whether a beam trace has been performed on the model,
            it *does not* mean that the last stored beam trace (i.e. :attr:`.Model.last_trace`)
            corresponds to the latest state of the model.

        :getter: `True` if the mode has been traced at least once, `False` otherwise.
        """
        return self.last_trace is not None

    @property
    def last_trace(self):
        """An instance of :class:`.BeamTraceSolution` containing the output of the most
        recently stored beam trace performed on the model.

        :getter: Returns a copy of the most recently stored beam trace output. Read-only.
        """
        return copy(self.__last_trace)

    @locked_when_built
    def tag_node(self, node, tag):
        """Tag a node with a unique name.

        Access to this node can then be performed with::

            node = model.<tag_name>

        Parameters
        ----------
        node : :class:`.Node`
            An instance of a node already present in the model.

        tag : str
            Unique tag name of the node.
        """
        self.__node_exists_check(node)

        if hasattr(self, tag):
            raise Exception(f"Tagged name: {tag} already exists in the model.")

        node._set_tag(tag)

        self._unfreeze()
        setattr(self, tag, node)
        self._freeze()

    def get_parameters(
        self, *, include=None, exclude=None, are_changing=None, are_symbolic=None
    ):
        """Get all or a filtered list of parameters from all elements in the model.

        Parameters
        ----------
        include : [iterable|str], optional
            Parameters that *should* be included.

            If a single string is given it can be a Unix file style wildcard (See ``fnmatch``).
            A value of None means everything is included.

            If an iterable is provided it must be a list of names or Parameter objects.

        exclude : [iterable|str], optional
            Parameters that *should not* be included.

            If a single string is given it can be a Unix file style wildcard (See ``fnmatch``).
            A value of None means nothing is excluded.

            If an iterable is provided it must be a list of names or Parameter objects.

        are_changing : boolean, optional
            Filter if Parameter has a value that will be marked as changing during a simulation.
            Note this might be a user chaniging variable or a symbolic value whose arguments
            are changing.

        are_symbolic : boolean, optional
            Filter if Parameter has a symbolic value. If set to None, not filtering is done.

        Returns
        -------
        parameters : list
            List of filtered Parameters
        """
        from fnmatch import fnmatch

        name_predicates = []
        bool_predicates = []

        if exclude is not None:
            if isinstance(exclude, str):
                name_predicates.append(lambda x: not fnmatch(x, exclude))
            else:
                name_predicates.append(lambda x: (x not in exclude))

        if include is not None:
            if isinstance(include, str):
                name_predicates.append(lambda x: fnmatch(x, include))
            else:
                name_predicates.append(lambda x: (x in include))

        if are_changing is not None:
            bool_predicates.append(lambda x: x.is_changing == are_changing)

        if are_symbolic is not None:
            bool_predicates.append(lambda x: x.is_symbolic == are_symbolic)

        return [  # get all parameters
            p
            for el in self.elements.values()
            for p in el.parameters
            if all(pred(p.full_name) for pred in name_predicates)
            and all(pred(p) for pred in bool_predicates)
        ]

    @contextmanager
    def temporary_parameters(self, include=None, exclude=None):
        """Context manager that lets user change any ModelParameter then return it to
        the original value once completed. When the Model is in this temporary state it
        cannot have any structural changes, such as adding or removing components.

        There is also the ability to include or exclude certain parameters from reverting
        back to their previous values if needed.

        Parameters
        ----------
        include : iterable or str, optional
            Parameters that *should* be reverted once the context has exitted.

            If a single string is given it can be a Unix file style wildcard (See ``fnmatch``).
            A value of None means everything is included.

            If an iterable is provided it must be a list of names or Parameter objects.

        exclude : iterable or str, optional
            Parameters that *should not* be reverted once the context has exitted.

            If a single string is given it can be a Unix file style wildcard (See ``fnmatch``).
            A value of None means nothing is excluded.

            If an iterable is provided it must be a list of names or Parameter objects.

        Examples
        --------
        .. code-block::

            import finesse
            model = finesse.Model()
            model.parse('''
            l l1 P=1
            m m1 R=0.99 T=0.01 Rc=-1934
            m m2 R=1 T=0 Rc=2245
            m m3 R=1 T=0 Rc=10000
            '''
            )
            with model.temporary_parameters():
                model.m1.Rc = 100
                print(model.m1.Rc)
            print(model.m1.Rc)

            # Only reset m2 parameters
            with model.temporary_parameters(include="m2.*"):
                ...

            # Only reset m2.phi and m1.phi parameters
            with model.temporary_parameters(include=("m2.phi", "m1.phi")):
                ...

            # Reset everything apart from all phi parameters
            with model.temporary_parameters(exclude="*.phi"):
                ...

            # Reset everything apart from all phi parameters
            with model.temporary_parameters(exclude="m[13].phi"):
                ...
        """
        params = self.get_parameters(include=include, exclude=exclude)
        try:
            self.__lock_model_change = True  # stop any structural changes to model
            # Get the current values of all parameters
            initial_values = {p: copy(p.value) for p in params}
            initial_settings = deepcopy(self._settings)
            yield
        except Exception as ex:
            raise ex
        finally:
            # Reset the values on exit
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=ModelParameterSettingWarning)
                for p in params:
                    if p.value != initial_values[p]:
                        p.value = initial_values[p]

            self._settings = initial_settings
            self.__lock_model_change = False

    @locked_when_built
    def remove(self, obj):
        """Removes an object from the model.

        .. note::

            If a string is passed, it will be looked up
            via self.elements.

        Parameters
        ----------
        obj : :class:`.Frequency` or sub-class of :class:`.ModelElement`
            The object to remove from the model.

        Raises
        ------
        Exception
            If the matrix has already been built or there is no component
            with the given name in the model.
        """
        if self.__lock_model_change:
            raise FinesseException("Model is locked and cannot be added or removed to.")

        if isinstance(obj, str):
            obj = self.elements[obj]

        if obj in self.__not_removable:
            raise FinesseException(f"{obj} cannot be removed from the model.")

        if isinstance(obj, ModelElement):
            # Check that any of this elements parameters are not being referenced by
            # someone else in the model
            symbolic_params = (
                p for p in self.all_parameters if p.is_symbolic and p.owner is not obj
            )
            for sp in symbolic_params:
                for p in obj.parameters:
                    if p in sp.value.parameters():
                        raise FinesseException(
                            f"Cannot remove element {repr(obj)}.\nParameter {repr(p)} is being used by {repr(sp)}."
                        )

            if obj in self.__components:
                nodes = obj.nodes

                # stores (port1, port2) keys where port1 should now connect to port2
                pairs = {}
                for name, node in nodes.items():
                    if node.type != NodeType.OPTICAL or not node.is_input:
                        continue

                    predecessors = list(self.network.predecessors(name))
                    if not predecessors:
                        continue
                    pre = predecessors[0]

                    # immediate successors of the node - always exist
                    im_succ = list(self.network.successors(name))
                    # find only the successor node which is at a different port
                    match = list(
                        filter(
                            lambda n: self.network.nodes[n]["weakref"]().port
                            != node.port,
                            im_succ,
                        )
                    )[0]

                    # successors of the immediate successors
                    successors = list(self.network.successors(match))
                    if not successors:
                        continue
                    succ = successors[0]

                    p1 = self.network.nodes[pre]["weakref"]().port
                    p2 = self.network.nodes[succ]["weakref"]().port

                    # don't add the port pair again if we already did the
                    # previous propagation from the opposite port
                    if (p2, p1) not in pairs:
                        p1_space = p1.space
                        p2_space = p2.space
                        pairs[(p1, p2)] = p1_space.L.value + p2_space.L.value

                        self.network.remove_edge(pre, name)
                        self.network.remove_edge(
                            node.opposite.full_name,
                            self.network.nodes[pre]["weakref"]().opposite.full_name,
                        )
                        self.network.remove_edge(match, succ)
                        self.network.remove_edge(
                            self.network.nodes[succ]["weakref"]().opposite.full_name,
                            self.network.nodes[match]["weakref"]().opposite.full_name,
                        )

                        for n in p1.nodes:
                            try:
                                self.network.remove_edge(
                                    p1_space.phase_sig.i.full_name, n.full_name
                                )
                            except nx.exception.NetworkXError:
                                pass

                        for n in p2.nodes:
                            try:
                                self.network.remove_edge(
                                    p2_space.phase_sig.i.full_name, n.full_name
                                )
                            except nx.exception.NetworkXError:
                                pass

                        self.network.remove_node(name)

                        del self.__elements[p1_space.name]
                        del self.__elements[p2_space.name]

                for (p, s), L in pairs.items():
                    self.connect(p, s, L=L)

                del self.__components[obj]

                self._rebuild_trace_forest = True

            elif isinstance(obj, (Space, Wire)):
                # Remove any connections from this element
                self.network.remove_edges_from(
                    (
                        (n[0].full_name, n[1].full_name)
                        for n in obj.all_internal_connections.values()
                    )
                )
                # Remove any signal nodes too
                self.network.remove_nodes_from((n.full_name for n in obj.signal_nodes))

                if isinstance(obj, Space):
                    if isinstance(obj.p1.i.component, Surface):
                        obj.p1.i.component._resymbolise_ABCDs()
                    if isinstance(obj.p2.o.component, Surface):
                        obj.p2.o.component._resymbolise_ABCDs()

            elif obj in self.detectors:
                del self.__detectors[obj]
            elif obj in self.__cavities or obj in self.__gausses.values():
                args = ("order", "disable", "enable_only")
                for arg in args:
                    thing = self.__sim_trace_config[arg]
                    if thing is not None:
                        if obj in thing:
                            thing.remove(obj)
                        elif obj.name in thing:
                            thing.remove(obj.name)

                if obj in self.__trace_order:
                    self.__trace_order.remove(obj)

                if obj in self.__cavities:
                    del self.__cavities[obj]
                elif obj in self.__gausses.values():
                    del self.__gausses[obj.node]

                self._rebuild_trace_forest = True
            elif obj in self.__locks:
                del self.__locks[obj]
            else:
                raise Exception(
                    "Element with name {} not in this model".format(obj.name)
                )

            if hasattr(obj, "_on_remove"):
                obj._on_remove()
            obj._set_model(None)
            del self.__elements[obj.name]

            # Remove element from any namespaces
            for namespace in obj._namespace:
                parent = self
                for _ in namespace.split("."):
                    if len(_) > 0:
                        if hasattr(parent, _):
                            parent = getattr(parent, _)
                delattr(parent, obj.name)
        else:
            raise TypeError(
                "Object {} not recongised as a Finesse ModelElement.".format(obj)
            )

    def get(self, attr):
        """Get an attribute of the model using a string path representation like
        `l1.p1.o.q`.

        Examples
        --------
        Parse a simple model and extract the laser power model parameter:

        >>> import finesse
        >>> kat = finesse.Model()
        >>> kat.parse(\"\"\"
        ... l l1 P=2
        ... s s1 l1.p1 m1.p1
        ... m m1 R=0.5 T=0.5
        ... pd Pr m1.p1
        ... pd Pt m1.p2
        ... \"\"\")
        >>> kat.get("l1.P")
        <l1.P=2.0 @ 0x11aa56588>
        """
        return self._reduce_attr(attr.strip().split("."))

    @deprecated(reason="Use `Model.get`.")
    def reduce_get_attr(self, attr):
        return self.get(attr)

    def set(self, attr, value):
        """Set an attribute of the model using a string path representation like
        `l1.p1.o.q`."""
        attrs = attr.split(".")

        # Set the final attribute.
        setattr(
            self._reduce_attr(attrs[:-1]),
            attrs[-1],
            value,
        )

    @deprecated(reason="Use `Model.set`.")
    def reduce_set_attr(self, attr, value):
        return self.set(attr, value)

    def _reduce_attr(self, attrs):
        """Get the final attribute found by following the sequence in `attrs` in order
        starting at this model."""
        from functools import reduce

        # First try direct attributes (for components etc.).
        try:
            return reduce(getattr, attrs, self)
        except AttributeError:
            pass

        # Now try spaces.
        try:
            return reduce(getattr, attrs, self.spaces)
        except AttributeError:
            pass

        raise ModelAttributeError(self, attrs)

    @locked_when_built
    def add(self, obj, *, unremovable=False):
        """Adds an element (or sequence of elements) to the model - these can be
        :class:`.ModelElement` sub-class instances.

        When the object is added, an attribute defined by `obj.name` is set within
        the model allowing access to the object just added via `model.obj_name` where
        `obj_name = obj.name`.

        Parameters
        ----------
        obj : Sub-class of :class:`.ModelElement` (or sequence of)
            The object(s) to add to the model.
        unremovable : bool, optional
            When True, this object will not be able to be removed from this model
        Raises
        ------
        Exception
            If the matrix has already been built, the component has already
            been added to the model or `obj` is not of a valid type.
        """
        if self.__lock_model_change:
            raise FinesseException("Model is locked and cannot be added or removed to.")

        if is_iterable(obj):
            for o in obj:
                self.add(o)
            return

        try:
            if obj._model is not None:
                raise Exception(
                    f"Element {obj.name} already thinks it is attached to a different model"
                )
        except ComponentNotConnected:
            pass

        if obj.name in self.__elements:
            raise Exception(
                f"An element with the name {obj.name} is already present"
                f" in the model ({self.__elements[obj.name]})"
            )

        if obj._unique_element:
            if len(tuple(self.get_elements_of_type(type(obj)))) > 0:
                raise FinesseException(
                    f"An element with type {type(obj)} has already been added to the model"
                )

        assert isinstance(obj, ModelElement)

        obj._set_model(self)

        if isinstance(obj, Space):
            for node in obj.nodes.values():
                self.__add_node_to_graph(node, obj)

            for key in obj._registered_connections:
                From, To = obj._registered_connections[key]
                From_name, To_name = obj._registered_connections[key]
                From = obj.nodes[From_name]
                To = obj.nodes[To_name]
                self.__add_connection_to_graph(key, From, To, obj)

            # Need to re-calculate symbolic ABCD matrices for connected
            # surfaces now that refractive index symbols are different
            if isinstance(obj.p1.i.component, Surface):
                obj.p1.i.component._resymbolise_ABCDs()
            if isinstance(obj.p2.o.component, Surface):
                obj.p2.o.component._resymbolise_ABCDs()

        elif isinstance(obj, Wire):
            # Wires only have one connection each
            self.__add_connection_to_graph("WIRE", obj.nodeA, obj.nodeB, obj)

        elif isinstance(obj, detectors.Detector):
            # Tell component to associate itself with this model
            if obj.name in self.__detectors:
                raise Exception(
                    f"Detector with name {obj.name} already added to this model"
                )

            if obj.node is not None and obj.node._model != self:
                raise Exception(
                    f"The node of detector {obj.name}, {obj.node}, is not part of {self!r}"
                )

            elif isinstance(obj, detectors.CavityPropertyDetector):
                obj._set_cavity()

            elif isinstance(obj, detectors.Gouy):
                obj._lookup_spaces()

            self.__detectors[obj] = len(self.__detectors)

            # If the detector needs a modal basis defined then
            # switch on modes if not modal already
            if obj.needs_trace:
                if not self.is_modal:
                    self.modes(maxtem=0)

        elif isinstance(obj, Cavity):
            if obj.name in self.__cavities:
                raise Exception(f"cavity {repr(obj.name)} already added to this model")

            self.__cavities[obj] = len(self.__cavities)

            # compute all the cavity properties (including path determination)
            obj.initialise()

            self.__insert_trace_dependency(obj)

            if not obj.is_stable:
                warn(
                    f"cavity {repr(obj.name)} added to the model is unstable",
                    CavityUnstableWarning,
                )

            # Turn on HOMs if model is still plane-wave
            if not self.is_modal:
                self.modes(maxtem=0)

        elif isinstance(obj, Connector):
            if obj.name in self.__components:
                raise Exception(f"Element {repr(obj.name)} already added to this model")

            for _ in obj.nodes.values():
                self.__add_node_to_graph(_, obj)

            for key in obj._registered_connections:
                From_name, To_name = obj._registered_connections[key]
                From = obj.nodes[From_name]
                To = obj.nodes[To_name]
                self.__add_connection_to_graph(key, From, To, obj)

            self.__components[obj] = len(self.__components)

            if isinstance(obj, FrequencyGenerator):
                self._frequency_generators.append(obj)

        elif isinstance(obj, Lock):
            self.__locks[obj] = len(self.__locks)

        elif isinstance(obj, Gauss):
            obj.qx.wavelength = self.lambda0
            obj.qy.wavelength = self.lambda0

            space = obj.node.space
            if space is not None:
                nr = space.nr.value
            else:
                nr = 1.0
            obj.qx.nr = nr
            obj.qy.nr = nr

            current_gauss = self.__gausses.get(obj.node)
            if current_gauss is not None:
                raise ValueError(
                    f"A Gauss object with name {current_gauss.name} already exists "
                    f"at the node {obj.node.full_name}"
                )

            self.__gausses[obj.node] = obj

            self.__insert_trace_dependency(obj)

            # Turn on HOMs if model is still plane-wave
            if not self.is_modal:
                self.modes(maxtem=0)

        elif isinstance(obj, ModelElement):
            # Model elements come in a variety of forms, which are dealt with above
            # if the object isn't any of these the bare minimum contract is that we
            # tell it to associate itself with this model and call _on_add to let it
            # do some initialisation if necessary
            pass
        else:
            raise Exception("Could not add object {}".format(str(obj)))

        if obj._add_to_model_namespace:
            # If the elment requests asks it will be added to the model namespace
            if hasattr(self, obj.name):
                raise Exception(
                    f"Not a valid {obj.__class__.__name__} name. An attribute "
                    f"called `{obj.name}` already exists in the Model"
                )

            # Can add objects to multiple namespaces for collecting
            # together like components as well as easy access
            assert isinstance(obj._namespace, tuple)
            for namespace in obj._namespace:
                parent = self
                for _ in namespace.split("."):
                    if len(_) > 0:
                        if hasattr(parent, _):
                            curr = getattr(parent, _)
                        else:
                            curr = Freezable()
                        parent._unfreeze()
                        setattr(parent, _, curr)
                        parent._freeze()
                        parent = curr

                parent._unfreeze()
                setattr(parent, obj.name, obj)
                parent._freeze()

        if hasattr(obj, "_on_add"):
            obj._on_add(self)
        if hasattr(obj, "_on_frequency_change"):
            self.__frequency_change_callbacks.append(obj._on_frequency_change)

        self.__elements[obj.name] = obj
        if unremovable:
            self.__not_removable.add(obj)

        # Notify that the TraceForest needs rebuilding on next beam_trace call
        # when adding an object which can change the forest structure
        self._rebuild_trace_forest = isinstance(obj, (Connector, TraceDependency))

    @locked_when_built
    def __add_node_to_graph(self, node, owner):

        if not self.network.has_node(node.full_name):
            ref = node.full_name
            self.network.add_node(
                ref, weakref=weakref.ref(node), owner=weakref.ref(owner)
            )

            if node.type == NodeType.OPTICAL:
                self.network.nodes[ref]["optical"] = True
            elif node.type == NodeType.MECHANICAL:
                self.network.nodes[ref]["mechanical"] = True
            elif node.type == NodeType.ELECTRICAL:
                self.network.nodes[ref]["electrical"] = True
            else:
                raise Exception("Type unhandled")

        elif not owner._borrows_nodes and node.type == NodeType.OPTICAL:
            raise Exception("Node {} already added".format(node))

    @locked_when_built
    def __add_connection_to_graph(self, name, From, To, owner):

        for _ in [From, To]:
            if not self.network.has_node(_.full_name):
                raise Exception("Node {} hasn't been added".format(_))

        self.network.add_edge(
            From.full_name,
            To.full_name,
            name=name,
            in_ref=weakref.ref(From),
            out_ref=weakref.ref(To),
            owner=weakref.ref(owner),
            length=1,
            coupling_type=owner.coupling_type(From, To),
            internal=From is To,  # if edge is to the same element
        )

    @locked_when_built
    def parse(self, text, spec=None):
        """Parses kat script and adds the resulting objects to the model.

        Parameters
        ----------
        text : :py:class:`str`
            The kat script to parse.

        spec : :class:`.spec.BaseSpec`, optional
            The language specification to use. Defaults to :class:`.script.spec.KatSpec`.

        See Also
        --------
        parse_file : Parse script file.
        parse_legacy : Parse Finesse 2 kat script.
        parse_legacy_file : Parse Finesse 2 kat script file.
        """
        from .script import parse

        parse(text, model=self, spec=spec)

    @locked_when_built
    def parse_file(self, path, spec=None):
        """Parses kat script from a file and adds the resulting objects to the model.

        Parameters
        ----------
        path : str, :class:`pathlib.Path`, or file-like
            The path or file object to read kat script from. If an open file object is
            passed, it will be read from and left open. If a path is passed, it will be
            opened, read from, then closed.

        spec : :class:`.spec.BaseSpec`, optional
            The language specification to use. Defaults to
            :class:`.script.spec.KatSpec`.

        See Also
        --------
        parse : Parse script.
        parse_legacy : Parse Finesse 2 kat script.
        parse_legacy_file : Parse Finesse 2 kat script file.
        """
        from .script import parse_file

        parse_file(path, model=self, spec=spec)

    @locked_when_built
    def parse_legacy(self, text):
        """Parses legacy (Finesse 2) kat script and adds the resulting objects to the
        model.

        Parameters
        ----------
        text : :py:class:`str`
            The kat script to parse.

        See Also
        --------
        parse_legacy_file : Parse Finesse 2 kat script file.
        parse : Parse Finesse 3 kat script.
        parse_file : Parse Finesse 3 kat script file.
        """
        from .script import parse_legacy

        parse_legacy(text, model=self)

    @locked_when_built
    def parse_legacy_file(self, path):
        """Parses legacy (Finesse 2) kat script from a file and adds the resulting
        objects to the model.

        Parameters
        ----------
        path : str, :class:`pathlib.Path`, or file-like
            The path or file object to read kat script from. If an open file object is
            passed, it will be read from and left open. If a path is passed, it will be
            opened, read from, then closed.

        See Also
        --------
        parse_legacy : Parse Finesse 2 kat script.
        parse : Parse Finesse 3 kat script.
        parse_file : Parse Finesse 3 kat script file.
        """
        from .script import parse_legacy_file

        parse_legacy_file(path, model=self)

    def unparse(self, inplace=True):
        """Serialise the model to kat script.

        Returns
        -------
        str
            The generated kat script.
        """
        from .script import unparse

        return unparse(self, ref_graph=self.syntax_graph if inplace else None)

    def unparse_file(self, path, inplace=True):
        """Serialise the model to kat script in a file.

        Parameters
        ----------
        path : str, :class:`pathlib.Path`, or file-like
            The path or file object to write kat script to. If an open file object is
            passed, it will be written to and left open. If a path is passed, it will be
            opened, written to, then closed.
        """
        from .script import unparse_file

        unparse_file(path, self, ref_graph=self.syntax_graph if inplace else None)

    @locked_when_built
    def merge(
        self, other, from_comp, from_port, to_comp, to_port, name=None, L=0, nr=1
    ):
        """Merges the model `other` with this model using a connection at the specified
        ports.

        .. note::

            Upon completion of this method call the `Model` instance `other` will
            be invalidated. All components and nodes within `other` will be associated
            with **only** this model.

        Parameters
        ----------
        other : :class:`.Model`
            A model configuration to merge into this model instance.

        from_comp : Sub-class of :class:`.Connector`
            The component to start a connection from.

        from_port : int
            Port of `from_comp` to initiate the connection from.

        to_comp : Sub-class of :class:`.Connector`
            The component to bridge the connection to.

        to_port : int
            Port of `to_comp` to bridge the connection to.

        name : str
            Name of connecting :class:`.Space` instance.

        L : float
            Length of the connecting space.

        nr : float
            Index of refraction of the connecting space.
        """
        self._unfreeze()
        raise NotImplementedError()
        self._settings.homs_view += other.homs

        # combine components/detectors
        for node in list(other.network.nodes):
            try:
                self.add(node.component)
            except Exception:
                continue
        # combine spaces
        for edge_tuple in list(other.network.edges):
            for edge in edge_tuple:
                try:
                    self.add(edge.space)
                except Exception:
                    continue

        # combine cavities
        for cav in other.cavities:
            self.add(cav)

        self.__network = nx.compose(self.__network, other.network)

        self.connect(from_comp, from_port, to_comp, to_port, name=name, L=L, nr=nr)
        self._freeze()

    @locked_when_built
    def add_frequency(self, freq):
        """Add a source frequency to the model description.

        Parameters
        ----------
        :class:`float` or :class:`.Frequency`
            The frequency to add.
        """
        if freq in self.__frequencies:
            warn(f"frequency {repr(freq.name)} already added to model")
        else:
            self.__frequencies.add(freq)

    def get_frequency_object(self, frequency_value):
        if frequency_value in self.__freq_map:
            return self.__freq_map[frequency_value][0]
        else:
            return None

    @locked_when_built
    def chain(self, *args, start=None, port=None):
        """Utility function for connecting multiple connectable objects in a sequential
        list together. Between each item the connection details can be specified, such
        as length or refractive index. This function also adds the elements to the model
        and returns those as a tuple to for the user to store if required.

        Examples
        --------
        Make a quick 1m cavity and store the added components into
        variables::

            l1, m1, m2 = ifo.chain(Laser('l1'), Mirror('m1'), 1, Mirror('m2'))

        Or be more specific about connection parameters by providing a
        dictionary. This dictionary is passed to the
        :meth:`Model.connect` method as kwargs so see there for which
        options you can specify. For optical connections we can set
        lengths and refractive index of the space::

            ifo.chain(
                Laser('l1'),
                Mirror('AR'),
                {'L':1e-2, 'nr':1.45},
                Mirror('HR')
            )

        A pre-constructed :class:`.Space`, :class:`.Wire`:

            ifo.chain(
                Laser('l1'),
                Mirror('AR'),
                Space('scav', L=1e-2, nr=1.45),
                Mirror('HR')
            )

        The starting point of the chain can be specfied for more
        complicated setups like a Michelson::

            ifo = Model()
            ifo.chain(Laser('lsr'), Beamsplitter('bs'))

            # connecting YARM to BS
            ifo.chain(
                1,
                Mirror('itmy'),
                1,
                Mirror('etmy'),
                start=ifo.bs,
                port=2,
            )

            # connecting XARM to BS
            ifo.chain(
                1,
                Mirror('itmx'),
                1,
                Mirror('etmx'),
                start=ifo.bs,
                port=3,
            )

        Parameters
        ----------
        start: component, optional
            This is the component to start the chain from. If None, then
            a completely new chain of components is generated.
        port: int, optional (required if `start` defined)
            The port number at the `start` component provided to start
            the chain from. This must be a free unconnected port at the
            `start` component or an exception will be thrown.

        Returns
        -------
        tuple
            A tuple containing the objects added. The `start` component
            is never returned.
        """

        connectors = []
        connections = []
        was_prev_connector = False

        if start is not None:
            if start not in self.components:
                raise Exception("Component %s is not in this model" % start)

            if port is None:
                raise Exception(
                    "Port keyword argument must also be"
                    "provided if specifying a start for"
                    "the chain."
                )

            connectors.append(start)
            was_prev_connector = True

        for i, item in enumerate(args):
            if isinstance(item, Space) or isinstance(item, Wire):
                connections.append({"connector": item})
                was_prev_connector = False
            elif isinstance(item, Connector):
                if was_prev_connector:
                    if i == 0 and start is not None:
                        connections.append({"port": port})
                    else:
                        connections.append({})

                connectors.append(item)
                was_prev_connector = True
                self.add(item)
            elif isinstance(item, Number):
                connections.append({"L": item})

                if i == 0 and start is not None:
                    connections[-1]["port"] = port

                was_prev_connector = False
            else:
                connections.append(item)
                was_prev_connector = False

        pairs = list(pairwise(connectors))

        # There should always be an equal number of connections
        # for each pair of components, otherwise we are missing something...
        assert len(pairs) == len(connections)

        for (a, b), conn in zip(pairs, connections):
            if "port" in conn:
                port = conn["port"]
                del conn["port"]
            else:
                if len(a.optical_nodes) == 2:
                    port = a.p1
                elif len(a.optical_nodes) == 4:
                    port = a.p2
                elif len(a.optical_nodes) > 4:
                    break
                else:
                    raise Exception("Unhandled: " + str(a, len(a.nodes)))

            if type(port) is int:
                port = a.ports[port - 1]

            self.connect(port, b.p1, **conn)

        # Don't return the starting point the user specified
        if start is None:
            return connectors
        else:
            return connectors[1:]

    @locked_when_built
    def link(self, *args, verbose=False):
        def grab_between(predicate, args):
            """Yields a pair of objects with any objects matching the predicate in
            between."""
            items = []
            between = []

            for x in args:
                if type(x) is str:
                    try:
                        x = self.get_element(x)
                    except KeyError:
                        x = self.get(x)

                if predicate(x):
                    items.append(x)
                else:
                    between.append(x)

                if len(items) == 2:
                    yield tuple(items), tuple(between)
                    items.pop(0)
                    between.clear()

        def get_component(obj):
            if isinstance(obj, ModelElement):
                return obj
            else:
                return obj.component

        items = grab_between(lambda x: isinstance(x, (ModelElement, Port, Node)), args)
        for objs, details in items:
            comps = [get_component(_) for _ in objs]
            if all(comps[0] is _ for _ in comps):
                if verbose:
                    print(
                        f"{objs[0]!r} and {objs[1]!r} are of the same element so skipping this connection"
                    )
            else:
                self.connect(*objs, *details, verbose=verbose)

    def get_elements_connected_to(self, element):
        """Returns a set of elements that `element` is connected to.

        Parameters
        ----------
        element : str or :class:.`Element`
            Element to query connections of
        """
        element = self.get_element(element)
        edges = []
        for node in element.nodes:
            for edge in self.network.in_edges(node, data=True):
                if edge[2]["owner"]() is not element:
                    edges.append(edge)
            for edge in self.network.out_edges(node, data=True):
                if edge[2]["owner"]() is not element:
                    edges.append(edge)

        # spaces and wires connecting this element to something
        connected_to = set()
        for _ in edges:
            connected_to.add(_[2]["owner"]())
        return connected_to

    @locked_when_built
    def connect(
        self, A, B, L=0, nr=1, *, delay=None, name=None, verbose=False, connector=None
    ):
        """Connects two ports in a model together. The ports should be of the same type,
        e.g. both optical ports.

        This method will also accept components from the user, in such cases it
        will loop through the ports and use the first one in `.ports` that is
        currently unconnected.

        As `connect` will try to be somewhat smart in guessing what the user is
        trying to connect, use `verbose=True` to print what is actually
        getting connected.

        Parameters
        ----------
        A : :class:`.Connector` or :class:`.Port`
            Component to connect

        B : :class:`.Connector` or :class:`.Port`
            Other component to connect

        L : float, optional
            Length of newly created :class:`.Space` or :class:`.Wire`
            instance. If connecting electronics, L will be treated as
            a delay in seconds

        nr : float, optional
            Index of refraction of newly created :class:`.Space`.

        delay : float, optional
            Delay time for electrical connections.

        name : str, optional
            Name of newly created :class:`.Space` or :class:`.Wire` instance.

        verbose : bool, optional
            When True, the actual connections being made will be printed.

        Raises
        ------
        Exception
            If matrix has already been built, either of `compA` or
            `compB` are not present in the model, either of `portA` or
            `portB` are already connected or either of `portA` or
            `portB` are not valid options at the specified component(s).
        """
        ports = [None, None]

        if isinstance(A, str):
            A = self.get(A)
        if isinstance(B, str):
            B = self.get(B)

        for item in [A, B]:
            # Check if these have been added to a model, if not add to this
            # if item._model is None:
            try:
                _ = item._model
            except ComponentNotConnected:
                if hasattr(item, "component"):
                    # In case some port or node has been provided instead
                    # get the actual component to add
                    self.add(item.component)
                else:
                    self.add(item)

        def signal_ports(obj):
            return tuple(
                p
                for p in obj.ports
                if p.type in (NodeType.MECHANICAL, NodeType.ELECTRICAL)
            )

        def get_input_port(ports):
            if ports[0].nodes[0].direction == NodeDirection.INPUT:
                rtn = ports[0]
            else:
                rtn = ports[1]
            if verbose:
                print(f"Selecting input port {rtn!r} from {ports}")
            return rtn

        def get_output_port(ports):
            if ports[0].nodes[0].direction == NodeDirection.INPUT:
                rtn = ports[1]
            else:
                rtn = ports[0]
            if verbose:
                print(f"Selecting output port {rtn!r} from {ports}")
            return rtn

        def is_electronic_component(obj):
            return all(p.type == NodeType.ELECTRICAL for p in obj.ports)

        def get_next_optical_port(obj):
            rtn = None
            for p in obj.ports:
                if not p.is_connected and p.type == NodeType.OPTICAL:
                    rtn = p
                    break
            if rtn is None:
                raise FinesseException(
                    f"No unconnected optcial ports left at {obj.name} to automatically choose from. Please specify an electrical or mechanical one if that was your aim."
                )
            if verbose:
                print(f"Selecting port {rtn!r} for {obj!r}")
            return p

        # Aim here is to try and be smart and accept some more user friendly
        # inputs rather than always specifying the port name.
        for i, obj in enumerate((A, B)):
            if isinstance(obj, Port):  # User gave us a port so just use that
                ports[i] = obj
            elif isinstance(obj, SignalNode):
                ports[i] = obj
            elif isinstance(obj, ModelElement):
                Np = len(obj.ports)
                if Np == 1:
                    # just select the first port as that's our only option
                    ports[i] = obj.ports[0]
                elif Np > 1:
                    # multiple ports! So which one to choose?
                    if i == 0:
                        # If we are the first argument...
                        if is_electronic_component(obj):
                            if Np == 2:
                                # if the first component is a two port electronics
                                # grab the output port
                                ports[i] = get_output_port(obj.ports)
                            else:
                                raise Exception(
                                    f"Must specify a port when connecting {A!r} as it has more than 1 port."
                                )
                        else:
                            ports[i] = get_next_optical_port(obj)
                    else:
                        # From the A object try and guess what to look for
                        # on the second B object.
                        ptype = ports[0].type

                        if ptype == NodeType.OPTICAL:
                            # connecting from an optical port, so find the frst optical
                            # port that isn't connected to anything else
                            ports[i] = get_next_optical_port(obj)
                        else:  # must be elec or mech signal node
                            # connecting from an elec port, now find an input port
                            sig_ports = signal_ports(obj)
                            Nsp = len(sig_ports)
                            if Nsp == 1:  # just select the only option we have
                                ports[i] = sig_ports[0]
                            elif Nsp == 2:
                                ports[i] = get_input_port(sig_ports)
                            else:
                                raise FinesseException(
                                    f"Too many signal ports to choose from at {obj!r} to automatically choose from. Specify one of {sig_ports}"
                                )
                else:
                    raise Exception("Model element {} has no ports".format(obj.name))
            elif isinstance(obj, OpticalNode):
                raise FinesseException(
                    f"Optical node {obj!r} cannot be explicitly connected to. Use its port instead `{obj.port.full_name}`."
                )
            else:
                raise FinesseException(f"Input {obj!r} cannot be connected")

        if connector is None:
            try:
                if all(p.type == NodeType.OPTICAL for p in ports):
                    if delay is not None:
                        raise Exception("Can't set delay for an optical space")
                    connector = Space(name, *ports, L=L, nr=nr)
                elif all(isinstance(p, SignalNode) for p in ports):
                    # User specified signal nodes so just wire them up directly
                    connector = Wire(
                        name, *ports, delay=(delay if delay is None else L)
                    )
                elif (
                    ports[0].type == NodeType.ELECTRICAL
                    or ports[0].type == NodeType.MECHANICAL
                ):
                    if nr != 1:
                        raise Exception(
                            "Can't set refractive index for an electronic connection"
                        )
                    if delay is None:
                        delay = L
                    connector = Wire(name, *ports, delay=delay)
                else:
                    raise FinesseException(
                        f"Do not know how to connect {ports[0]!r} to {ports[1]!r}"
                    )
            except Exception as ex:
                raise FinesseException(
                    f"Whilst trying to connect {ports[0]!r} to {ports[1]!r}, the following exception occurred:\n{ex}"
                )
        else:
            connector.connect(*ports)

        self.add(connector)

    @locked_when_built
    def disconnect(self, A, B):
        """Disconnects two elements `A` and `B`."""

    def get_network(self, network_type="full"):
        """Get specified network.

        Parameters
        ----------
        network_type : str, optional
            The network type to export: full (nodes, ports and components), "components" (just
            components), or "optical" (the optical subnetwork).

        Returns
        -------
        :class:`networkx.DiGraph`
            The network.

        Raises
        ------
        ValueError
            If the specified network_type is unknown.
        """
        ncmp = network_type.casefold()

        if ncmp == "full":
            return self.network
        elif ncmp == "components":
            return self.to_component_network()
        elif ncmp == "optical":
            return self.optical_network

        raise ValueError(f"Unrecognised network type: '{network_type}'.")

    def plot_graph(self, network_type, **kwargs):
        """Plot the node network.

        Parameters
        ----------
        network_type : str
            The network type to plot (see :meth:`.Model.get_network`).

        Other Parameters
        ----------------
        **kwargs
            Keywords supported by :func:`.plot_nx_graph`.
        """
        from .plotting import plot_nx_graph

        plot_nx_graph(self.get_network(network_type), **kwargs)

    def __toggle_param_locks(self, state):
        """Togglin."""
        LOGGER.info(f"Toggle parameter lock to {state}")
        for k in self.__elements:
            el = self.__elements[k]
            for p in el._params:
                # if this is marked as tunable then don't lock it
                if p.is_tunable and state is True:
                    p._locked = False
                    LOGGER.info(f"{repr(p)} is not being locked")
                else:
                    p._locked = state

    def get_changing_edges_elements(self):
        """
        Returns
        -------
        tuple(set of (node1-name, node2-name) edges, dict(weakref(element):list))
            Returns a list of the network edges that will be changing, further information
            on the edge can be retreived directly from the model network. Also returned is
            a dictionary of elements and which parameter is changing
        """
        changing_elements = defaultdict(set)
        changing_edges = set()

        for _ in self.network.edges():
            owner = self.network.edges[_]["owner"]
            if owner() not in changing_elements:
                for p in owner().parameters:
                    if p.is_changing:
                        changing_elements[owner].add(p)
                        changing_edges.add(_)
        return changing_edges, changing_elements

    def unbuild(self):
        """If a model has been built then this function undoes the process so the model
        can be changed and rebuilt if required."""
        if not self.is_built:
            raise Exception("Model has not been built")

        # To unfreeze a graph you have to rebuild it
        self.__network = nx.DiGraph(self.__network)
        self.__toggle_param_locks(False)
        self.__is_built = False
        self._on_unbuild()  # fire event

    @locked_when_built
    def run(self, analysis=None, return_state=False, progress_bar=False):
        """Runs the current analysis set for this model. If no analysis has been set in
        the model and the ``analysis`` argument is None, then this will run a
        ``Noxaxis()`` on the current model.

        If a separate analysis has been provided with the `analysis` argument then
        this will be run instead of what has been set to `model.analysis`.

        Parameters
        ----------
        analysis : [str, Action], optional
            KatScript code for an analysis or an analysis object to run.

        return_state : bool, optional
            Whether to return the state of each model generated by this analysis.

        progress_bar : bool, optional
            Whether to show progress bars or not

        Returns
        -------
        sol : Solution Object
            Solution to the analysis being performed
        states : objects, only when return_state == True
            States generated by the analysis

        Examples
        --------
        Run a model with the analysis specified in the original KatScript
        >>> import finesse
        >>> model = finesse.Model()
        >>> model.parse('''
        ... l l1
        ... pd P l1.p1.o
        ... # Analysis
        ... for(l1.P, [0, 1, 2, 3], print(l1.P))
        ... ''')
        >>> model.run()

        Or you can run a separate analysis
        >>> model.run("noxaxis()")
        """
        from .analysis.actions import Noxaxis, Action

        curr_analysis = self.analysis
        try:
            if analysis is None:
                # nothing has been set so use what is in the model or noxaxis if nothing
                _analysis = self.analysis or Noxaxis()
            elif isinstance(analysis, str):
                # Katscript analysis requested
                self.parse(analysis)
                _analysis = self.analysis
            elif isinstance(analysis, Action):
                _analysis = analysis
            else:
                raise ValueError(f"Cannot handle analysis input `{analysis}`")

            rtn = _analysis._run(
                self, return_state=return_state, progress_bar=progress_bar
            )

            if not return_state:
                s = rtn
            else:
                s, states = rtn

            # Return first actual solution for something rather than base
            # unless there's multiple children
            while type(s) is BaseSolution and len(s.children) == 1:
                _s = s.children[0]
                _s.parent = None
                s.children.clear()
                s = _s

            if not return_state:
                return s
            else:
                return s, states
        finally:
            self.analysis = curr_analysis

    def get_element(self, value):
        """Returns an element in this model that matches the requested value. This input
        can be either a string name or an element that might be owned by another model.
        In the latter case the `name` attribute will be extracted from the value and a
        search done in this model for an equivalent element.

        Parameters
        ----------
        value : [str|`Element`]
            Name or equivalently named `Element` object to extract from this
            model.

        Raises
        ------
        `KeyError` when element cannot be found or `FinesseException` when the
        input `value` cannot be used.

        Examples
        --------
            >>> import finesse
            >>> model = finesse.Model()
            >>> model.parse('''
            ... l l1 P=1
            ... l l2 P=2
            ... ''')
            >>> model.get_element('l1'), model.get_element('l2')
            (<'l1' @ 0x122cf9fa0 (Laser)>, <'l2' @ 0x122cf9f40 (Laser)>)

        Creating a copy of the model and getting elements will return elements
        with the same name but different `id`.

            >>> model2 = model.deepcopy()
            >>> model2.get_element('l1'), model2.get_element('l2')
            (<'l1' @ 0x122d35c10 (Laser)>, <'l2' @ 0x122d35df0 (Laser)>)

        Now if we try and select `l1` using an element from a different model we
        should get the correct element with name `l1` from that model
            >>> model.get_element(model2.l1)
            <'l1' @ 0x122cf9fa0 (Laser)>
            >>> model2.get_element(model.l1)
            <'l1' @ 0x122d35c10 (Laser)>
        """
        if isinstance(value, str):
            return self.elements[value]
        elif hasattr(value, "name"):
            return self.elements[value.name]
        else:
            raise FinesseException(f"Cannot get an element using the input {value}")

    def get_elements_of_type(self, *element_type):
        """Extracts elements of a specific type from this model.

        Parameters
        ----------
        *element_type : type or sequence of types
            The element type(s) to retrieve.

        Returns
        -------
        generator
            The filtered results.

        Examples
        --------
        >>> IFO.get_elements_of_type(finesse.components.Mirror)
        <filter object at 0x7fa34da6a080>
        >>> tuple(IFO.get_elements_of_type(finesse.components.Mirror))
        (<'m2' @ 0x7ff81a50b6a0 (Mirror)>, <'m1' @ 0x7ff81a50be48 (Mirror)>)
        >>> tuple(IFO.get_elements_of_type(finesse.components.Mirror, finesse.components.Beamsplitter))
        (<'m2' @ 0x7ff81a50b6a0 (Mirror)>, <'m1' @ 0x7ff81a50be48 (Mirror)>, <'bs1' @ 0x7ff81a50bf33 (Beamsplitter)>)
        """
        return filter(lambda x: isinstance(x, element_type), self.elements.values())

    def get_active_signal_nodes(self):
        """Returns the electrical and mechanical nodes that are active in a model, i.e.
        ones that need to be solved for because:

            * they have both input and output edges
            * have output edges and is a signal input
            * is used by a detector
            * has an input optical edge and some output edge

        This could be more sophisticated and perhaps use the graph
        in a more correct way. For example, this will not prune
        some long line of electrical components connected to a
        mechanical node that drives some optical field. Or in other
        words, it will not determine if an input edge has an active
        node on the other end.

        Returns
        -------
        tuple of nodes
        """

        active = set()
        for node in self.signal_nodes:
            # can be some signal gen input
            # or this node might be used as some output
            is_active = (
                node.has_signal_injection or len(node.used_in_detector_output) > 0
            )
            if not is_active:
                full_name = node.full_name
                # For a node to be potentially active it needs to have
                # both input and output edges. If not then there will
                # not be any information flowinging through it, as we're
                # not injecting, etc. into it either
                is_active |= (
                    self.network.in_degree(full_name) > 0
                    and self.network.out_degree(full_name) > 0
                )
            if is_active:
                active.add(node)
        # add nodes that wires will need
        if hasattr(self, "wires"):
            for w in self.wires:
                active.add(w.nodeA)
                active.add(w.nodeB)

        return tuple(active)

    def __pre_build_checks(self):
        # TODO (sjr) Probably need different checks dependent upon what type
        #            of simulation is about to built and executed eventually

        if not self.is_modal:
            dets_req_trace = list(filter(lambda d: d.needs_trace, self.detectors))
            if dets_req_trace:
                warn(
                    f"Switching on modes (at maxtem = 0) as the model contains the "
                    f"following detectors which require a modal basis: "
                    f"{[d.name for d in dets_req_trace]}"
                )
                self.modes(maxtem=0)

        expect_unstable_handle = ("auto", "mask", "abort")
        unstable_handle = self.sim_trace_config.get("unstable_handling")
        if unstable_handle not in expect_unstable_handle:
            raise ValueError(
                "Expected 'unstable_handling' entry of sim_trace_config to be one of "
                f"{', '.join(expect_unstable_handle)}; but got {unstable_handle}."
            )

        if self._settings.phase_config.zero_k00:
            if not np.all(self.homs[0] == [0, 0]):
                raise RuntimeError(
                    "Model phase configuration is set up to zero HG00 -> HG00 "
                    "coupling coefficients but the HG00 mode is not included!"
                )

    @locked_when_built
    def _build(self, frequencies=None):
        """
        NOTE: Consider using :function:`finesse.model.Model.built()`
        instead of this method.

        This is the first step required to run a
        simulation of the model. At this stage the layout and connections
        of the model must be finalised so that the underlying sparse matrix
        can be allocated and laid out. If this changes the model must be
        rebuilt.

        What this method returns are Simulation objects. These are the
        matrix representation of the model which are used to generate
        numerical outputs. The Simulation and Model objects are linked
        together, changing the Model parameters will result in the
        Simulation objects using the new values when they are solved.

        A custom list of carrier frequencies can be specfied to run the simulations
        with. Audio frequencies will be generated from this list separately by the code. `None` will
        result in the default algorithm computing the required frequency bins,
        :func:`.frequency.generate_frequency_list`, which can be
        called by the user and added to if additional frequency bins are required.

        Parameters
        ----------
        frequencies : list of :class:`.Symbol`
            Custom list of carrier frequencies can be specfied to run the simulations with.

        Returns
        -------
        sim : object
            A single simulation object is returned that should be used to perform
            simulations with this model.

        Raises
        ------
        Exception
            If the model is in a built state already. It must be destroyed
            first before it can be built again.
        """
        if frequencies:
            raise NotImplementedError("Custom frequencies not implemented yet")

        self.__pre_build_checks()
        self._on_pre_build()

        nx.freeze(self.network)
        self.__is_built = True
        self.__toggle_param_locks(True)

        # TODO ddb I like this AccesSimulation idea but I think there's
        # some more refactoring to do with the simulations. Maybe
        #   BaseSimulation > TraceSimulation > CarrierSignalMatrixSimulation

        # TODO ddb forcing this to be true, ends up making logic difficult throughout
        # the simulation code with what is and is not allocated
        needs_matrix = True  # (
        #     any(d.needs_fields for d in self.detectors)
        #     or len(tuple(self.get_elements_of_type(_Readout))) > 0
        #     or self.fsig.f.value is not None
        # )
        # so far the only simulation we can build is a carrier+signal matrix type
        # of simulation. Eventually here we need some logic to decide what to run
        # and return the relevant simulation object.
        from finesse.simulations.basematrix import CarrierSignalMatrixSimulation

        return CarrierSignalMatrixSimulation(self, "sim", needs_matrix=needs_matrix)

    @locked_when_built
    @contextmanager
    def built(self):
        sim = self._build()

        try:
            sim.__enter__()
            # Yield and let the caller do something with the model
            yield sim

        finally:
            sim.__exit__(None, None, None)
            self.unbuild()

    def __node_exists_check(self, node):
        if not self.network.has_node(node.full_name):
            raise NodeException("Node {} is not in the model".format(node), node)

    def path(self, from_node, to_node, via_node=None):
        """Retrieves an ordered container of the path trace between the specified nodes.

        The return type is an :class:`.OpticalPath` instance which stores an underlying
        list of the path data (see the documentation for :class:`.OpticalPath` for details).

        Parameters
        ----------
        from_node : :class:`.Node`
            Node to trace from.

        to_node : :class:`.Node`
            Node to trace to.

        via_node : :class:`.Node` (or sequence of)
            Node(s) to traverse via in the path.

        Returns
        -------
        out : :class:`.OpticalPath`
            A container of the nodes and components between `from_node` and `to_node`
            in order.

        Raises
        ------
        e1 : :class:`.NodeException`
            If either of `from_node`, `to_node` are not contained within the model.

        e2 : :obj:`networkx.NetworkXNoPath`
            If no path can be found between `from_node` and `to_node`.
        """
        from_node, to_node, via_node = self.__parse_path_nodes(
            from_node, to_node, via_node
        )

        try:
            self.__node_exists_check(from_node)
            self.__node_exists_check(to_node)
        except NodeException:
            raise

        if (from_node is to_node) and (via_node is None):
            return OpticalPath([])

        from_node = from_node.full_name
        to_node = to_node.full_name

        if via_node is None:
            try:
                path = nx.shortest_path(self.optical_network, from_node, to_node)
            except nx.exception.NetworkXNoPath:
                raise

            path_between = []
            for node in path:
                node_ref = self.network.nodes[node]["weakref"]()

                path_between.append((node_ref, node_ref.component))

            fullpath = []
            for node, comp in path_between:
                if node.is_input:
                    fullpath.append((node, comp))
                else:
                    fullpath.append((node, node.space))

            return OpticalPath(fullpath)

        if not is_iterable(via_node):
            via_node = [via_node]

        via_node = [via.full_name for via in via_node]

        try:
            paths = [nx.shortest_path(self.optical_network, from_node, via_node[0])]
            # find intermediate paths
            for i, node in enumerate(via_node[:-1]):
                paths.append(
                    nx.shortest_path(self.optical_network, node, via_node[i + 1])
                )
            paths.append(nx.shortest_path(self.optical_network, via_node[-1], to_node))
        except nx.exception.NetworkXNoPath:
            raise

        path_between = [
            (
                self.network.nodes[node]["weakref"](),
                self.network.nodes[node]["weakref"]().component,
            )
            for node in paths[0]
        ]

        for path in paths[1:]:
            path_between += [
                (
                    self.network.nodes[node]["weakref"](),
                    self.network.nodes[node]["weakref"]().component,
                )
                for node in path
            ][
                1:
            ]  # don't want to repeat via node

        fullpath = []
        for node, comp in path_between:
            if node.is_input:
                fullpath.append((node, comp))
            else:
                fullpath.append((node, node.space))

        return OpticalPath(fullpath)

    def sub_model(self, from_node, to_node):
        """Obtains a subgraph of the complete configuration graph between the two
        specified nodes.

        Parameters
        ----------
        from_node : :class:`.Node`
            Node to trace from.

        to_node : :class:`.Node`
            Node to trace to.

        Returns
        -------
        G : ``networkx.graphviews.SubDiGraph``
            A SubGraph view of the subgraph between `from_node` and `to_node`.
        """
        try:
            self.__node_exists_check(from_node)
            self.__node_exists_check(to_node)
        except NodeException:
            raise

        nodes_between_set = {
            node
            for path in nx.all_simple_paths(
                self.__network, source=from_node, target=to_node
            )
            for node in path
        }
        return self.__network.subgraph(nodes_between_set)

    def component_tree(self, root=None):
        """Retrieves a tree containing the network representing the components connected
        to the specified root.

        Parameters
        ----------
        root : :class:`.ModelElement`
            The component to use as the root of the tree.

        Returns
        -------
        :class:`.TreeNode`
            The root tree node, with connected components as branches.

        Raises
        ------
        ValueError
            If the specified root is not a model element.
        """
        from finesse.components import Laser

        if root is None:
            for root in self.components:
                if isinstance(root, Laser):
                    break
        else:
            if root not in self.components:
                raise ValueError("Specified root is not a component.")
        return TreeNode.from_network(self.to_component_network(), root.name)

    # Method name is a little mis-leading here but anyway...
    def _update_symbolic_abcds(self):
        """Updates the *numeric* ABCD matrices of all components which have geometric
        parameters which contain symbolic references to other parameters."""
        # TODO (sjr) Replace with a loop over just pre-determined geometric parameters
        #            for efficiency, probably not a big deal currently though (I hope)
        done = set()
        for el in self.__elements.values():
            if el in done:
                continue

            for p in el.parameters:
                # TODO (jwp): determine if is_symbolic is being updated correctly
                if p.is_geometric and p.is_symbolic:
                    el._re_eval_abcds()
                    done.add(el)

    def detect_mismatches(self, ignore_AR=True, **kwargs):
        """Detect the mode mismatches in the model.

        If you want to display these mismatches in a nicely formatted
        table then use :meth:`Model.print_mismatches`.

        Parameters
        ----------
        ignore_AR : bool, optional
            When True, with surfaces with R=0 the reflection mismatch is ignored
        kwargs : Keyword arguments
            Arguments to pass to :meth:`Model.beam_trace`.

        Returns
        -------
        mismatches : dict
            A dictionary of `(n1, n2): mms` where `n1` is the From node
            and `n2` is the To node. The value `mms` is another dict
            consisting of ``"x"`` and ``"y"`` keys mapping to the mismatch
            values for the tangential and sagittal planes, respectively.
        """
        # Perform the beam trace first so that trace_forest
        # gets updated if needs be
        trace = self.beam_trace(store=False, **kwargs)

        mismatches = {}
        couplings = self.trace_forest.find_potential_mismatch_couplings()

        # No mode mismatch couplings present
        if not couplings:
            return mismatches

        for node1, node2 in sorted(couplings, key=lambda npair: npair[0].full_name):
            component = node1.component
            if (
                ignore_AR
                and component.interaction_type(node1, node2)
                == InteractionType.REFLECTION
            ):
                if hasattr(component, "R") and component.R.value == 0:
                    continue

            qx1, qy1 = trace[node1]
            qx2, qy2 = trace[node2]

            nr1 = refractive_index(node1)
            nr2 = refractive_index(node2)
            # Both nodes attached to same component by definition
            comp = node1.component
            Mx = comp.ABCD(node1, node2, direction="x")
            My = comp.ABCD(node1, node2, direction="y")

            qx1_matched = transform_beam_param(Mx, qx1, nr1, nr2)
            qy1_matched = transform_beam_param(My, qy1, nr1, nr2)

            mismatches[(node1, node2)] = {}
            if qx1_matched != qx2:
                mismatches[(node1, node2)]["x"] = BeamParam.mismatch(qx1_matched, qx2)
            if qy1_matched != qy2:
                mismatches[(node1, node2)]["y"] = BeamParam.mismatch(qy1_matched, qy2)

            # Remove the entry if the mismatch values in both planes were zero
            if not mismatches[(node1, node2)]:
                del mismatches[(node1, node2)]

        return mismatches

    def print_mismatches(self, table_fmt="fancy_grid", ignore_AR=True, **kwargs):
        """Prints the mismatches computed by :meth:`Model.detect_mismatches` to an
        easily readable table.

        Parameters
        ----------
        table_fmt : str, optional
            Table format option to pass to tabulate.
        ignore_AR : bool, optional
            When True, with surfaces with R=0 the reflection mismatch is ignored
        kwargs : Keyword arguments
            Arguments to pass to :meth:`Model.beam_trace`.
        """
        from tabulate import tabulate

        headers = ["Coupling", "Mismatch (x)", "Mismatch (y)"]
        table = []

        mismatches = self.detect_mismatches(ignore_AR=ignore_AR, **kwargs)
        for (n1, n2), mm_values in mismatches.items():
            mmx = mm_values.get("x", 0)
            mmy = mm_values.get("y", 0)

            table.append([f"{n1.full_name} -> {n2.full_name}", mmx, mmy])

        tb = tabulate(table, headers, tablefmt=table_fmt)
        print(tb)

    def compute_space_gouys(self, deg=True, **kwargs):
        """Calculate the Gouy phases accumulated over each space.

        If you want to display these phases in a nicely formatted
        table then use :meth:`Model.print_space_gouys`.

        Parameters
        ----------
        deg : bool, optional; default = True
            Whether to convert each phase to degrees.

        kwargs : Keyword arguments
            Arguments to pass to :meth:`Model.beam_trace`.

        Returns
        -------
        gouys : dict
            A dictionary of `space: gouy` where `space` is a :class:`.Space`
            object and `gouy` is another dict consisting of ``"x"`` and ``"y"``
            keys mapping to the Gouy phase values for the tangential and
            sagittal planes, respectively.
        """
        trace = self.beam_trace(store=False, **kwargs)

        scale_func = math.degrees if deg else lambda x: x

        gouys = {}
        for space in self.spaces:
            qx_p1o, qy_p1o = trace[space.p1.i]
            qx_p2i, qy_p2i = trace[space.p2.o]

            gouys[space] = {
                "x": scale_func(abs(qx_p2i.psi - qx_p1o.psi)),
                "y": scale_func(abs(qy_p2i.psi - qy_p1o.psi)),
            }

        return gouys

    def print_space_gouys(self, table_fmt="fancy_grid", deg=True, **kwargs):
        """Prints the space Gouy phases, as computed by
        :meth:`Model.compute_space_gouys`, to an easily readable table.

        Parameters
        ----------
        table_fmt : str, optional
            Table format option to pass to tabulate.

        deg : bool, optional; default = True
            Whether to convert each phase to degrees.

        kwargs : Keyword arguments
            Arguments to pass to :meth:`Model.beam_trace`.
        """
        from tabulate import tabulate

        units = "deg" if deg else "rad"
        headers = ["Space", f"Gouy (x) [{units}]", f"Gouy (y) [{units}]"]
        table = []

        gouys = self.compute_space_gouys(deg=deg, **kwargs)
        for space, gouy_d in gouys.items():
            gouy_x = gouy_d.get("x", 0)
            gouy_y = gouy_d.get("y", 0)

            table.append([f"{space.name}", gouy_x, gouy_y])

        print(tabulate(table, headers, tablefmt=table_fmt))

    @locked_when_built
    def create_mismatch(self, node, w0_mm=0, z_mm=0):
        """Sets the beam parameters such that a mismatch of the specified percentage
        magnitude (in terms of :math:`w_0` and :math:`z`) exists at the given `node`.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            The node to to create the mismatch at.

        w0_mm : float or sequence, optional
            The percentage magnitude of the mismatch in the waist size. This
            can also be a two-element sequence specifying the waist size mismatches
            for an astigmatic beam. Defaults to zero percent for both planes.

        z_mm : float or sequence, optional
            The percentage magntiude of the mismatch in the distance to
            the waist. This can also be a two-element sequence specifying the distance
            to waist mismatches for an astigmatic beam. Defaults to zero percent for
            both planes.

        Returns
        -------
        gauss : :class:`.Gauss`
            The Gauss object created or modified via this mismatch.
        """
        if not self.__network.has_node(node.full_name):
            raise NodeException("Specified node does not exist within the model", node)

        trace = self.beam_trace(store=False)
        qx, qy = trace[node]
        qx_w0, qy_w0 = qx.w0, qy.w0
        qx_z, qy_z = qx.z, qy.z

        if not is_iterable(w0_mm):
            qx_w0 *= 1 + (w0_mm / 100)
            qy_w0 *= 1 + (w0_mm / 100)
        else:
            qx_w0 *= 1 + (w0_mm[0] / 100)
            qy_w0 *= 1 + (w0_mm[1] / 100)

        if not is_iterable(z_mm):
            qx_z *= 1 + (z_mm / 100)
            qy_z *= 1 + (z_mm / 100)
        else:
            qx_z *= 1 + (z_mm[0] / 100)
            qy_z *= 1 + (z_mm[1] / 100)

        nr = refractive_index(node)
        qx_bp = BeamParam(w0=qx_w0, z=qx_z, nr=nr)
        qy_bp = BeamParam(w0=qy_w0, z=qy_z, nr=nr)

        if node in self.__gausses:
            self.update_gauss(node, qx_bp, qy_bp)
        else:
            name = f"AUTO_MM_{node.component.name}"
            self.add(Gauss(name, node, qx=qx_bp, qy=qy_bp))

        return self.__gausses.get(node)

    @locked_when_built
    def add_matched_gauss(self, node, name=None, priority=0, matched_to=None):
        """Adds a :class:`.Gauss` object mode matched to the model at the specified
        `node`. If `matched_to` is given then the Gauss object will be matched to this,
        otherwise it will be mode matched to whichever dependency the `node` relies upon
        currently.

        Parameters
        ----------
        node :class:`.OpticalNode`
            The node instance to add the Gauss at.

        name : str, optional
            Optional name of the new Gauss object. If not specified then the name
            will be automatically given as "AUTO_MM_nodename" where `nodename` is
            the node's :attr:`full name <.Node.full_name>`.

        priority : int, optional; default: 0
            The priority value of the Gauss object. See :attr:`.TraceDependency.priority`
            for details on the argument.

        matched_to : :class:`.TraceDependency`, optional
            The trace dependency to solely match to.
        """
        if not self.__network.has_node(node.full_name):
            raise NodeException("Specified node does not exist within the model", node)

        if node in self.__gausses:
            raise ValueError(f"A Gauss object already exists at node {node.full_name}")

        if matched_to is not None and not isinstance(
            matched_to, (TraceDependency, str)
        ):
            raise ValueError("Expected matched_to arg to be of type TraceDependency.")

        trace = self.beam_trace(enable_only=matched_to, store=False)
        qx, qy = trace[node]

        if name is None:
            name = f"AUTO_MM_{node.component.name}"

        self.add(Gauss(name, node, qx=qx, qy=qy, priority=priority))
        return self.__gausses.get(node)

    def update_gauss(self, node, qx=None, qy=None):
        """Update the value of a manual beam parameter (i.e. :class:`.Gauss` object) at
        the specified `node`.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            The node instance to update the gauss at.

        qx : :class:`.BeamParam` or complex, optional
            Beam parameter in tangential plane.

        qy : :class:`.BeamParam` or complex, optional
            Beam parameter in sagittal plane.
        """
        if not isinstance(node, OpticalNode):
            raise TypeError(
                f"Expected argument 'node' to be of type OpticalNode "
                f"but got value of type {type(node)}"
            )

        gauss = self.__gausses.get(node)
        if gauss is None:
            raise ValueError(
                f"Node {node.full_name} has no Gauss object associated with it."
            )

        if qx is None and qy is None:
            warn("Model.update_gauss called with no change to qx, qy.")

        if qx is not None:
            self.__gausses[node].qx = qx
        if qy is not None:
            self.__gausses[node].qy = qy

    def cavity_mismatch(self, cav1=None, cav2=None):
        """See :func:`finesse.tracing.tools.compute_cavity_mismatches`"""
        return tracetools.compute_cavity_mismatches(self, cav1, cav2)

    def print_cavity_mismatches(
        self, direction=None, percent=False, tablefmt="fancy_grid"
    ):
        """Prints the mismatches between each cavity in an easily readable table format.

        If either of each cavity in a coupling is unstable then the mismatch values
        between these will be displayed as ``nan``.

        Parameters
        ----------
        direction : str, optional; default: None
            The plane to compute mismatches in, "x" for tangential, "y" for sagittal. If
            not given then tables for both planes will be printed.

        percent : bool, optional; default: False
            Whether mismatch values are displayed in terms of percentage. Defaults to
            False such that the values are given as fractional mismatches.

        table_fmt : str, optional
            Table format option to pass to tabulate.
        """
        if not self.cavities:
            warn("No cavities present in the model.")
            return

        from tabulate import tabulate

        mmx, mmy = self.cavity_mismatch()

        headers = [cav.name for cav in self.cavities]
        table_x = []
        table_y = []

        scale = 100 if percent else 1
        for cav1 in self.cavities:
            row_x = [cav1.name]
            row_y = [cav1.name]
            for cav2 in self.cavities:
                row_x.append(scale * mmx[(cav1.name, cav2.name)])
                row_y.append(scale * mmy[(cav1.name, cav2.name)])

            table_x.append(row_x)
            table_y.append(row_y)

        if direction is None:
            direction = "x", "y"

        if "x" in direction:
            headers_x = headers.copy()
            headers_x.insert(0, "(Tangential plane)")
            tbx = tabulate(table_x, headers_x, tablefmt=tablefmt)
            print(tbx)
        if "y" in direction:
            headers_y = headers.copy()
            headers_y.insert(0, " (Sagittal plane) ")
            tby = tabulate(table_y, headers_y, tablefmt=tablefmt)
            print(tby)

    def __optical_node_from_str(self, name, dir_if_port="o", reject_ports=False):
        args = name.split(".")
        if len(args) == 2:  # name is a port string
            if reject_ports:
                raise ValueError(
                    f"Via port {name} is ambiguous, cannot safely assume node "
                    "direction. Please specify the full node string instead."
                )
            name += "." + dir_if_port
        else:
            if len(args) != 3:
                raise ValueError(f"Unexpected port or node name format: {name}")

        return self.network.nodes[name]["weakref"]()

    def __parse_path_nodes(self, from_node, to_node, via_node):
        if from_node is not None and not isinstance(from_node, OpticalNode):
            if isinstance(from_node, Port):
                from_node = from_node.o
            elif isinstance(from_node, str):
                from_node = self.__optical_node_from_str(from_node, dir_if_port="o")
            else:
                raise TypeError("Unexpected type for from_node.")

        if to_node is not None and not isinstance(to_node, OpticalNode):
            if isinstance(to_node, Port):
                to_node = to_node.i
            elif isinstance(to_node, str):
                to_node = self.__optical_node_from_str(to_node, dir_if_port="i")
            else:
                raise TypeError("Unexpected type for to_node.")

        if via_node is not None and not isinstance(via_node, OpticalNode):
            if isinstance(via_node, Port):
                raise ValueError(
                    f"Via port {via_node} is ambiguous, cannot safely assume node "
                    "direction. Please specify the optical node instead."
                )
            elif isinstance(via_node, str):
                via_node = self.__optical_node_from_str(via_node, reject_ports=True)
            else:
                raise TypeError("Unexpected type for via_node.")

        return from_node, to_node, via_node

    def ABCD(
        self,
        from_node=None,
        to_node=None,
        via_node=None,
        path=None,
        direction="x",
        symbolic=False,
        solution_name=None,
    ):
        """See :func:`finesse.tracing.tools.compute_abcd`

        .. note::

            The only difference to the above function is that any of `from_node`, `to_node`,
            `via_node` can be specified as strings.
        """
        fn, tn, vn = self.__parse_path_nodes(from_node, to_node, via_node)
        return tracetools.compute_abcd(
            fn, tn, vn, path, direction, symbolic, solution_name
        )

    def acc_gouy(
        self,
        from_node=None,
        to_node=None,
        via_node=None,
        path=None,
        q_in=None,
        direction="x",
        symbolic=False,
        degrees=True,
        **kwargs,
    ):
        """See :func:`finesse.tracing.tools.acc_gouy`

        .. note::

            The only difference to the above function is that any of `from_node`, `to_node`,
            `via_node` can be specified as strings.
        """
        fn, tn, vn = self.__parse_path_nodes(from_node, to_node, via_node)
        return tracetools.acc_gouy(
            fn,
            tn,
            vn,
            path,
            q_in,
            direction,
            symbolic,
            degrees,
            **kwargs,
        )

    def propagate_beam(
        self,
        from_node=None,
        to_node=None,
        via_node=None,
        path=None,
        q_in=None,
        direction="x",
        symbolic=False,
        solution_name=None,
        **kwargs,
    ):
        """See :func:`finesse.tracing.tools.propagate_beam`

        .. note::

            The only difference to the above function is that any of `from_node`, `to_node`,
            `via_node` can be specified as strings.
        """
        fn, tn, vn = self.__parse_path_nodes(from_node, to_node, via_node)
        return tracetools.propagate_beam(
            fn,
            tn,
            vn,
            path,
            q_in,
            direction,
            symbolic,
            solution_name,
            **kwargs,
        )

    def propagate_beam_astig(
        self,
        from_node=None,
        to_node=None,
        via_node=None,
        path=None,
        qx_in=None,
        qy_in=None,
        symbolic=False,
        solution_name=None,
        **kwargs,
    ):
        """See :func:`finesse.tracing.tools.propagate_beam_astig`

        .. note::

            The only difference to the above function is that any of `from_node`, `to_node`,
            `via_node` can be specified as strings.
        """
        fn, tn, vn = self.__parse_path_nodes(from_node, to_node, via_node)
        return tracetools.propagate_beam_astig(
            fn,
            tn,
            vn,
            path,
            qx_in,
            qy_in,
            symbolic,
            solution_name,
            **kwargs,
        )

    def beam_trace(
        self,
        order=None,
        disable=None,
        enable_only=None,
        symmetric=True,
        store=True,
        solution_name="beam_trace",
    ):
        """Performs a full beam trace on the model, calculating the beam parameters at
        each optical node.

        Beam tracing requires at least one stable :class:`.TraceDependency` object -
        defined as a :class:`.Gauss` or :class:`.Cavity` object - in the model. Note
        that :class:`.Cavity` objects are not determined automatically, they must be
        explicitly added to the model.

        The order in which the beam tracing is performed is as follows:

         * All internal cavity traces are carried out initially, i.e. any nodes
           that are part of a path of a :class:`.Cavity` instance in the model will
           be traced using the cavity eigenmode as the basis. See the note below for
           what happens in the case of overlapping cavities.
         * If `order` is **not** specified, then the dependency ordering given by
           :attr:`.Model.trace_order` is used; i.e. beam traces are performed from
           each dependency in this list where any overlapping trees from multiple
           dependencies will always use the first dependency's tree.
         * If `order` **is** specified, then beam traces from each dependency given in this
           argument will be carried out in the given order, in the same way as above. This
           effectively allows temporary overriding of the trace order for specific beam
           trace calls.

        Certain dependencies can be switched off via the `disable` or `enable_only` arguments.

        Full details on the beam tracing algorithm are given in :ref:`tracing_manual`.

        .. note::

            .. rubric:: Overlapping cavities

            In complicated configurations, such as dual-recycled Michelson interferometers, it is
            often the case that there will be *overlapping* cavities; i.e. cavities which share
            common optical nodes in their paths. This naturally leads to the question - in which
            basis are these common nodes being set?

            The algorithm used by this method will prioritise the internal trace of the cavity
            as follows:

             * If `order` is **not** given then the cavity appearing first in :attr:`.Model.trace_order`
               will be used for setting the beam parameters of all nodes in this cavity path - *including*
               any nodes which are shared with other cavity instances.
             * Otherwise, the cavity appearing first in `order` will be used in the same way.

        Parameters
        ----------
        order : sequence, optional; default: None
            A priority list of dependencies to trace in order. These dependencies
            can be either :class:`.Cavity` / :class:`.Gauss` objects or the names of these
            objects. If this argument is not specified then beam tracing will be performed
            using the order defined in :attr:`.Model.trace_order`.

            This argument allows temporary overriding of the model trace order for a given
            beam trace call, without needing to change the :attr:`.TraceDependency.priority`
            values of any dependencies in the model (which would affect all future beam
            traces in which `order` is not specified). Note that, if specifying this argument,
            a sub-set of the trace dependencies in the model can be given --- any dependencies
            not in the given `order` will retain their original ordering.

        disable : sequence, optional: default: None
            A single dependency or list of dependencies to disable. These dependencies can
            be either :class:`.Cavity` / :class:`.Gauss` objects or the names of these objects.

            Note that this argument is ignored if `enable_only` is specified.

        enable_only : sequence, optional: default: None
            A single dependency or list of dependencies to explicity enable, all other
            dependencies will be switched off for the trace call. These dependencies can
            be either :class:`.Cavity` / :class:`.Gauss` objects or the names of these objects.

        symmetric : bool, optional; default: true
            Flag to determine whether the beam parameters at :attr:`.OpticalNode.opposite` nodes
            of each node encountered during the beam trace get set to the :meth:`.BeamParam.reverse`
            of the "forward" propagated beam parameter.

        store : bool, optional; default: True
            Flag to determine whether to store the results of a beam trace in
            in the :attr:`Model.last_trace` property. Note that if this is set
            to False then accessing beam parameters via :class:`.OpticalNode`
            instances directly will give the *last stored* beam parameter at that
            node (i.e. not those given by this trace call).

        Raises
        ------
        ex : :class:`.BeamTraceException`
            If there are no :class:`.Gauss` objects or stable :class:`.Cavity` instances
            present in the model.

        ex_v: :class:`.ValueError`
            If `order` was specified and it contains an invalid item.

        ex_tr : :class:`.TotalReflectionError`
            If a :class:`.Beamsplitter` object is present in the model with an angle of
            incidence and associated refractive indices giving total internal reflection.

        Returns
        -------
        out : :class:`.BeamTraceSolution`
            An object representing the results of the tracing routine.
        """
        LOGGER.info("Beam trace triggered on %s", self)

        # No override given
        if order is None:
            order = self.trace_order
        # Override to model trace_order given, so verify and make it
        else:
            order = self.__make_trace_order_override(order)

        # No cavities nor gausses present
        if not order:
            raise BeamTraceException(_invalid_trace_reason())

        Norder = len(order)
        Ndeps = len(self.cavities) + len(self.gausses)
        if Norder != Ndeps:
            raise BeamTraceException(
                f"Bug encountered! Length of trace order dependency list ({Norder}) "
                f"not equal to number of tracing dependencies ({Ndeps})."
            )

        self._update_symbolic_abcds()

        # Remove specific dependencies from order
        if disable is not None and enable_only is None:
            if not is_iterable(disable):
                disable = [disable]

            for item in disable:
                if isinstance(item, str):
                    item_obj = self.__elements.get(item)
                else:
                    item_obj = item

                if isinstance(item_obj, TraceDependency):
                    try:
                        order.remove(item_obj)
                    except ValueError:
                        LOGGER.info(
                            f"Ignoring duplicate item {repr(item)} in disable sequence"
                        )
                else:
                    LOGGER.info(
                        f"ignoring unrecognised item {repr(item)} in disable sequence"
                    )

        # Filter order to just contain dependencies in enable_only
        if enable_only is not None:
            if disable is not None:
                warn("Ignoring argument 'disable' as 'enable_only' has been given.")

            if not is_iterable(enable_only):
                enable_only = [enable_only]
            else:
                enable_only = list(enable_only)

            for i, item in enumerate(enable_only):
                if isinstance(item, str):
                    item_obj = self.__elements.get(item)
                else:
                    item_obj = item

                if not isinstance(item_obj, TraceDependency):
                    warn(
                        f"ignoring unrecognised item {repr(item_obj)} in enable_only "
                        f"sequence"
                    )

                enable_only[i] = item_obj

            order = list(filter(lambda x: x in enable_only, order))

        all_cavities = list(filter(lambda x: isinstance(x, Cavity), order))
        stable_cavities = list(filter(lambda x: x.is_stable, all_cavities))
        gausses = list(filter(lambda x: isinstance(x, Gauss), order))
        if not stable_cavities and not gausses:
            raise BeamTraceException(_invalid_trace_reason(all_cavities))

        # Ensure only gausses and *stable* cavities get passed to trace forest planting
        order = list(filter(lambda x: x in stable_cavities or x in gausses, order))
        unstable_cavities = set(all_cavities).difference(stable_cavities)
        if unstable_cavities:
            warn(
                f"The cavities {[uc.name for uc in unstable_cavities]} are unstable "
                f"and will not be used for beam tracing.",
                CavityUnstableWarning,
            )

        # Save the planet! Here we only clear and re-plant the forest if:
        #  - a component has been added / removed from the model since last
        #    call (taken into account in Model.add, Model.remove already)
        #  - the symmetric flag has changed since the last plant
        #  - or the tracing priority has changed
        self._rebuild_trace_forest |= (
            self.trace_forest.symmetric != symmetric
            or self.trace_forest.dependencies != order
        )
        if self._rebuild_trace_forest:
            LOGGER.info(
                "Re-planting the model trace forest with dependency order: %s",
                [d.name for d in order],
            )
            self.trace_forest.symmetric = symmetric
            self.trace_forest.plant(order)
            LOGGER.info("Planted the full model trace forest: %s", self.trace_forest)
            self._rebuild_trace_forest = False

        trace_results = self.trace_forest.trace_beam()
        trace = BeamTraceSolution(solution_name, trace_results)

        LOGGER.debug("\n%s", trace)

        if store:
            self.__last_trace = trace

        return trace

    def __make_trace_order_override(self, override):
        """Construct an override list for the current trace order."""
        if not is_iterable(override):
            override = [override]

        order = []
        # For all the items in value, append these in
        # order to the new dependency order list
        for item in override:
            if isinstance(item, str):
                dep = self.__elements.get(item)
                if dep is None:
                    raise ValueError(
                        f"Error in tracing order override:\n"
                        f"    No item of name {item} exists in the model."
                    )
            else:
                dep = item

            if isinstance(dep, Cavity):
                if dep not in self.__cavities:
                    raise ValueError(
                        f"Error in tracing order override:\n"
                        f"    Cavity {dep.name} is not part of the model."
                    )
            elif isinstance(dep, Gauss):
                if dep not in self.__gausses.values():
                    raise ValueError(
                        f"Error in tracing order override:\n"
                        f"    Gauss {dep.name} is not part of the model."
                    )
            else:
                raise ValueError(
                    f"Error in tracing order override:\n"
                    f"    Item {dep} is neither a Cavity nor a Gauss object."
                )

            if dep in order:
                LOGGER.info(
                    f"ignoring duplicate dependency {repr(dep.name)} in tracing order "
                    f"override"
                )
            else:
                order.append(dep)

        # Take all the remaining dependencies that were not in override and
        # append these to the end of the dependency order list
        # -> this means that the original order of those dependencies is
        #    retained, the only ordering that has changed is those that
        #    were included in the override
        for item in self.trace_order:
            if item not in order:
                order.append(item)

        return order


def _invalid_trace_reason(cavities=None):
    msg = """Unable to perform a beam trace!

- No manually set beam parameters have been specified.
        """

    def gfactor_str(cavity):
        gx, gy = cavity.g
        if cavity.gx == cavity.gy:
            return f"g = {gx}"

        return f"gx = {gx}, gy = {gy}"

    if cavities is None:
        cavities = []

    crit = ", ".join(
        [f"{cav.name}: {gfactor_str(cav)}" for cav in cavities if cav.is_critical]
    )
    unst = ", ".join(
        [
            f"{cav.name}: {gfactor_str(cav)}"
            for cav in cavities
            if not cav.is_stable and not cav.is_critical
        ]
    )

    if cavities:
        msg += f"""
- All cavities included in the model are unstable / critical.
    - Critical cavities -- {crit}
    - Unstable cavities -- {unst}
        """
    else:
        msg += """
- No cavities are present in the model. Note that cavity objects must be
  explicitly added, they are NOT auto-generated from your configuration.
        """

    return msg
