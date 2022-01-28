"""Test utilities.

Put any misc functionality shared by multiple tests here.
"""

import re
from textwrap import dedent
import numpy as np
import networkx as nx
from hypothesis import assume
from hypothesis.strategies import (
    composite,
    recursive,
    one_of,
    integers,
    floats,
    complex_numbers,
    characters,
    text,
    lists,
    sampled_from,
    from_regex,
    dictionaries,
)
from finesse import Model
from finesse.symbols import OPERATORS
from finesse.components import Cavity, Gauss
from finesse.detectors.general import Detector
from finesse.script.spec import KatSpec


_SPEC = KatSpec()
_MODEL = Model()

# Names that cannot be used for elements.
RESERVED_NAMES = {*dir(_MODEL), *_SPEC.reserved_names}


# FIXME: don't hard-code these.
BINARY_OPERATIONS = (
    "__add__",
    "__sub__",
    "__mul__",
    "__truediv__",
    "__floordiv__",
    "__pow__",
)


def dedent_multiline(text):
    """Dedent multiline text, stripping preceding and succeeding newlines.

    This is useful for specifying multiline strings in tests without having to
    compensate for the indentation.
    """
    return dedent(text).strip()


def escape_full(pattern):
    """Escape regex `pattern`, adding start (`^`) and end (`$`) markers.

    This is useful in combination with the `match` argument to pytest's `raises` context
    manager. It can be used to escape error messages that are intended to be matched
    exactly.
    """
    return "^" + re.escape(pattern) + "$"


@composite
def numbers(draw, operations=False):
    """Any type of number."""
    cmplx_kwargs = dict(
        min_magnitude=0, max_magnitude=1, allow_nan=False, allow_infinity=False
    )

    if operations:
        # Wrap complex numbers in Operation objects.
        cmplx_strategy = complex_number_operations(**cmplx_kwargs)
    else:
        cmplx_strategy = complex_numbers(**cmplx_kwargs)

    return draw(
        one_of(
            floats(min_value=-1, max_value=1, allow_nan=False, allow_infinity=False),
            integers(min_value=-1, max_value=1),
            cmplx_strategy,
        )
    )


@composite
def complex_number_operations(draw, **kwargs):
    number = draw(complex_numbers(**kwargs))
    operation = OPERATORS["__sub__"] if number.imag < 0 else OPERATORS["__add__"]
    return operation(number.real, abs(number.imag))


@composite
def open_expressions(draw, rhs):
    lval = draw(numbers())
    operation = draw(sampled_from(BINARY_OPERATIONS))
    rval = draw(rhs)

    try:
        assume(operation not in ("/", "//") and rhs != 0)
    except TypeError:
        # Input type cannot be compared to zero.
        pass

    return OPERATORS[operation](lval, rval)


# TODO: make an Operation for parenthesised expressions
# @composite
# def bracketed_expressions(draw, rhs):
#     return f"({draw(open_expressions(rhs))})"


@composite
def expressions(draw, rhs=numbers()):
    # return draw(one_of(open_expressions(rhs), bracketed_expressions(rhs)))
    return draw(open_expressions(rhs))


@composite
def recursive_expressions(draw, max_leaves=25):
    """Generate nested expressions up to max_leaves."""
    return draw(
        recursive(
            expressions(), lambda rhs: expressions(rhs=rhs), max_leaves=max_leaves
        )
    )


@composite
def recursive_arrays(draw, operations=False):
    """Generate nested arrays up to max_leaves."""
    return [draw(recursive(numbers(operations=operations), lists))]


@composite
def line(draw, nonempty=False):
    """A single line of text."""
    # Blacklist control characters.
    return draw(
        text(
            min_size=1 if nonempty else 0,
            alphabet=characters(blacklist_categories=("Cs", "Cc")),
        )
    )


@composite
def kat_name(draw):
    """Valid kat script name."""
    name = draw(from_regex("^[a-zA-Z_][a-zA-Z0-9_]*$", fullmatch=True))
    assume(name not in RESERVED_NAMES)
    return name


@composite
def kat_empty(draw, multiline=False):
    if multiline:
        pattern = "^[ \t]*$"
    else:
        pattern = "^[ \t\n]*$"
    return draw(from_regex(pattern, fullmatch=True))


@composite
def kat_comment(draw):
    # Blacklist control characters.
    comment = draw(line())
    return f"#{comment}"


# Valid normal fraction for reflectivity etc.
KAT_NORMAL_FLOAT = floats(min_value=0, max_value=1, allow_nan=False)


