from atqo import ActorBase, Capability, CapabilitySet, Scheduler, SchedulerTask
from atqo.distributed_apis import DEFAULT_DIST_API_KEY
from atqo.simplified_functions import BatchProd

LIMIT_DIC = {"A": 3}

cap1 = Capability({"A": 1})
cap2 = Capability({"A": 1})


class Actor(ActorBase):
    def consume(self, task_arg):
        return f"done-{task_arg}"


class ListProd:
    def __init__(self, list_base, batch_size) -> None:
        self._size = batch_size
        self._list = list_base
        self._i = 0

    def __call__(self):
        out = []
        for _ in range(self._size):
            try:
                out.append(self._list[self._i])
                self._i += 1
            except IndexError:
                break
        return out


def test_over_actors():

    dist_sys = DEFAULT_DIST_API_KEY
    actor_dict = {
        CapabilitySet([cap2, cap1]): Actor,
    }

    scheduler = Scheduler(
        actor_dict=actor_dict,
        resource_limits=LIMIT_DIC,
        distributed_system=dist_sys,
        verbose=True,
    )

    tasks = [
        SchedulerTask("task1", requirements=[cap1]),
    ]

    out = []

    def _proc(ol):
        for e in ol:
            out.append(e)

    scheduler.process(BatchProd(tasks, 2, lambda x: x), result_processor=_proc)
    scheduler.join()

    assert out == ["done-task1"]


def test_recurse():
    dist_sys = DEFAULT_DIST_API_KEY
    actor_dict = {
        CapabilitySet([cap2, cap1]): Actor,
    }

    scheduler = Scheduler(
        actor_dict=actor_dict,
        resource_limits=LIMIT_DIC,
        distributed_system=dist_sys,
        verbose=True,
    )

    tasks = [
        SchedulerTask(f"task{i}", requirements=[cap1]) for i in range(1, 9)
    ]

    out = []

    def _proc(ol):
        size = 0
        for e in ol:
            size += 1
            out.append(e)
        for i in range(size // 2):
            tasks.append(tasks[i])

    scheduler.process(ListProd(tasks, 10), result_processor=_proc)
    scheduler.join()

    muls = [(1, 4), (2, 3), (3, 2), (4, 2), *[(i2, 1) for i2 in range(5, 9)]]

    assert sorted(out) == sum(
        [[f"done-task{i}"] * k for i, k in muls],
        [],
    )
