"""Beam propagation tools for use outside of a simulation context.

The recommended function for most use-cases is
:func:`~finesse.tracing.tools.propagate_beam` (and
:func:`~finesse.tracing.tools.propagate_beam_astig` for astigmatic beam propagations)
which traces a beam through a specified path of a model. See :ref:`propagating_beams`
for details and examples.
"""

import logging

import numpy as np

from ..components import Cavity
from ..components.general import InteractionType
from ..gaussian import BeamParam
from ..paths import OpticalPath
from ..env import warn
from ..tracing.tree import TraceTree
from ..solutions import (
    ABCDSolution,
    PropagationSolution,
    AstigmaticPropagationSolution,
)
from ..utilities import refractive_index

from . import cytools

LOGGER = logging.getLogger(__name__)


### Composite ABCD matrices ###


def compute_abcd(
    from_node=None,
    to_node=None,
    via_node=None,
    path=None,
    direction="x",
    symbolic=False,
    solution_name=None,
):
    """Computes the composite ABCD matrix through a given path.

    By setting the argument `symbolic` to true, this method will return a symbolic
    representation of the ABCD matrix rather than a numeric matrix.

    Parameters
    ----------
    from_node : :class:`.Node`
        Node to trace from.

    to_node : :class:`.Node`
        Node to trace to.

    via_node : :class:`.Node`, optional
        Optional node to trace via.

    path : :class:`.OpticalPath`, optional
        A pre-generated path to use (produced from a call to :meth:`.Model.path`).

    directon : str, optional; default: "x"
        Direction of ABCD matrix computation (can be 'x', for tangential plane,
        or 'y', for sagittal plane).

    symbolic : bool, optional; default: False
        Flag indicating whether to compute a symbolic ABCD matrix.

    Returns
    -------
    out : :class:`.ABCDSolution`
        ABCD matrix solution object between the specified nodes.
    """
    path = _make_path(from_node, to_node, via_node, path)
    # Make a tree from the forward path...
    t_initial = TraceTree.from_path(path.nodes_only)
    if t_initial is None:
        raise ValueError("Cannot compute ABCD matrix from a node to itself!")
    # ... then get the last branch as full ABCD is
    #     computed from multiplying each ABCD upwards
    #     through the full tree (i.e. correct multiplication order)
    t = t_initial.get_last_left_branch()

    t.node._model._update_symbolic_abcds()

    if symbolic:
        M = cytools.compute_symbolic_abcd(t, direction)
    else:
        M = cytools.compute_numeric_abcd(t, direction)

    fn = path.nodes_only[0]
    tn = path.nodes_only[-1]
    comp1 = fn.component
    comp2 = tn.component
    # Workaround for ABCD at single connector, reverting minus sign applied
    # due to co-ordinate system transformation on reflection
    if (
        comp1 is comp2
        and direction == "x"
        and comp1.is_valid_coupling(fn, tn)
        and comp1.interaction_type(fn, tn) == InteractionType.REFLECTION
    ):
        M *= -1

    if solution_name is None:
        solution_name = f"ABCD_{fn.full_name}_{tn.full_name}_{direction}"
        if symbolic:
            solution_name += "_sym"

    return ABCDSolution(solution_name, M, direction, symbolic)


### Accumulated Gouy phases ###


