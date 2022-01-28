"""Test parsed element order.

Compilation of elements into a model does not necessarily follow script order. At the
end of compilation the elements are re-ordered based on their script order. Multiple
calls to parse should result in elements appearing first in their parse sequence then in
script order for that particular script.
"""

from itertools import permutations
import pytest
from finesse.components import Mirror


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    return spec


def _element_order(model):
    elements = list(model.elements)
    # The first item is always fsig, and we don't return that to the test.
    assert elements.pop(0) == "fsig"
    return elements


# Some element names in every possible script order.
_ELEMENT_NAMES_1 = pytest.mark.parametrize(
    "names1", list(permutations(["el1", "el2", "el3"]))
)
_ELEMENT_NAMES_2 = pytest.mark.parametrize(
    "names2", list(permutations(["el4", "el5", "el6"]))
)


@_ELEMENT_NAMES_1
def test_parse_no_existing_elements(compiler, model, names1):
    """Check order after parsing into an empty model."""
    compiler.compile(
        "\n".join([f"fake_element {name}" for name in names1]), model=model
    )
    assert _element_order(model) == list(names1)


@_ELEMENT_NAMES_1
@_ELEMENT_NAMES_2
def test_single_parse_with_existing_elements__python(compiler, model, names1, names2):
    """Check order after parsing into model with existing elements added via Python."""
    for name in names1:
        model.add(Mirror(name))
    assert _element_order(model) == list(names1)
    compiler.compile(
        "\n".join([f"fake_element {name}" for name in names2]), model=model
    )
    assert _element_order(model) == list(names1 + names2)


@_ELEMENT_NAMES_1
@_ELEMENT_NAMES_2
def test_single_parse_with_existing_elements__katscript(
    compiler, model, names1, names2
):
    """Check order after parsing into model with existing elements added via
    KatScript."""
    compiler.compile(
        "\n".join([f"fake_element {name}" for name in names1]), model=model
    )
    assert _element_order(model) == list(names1)
    compiler.compile(
        "\n".join([f"fake_element {name}" for name in names2]), model=model
    )
    assert _element_order(model) == list(names1 + names2)
