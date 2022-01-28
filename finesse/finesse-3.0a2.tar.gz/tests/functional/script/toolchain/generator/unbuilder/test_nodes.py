import pytest


@pytest.fixture
def fake_detector_cls(fake_element_cls):
    class FakeDetector(fake_element_cls):
        def __init__(self, name, target):
            super().__init__(name)
            self.target = target

    return FakeDetector


@pytest.fixture
def spec(spec, fake_element_adapter_factory, fake_element_cls):
    spec.register_element(fake_element_adapter_factory(fake_element_cls))
    spec.register_element(
        fake_element_adapter_factory(fake_detector_cls, "fake_detector")
    )
    return spec


def test_port(unbuilder, model, element_dump, fake_element_cls, fake_detector_cls):
    model.add(fake_element_cls("myel"))
    mydet = fake_detector_cls("mydet", target=model.myel.p1)
    model.add(mydet)
    dump = next(iter(element_dump("fake_detector", fake_detector_cls, model)))
    script = unbuilder.unbuild(dump)
    assert script == "fake_detector mydet target=myel.p1"


def test_node(unbuilder, model, element_dump, fake_element_cls, fake_detector_cls):
    model.add(fake_element_cls("myel"))
    mydet = fake_detector_cls("mydet", target=model.myel.p1.o)
    model.add(mydet)
    dump = next(iter(element_dump("fake_detector", fake_detector_cls, model)))
    script = unbuilder.unbuild(dump)
    assert script == "fake_detector mydet target=myel.p1.o"