@composite
def kat_scalar(draw, nonnegative=False):
    """Kat script scalar value, including SI suffices."""
    min_value = 0 if nonnegative else None
    value = draw(floats(min_value=min_value, allow_nan=False, allow_infinity=False))
    items = [value]

    # Can't add a suffix for scientific notation.
    if "e" not in str(value):
        suffix = draw(sampled_from("pnumkMGT"))
        items.append(f"{value}{suffix}")

    return draw(sampled_from(items))


@composite
def kat_rtl(draw):
    """R, T, L adding up to 1."""
    R = draw(KAT_NORMAL_FLOAT, label="R")
    T = draw(KAT_NORMAL_FLOAT, label="T")
    L = draw(KAT_NORMAL_FLOAT, label="L")

    # Don't allow R, T and L to be too small.
    if R != 0:
        assume(R > 1e-3)
    if T != 0:
        assume(T > 1e-3)
    if L != 0:
        assume(L > 1e-3)

    total = R + T + L
    assume(total > 0)
    R /= total
    T /= total
    L /= total
    return R, T, L


@composite
def kat_laser(draw):
    directive = draw(sampled_from(_SPEC.elements["laser"].aliases))
    name = draw(kat_name())
    params = draw(
        dictionaries(keys=sampled_from(("P", "f", "phase")), values=kat_scalar())
    )
    paramstr = " ".join([f"{k}={v}" for k, v in params.items()])
    return f"{directive} {name} {paramstr}"


@composite
def kat_mirror(draw):
    directive = draw(sampled_from(_SPEC.elements["mirror"].aliases))
    name = draw(kat_name())
    R, T, L = draw(kat_rtl())
    return f"{directive} {name} R={R} T={T} L={L}"


@composite
def kat_beamsplitter(draw):
    directive = draw(sampled_from(_SPEC.elements["beamsplitter"].aliases))
    name = draw(kat_name())
    R, T, L = draw(kat_rtl())
    return f"{directive} {name} R={R} T={T} L={L}"


@composite
def kat_element(draw):
    return draw(one_of(kat_laser(), kat_mirror(), kat_beamsplitter()))


@composite
def kat_script_line(draw):
    """Generate kat script line."""
    return draw(one_of(kat_empty(), kat_comment(), kat_element()))


def assert_models_equivalent(model_a, model_b):
    """Check :class:`.Model` equality.

    This checks that the two specified models are identical in a shallow way, i.e. they have
    elements with the same properties, equivalent networks, actions, etc.

    This is implemented here and not as `Model.__eq__` because :class:`.Model` must be hashable.
    """
    assert_actions_equivalent(model_a.analysis, model_b.analysis)

    for el_a, el_b in zip(sorted(model_a.elements), sorted(model_b.elements)):
        assert_model_elements_equivalent(model_a.elements[el_a], model_b.elements[el_b])

    assert_networks_equivalent(model_a.network, model_b.network)


def assert_networks_equivalent(network_a, network_b):
    """Check that two :class:`NetworkX graphs <nx.classes.graph.Graph>` are equal."""
    assert nx.is_isomorphic(
        network_a, network_b
    ), f"{network_a!r} is not an isomorph of {network_b!r}"


