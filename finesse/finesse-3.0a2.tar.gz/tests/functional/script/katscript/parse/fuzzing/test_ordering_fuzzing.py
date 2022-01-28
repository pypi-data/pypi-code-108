"""Tests for making sure that order in katscript doesn't matter."""

import pytest
from hypothesis import given, settings
from hypothesis.strategies import permutations
from finesse.script import parse
from .....diff import assert_models_equivalent


# A script with a `cav` command which normally has to be built last.
SCRIPT = """
l L0 P=1
s s0 L0.p1 EOM1.p1
mod EOM1 f=100M midx=0.1 order=1 mod_type=pm
s s1 EOM1.p2 ITM.p1 L=1
m ITM R=0.99 T=0.01 Rc=-0.9
s sCAV ITM.p2 ETM.p1 L=1
m ETM R=0.99 T=0.01 phi=123 Rc=0.9
pd1 REFL_I ITM.p1.o 100M 0
cav FP ITM.p2.o
"""


@pytest.fixture(scope="package")
def reference_model():
    """The parsed model without any re-ordering."""
    return parse(SCRIPT)


@given(scriptlines=permutations(SCRIPT.splitlines()))
@settings(deadline=1000)  # See #292.
def test_script_order_doesnt_matter(scriptlines, reference_model):
    """Test that script order does not matter.

    This test works by randomly reordering the lines of the reference script, then
    parsing and comparing the model to the reference model.
    """
    model = parse("\n".join(scriptlines))
    assert_models_equivalent(reference_model, model)