def acc_gouy(
    from_node=None,
    to_node=None,
    via_node=None,
    path=None,
    q_in=None,
    direction="x",
    symbolic=False,
    deg=True,
    **kwargs,
):
    """Computes the accumulated Gouy phase along a specified path.

    By setting the argument `symbolic` to true, this method will return a symbolic
    representation of the accumulated Gouy phase rather than a number.

    If the argument `q_in` is not specified then this value will be determined
    from a call to :meth:`.Model.beam_trace`. Arguments to this beam trace call can be
    passed via the `kwargs` of this method.

    Parameters
    ----------
    from_node : :class:`.Node`
        Node to trace from.

    to_node : :class:`.Node`
        Node to trace to.

    via_node : :class:`.Node`, optional
        Optional node to trace via.

    path : :class:`.OpticalPath`, optional
        A pre-generated path to use.

    q_in : :class:`.BeamParam`, complex, optional
        Beam parameter to use at starting node. If not specified then
        this will be determined from a beam trace. Note that, if specified,
        this can also be a symbolic beam parameter.

    direction : str, optional; default: "x"
        Plane of computation (can be 'x', 'y' or `None`).

    symbolic : bool, optional; default: False
        Flag determining whether to return a symbolic representation.

    degrees : bool, optional; default: True
        Flag determining whether to convert return value from radians to degrees.
    """
    path = _make_path(from_node, to_node, via_node, path)
    t = TraceTree.from_path(path.nodes_only)
    if t is None:
        raise ValueError(
            "Cannot calculate accumulated Gouy phase from a node to itself!"
        )

    q_in = _make_input_q(q_in, t.node, direction, **kwargs)
    if q_in.wavelength != t.node._model.lambda0:
        warn(
            f"In acc_gouy:\n"
            f"    Wavelength of input beam parameter ({q_in.wavelength} m) not equal "
            f"to wavelength of model associated with path ({t.node._model.lambda0} m)."
        )
    if q_in.symbolic and not symbolic:
        LOGGER.info(
            "In acc_gouy:\n"
            "    Specified q_in argument is symbolic, switching on "
            "symbolic Gouy phase accumulation."
        )
        symbolic = True

    if symbolic:
        return cytools.compute_symbolic_acc_gouy(t, q_in, direction, deg)

    return cytools.compute_numeric_acc_gouy(t, complex(q_in), direction, deg)


### Arbitrary beam propagations ###