def assert_model_elements_equivalent(comp_a, comp_b):
    """Check :class:`.ModelElement` equality.

    This is implemented here and not as `ModelElement.__eq__` because `ModelElement`
    must be hashable.
    """

    if not isinstance(comp_a, comp_b.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError(
            f"Cannot compare {comp_a!r} with type {type(comp_a).__name__} to "
            f"{comp_b!r} with type {type(comp_b).__name__}"
        )

    assert comp_a.name == comp_a.name
    for param_a, param_b in zip(comp_a.parameters, comp_b.parameters):
        assert_parameters_equivalent(param_a, param_b)


def assert_parameters_equivalent(param_a, param_b, expected=None):
    """Check model parameter equality.

    This is implemented here and not as `ModelParameter.__eq__` because `ModelParameter`
    must be hashable.
    """
    if not isinstance(param_a, param_b.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError(
            f"Cannot compare {param_a!r} with type {type(param_b).__name__} to "
            f"{param_a!r} with type {type(param_b).__name__}"
        )

    val_a = param_a.eval()
    val_b = param_b.eval()

    assert (
        val_a == val_b
    ), f"{param_a!r} and {param_b!r} do not evaluate to the same value"

    if expected is not None:
        assert val_a == expected, f"{param_a!r} != {expected}"
        assert val_b == expected, f"{param_b!r} != {expected}"


def assert_cavities_equivalent(cav_a, cav_b):
    """Check cavity equality.

    This is implemented here and not as `Cavity.__eq__` because `Cavity` must be
    hashable.
    """
    if not isinstance(cav_b, cav_a.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError

    assert_model_elements_equivalent(cav_a, cav_b)
    assert isinstance(cav_a, Cavity), f"{cav_a!r} is not a Cavity"
    assert isinstance(cav_b, Cavity), f"{cav_b!r} is not a Cavity"
    assert (
        cav_a.round_trip_length == cav_b.round_trip_length
    ), f"{cav_a!r} round trip length != {cav_b!r} round trip length"
    assert np.all(
        cav_a.gouy == cav_b.gouy
    ), f"{cav_a!r} round trip gouy != {cav_b!r} round trip gouy"
    assert cav_a.FSR == cav_b.FSR, f"{cav_a!r} FSR != {cav_b!r} FSR"
    assert cav_a.loss == cav_b.loss, f"{cav_a!r} loss != {cav_b!r} loss"
    assert cav_a.finesse == cav_b.finesse, f"{cav_a!r} finesse != {cav_b!r} finesse"
    assert cav_a.FWHM == cav_b.FWHM, f"{cav_a!r} FWHM != {cav_b!r} FWHM"
    assert cav_a.pole == cav_b.pole, f"{cav_a!r} pole != {cav_b!r} pole"
    assert np.all(
        cav_a.mode_separation == cav_b.mode_separation
    ), f"{cav_a!r} mode separation != {cav_b!r} mode separation"
    assert np.all(cav_a.S == cav_b.S), f"{cav_a!r} resolution != {cav_b!r} resolution"
    assert np.all(cav_a.ABCDx == cav_b.ABCDx), f"{cav_a!r} ABCDx != {cav_b!r} ABCDx"
    assert np.all(cav_a.ABCDy == cav_b.ABCDy), f"{cav_a!r} ABCDy != {cav_b!r} ABCDy"
    assert np.all(cav_a.q == cav_b.q), f"{cav_a!r} q != {cav_b!r} q"
    assert np.all(cav_a.g == cav_b.g), f"{cav_a!r} g != {cav_b!r} g"


def assert_gauss_commands_equivalent(gauss_a, gauss_b):
    """Check gauss command equality.

    This is implemented here and not as `Gauss.__eq__` because `Gauss` must be hashable.
    """
    if not isinstance(gauss_b, gauss_a.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError

    assert_model_elements_equivalent(gauss_a, gauss_b)
    assert isinstance(gauss_a, Gauss), f"{gauss_a!r} is not a Gauss"
    assert isinstance(gauss_b, Gauss), f"{gauss_b!r} is not a Gauss"
    # TODO: add more gauss command comparisons.


def assert_detectors_equivalent(det_a, det_b):
    """Check detector equality.

    This is implemented here and not as `Detector.__eq__` because `Detector` must be
    hashable.
    """
    if not isinstance(det_b, det_a.__class__):
        # Don't attempt to compare against unrelated types.
        raise NotImplementedError

    assert_model_elements_equivalent(det_a, det_b)
    assert isinstance(det_a, Detector), f"{det_a!r} is not a Detector"
    assert isinstance(det_b, Detector), f"{det_b!r} is not a Detector"
    # TODO: add more detector comparisons.


def assert_actions_equivalent(act_a, act_b):
    """Check action equality.

    This is implemented here and not as `Action.__eq__` because `Action` must be
    hashable.
    """
    # TODO: compare more things.
    # Compare trees.
    # TODO ddb - this doesn't really work for testing equivalence of Actions anymore
    # assert str(act_a) == str(act_b), f"Action {act_a!r} != Action {act_b!r} {str(act_a)} {str(act_b)}"
    return True


def assert_nodes_equivalent(node_a, node_b):
    """Check node equality.

    This is implemented here and not as `Node.__eq__` because `Node` must be hashable.
    """
    assert node_a.name == node_b.name, f"{node_a!r} name != {node_b!r} name"
    assert_model_elements_equivalent(node_a.component, node_b.component)


def assert_generate_reparse_equivalent(parser, generator, model, **kwargs):
    """Helper function for checking that generated kat script for a model reparses into
    an equivalent model."""
    assert (
        model.analysis is not None
    ), "For comparison, model must have an explicit analysis defined."

    script = generator.dump(model, **kwargs)
    parsed_model = parser.parse(script)
    assert_models_equivalent(model, parsed_model)


def assert_trace_trees_equal(t1, t2):
    """Check TraceTree equality."""
    # Both t1 and t2 must be None or not None.
    if t1 is None and t2 is None:
        # Nothing to test.
        return
    elif (t1 is None and t2 is not None) or (t1 is not None and t2 is None):
        assert False

    assert t1.node == t2.node, f"{t1} node {t1.node} != {t2} node {t2.node}"
    assert (
        t1.dependency == t2.dependency
    ), f"{t1} dependency {t1.dependency} != {t2} dependency {t2.dependency}"

    assert_trace_trees_equal(t1.left, t2.left)
    assert_trace_trees_equal(t1.right, t2.right)
