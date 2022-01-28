import pytest
from ..data import ARRAYS


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


@pytest.mark.parametrize("katarray,_", ARRAYS)
def test_array(compiler, regenerate, katarray, _):
    script = f"fake_element  myelement  {katarray}"
    model = compiler.compile(script)
    regenerated = regenerate(model)
    assert regenerated == script
