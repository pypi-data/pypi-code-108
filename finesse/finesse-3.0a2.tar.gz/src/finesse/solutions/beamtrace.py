"""Solution objects for beam propagations."""

import logging
import typing

import numpy as np

from ..components import Cavity, Space
from ..components.general import Connector
from ..components.node import Port, OpticalNode
from ..env import is_interactive, warn
from ..gaussian import BeamParam
from ..symbols import evaluate, Symbol
from ..solutions.base import BaseSolution
from ..utilities.misc import is_iterable, pairwise

LOGGER = logging.getLogger(__name__)


class ABCDSolution(BaseSolution):
    """Solution for a composite ABCD calculation.

    Parameters
    ----------
    M : array-like or two-element tuple of array-like
        The ABCD matrix / matrices.

    direction : str
        Direction / plane of computation.

        ``"both"`` indicates that `M` is a tuple of the ABCD matrices
        computed over both the tangential and sagittal planes.

        ``"x"`` implies M is the ABCD matrix computed over the tangential plane.

        ``"y"`` implies M is the ABCD matrix computed over the sagittal plane.

    symbolic : bool
        Flag indicating whether the calculations are symbolic.
    """

    def __init__(self, name, M, direction, symbolic):
        super().__init__(name)
        self.empty = False  # tree drawing fill circle

        self._M = M
        self.__direction = direction
        self.__symbolic = symbolic

    def __str__(self):
        return str(self._M)

    @property
    def direction(self):
        """The plane in which this ABCD matrix was computed - 'x'
        for tangential, 'y' for sagittal.

        :getter: Returns the ABCD matrix plane.
        """
        return self.__direction

    @property
    def symbolic(self):
        """Indicates whether this ABCD solution is symbolic.

        :getter: Returns `True` if this stores symbolic expressions, `False` otherwise.
        """
        return self.__symbolic

    @property
    def M(self):
        """A copy of the underlying ABCD matrix as a :class:`numpy.ndarray`.

        :getter: Returns a copy of underlying ABCD matrix.
        """
        return self._M.copy()

    def eval(self):
        """Evaluate the symbolic ABCD matrix.

        Computes the numeric form of the ABCD matrix using
        the ``eval`` method of each parameter reference.

        Returns
        -------
        out : :class:`numpy.ndarray`
            A numeric matrix for the evaluated ABCD.
        """
        if not self.symbolic:
            return self.M

        return evaluate(self.M)