def propagate_beam(
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
    """Propagates a beam through a specified path, returning dictionaries of the beam
    parameter at each node and component.

    This method returns a :class:`.PropagationSolution` instance.

    See :ref:`propagating_beams` for details and examples on using this function.

    By setting the argument `symbolic` to true, this method will return symbolic
    representations of the beam parameters, ABCD matrices and accumulated Gouy phases.

    The argument `q_in` can be used to specify an arbitrary input beam parameter
    to be used at the starting node of the propagation. If not given then this
    will be determined from a call to :meth:`.Model.beam_trace`. Arguments to this
    beam trace call can be passed via the `kwargs` of this method.

    Parameters
    ----------
    from_node : :class:`.Node`
        Node to trace from.

    to_node : :class:`.Node`
        Node to trace to.

    via_node : :class:`.Node`, optional
        Optional node to trace via.

    path : :class:`.OpticalPath`, optional
        A pre-generated path to use.

    q_in : :class:`.BeamParam`, complex, optional
        Beam parameter to use at starting node. If not specified then
        this will be determined from a beam trace. Note that, if specified,
        this can also be a symbolic beam parameter.

    direction : str, optional; default: "x"
        Plane of computation (can be 'x', 'y' or `None`).

    symbolic : bool, optional; default: False
        Flag determining whether to return a symbolic representation.

    Returns
    -------
    ps : :class:`.PropagationSolution`
        A solution object for the propagation.
    """
    path = _make_path(from_node, to_node, via_node, path)
    t = TraceTree.from_path(path.nodes_only)
    if t is None:
        raise ValueError("Cannot propagate beam from a node to itself!")

    q_in = _make_input_q(q_in, t.node, direction, **kwargs)
    if q_in.wavelength != t.node._model.lambda0:
        warn(
            f"In propagate_beam:\n"
            f"    Wavelength of input beam parameter ({q_in.wavelength} m) not equal "
            f"to wavelength of model associated with path ({t.node._model.lambda0} m)."
        )
    if q_in.symbolic and not symbolic:
        LOGGER.info(
            "In propagate_beam:\n"
            "    Specified q_in argument is symbolic, switching on "
            "symbolic propagation."
        )
        symbolic = True

    if symbolic:
        node_info, comp_info = cytools.propagate_beam_symbolic(t, q_in, direction)
    else:
        node_info, comp_info = cytools.propagate_beam_numeric(t, q_in, direction)

    if solution_name is None:
        fn = path.nodes_only[0]
        tn = path.nodes_only[-1]

        solution_name = f"Propagation_{fn.full_name}_{tn.full_name}_{direction}"
        if symbolic:
            solution_name += "_sym"

    return PropagationSolution(solution_name, node_info, comp_info, symbolic)


def propagate_beam_astig(
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
    """Propagates the beam through a specified path over both the tangential and
    sagittal planes.

    Internally this calls :func:`~finesse.tracing.tools.propagate_beam` twice - for both
    the tangential and sagittal planes - and returns a solution object which stores the
    returns of these as properties.

    Parameters
    ----------
    from_node : :class:`.Node`
        Node to trace from.

    to_node : :class:`.Node`
        Node to trace to.

    via_node : :class:`.Node`, optional
        Optional node to trace via.

    path : :class:`.OpticalPath`, optional
        A pre-generated path to use.

    qx_in : :class:`.BeamParam`, complex, optional
        Beam parameter, in the tangential plane, to use at starting node. If not
        specified then this will be determined from a beam trace. Note that,
        if specified, this can also be a symbolic beam parameter.

    qy_in : :class:`.BeamParam`, complex, optional
        Beam parameter, in the sagittal plane, to use at starting node. If not
        specified then this will be determined from a beam trace. Note that,
        if specified, this can also be a symbolic beam parameter.

    symbolic : bool, optional; default: False
        Flag determining whether to return a symbolic representation.

    Returns
    -------
    astig_sol : :class:`.AstigmaticPropagationSolution`
        A solution object consisting of the propagation solutions for both planes
        and methods for accessing the per-plane beam parameters and overlaps.
    """
    path = _make_path(from_node, to_node, via_node, path)
    ps_x = propagate_beam(
        path=path, q_in=qx_in, direction="x", symbolic=symbolic, **kwargs
    )
    ps_y = propagate_beam(
        path=path, q_in=qy_in, direction="y", symbolic=symbolic, **kwargs
    )

    if solution_name is None:
        fn = path.nodes_only[0]
        tn = path.nodes_only[-1]

        solution_name = f"AstigProp_{fn.full_name}_{tn.full_name}"
        if symbolic:
            solution_name += "_sym"

    return AstigmaticPropagationSolution(solution_name, ps_x, ps_y)


### Computing mode mismatches ###


def compute_cavity_mismatches(model, cav1=None, cav2=None):
    """Computes the mismatch parameter (see :meth:`.BeamParam.mismatch` for the
    equation) between cavities of the model.

    If either / both of `cav1`, `cav2` are not specified then these will be set to
    all the cavities of the model. This means that the default behaviour of this method
    (specifying no args) is to compute mismatches between each cavity in the model.

    If either of each cavity in a coupling is unstable then the mismatch values
    between these will be given as ``np.nan``.

    Parameters
    ----------
    cav1 : :class:`.Cavity`, str, optional; default: None
        A single cavity object (or its name). Defaults to None such that
        all cavities are used.

    cav2 : :class:`.Cavity`, str, optional; default: None
        A single cavity object (or its name). Defaults to None such that
        all cavities are used.

    Returns
    -------
    mmx : float or dict
        If both `cav1` and `cav2` were specified then this will be a single number
        giving the mismatch between these cavities in the tangential plane.

        Otherwise, mmx is a dictionary of ``(c1, c2): mm_x`` mappings, where `c1`
        and `c2` are the cavity names and `mm_x` is the mismatch between any two
        cavities in the tangential plane.

    mmy : float or dict
        If both `cav1` and `cav2` were specified then this will be a single number
        giving the mismatch between these cavities in the sagittal plane.

        Otherwise, mmy is a dictionary of ``(c1, c2): mm_y`` mappings, where `c1`
        and `c2` are the cavity names and `mm_y` is the mismatch between any two
        cavities in the sagittal plane.
    """
    if cav1 is None:
        cavs_outer = model.cavities
    else:
        if isinstance(cav1, str):
            _c1 = model.elements.get(cav1)
        else:
            _c1 = cav1
        if not isinstance(_c1, Cavity):
            raise ValueError(f"Invalid argument type/name for cav1: {cav1}")

        cavs_outer = [_c1]

    if cav2 is None:
        cavs_inner = model.cavities
    else:
        if isinstance(cav2, str):
            _c2 = model.elements.get(cav2)
        else:
            _c2 = cav2
        if not isinstance(_c2, Cavity):
            raise ValueError(f"Invalid argument type/name for cav2: {cav2}")

        cavs_inner = [_c2]

    mm_x = {}
    mm_y = {}
    for c1 in cavs_outer:
        if not c1.is_stable:
            for c2 in cavs_inner:
                mm_x[(c1.name, c2.name)] = mm_x[(c2.name, c1.name)] = np.nan
                mm_y[(c1.name, c2.name)] = mm_y[(c2.name, c1.name)] = np.nan
        else:
            trace = model.beam_trace(store=False, enable_only=c1)
            for c2 in cavs_inner:
                if not c2.is_stable:
                    mm_x[(c1.name, c2.name)] = mm_x[(c2.name, c1.name)] = np.nan
                    mm_y[(c1.name, c2.name)] = mm_y[(c2.name, c1.name)] = np.nan
                elif c1 is c2:
                    mm_x[(c1.name, c2.name)] = mm_x[(c2.name, c1.name)] = 0
                    mm_y[(c1.name, c2.name)] = mm_y[(c2.name, c1.name)] = 0
                else:
                    q1x, q1y = trace[c2.source]
                    q2x, q2y = c2.qx, c2.qy

                    mmx = BeamParam.mismatch(q1x, q2x)
                    mmy = BeamParam.mismatch(q1y, q2y)

                    mm_x[(c1.name, c2.name)] = mm_x[(c2.name, c1.name)] = mmx
                    mm_y[(c1.name, c2.name)] = mm_y[(c2.name, c1.name)] = mmy

    if cav1 is not None and cav2 is not None:
        return list(mm_x.values())[0], list(mm_y.values())[0]

    return mm_x, mm_y


### Convenience functions ###


def _make_path(from_node, to_node, via_node, path):
    if path is not None:
        if from_node is not None or to_node is not None or via_node is not None:
            raise ValueError(
                "Cannot specify both path and any of " "(from_node, to_node, via_node)."
            )

        if not isinstance(path, OpticalPath):
            raise TypeError(
                "Expected path to be of type OpticalPath (i.e. return "
                "value of a Model.path call), but got an object of "
                f"type: {type(path)}"
            )
    else:
        if from_node is None or to_node is None:
            raise ValueError("One of: path OR (from_node, to_node) must be specified.")

        model = from_node._model
        if to_node._model is not model:
            raise ValueError(
                f"{from_node.full_name} and {to_node.full_name} are from "
                "different models."
            )
        path = model.path(from_node, to_node, via_node=via_node)

    return path


def _make_input_q(q_in, node, direction, **kwargs):
    model = node._model
    if q_in is None:
        trace = model.beam_trace(store=False, **kwargs)

        qx_in, qy_in = trace[node]
        if direction == "x":
            q_in = qx_in
        else:
            q_in = qy_in
    else:
        model._update_symbolic_abcds()

        if not isinstance(q_in, BeamParam):
            q_in = BeamParam(
                q=q_in,
                wavelength=model.lambda0,
                nr=refractive_index(node),
            )

    return q_in
