import pytest
from ...data import ARRAYS


# Override default element to take one argument.
@pytest.fixture
def fake_element_cls(fake_element_cls):
    class FakeElement(fake_element_cls):
        def __init__(self, name, a):
            super().__init__(name)
            self.a = a

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    return spec


@pytest.mark.parametrize("_,array", ARRAYS)
def test_array(unbuilder, model, element_dump, fake_element_cls, array, _):
    model.add(fake_element_cls("myel", a=array))
    dump = next(iter(element_dump("fake_element", fake_element_cls, model)))
    script = unbuilder.unbuild(dump)
    reference = f"fake_element myel a={array}"
    assert script == reference