class PropagationSolution(BaseSolution):
    """Solution representation of a call to
    :func:`~finesse.tracing.tools.propagate_beam`.

    This class contains useful attributes and methods for accessing properties of the
    beam that was propagated through the path specified by the above function call. If
    this propagation call was symbolic then each property returned from this class will
    also be symbolic - evaluate these using the ``eval`` method of the symbolic
    expression.

    Note that PropagationSolution objects are returned via
    :func:`~finesse.tracing.tools.propagate_beam` (or :meth:`.Model.propagate_beam`),
    they should never need to be created manually.

    See :ref:`propagating_beams` for details and examples on using this class.
    """

    def __init__(self, name, node_info, comp_info, symbolic):
        super().__init__(name)
        self.node_info = node_info
        self.comp_info = comp_info
        self.__symbolic = symbolic

        self.total_acc_gouy = 0
        for info in comp_info.values():
            self.total_acc_gouy += info.get("acc_gouy", 0)

        self.empty = False

        # NOTE (sjr) For non-symbolic propagations, we need to store the fixed
        #            space length as it was at the time of the propagate_beam
        #            call to avoid any issues (when plotting the solution) if a
        #            space length is changed in the model afterwards
        if not self.symbolic:
            self.__frozen_space_lengths = {
                space: evaluate(space.L.value) for space in self.spaces
            }
        else:
            self.__frozen_space_lengths = {}

    def __get_model(self):
        nodes = list(self.node_info.keys())
        if not nodes:
            return None

        return nodes[0]._model

    def __get_component(self, x):
        if isinstance(x, str):
            name = x
            model = self.__get_model()
            if model is None:
                raise RuntimeError("Empty PropagationSolution - no path traversed!")

            x = model.elements.get(name)
            if x is None:
                raise ValueError(f"No component of name {name} exists in the model")

        if not isinstance(x, Connector):
            raise TypeError(
                "Invalid type for component. Expected Connector " f"but got {type(x)}"
            )

        if x not in self.comp_info:
            raise ValueError(
                f"No component of name {x.name} exists in the propagated path"
            )

        return x

    def __get_node(self, x: str):
        if len(x.split(".")) != 3:
            raise ValueError(f"Unexpected node name format: {x}")

        model = self.__get_model()
        if model is None:
            raise RuntimeError("Empty PropagationSolution - no path traversed!")

        if not model.network.has_node(x):
            raise ValueError(f"No node of name {x} exists in the model.")

        return model.network.nodes[x]["weakref"]()

    @property
    def symbolic(self):
        """Whether the propagation solution is symbolic."""
        return self.__symbolic

    @property
    def start_node(self):
        """The starting node of the propagation."""
        nodes = list(self.node_info.keys())
        if not nodes:
            return None

        return nodes[0]

    @property
    def end_node(self):
        """The final node of the propagation."""
        nodes = list(self.node_info.keys())
        if not nodes:
            return None

        return nodes[-1]

    @property
    def nodes(self):
        """A list of all the nodes traversed, in order."""
        return list(self.node_info.keys())

    @property
    def ports(self):
        """A list of all the ports traversed, in order."""
        return list(dict.fromkeys(node.port for node in self.nodes))

    @property
    def spaces(self):
        """A list of all spaces traversed, in order."""
        space_entries = dict(
            filter(lambda x: "acc_gouy" in x[1], self.comp_info.items())
        )
        return list(space_entries.keys())

    @property
    def components(self):
        """A list of all components (excluding spaces) traversed, in order."""
        return list(filter(lambda x: not isinstance(x, Space), self.comp_info.keys()))

    @property
    def positions(self):
        """A dictionary of the :class:`.Connector` instances to their positions
        (relative to the start node)."""
        pos = {}
        for node, info in self.node_info.items():
            if node.component in pos:
                continue

            pos[node.component] = info["z"]

        return pos

    @property
    def path_length(self):
        """The geometric path length of the traversed path.

        Equal to the sum of each space length in the path.
        """
        nodes = list(self.node_info.keys())
        if not nodes:
            return 0

        return self.node_info[nodes[-1]]["z"]

    @property
    def optical_path_length(self):
        """The optical path length of the traversed path.

        Equal to the sum of the product of each space length and refractive index in the
        path.
        """
        nodes = self.nodes
        if not nodes:
            return 0

        return self.node_info[nodes[-1]]["z_optical"]

    @property
    def beamsizes(self):
        """Dictionary of node to beam size mappings."""
        return {node: info["q"].w for node, info in self.node_info.items()}

    @property
    def ws(self):
        """Identical to :attr:`PropagationSolution.beamsizes`"""
        return self.beamsizes

    @property
    def waistpositions(self):
        """Dictionary of node to waist position (as measured from node) mappings."""
        return {node: info["q"].z for node, info in self.node_info.items()}

    @property
    def z0s(self):
        """Identical to :attr:`PropagationSolution.waistpositions`"""
        return self.waistpositions

    @property
    def qs(self):
        """Dictionary of node to beam parameter mappings."""
        return {node: info["q"] for node, info in self.node_info.items()}

    @property
    def full_ABCD(self):
        """The full, composite ABCD matrix from the start to the end of the path."""
        last_node_info = list(self.node_info.values())[-1]
        return last_node_info["ABCD"]

    def acc_gouy(self, *args):
        """Accumulated Gouy phase over a sequence of spaces.

        Parameters
        ----------
        args : sequence of args
            Space components or names of spaces.

        Returns
        -------
        agouy : float or :class:`.Operation`
            The accumulated Gouy phase over the given spaces.
        """
        agouy = 0
        model = self.__get_model()
        if model is None:
            return agouy

        for space in args:
            if isinstance(space, str):
                space = model.elements.get(space)

            agouy += self.comp_info[space]["acc_gouy"]
        return agouy

    def acc_gouy_up_to(self, point):
        """Accumulated Gouy phase up to a `point` in the traversed path.

        This computes the cumulative Gouy phase from the
        :attr:`.PropagationSolution.start_node` to the specified `point`.

        Parameters
        ----------
        point : :class:`.OpticalNode` or :class:`.Port` or :class:`.Connector` or str
            A node, port, component or name of component up to which to compute
            the accumulated Gouy phase.

        Returns
        -------
        agouy : float or :class:`.Operation`
            The accumulated Gouy phase up to the given `point`.
        """

        if isinstance(point, (OpticalNode, Port)):
            point = point.component

        point = self.__get_component(point)

        agouy = 0
        for comp, info in self.comp_info.items():
            if comp == point:
                break

            agouy += info.get("acc_gouy", 0)
        return agouy

    def abcd(self, up_to):
        """Composite ABCD matrix up to a specific point in the path.

        Parameters
        ----------
        up_to : :class:`.OpticalNode` or :class:`.Port`
            The location in the path at which to get the composite ABCD matrix. This
            can be an optical node or a port.

        Returns
        -------
        M : :class:`numpy.ndarray`
            The ABCD matrix, as a NumPy array, computed up to the specified location.

        Raises
        ------
        ke : KeyError
            If `up_to` is a node or port which does not exist within the solution.

        te : TypeError
            If `up_to` is not an :class:`.OpticalNode` or :class:`.Port`.
        """
        if isinstance(up_to, OpticalNode):
            if up_to not in self.node_info:
                raise KeyError(
                    f"No optical node of name {up_to.full_name} in the solution."
                )

            M = self.node_info[up_to]["ABCD"]

        elif isinstance(up_to, Port):
            ientry = self.node_info.get(up_to.i, {})
            oentry = self.node_info.get(up_to.o, {})

            if not ientry and not oentry:
                raise KeyError(f"No port of name {up_to.full_name} in the solution.")

            in_M = ientry.get("ABCD", None)
            out_M = oentry.get("ABCD", None)

            if in_M is not None:
                M = in_M
            elif out_M is not None:
                M = out_M
            else:
                raise RuntimeError(
                    "Bug encountered! No composite ABCD matrix entry found "
                    f"at the port {up_to.full_name}."
                )

        ## TODO (sjr) Add support for up_to being a Connector (or name of Connector)

        else:
            raise TypeError(f"Invalid type for up_to: {up_to}")

        return M

    def q(self, at) -> BeamParam:
        """Beam parameter at a given node of the path.

        Parameters
        ----------
        at : :class:`.OpticalNode` or str
            The location in the path at which to get the beam parameter. This can
            be an optical node or the name of the optical node.

        Returns
        -------
        q : :class:`.BeamParam`
            The beam parameter corresponding to the specified node.

        Raises
        ------
        ke : KeyError
            If `at` is a node which does not exist within the solution.

        ve : ValueError
            If `at` is a string corresponding to a node which doesn't
            exist in the associated model.

        te : TypeError
            If `at` is not an :class:`.OpticalNode` or a string.
        """
        if isinstance(at, str):
            at = self.__get_node(at)

        if isinstance(at, OpticalNode):
            if at not in self.node_info:
                if at.opposite in self.node_info:
                    # If the opposite node direction is in the solution
                    # then return the reverse of this beam parameter at
                    # this node (i.e. -q*)
                    q = self.node_info[at.opposite]["q"].reverse()
                else:
                    raise KeyError(
                        f"No optical node of name {at.full_name} (nor its opposite) "
                        f"in the solution."
                    )
            else:
                q = self.node_info[at]["q"]
        else:
            raise TypeError(f"Invalid type for at: {at}")

        return q

    def beamsize(self, at):
        """Beam radius at a given location of the path.

        Parameters
        ----------
        See :meth:`.PropagationSolution.q`.

        Returns
        -------
        w : float or :class:`.Operation`
            Beam size corresponding to the specified node.

        Raises
        ------
        See :meth:`.PropagationSolution.q`.
        """
        return self.q(at).w

    def w(self, at):
        """Identical to :meth:`PropagationSolution.beamsize`."""
        return self.beamsize(at)

    def waistsize(self, at):
        """Waist radius as measured from a given location of the path.

        Parameters
        ----------
        See :meth:`.PropagationSolution.q`.

        Returns
        -------
        w : float or :class:`.Operation`
            Waist size using the beam parameter basis at the specified node.

        Raises
        ------
        See :meth:`.PropagationSolution.q`.
        """
        return self.q(at).w0

    def w0(self, at):
        """Identical to :meth:`PropagationSolution.waistsize`."""
        return self.waistsize(at)

    def waistpos(self, from_point):
        """Waist position as measured at `from_point`.

        Parameters
        ----------
        See :meth:`.PropagationSolution.q`.

        Returns
        -------
        w : float or :class:`.Operation`
            Distance to the waist from the specified node.

        Raises
        ------
        See :meth:`.PropagationSolution.q`.
        """
        return self.q(from_point).z

    def z0(self, from_point):
        """Identical to :meth:`PropagationSolution.waistpos`."""
        return self.waistpos(from_point)

    def __getitem__(self, key):
        if isinstance(key, OpticalNode):
            return self.node_info[key]

        if isinstance(key, Connector) or isinstance(key, str):
            key = self.__get_component(key)
            return self.comp_info[key]

        raise TypeError(f"Invalid type for key: {key}")

    def compute_distances_matrix(self, ztype="geometric", subs=None):
        """Compute the distances between each optic, relative to each other.

        Returns a dict of dicts for each "delta z". Note that each distance value is
        in metres. Use :meth:`PropagationSolution.print_distances_matrix` to print a tabulated
        string representation of this dict.

        Parameters
        ----------
        ztype : str, optional; default: "geometric"
            Type of distance, can be either 'geometric' or 'optical'. In the former case
            the values are the distances between each optic in terms of sums of space lengths
            of each space between them. In the latter case, each value is instead the optical
            path length between each component, i.e. the sum of the product of the space
            length and refractive index of each space between them.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.

        Returns
        -------
        deltas : dict
            Dict of dicts for each dz between components.
        """
        if not self.symbolic and subs is not None:
            warn(f"Ignoring {subs=} kwarg as PropagationSolution is non-symbolic.")

        deltas = {}
        outer_done = set()
        for node1, info1 in self.node_info.items():
            comp1 = node1.component
            if comp1 in outer_done:
                continue

            inner_done = set()
            deltas[comp1] = {}
            for node2, info2 in self.node_info.items():
                comp2 = node2.component
                if comp2 in inner_done:
                    continue

                z2 = self._eval_z_for_display(info2, ztype=ztype, subs=subs)
                z1 = self._eval_z_for_display(info1, ztype=ztype, subs=subs)
                deltas[comp1][comp2] = z2 - z1
                inner_done.add(comp2)

            outer_done.add(comp1)

        return deltas

    def print_distances_matrix(
        self, scale=1, ztype="geometric", tablefmt="fancy_grid", subs=None
    ):
        """Print the distances between each optic, relative to each other, in a table.

        Note that all distances are in metres by default. You can apply a scaling factor,
        via the `scale` argument, to all values to change the units accordingly.

        Parameters
        ----------
        ztype : str, optional; default: "geometric:
            See :meth:`.PropagationSolution.compute_distances_matrix`.

        scale : float, optional
            Scaling factor to apply to distances. Defaults to unity such
            that all distances are in metres.

        tablefmt : str, optional; default: "fancy_grid"
            The plain-text table format to pass to tabulate.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.
        """
        from tabulate import tabulate

        deltas = self.compute_distances_matrix(ztype=ztype, subs=subs)

        table = []
        headers = [comp.name for comp in self.components]

        for comp1 in deltas:
            entry = [comp1.name]
            for dz in deltas[comp1].values():
                entry.append(scale * dz)
            table.append(entry)

        print(tabulate(table, headers, tablefmt=tablefmt))

    def position(self, point, ptype="geometric"):
        """Gets the position of the specified `point` relative to the start node.

        Parameters
        ----------
        point : :class:`.OpticalNode` or :class:`.Port` or :class:`.Connector` or str
            The location in the path from which to obtain the relative position. This can
            be an optical node, a port, a connector or the name of a connector.

        ptype : str
            Type of distance, can be either 'geometric' or 'optical'. In the former case
            the value returned is the distance from the start node to `point` as a sum
            of each space length. In the latter case the value returned will be the optical
            path length from the start node to `point`, i.e. a sum of each space length
            multiplied by its refractive index.

        Returns
        -------
        z : float or symbol
            The relative distance from the start node to the measured `point`.
        """
        if ptype.casefold() == "geometric":
            zentry = "z"
        elif ptype.casefold() == "optical":
            zentry = "z_optical"
        else:
            raise ValueError(
                f"Unrecognised value for ptype: {ptype}. This must be either "
                "'geometric' or 'optical'."
            )

        if isinstance(point, OpticalNode):
            if point not in self.node_info:
                raise KeyError(
                    f"No optical node of name {point.full_name} in the solution."
                )
            else:
                z = self.node_info[point][zentry]
        elif isinstance(point, Port):
            ientry = self.node_info.get(point.i, {})
            oentry = self.node_info.get(point.o, {})

            if not ientry and not oentry:
                raise KeyError(f"No port of name {point.full_name} in the solution.")

            z1 = ientry.get(zentry, None)
            z2 = oentry.get(zentry, None)

            if z1 is not None and z2 is not None:
                if z1 != z2:
                    raise RuntimeError(
                        f"Bug encountered! Positions of nodes {point.i.full_name} "
                        f"and {point.o.full_name} not equal ({z1} != {z2})"
                    )
                z = z1
            else:
                z = z1 or z2
        elif isinstance(point, Connector) or isinstance(point, str):
            point = self.__get_component(point)
            z = None
            for node in point.optical_nodes:
                if node in self.node_info:
                    z = self.node_info[node][zentry]
                    break

            if z is None:
                raise KeyError(f"No component of name {point.name} in the solution.")
        else:
            raise TypeError("Unrecognised type for argument point.")

        return z

    def make_table(self, tablefmt="fancy_grid", subs=None):
        """Construct a table showing the beam properties at each node.

        Parameters
        ----------
        tablefmt : str, optional; default: "fancy_grid"
            The plain-text table format to pass to tabulate.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.

        Returns
        -------
        table : str
            The table as a string.
        """
        from tabulate import tabulate

        if not self.symbolic and subs is not None:
            warn(f"Ignoring {subs=} kwarg as PropagationSolution is non-symbolic.")

        table = []
        headers = [
            "Name",
            "z [m]",
            "w0 [mm]",
            "zr [m]",
            "w [mm]",
            "RoC [m]",
            "Acc. Gouy [deg]",
            "q",
        ]

        format_q = lambda q: f"{q.real:.3f} + {q.imag:.3f}j"

        agouy = 0
        for node, info in self.node_info.items():
            name = node.full_name
            z = self._eval_z_for_display(info, subs=subs)
            q = self._eval_q_for_display(info, subs=subs)

            w0 = q.w0 / 1e-3
            zr = q.zr
            w = q.w / 1e-3
            Rc = q.Rc

            if node.is_input:  # accumulate the Gouy phase
                space_info = self.comp_info.get(node.space)
                if space_info:
                    agouy += space_info.get("acc_gouy", 0)

            if isinstance(agouy, Symbol):
                agouy_val = agouy.eval(subs=subs)
            else:
                agouy_val = agouy

            table.append([name, z, w0, zr, w, Rc, agouy_val, format_q(q)])

        return tabulate(table, headers, tablefmt=tablefmt)

    def __str__(self):
        return self.make_table()

    def print(self, tablefmt="fancy_grid", subs=None):
        """Print the propagated beam properties at each node in a table format.

        This internally calls :meth:`.PropagationSolution.make_table` and
        prints its return string.

        Parameters
        ----------
        tablefmt : str, optional; default: "fancy_grid"
            The plain-text table format to pass to tabulate.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.
        """
        print(self.make_table(tablefmt=tablefmt, subs=subs))

    def _eval_z_for_display(self, info, ztype="geometric", subs=None):
        if ztype.casefold() == "geometric":
            z = info["z"]
        elif ztype.casefold() == "optical":
            z = info["z_optical"]
        else:
            raise ValueError(f"Unrecognised ztype: {ztype}")

        if self.symbolic and isinstance(z, Symbol):
            if subs is not None:
                if not isinstance(subs, dict):
                    raise TypeError("Expected argument subs to be of type dict")

                if any(is_iterable(arg) for arg in subs.values()):
                    raise ValueError(
                        "Parameter substitutions for plotting / printing must "
                        "not use arrays of values."
                    )
            z = z.eval(subs=subs)

        return z

    def _eval_q_for_display(self, info, subs=None):
        q = info["q"]
        if self.symbolic and q.symbolic:
            if subs is not None:
                if not isinstance(subs, dict):
                    raise TypeError("Expected argument subs to be of type dict")

                if any(is_iterable(arg) for arg in subs.values()):
                    raise ValueError(
                        "Parameter substitutions for plotting / printing must "
                        "not use arrays of values."
                    )
            q = q.eval(subs=subs)

        return q

    def _eval_L_for_display(self, space, subs=None):
        if self.symbolic:
            if subs is not None:
                if not isinstance(subs, dict):
                    raise TypeError("Expected argument subs to be of type dict")

                if any(is_iterable(arg) for arg in subs.values()):
                    raise ValueError(
                        "Parameter substitutions for plotting / printing must "
                        "not use arrays of values."
                    )
            L = space.L.ref.eval(subs=subs)
        else:
            L = self.__frozen_space_lengths[space]

        return L

    def segment(self, node, *args, normalise_z=True, w_scale=1, npts=400, subs=None):
        """Obtain data for a segment of the beam over the space attached to the
        specified `node`.

        The expected, valid positional `args` are any combination of:

          * "beamsize",
          * "gouy",
          * "curvature",

        where all three will be used by default if none of these are given.

        Use :meth:`.PropagationSolution.all_segments` to obtain the beam data
        over all spaces of the solution.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            The starting node of the segment.

        normalise_z : bool, optional; default: True
            Whether to normalise returned ``data["z"]`` array such that
            first value of this is zero.

        w_scale : scalar, optional; default: 1
            Quantity to scale beam size values by if calculating these. For
            example, specify `w_scale = 1e3` to get beam sizes in mm. By
            default the units of the beam size will be in metres.

        npts : int, optional; default: 400
            Number of points to use for computing data values.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.

        Returns
        -------
        zs : :class:`numpy.ndarray`
            Array of z-axis values corresponding to the position of the node
            up to the length of the attached space. If `normalise_z` is True
            then the position of `node` will be subtracted from all values, such
            that the first value in this array will be zero.

        data : dict
            Dictionary of data mapping ``args : values``, where `args` are those
            specified (see above) and `values` are the arrays of values corresponding
            to each of these args as a function of the z-axis values.
        """
        if not args:
            args = ("beamsize", "gouy", "curvature")

        if not isinstance(node, OpticalNode):
            raise NotImplementedError(
                "Obtaining beam segments from locations other than OpticalNodes "
                "is not yet supported."
            )

        if node.is_input or node is self.end_node:
            raise ValueError(
                "Cannot obtain a beam segment corresponding to "
                f"the node {node.full_name}. This node must be an "
                "output node and cannot be the end node of the solution."
            )

        info = self.node_info.get(node)
        if info is None:
            raise ValueError(f"Node {node.full_name} not present in the solution!")

        # Store the z data and each arg data array here
        data = {}

        z = self._eval_z_for_display(info, subs=subs)
        q = self._eval_q_for_display(info, subs=subs)
        # Make array of values from [0, space_length]
        L = self._eval_L_for_display(node.space, subs=subs)
        intra_zs = np.linspace(0, L, npts)

        zs = z + intra_zs
        if normalise_z:
            zs -= zs[0]

        for arg in args:
            values = getattr(q, arg)(q.z + intra_zs)

            if arg == "beamsize":
                values *= w_scale

            # Computing Gouy phase so convert to degrees and
            # subtract first value to get Gouy phase accumulated
            # over the segment rather than absolute phases
            if arg == "gouy":
                values = np.degrees(values)
                values -= values[0]

            data[arg] = values

        return zs, data

    def __adaptive_npts_per_segment(self, N, subs=None):
        dS_per_space = {}
        via_waists = {}
        end_node = self.end_node
        for (node1, node2) in pairwise(self.nodes):
            if node1.is_input or node1 is end_node:
                continue

            space = node1.space
            q1 = self._eval_q_for_display(self.node_info[node1], subs=subs)
            q2 = self._eval_q_for_display(self.node_info[node2], subs=subs)

            # Compute change in defocus over the space
            dS_per_space[space] = abs(q2.S - q1.S)
            # And determine whether we go through a waist
            via_waists[space] = np.sign(q1.S) != np.sign(q2.S)

        # Get the maximum defocus change
        max_dS = max(dS_per_space.values())
        for (space, dS), via_waist in zip(dS_per_space.items(), via_waists.values()):
            # If a waist exists in this space then want to automatically
            # increase the weighting by resetting dS to twice the maximum
            # so that resolution increases around the waist
            if via_waist:
                dS_per_space[space] = max_dS * 2

        dS_sum = sum(dS_per_space.values())
        npts_per_space = {}
        for space, dS in dS_per_space.items():
            # Now determine the number of points to use for this segment
            # by the size of the defocus change
            n = int(N * dS / dS_sum)
            # If the defocus change was zero, or small enough such that n is
            # less than two, let's just set the number of points for this
            # segment to two, this means that total number of points can
            # be a few larger than N but that's not really a problem
            if n < 2:
                n = 2

            npts_per_space[space] = n

        return npts_per_space

    def __equal_npts_per_segment(self, N, **_):
        nspaces = len(self.spaces)
        npts_per_space = {}
        for space in self.spaces:
            npts_per_space[space] = int(N / nspaces)

        return npts_per_space

    def __all_npts_per_segment(self, N, **_):
        npts_per_space = {}
        for space in self.spaces:
            npts_per_space[space] = N

        return npts_per_space

    def all_segments(
        self,
        *args,
        add_gouy=True,
        w_scale=1,
        npts=1000,
        resolution="adaptive",
        subs=None,
    ):
        """Construct a dictionary containing beam data for all segments of the solution.

        The expected, valid positional arguments are any combination of:

          * "beamsize",
          * "gouy",
          * "curvature",

        where all three will be used by default if no args are given.

        Use :meth:`.PropagationSolution.segment` to obtain the beam data
        over a single space of the solution.

        Parameters
        ----------
        add_gouy : bool, optional; default: True
            Whether to add the last Gouy phase from previous segment
            to all values of current segment, thereby constructing each
            "gouy" array entry as accumulated Gouy phases over all
            segments.

        w_scale : scalar, optional; default: 1
            Quantity to scale beam size values by if calculating these. For
            example, specify `w_scale = 1e3` to get beam sizes in mm. By
            default the units of the beam size will be in metres.

        npts : int, optional; default: 1000
            Number of points to use for computing data values. The actual number
            of data points used per segment depends upon the `resolution` argument.

        resolution : str, optional; default: "adaptive"
            The method of segment resolution setting to use. This can be one
            of three arguments:

              * "adaptive": Sets the number of points per segment in such a way as
                to attempt to increase the resolution near the waist. Each segment
                will have a number of points allocated to it accordingly, with the
                total number of points across all segments then approximately equal
                to `npts`.
              * "equal": Allocates an equal number of points to each segment, i.e.
                each segment has ``int(npts / len(self.spaces))`` points.
              * "all": Gives ``npts`` to all segments, such that the total number of
                data points across all segments is ``len(self.spaces) * npts``.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.

        Returns
        -------
        data : dict
            Dictionary of data mapping ``space : zs, segdata``, where `space` is
            each space (i.e. segment) in the solution path, `zs` are the z-axis
            values and `segdata` is the dict of data values for the targeted beam
            properties over the space.
        """
        data = {}

        if not args:
            args = ("beamsize", "gouy", "curvature")

        resolution_map = {
            "adaptive": self.__adaptive_npts_per_segment,
            "equal": self.__equal_npts_per_segment,
            "all": self.__all_npts_per_segment,
        }
        resolution_method = resolution_map.get(resolution.casefold())
        if resolution_method is None:
            raise ValueError(
                f"Unexpected value for resolution argument: {resolution}. Expected "
                "one of: 'adaptive', 'equal' or 'all'."
            )

        npts_per_space = resolution_method(npts, subs=subs)

        prev_gouy = 0
        end_node = self.end_node
        for node in self.nodes:
            if node.is_input or node is end_node:
                continue

            zs, segdata = self.segment(
                node,
                *args,
                # Don't want to normalise each start z to zero now as
                # we want each to start from actual node position
                normalise_z=False,
                w_scale=w_scale,
                npts=npts_per_space[node.space],
                subs=subs,
            )

            # Accumulating Gouy over all segments so make adjustments
            if "gouy" in args and add_gouy:
                gouys = segdata["gouy"]
                # Add on the last value of Gouy from prev segment so
                # that phase is accumulated over full path
                gouys += prev_gouy
                prev_gouy = gouys[-1]

            data[node.space] = zs, segdata

        return data

    def plot_beamsizes(self, **kwargs):
        """Plot the beam sizes over the propagated path.

        This is just a convenience wrapper which is identical to calling
        :meth:`PropagationSolution.plot` with ``"beamsize"`` as the arg.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        ax : Axis
            Handle to the axis.
        """
        return self.plot("beamsize", **kwargs)

    def plot_acc_gouy(self, **kwargs):
        """Plot the accumulated Gouy phases over the propagated path.

        This is just a convenience wrapper which is identical to calling
        :meth:`PropagationSolution.plot` with ``"gouy"`` as the arg.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        ax : Axis
            Handle to the axis.
        """
        return self.plot("gouy", **kwargs)

    def plot_curvatures(self, **kwargs):
        """Plot the wavefront curvatures over the propagated path.

        This is just a convenience wrapper which is identical to calling
        :meth:`PropagationSolution.plot` with ``"curvature"`` as the arg.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        ax : Axis
            Handle to the axis.
        """
        return self.plot("curvature", **kwargs)

    def plot(
        self,
        *args,
        filename=None,
        show=True,
        ignore=None,
        name_xoffsets=None,
        name_yoffsets=None,
        ylims=None,
        npts=1000,
        resolution="adaptive",
        subs=None,
    ):
        """Plot any combination of the beam sizes, accumulated Gouy phases and / or
        wavefront curvatures over the propagated path.

        The expected, valid positional arguments are any combination of:
            - "beamsize",
            - "gouy",
            - "curvature",

        or "all" to plot all of the above.

        If no positional args are given then the beamsize (first axis) and accumulated
        Gouy phase (second axis) will be plotted by default.

        The locations of each component will be marked on the figure, unless the
        component is in `ignore` or the component has "AR" or "HR" in its name.

        Parameters
        ----------
        filename : str or file-like, optional
            Name of a file or existing file object to save the figure to.

        show : bool, optional; default: True
            Whether to show the figure.

        ignore : component, sequence of, optional
            A component or sequence of components to ignore when
            making markers.

        name_xoffsets : dict, optional
            Dictionary of component names to x-axis offsets for shifting where the
            component name text is placed. The offset value is interpreted in terms
            of data co-ordinates.

        name_yoffsets : dict, optional
            Dictionary of component names to y-axis offsets for shifting where the
            component name text is placed. The offset value is interpreted in terms
            of data co-ordinates.

        ylims : dict, optional
            Dictionary of target names (i.e. "beamsize", "gouy" or "curvature") to
            manual axis y-limits.

        npts : int, optional; default: 1000
            See equivalent argument in :meth:`.PropagationSolution.all_segments`.

        resolution : str, optional; default: "adaptive"
            See equivalent argument in :meth:`.PropagationSolution.all_segments`.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        axs : axes
            The axis handles.
        """
        import matplotlib.pyplot as plt

        if not args:
            args = ("beamsize", "gouy")
        if "all" in args:
            args = ("beamsize", "gouy", "curvature")

        valid_args = ("beamsize", "gouy", "curvature")
        if any(arg not in valid_args for arg in args):
            raise ValueError(
                "Invalid target argument in args, expected any "
                f"combination of {valid_args} or 'all'"
            )

        if not self.symbolic and subs is not None:
            warn(f"Ignoring {subs=} kwarg as PropagationSolution is non-symbolic.")

        N = len(args)
        fig, axs = plt.subplots(N, 1, sharex=True)
        if N == 1:
            axs = [axs]

        maximums = {k: 0 for k in args}
        minimums = {k: float("inf") for k in args}
        data = self.all_segments(
            *args, w_scale=1e3, npts=npts, resolution=resolution, subs=subs
        )
        for zs, segd in data.values():
            for i, arg in enumerate(args):
                y = segd[arg]
                if arg == "beamsize":
                    axs[i].fill_between(zs, y, -y, color="r")
                else:
                    axs[i].plot(zs, y)

                maximums[arg] = max(maximums[arg], y.max())
                minimums[arg] = min(minimums[arg], y.min())

        if ignore is None:
            ignore = []
        if not is_iterable(ignore):
            ignore = [ignore]

        if name_xoffsets is None:
            name_xoffsets = {}
        if name_yoffsets is None:
            name_yoffsets = {}

        for node, info in self.node_info.items():
            if node.is_input:
                z = self._eval_z_for_display(info, subs=subs)

                comp = node.component
                if "AR" not in comp.name and comp not in ignore:
                    name = comp.name
                    x_offset = name_xoffsets.get(name, 0)
                    y_offset = name_yoffsets.get(name, 0)
                    # display the name in a nicer way
                    name = name.replace("_", "\n")
                    n_newlines = name.count("\n")

                    for i, arg in enumerate(args):
                        if not i:
                            axs[i].axvline(
                                z, 0.12 + 0.1 * n_newlines, color="k", linestyle="--"
                            )

                            if arg == "beamsize":
                                ytext_pos = -1 * maximums[arg]
                            else:
                                ytext_pos = minimums[arg]

                            ytext_pos += y_offset
                            axs[i].text(
                                z + x_offset, ytext_pos, name, ha="center", va="center"
                            )
                        else:
                            axs[i].axvline(z, color="k", linestyle="--")

        for ax in axs:
            ax.set_xlim(0, None)

        axs[-1].set_xlabel("Distance [m]")

        ylabel_mappings = {
            "beamsize": "Beam size [mm]",
            "gouy": "Gouy phase\naccumulation [deg]",
            "curvature": "Wavefront curvature [1/m]",
        }
        if ylims is None:
            ylims = {}
        for i, arg in enumerate(args):
            if arg != "beamsize":
                ylim = ylims.get(arg, None)
                if ylim is None:
                    axs[i].set_ylim(0 if arg == "gouy" else None, maximums[arg])
                else:
                    axs[i].set_ylim(ylim[0], ylim[1])

            ylabel = ylabel_mappings.get(arg, arg)
            axs[i].set_ylabel(ylabel)

        if filename is not None:
            fig.savefig(filename)
        if show:
            plt.show()

        if N == 1:
            return fig, axs[0]

        return fig, axs

    def animate_beamsizes(self, subs, **kwargs):
        """Animate the beam sizes over the propagated path.

        This is just a convenience wrapper which is identical to calling
        :meth:`PropagationSolution.animate` with ``"beamsize"`` as the arg.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        ax : Axis
            Handle to the axis.

        an : FuncAnimation
            Handle to the animation.
        """
        return self.animate(subs, "beamsize", **kwargs)

    def animate_acc_gouy(self, subs, **kwargs):
        """Animate the accumulated Gouy phases over the propagated path.

        This is just a convenience wrapper which is identical to calling
        :meth:`PropagationSolution.animate` with ``"gouy"`` as the arg.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        ax : Axis
            Handle to the axis.

        an : FuncAnimation
            Handle to the animation.
        """
        return self.animate(subs, "gouy", **kwargs)

    def animate_curvatures(self, subs, **kwargs):
        """Animate the wavefront curvatures over the propagated path.

        This is just a convenience wrapper which is identical to calling
        :meth:`PropagationSolution.animate` with ``"curvature"`` as the arg.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        ax : Axis
            Handle to the axis.

        an : FuncAnimation
            Handle to the animation.
        """
        return self.animate(subs, "curvature", **kwargs)

    def animate(
        self,
        subs,
        *args,
        filename=None,
        show=True,
        ignore=None,
        name_xoffsets=None,
        name_yoffsets=None,
        ylims=None,
        npts=200,
        blit=True,
        interval=200,
    ):
        """Animate any combination of the beam sizes, accumulated Gouy phases and / or
        wavefront curvatures over the propagated path using the substitution parameters
        in `subs`.

        The expected, valid positional arguments (i.e. `*args`) are any combination of:
            - "beamsize",
            - "gouy",
            - "curvature",

        or "all" to animate all of the above.

        If no positional args are given then the beamsize (first axis) and accumulated
        Gouy phase (second axis) will be animated by default.

        At least one model parameter substitution in `subs` must be
        array-like - this will then be the animation axis. If more than
        one are array-like then each array must be the same size - the
        substitutions will then be carried out simulatenously. Any scalar
        value entry in `subs` will be applied before the animation axis.

        Parameters
        ----------
        subs : dict
            Dictionary of model parameter substitutions. At least one entry
            must be array-like such than animation can be performed over this
            axis.

            If multiple substitutions are arrays then they must all be the same
            size.

        filename : str, optional
            Name of a file to save the animation to.

        show : bool, optional; default: True
            Whether to show the resulting animation.

        ignore : component, sequence of, optional
            A component or sequence of components to ignore when
            making markers.

        name_xoffsets : dict, optional
            Dictionary of component names to x-axis offsets for shifting where the
            component name text is placed. The offset value is interpreted in terms
            of data co-ordinates.

        name_yoffsets : dict, optional
            Dictionary of component names to y-axis offsets for shifting where the
            component name text is placed. The offset value is interpreted in terms
            of data co-ordinates.

        ylims : dict, optional
            Dictionary of target names (i.e. "beamsize", "gouy" or "curvature") to
            manual axis y-limits.

        npts : int, optional; default: 200
            Number of points to use for computing beam sizes and
            Gouy phases over spaces.

        blit : bool, optional; default: True
            Whether blitting is used to optimize drawing.

        interval : int, optional; default: 200
            Delay between frames in milliseconds.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        axs : axes
            The axis handles.

        an : FuncAnimation
            Handle to the animation.
        """
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        if not self.symbolic:
            raise RuntimeError(
                "Animation is only applicable to symbolic PropagationSolution objects"
            )

        if not args:
            args = ("beamsize", "gouy")
        if "all" in args:
            args = ("beamsize", "gouy", "curvature")

        valid_args = ("beamsize", "gouy", "curvature")
        if any(arg not in valid_args for arg in args):
            raise ValueError(
                "Invalid target argument in args, expected any "
                f"combination of {valid_args} or 'all'"
            )

        anim_params = dict(filter(lambda x: is_iterable(x[1]), subs.items()))
        if not anim_params:
            raise ValueError("Expected at least one array-like substitution in subs.")
        N = len(list(anim_params.values())[0])
        if any(len(arr) != N for arr in anim_params.values()):
            raise ValueError("Lengths of all array-like substitutions must be equal.")

        # Dictionary of singular value substitutions to use at each animation point
        isubs = {}

        static_params = dict(filter(lambda x: not is_iterable(x[1]), subs.items()))
        # Set fixed parameter substitutions
        for param, value in static_params.items():
            isubs[param] = value

        if ignore is None:
            ignore = []
        if not is_iterable(ignore):
            ignore = [ignore]

        # Data dictionaries storing arrays of propagated distances, beamsizes
        # accumulated Gouy phases and component positions at each node
        # for each animation point
        node_xdata = {}
        node_ydata = {k: {} for k in args}

        comp_positions = {}
        for node in self.node_info:
            if not node.is_input:
                node_xdata[node] = np.zeros((N, npts))
                for arg in args:
                    node_ydata[arg][node] = np.zeros((N, npts))
            else:
                comp = node.component
                if "AR" not in comp.name and comp not in ignore:
                    comp_positions[node] = np.ma.zeros(N)

        maximums = {k: 0 for k in args}
        minimums = {k: float("inf") for k in args}
        end_node = self.end_node
        for i in range(N):
            # Update animation parameters
            for param, array in anim_params.items():
                isubs[param] = array[i]

            # TODO (sjr) Replace this loop with an all_segments call, will require
            #            some careful rejigging of code in this method so I'll leave
            #            this for a later date
            prev_acc_gouy = 0
            for node, info in self.node_info.items():
                if not node.is_input and node != end_node:
                    z = self._eval_z_for_display(info, subs=isubs)
                    q = self._eval_q_for_display(info, subs=isubs)
                    # Make array of values from [0, space_length]
                    L = self._eval_L_for_display(node.space, subs=isubs)
                    intra_zs = np.linspace(0, L, npts)

                    node_xdata[node][i][:] = z + intra_zs
                    for arg in args:
                        data = getattr(q, arg)(q.z + intra_zs)
                        if arg == "beamsize":
                            data /= 1e-3  # scale to mm
                        elif arg == "gouy":
                            # Plotting accumulated Gouy so need to modify data as follows:
                            #  - convert to degrees
                            #  - subtract the Gouy phase directly at the output node to get
                            #    Gouy phase accumulated over this space
                            #  - then add previous accumulated Gouy to keep cumulative over full path
                            data = np.degrees(data)
                            data -= data[0]
                            data += prev_acc_gouy
                            prev_acc_gouy = data[-1]

                        maximums[arg] = max(maximums[arg], data.max())
                        minimums[arg] = min(minimums[arg], data.min())
                        node_ydata[arg][node][i][:] = data
                else:
                    if node in comp_positions:
                        comp_positions[node][i] = self._eval_z_for_display(
                            info, subs=isubs
                        )

        Np = len(args)
        fig, axs = plt.subplots(Np, 1, sharex=True)
        if Np == 1:
            axs = [axs]

        # Lists of the various artists to animate
        collections = []  # beam size fill shapes
        lines = {k: [] for k in args if k != "beamsize"}
        comp_pos_lines = []  # component position lines
        comp_name_texts = []  # names of components
        for i, arg in enumerate(args):
            for xdata, ydata in zip(node_xdata.values(), node_ydata[arg].values()):
                if arg == "beamsize":
                    collections.append(
                        axs[i].fill_between(xdata[0], ydata[0], -ydata[0], color="r")
                    )
                else:
                    (line,) = axs[i].plot([], [])
                    lines[arg].append(line)

        if name_xoffsets is None:
            name_xoffsets = {}
        if name_yoffsets is None:
            name_yoffsets = {}

        comp_name_offsets = []
        for node, zs in comp_positions.items():
            name = node.component.name
            x_offset = name_xoffsets.get(name, 0)
            y_offset = name_yoffsets.get(name, 0)
            name = name.replace("_", "\n")
            n_newlines = name.count("\n")

            for i, arg in enumerate(args):
                z0 = zs[0]
                if not i:
                    vline = axs[i].axvline(
                        z0, 0.12 + 0.1 * n_newlines, color="k", linestyle="--"
                    )

                    if arg == "beamsize":
                        ytext_pos = -1 * maximums[arg]
                    else:
                        ytext_pos = minimums[arg]

                    ytext_pos += y_offset
                    ct = axs[i].text(
                        z0 + x_offset, ytext_pos, name, ha="center", va="center"
                    )
                    comp_name_texts.append(ct)
                    comp_name_offsets.append(x_offset)
                else:
                    vline = axs[i].axvline(z0, color="k", linestyle="--")

                comp_pos_lines.append(vline)

        anim_txt_former = lambda k: "\n".join(
            f"{p.component.name} {p.name} = {v[k]:.2f} {p.units}"
            for p, v in anim_params.items()
        )
        anim_text = axs[-1].text(
            0.15,
            0.9,
            "",
            ha="center",
            va="center",
            transform=axs[-1].transAxes,
        )

        axs[-1].set_xlabel("Distance [m]")

        ylabel_mappings = {
            "beamsize": "Beam size [mm]",
            "gouy": "Gouy phase\naccumulation [deg]",
            "curvature": "Wavefront curvature [1/m]",
        }
        if ylims is None:
            ylims = {}
        for i, arg in enumerate(args):
            if arg != "beamsize":
                ylim = ylims.get(arg, None)
                if ylim is None:
                    axs[i].set_ylim(0 if arg == "gouy" else None, maximums[arg])
                else:
                    axs[i].set_ylim(ylim[0], ylim[1])

            ylabel = ylabel_mappings.get(arg, arg)
            axs[i].set_ylabel(ylabel)

        # Set maximum propagated distance
        max_x = 0
        for xdata in node_xdata.values():
            max_x = max(max_x, xdata.max())
        for ax in axs:
            ax.set_xlim(0, max_x)

        try:
            w_ax_index = args.index("beamsize")
        except ValueError:
            w_ax_index = -1

        all_artists = collections + comp_pos_lines + comp_name_texts + [anim_text]
        for arg in args:
            if arg == "beamsize":
                continue
            all_artists += lines[arg]

        # Need to create a dummy fig and ax for making a fill_between collection
        # in each segment -> the actual collections then get modified using the
        # vertices of this dummy collection during the animation
        dummy_fig, dummy_ax = plt.subplots()

        def animate(frame_index):
            if w_ax_index != -1:
                for coll, xdata, ydata_w in zip(
                    collections,
                    node_xdata.values(),
                    node_ydata["beamsize"].values(),
                ):
                    dummy_coll = dummy_ax.fill_between(
                        xdata[frame_index],
                        ydata_w[frame_index],
                        -ydata_w[frame_index],
                        color="r",
                    )
                    dummy_path = dummy_coll.get_paths()[0]
                    path = coll.get_paths()[0]
                    path.vertices[:, 0] = dummy_path.vertices[:, 0]
                    path.vertices[:, 1] = dummy_path.vertices[:, 1]

            for arg in args:
                if arg == "beamsize":
                    continue

                for line, xdata, ydata in zip(
                    lines[arg],
                    node_xdata.values(),
                    node_ydata[arg].values(),
                ):
                    line.set_xdata(xdata[frame_index])
                    line.set_ydata(ydata[frame_index])

            for j, zs in zip(
                range(0, len(comp_pos_lines), Np), comp_positions.values()
            ):
                for i in range(Np):
                    vline = comp_pos_lines[j + i]
                    vline.set_xdata(zs[frame_index])

            for ctname_txt, offset, zs in zip(
                comp_name_texts, comp_name_offsets, comp_positions.values()
            ):
                ctname_txt.set_x(zs[frame_index] + offset)

            anim_text.set_text(anim_txt_former(frame_index))

            return all_artists

        an = animation.FuncAnimation(
            fig, animate, frames=N, blit=blit, interval=interval
        )
        # Get rid of the dummy figure now so that it doesn't get shown / saved
        plt.close(dummy_fig)

        if filename is not None:
            an.save(filename)

        if show:
            plt.show()

        if Np == 1:
            return fig, axs[0], an

        return fig, axs, an


