import attr
import pytest

from levo_commons.events import Finished, Payload


@attr.s(slots=True)
class ExamplePayload(Payload):
    foo: int = attr.ib()


def test_events_api():
    event = Finished(running_time=1.0, payload=ExamplePayload(foo=42))
    assert event.running_time == pytest.approx(1.0)
    assert event.asdict() == {
        "payload": {"foo": 42},
        "running_time": pytest.approx(1.0),
    }
