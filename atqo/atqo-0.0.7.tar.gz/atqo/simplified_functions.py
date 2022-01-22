from itertools import islice
from multiprocessing import cpu_count

from .bases import ActorBase
from .core import Scheduler, SchedulerTask
from .distributed_apis import DEFAULT_DIST_API_KEY
from .resource_handling import Capability, CapabilitySet
from .utils import partial_wrap

_RES = "CPU"
_CAP = Capability({_RES: 1})
_Task = partial_wrap(SchedulerTask, requirements=[_CAP])


class BatchProd:
    def __init__(self, iterable, batch_size, mapper=_Task) -> None:
        self._size = batch_size
        self._it = iter(iterable)
        self._mapper = mapper

    def __call__(self):
        return [*map(self._mapper, islice(self._it, self._size))]


class ActWrap(ActorBase):
    def __init__(self, fun) -> None:
        self._f = fun

    def consume(self, task_arg):
        return self._f(task_arg)


def get_simp_scheduler(n, fun, dist_sys) -> Scheduler:
    return Scheduler(
        actor_dict={CapabilitySet([_CAP]): partial_wrap(ActWrap, fun=fun)},
        resource_limits={_RES: n},
        distributed_system=dist_sys,
    )


def parallel_map(
    fun,
    iterable,
    dist_api=DEFAULT_DIST_API_KEY,
    batch_size=None,
    min_queue_size=None,
    workers=None,
):
    nw = workers or cpu_count()
    batch_size = batch_size or nw * 5
    min_queue_size = min_queue_size or batch_size // 2

    scheduler = get_simp_scheduler(nw, fun, dist_api)

    out = []

    scheduler.process(
        batch_producer=BatchProd(iterable, batch_size),
        result_processor=lambda li: [*map(out.append, li)],
        min_queue_size=min_queue_size,
    )
    scheduler.join()
    return out