class AstigmaticPropagationSolution(BaseSolution):
    """Solution representation of a call to
    :func:`finesse.tracing.tools.propagate_beam_astig`.

    Internally this stores two :class:`.PropagationSolution` instances which are used to
    access the per-plane beam parameters. These propagation solutions can be accessed
    via :attr:`.AstigmaticPropagationSolution.ps_x` and
    :attr:`.AstigmaticPropagationSolution.ps_y` for the tangential and sagittal planes,
    respectively.
    """

    def __init__(self, name, ps_x: PropagationSolution, ps_y: PropagationSolution):
        super().__init__(name)
        self.__ps_x = ps_x
        self.__ps_y = ps_y
        self.__symbolic = ps_x.symbolic

        self.empty = False

    @property
    def symbolic(self):
        """Whether the astigmatism solution is symbolic."""
        return self.__symbolic

    @property
    def ps_x(self):
        """The internal :class:`.PropagationSolution` for the tangential plane."""
        return self.__ps_x

    @property
    def ps_y(self):
        """The internal :class:`.PropagationSolution` for the sagittal plane."""
        return self.__ps_y

    @property
    def start_node(self):
        """The starting node of the propagation."""
        return self.ps_x.start_node

    @property
    def end_node(self):
        """The final node of the propagation."""
        return self.ps_x.end_node

    @property
    def nodes(self):
        """A list of all the nodes traversed, in order."""
        return self.ps_x.nodes

    @property
    def ports(self):
        """A list of all the ports traversed, in order."""
        return self.ps_x.ports

    @property
    def spaces(self):
        """A list of all spaces traversed, in order."""
        return self.ps_x.spaces

    @property
    def components(self):
        """A list of all components (excluding spaces) traversed, in order."""
        return self.ps_x.components

    @property
    def path_length(self):
        """The geometric path length of the traversed path."""
        return self.ps_x.path_length

    @property
    def overlaps(self):
        """A dict of nodes to the qx, qy overlaps at these nodes."""
        return {node: self.overlap(node) for node in self.nodes}

    def qx(self, at):
        """Tangential beam parameter at a given location of the path.

        See :meth:`.PropagationSolution.q` for parameters and return object
        descriptions.
        """
        return self.ps_x.q(at)

    def qy(self, at):
        """Sagittal beam parameter at a given location of the path.

        See :meth:`.PropagationSolution.q` for parameters and return object
        descriptions.
        """
        return self.ps_y.q(at)

    def overlap(self, at):
        """Overlap between tangential and sagittal beam parameters at a given location
        of the path.

        See :meth:`.PropagationSolution.q` for parameters description.

        Returns
        -------
        O : float or :class:`.Operation`
            Overlap between the beam parameters in each plane, at the specified node.
        """
        return BeamParam.overlap(self.qx(at), self.qy(at))

    def plot(
        self,
        *args,
        filename=None,
        show=True,
        ignore=None,
        name_xoffsets=None,
        name_yoffsets=None,
        ylims=None,
        npts=1000,
        resolution="equal",
        subs=None,
    ):
        """Plot any combination of the beam sizes, accumulated Gouy phases and / or
        wavefront curvatures over the propagated path, showing the values for both
        planes.

        The expected, valid positional arguments are any combination of:
            - "beamsize",
            - "gouy",
            - "curvature",

        or "all" to plot all of the above.

        If no positional args are given then the beamsize (first axis) and accumulated
        Gouy phase (second axis) will be plotted by default.

        .. note::

            The resulting figure will be divided into two columns, the first giving the
            absolute quantity values for both planes and the second giving the difference
            between the quantities in the two planes (tangential plane minus sagittal plane).

            For beam size plots, the tangential plane values are shown in red whilst
            sagittal are shown in blue. Whilst for any other quantity, the tangential
            plane values are solid lines and sagittal are dashed lines.

        The locations of each component will be marked on the figure, unless the
        component is in `ignore` or the component has "AR" or "HR" in its name.

        Parameters
        ----------
        filename : str or file-like, optional
            Name of a file or existing file object to save the figure to.

        show : bool, optional; default: True
            Whether to show the figure.

        ignore : component, sequence of, optional
            A component or sequence of components to ignore when
            making markers.

        name_xoffsets : dict, optional
            Dictionary of component names to x-axis offsets for shifting where the
            component name text is placed. The offset value is interpreted in terms
            of data co-ordinates.

        name_yoffsets : dict, optional
            Dictionary of component names to y-axis offsets for shifting where the
            component name text is placed. The offset value is interpreted in terms
            of data co-ordinates.

        ylims : dict, optional
            Dictionary of target names (i.e. "beamsize", "gouy" or "curvature") to
            manual axis y-limits.

        npts : int, optional; default: 1000
            See equivalent argument in :meth:`.PropagationSolution.all_segments`.

        resolution : str, optional; default: "equal"
            See equivalent argument in :meth:`.PropagationSolution.all_segments`.

        subs : dict, optional
            A dictionary of model parameter to value substitutions
            to pass to the ``eval`` methods of symbolic expressions.

            If this solution object is not symbolic then this argument
            is ignored.

        Returns
        -------
        fig : Figure
            Handle to the figure.

        axs : axes
            The axis handles.
        """
        import matplotlib.pyplot as plt

        if not args:
            args = ("beamsize", "gouy")
        if "all" in args:
            args = ("beamsize", "gouy", "curvature")

        valid_args = ("beamsize", "gouy", "curvature")
        if any(arg not in valid_args for arg in args):
            raise ValueError(
                "Invalid target argument in args, expected any "
                f"combination of {valid_args} or 'all'"
            )

        if not self.symbolic and subs is not None:
            warn(
                f"Ignoring {subs=} kwarg as AstigmaticPropagationSolution is "
                f"non-symbolic."
            )

        N = len(args)
        fig, axs = plt.subplots(N, 2, sharex=True)
        if N == 1:
            axs = np.array([axs])

        maximums = {k: 0 for k in args}
        diff_mins = {k: 0 for k in args}

        if resolution.casefold() == "adaptive":
            raise NotImplementedError(
                "Adaptive resolution method for astigmatic propagation solution "
                "plotting has an outstanding issue and so is not yet supported."
            )

        data_x = self.ps_x.all_segments(
            w_scale=1e3, npts=npts, resolution=resolution, subs=subs
        )
        data_y = self.ps_y.all_segments(
            w_scale=1e3, npts=npts, resolution=resolution, subs=subs
        )

        for (zs_x, segd_x), (zs_y, segd_y) in zip(data_x.values(), data_y.values()):
            for i, arg in enumerate(args):
                vx = segd_x[arg]
                vy = segd_y[arg]
                if arg == "beamsize":
                    axs[i][0].fill_between(zs_x, vx, -vx, color="r", alpha=0.5)
                    axs[i][0].fill_between(zs_y, vy, -vy, color="b", alpha=0.5)
                else:
                    axs[i][0].plot(zs_x, vx)
                    axs[i][0].plot(zs_y, vy, linestyle="--")

                # TODO (sjr) This currently won't work with adaptive resolution
                #            method as vx and vy may be different size arrays.
                #            Need to find a way to resolve this. Maybe just force
                #            each segment in data_x, data_y to have same points
                #            between the two (bit annoying to handle though).
                axs[i][1].plot(zs_x, vx - vy, color="k")

                maximums[arg] = max(maximums[arg], vx.max(), vy.max())
                diff_mins[arg] = min(diff_mins[arg], (vx - vy).min())

        if ignore is None:
            ignore = []
        if not is_iterable(ignore):
            ignore = [ignore]

        if name_xoffsets is None:
            name_xoffsets = {}
        if name_yoffsets is None:
            name_yoffsets = {}

        for node, info in self.ps_x.node_info.items():
            if node.is_input:
                z = self.ps_x._eval_z_for_display(info, subs=subs)

                comp = node.component
                if "AR" not in comp.name and comp not in ignore:
                    name = comp.name
                    x_offset = name_xoffsets.get(name, 0)
                    y_offset = name_yoffsets.get(name, 0)
                    # display the name in a nicer way
                    name = name.replace("_", "\n")
                    n_newlines = name.count("\n")

                    for i, arg in enumerate(args):
                        if not i:
                            for ax in axs[i]:
                                ax.axvline(
                                    z,
                                    0.12 + 0.1 * n_newlines,
                                    color="k",
                                    linestyle="--",
                                )

                            if arg == "beamsize":
                                ytext_pos = [-1 * maximums[arg], diff_mins[arg]]
                            else:
                                ytext_pos = [0, 0]

                            for ax, ytp in zip(axs[i], ytext_pos):
                                ax.text(
                                    z + x_offset,
                                    ytp + y_offset,
                                    name,
                                    ha="center",
                                    va="center",
                                )
                        else:
                            for ax in axs[i]:
                                ax.axvline(z, color="k", linestyle="--")

        for ax in axs.flatten():
            ax.set_xlim(0, None)

        for ax in axs[-1]:
            ax.set_xlabel("Distance [m]")

        ylabel_mappings = {
            "beamsize": "Beam size [mm]",
            "gouy": "Gouy phase\naccumulation [deg]",
            "curvature": "Wavefront curvature [1/m]",
        }
        ylabel_diff_mappings = {
            "beamsize": r"$\mathrm{w}_\mathrm{x} - \mathrm{w}_\mathrm{y}$ [mm]",
            "gouy": r"$\psi_\mathrm{x} - \psi_\mathrm{y}$ [deg]",
            "curvature": r"$\mathrm{S}_\mathrm{x} - \mathrm{S}_\mathrm{y}$ [1/m]",
        }
        if ylims is None:
            ylims = {}
        for i, arg in enumerate(args):
            if arg != "beamsize":
                ylim = ylims.get(arg, None)
                if ylim is None:
                    axs[i][0].set_ylim(0 if arg == "gouy" else None, maximums[arg])
                else:
                    axs[i][0].set_ylim(ylim[0], ylim[1])

            ylabel = ylabel_mappings.get(arg, arg)
            axs[i][0].set_ylabel(ylabel)

            dylabel = ylabel_diff_mappings.get(arg)
            axs[i][1].set_ylabel(dylabel)

        if filename is not None:
            fig.savefig(filename)
        if show:
            plt.show()

        if N == 1:
            return fig, axs[0]

        return fig, axs


