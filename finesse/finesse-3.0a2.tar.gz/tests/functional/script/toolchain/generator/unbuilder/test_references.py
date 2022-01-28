import pytest


# Override default element to take two model parameter arguments.
@pytest.fixture
def fake_element_cls(fake_element_cls, fake_float_parameter):
    @fake_float_parameter("a", "Fake Parameter A")
    @fake_float_parameter("b", "Fake Parameter B")
    class FakeElement(fake_element_cls):
        def __init__(self, name, a=None, b=None):
            super().__init__(name)
            self.a = a
            self.b = b

    return FakeElement


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls, finesse_binop_sub):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.binary_operators["-"] = finesse_binop_sub
    return spec


def test_reference(unbuilder, model, element_dump, fake_element_cls):
    model.add(fake_element_cls("myel1"))
    model.add(fake_element_cls("myel2"))
    model.myel1.b.value = 0
    model.myel1.a = 1 - model.myel1.b.ref
    model.myel2.a = model.myel1.a.ref
    model.myel2.b = model.myel1.b.ref
    dumps = iter(element_dump("fake_element", fake_element_cls, model))
    assert unbuilder.unbuild(next(dumps)) == "fake_element myel1 a=(1-&myel1.b) b=0.0"
    assert unbuilder.unbuild(next(dumps)) == "fake_element myel2 a=&myel1.a b=&myel1.b"
