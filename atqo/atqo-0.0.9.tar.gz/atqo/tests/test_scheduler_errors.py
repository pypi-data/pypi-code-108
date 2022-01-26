import pytest

from atqo.core import Scheduler, SchedulerTask
from atqo.exceptions import NotEnoughResources
from atqo.resource_handling import Capability, CapabilitySet


def test_empty_scheduler():
    scheduler = Scheduler({}, {})
    assert scheduler.is_idle
    assert scheduler.is_empty
    assert scheduler.queued_task_count == 0


def test_dead_end():

    cap1 = Capability({"A": 1})
    cap2 = Capability({"A": 2})

    scheduler = Scheduler({CapabilitySet([cap1]): None}, {"A": 1})

    with pytest.raises(NotEnoughResources):
        scheduler.refill_task_queue(
            [SchedulerTask("x", requirements=[cap1, cap2])]
        )