class BeamTraceSolution(BaseSolution):
    """Trace solution corresponding to calls to :meth:`.Model.beam_trace`.

    Note that BeamTraceSolution objects are returned via :meth:`.Model.beam_trace`
    calls, they should never need to be created manually.

    This class provides a dict-like interface to beam trace solution data. If
    ``trace`` is an instance of this class then one can access the beam parameters
    at both planes of a node via::

        # Using the look-up key notation
        qx, qy = trace[node]

        # Or the get method
        qx, qy = trace.get(node)

    One can also access individual plane beam parameters with::

        # Tangential plane
        qx = trace[node].qx

        # Sagittal plane
        qy = trace[node].qy

    A copy of the Python dictionary which stores all the underlying ``node : (qx, qy)``
    mappings can be obtained with the :attr:`.BeamTraceSolution.data` property.

    To draw a forest representation of the trace solution data, one can simply do::

        # Prints the forest of beam parameters
        print(trace)

        # Stores the forest as a string
        trace_str = str(trace)

    This forest will be ordered by the trace order used for the associated :meth:`.Model.beam_trace`
    call which constructed this solution.
    """

    NodeData = typing.NamedTuple("NodeData", [("qx", BeamParam), ("qy", BeamParam)])

    def __init__(self, name, data, forest=None):
        super().__init__(name)
        self._data = {node: self.NodeData(qx, qy) for node, (qx, qy) in data.items()}

        self.__forest = forest
        self.empty = False  # tree drawing fill circle

        # TODO (sjr) Temporary workaround for #328, need better output colouring
        interactive = is_interactive()
        self.__start_highlight = ": \x1b[0;32;40m[" if not interactive else ": ["
        self.__end_highlight = "]\x1b[0m" if not interactive else "]"

    def items(self):
        """A view on the underlying dict items."""
        return self._data.items()

    def values(self):
        """A view on the underlying dict values."""
        return self._data.values()

    def keys(self):
        """A view on the underlying dict keys."""
        return self._data.keys()

    @property
    def data(self):
        """A copy of the underlying dictionary of beam trace solution data.

        :getter: Returns the beam trace solution data. Read-only.
        """
        return self._data.copy()

    @property
    def data_qx(self):
        """A copy of the underlying `data` dictionary but with only the tangential plane
        beam parameters selected.

        :getter: Returns a dictionary of traced nodes with corresponding
                 tangential plane beam parameters (read-only).
        """
        return {node: qx for node, (qx, _) in self._data.items()}

    @property
    def data_qy(self):
        """A copy of the underlying `data` dictionary but with only the sagittal plane
        beam parameters selected.

        :getter: Returns a dictionary of traced nodes with corresponding
                 sagittal plane beam parameters (read-only).
        """
        return {node: qy for node, (_, qy) in self._data.items()}

    def __getitem__(self, node):
        if isinstance(node, OpticalNode):
            return self._data[node]

        if isinstance(node, Port):
            in_q = self._data.get(node.i, None)
            out_q = self._data.get(node.o, None)

            if in_q is None and out_q is None:
                raise KeyError(f"Port {node} not in the trace data.")

            return {node.i: in_q, node.o: out_q}

        if isinstance(node, Connector):
            return {n: self._data[n] for n in node.optical_nodes}

        raise TypeError(
            "Expected key to be of type OpticalNode, Port or Connector "
            f"but got object of type: {type(node)}"
        )

    def get(self, node, default=None):
        """Gets the beam parameter(s) at the specified node / port.

        Note that `node` can be an instance of :class:`.OpticalNode`, resulting in
        this method returning qx and qy for that specific node, *or* it can be an
        object of type :class:`.Port` - in which case a dictionary of both the
        input and output node beam parameters are returned.

        Parameters
        ----------
        node : :class:`.OpticalNode` or :class:`.Port`
            The node or port to access.

        default : any, optional; default: None
            The value to return if `node` does not exist within the trace data.
        """
        try:
            return self[node]
        except KeyError:
            return default
        except TypeError:
            raise

    def q(self, node):
        """A convenience method for getting the non-astigmatic beam parameter at a node.

        .. warning::
            This is only intended to be used on nodes which do not exhibit astigmatism. If
            qx != qy at the node then this method will raise a ValueError.

            To get both qx and qy at a node use either::

                qx, qy = trace[node]

            or::

                qx, qy = trace.get(node)

            where ``trace`` is an instance of this class.

        Parameters
        ----------
        node : :class:`.OpticalNode`
            The node at which to obtain q.

        Returns
        -------
        q : :class:`.BeamParam`
            The beam parameter (which is the same in both planes) at the node.

        Raises
        ------
        ex : ValueError
            If the beam parameters qx != qy at the node.
        """
        qx, qy = self._data[node]
        if qx != qy:
            raise ValueError(
                f"Beam parameters qx != qy at node {node.full_name}. Use "
                "sub-script operator or BeamTraceSolution.get to obtain both "
                "qx and qy in general."
            )

        return qx

    def __str_q(self, q=None, node=None):
        if node is not None:
            qx, qy = self._data[node]
        if q is not None:
            if isinstance(q, tuple):
                qx, qy = q
            else:
                qx = qy = q

        format_q = lambda q: f"{q.real:.2f} + {q.imag:.2f}j"

        if qx != qy:
            return f"qx = {format_q(qx)}, qy = {format_q(qy)}"

        return f"q = {format_q(qx)}"

    def __draw_tree(self, tree, lpad, lines):
        branch = "├─"
        pipe = "│"
        end = "╰─"
        dash = "─"

        ltree = tree.left
        rtree = tree.right

        if ltree is not None:
            s = branch + dash
            if rtree is None:
                s = end + dash
                pad = "   "
            else:
                s = branch + dash
                pad = pipe + "   "
            lines.append(
                lpad
                + s
                + "o"
                + " "
                + ltree.node.full_name
                + self.__start_highlight
                + self.__str_q(node=ltree.node)
                + self.__end_highlight
            )
            self.__draw_tree(ltree, lpad + pad, lines)

        if rtree is not None:
            s = end + dash
            pad = "   "
            lines.append(
                lpad
                + s
                + "o"
                + " "
                + rtree.node.full_name
                + self.__start_highlight
                + self.__str_q(node=rtree.node)
                + self.__end_highlight
            )
            self.__draw_tree(rtree, lpad + pad, lines)

    def __str__(self):
        all_trees = ""

        format_g = lambda gx, gy: f"gx = {gx}, gy = {gy}" if gx != gy else f"g = {gx}"
        cav_info = (
            lambda cav: f"({self.__str_q(q=(cav.qx, cav.qy))}, {format_g(cav.gx, cav.gy)})"
        )

        nodes = list(self._data.keys())
        if not nodes:
            return all_trees

        if self.__forest is None:  # Drawing a full model beam trace
            forest = nodes[0]._model.trace_forest.forest
        else:  # Drawing a custom forest, e.g. from a single cavity trace
            forest = self.__forest

        for tree in forest:
            lines = [
                "    "
                + "o"
                + " "
                + tree.node.full_name
                + self.__start_highlight
                + self.__str_q(node=tree.node)
                + self.__end_highlight
            ]
            self.__draw_tree(tree, "", lines)
            tree_s = "\n    ".join(lines)

            dep = tree.dependency
            if tree.is_source and isinstance(dep, Cavity):
                all_trees += (
                    f"\nInternal trace of cavity: {dep.name} {cav_info(dep)}\n\n"
                )
            else:
                all_trees += f"\nDependency: {dep.name}\n\n"
            all_trees += tree_s + "\n"

        return all_trees

    def print(self):
        """Draws the trace solution as a forest of beam parameters.

        This uses the :class:`.TraceForest` structure associated with the model that
        constructed this solution, where each tree is ordered by the trace order of the
        relevant call to the beam tracing method.
        """
        print(str(self))
