import asyncio
import logging
import multiprocessing as mp
from asyncio import Future
from concurrent.futures import ProcessPoolExecutor
from functools import partial, partialmethod
from typing import TYPE_CHECKING, Type

from structlog import get_logger

from .bases import ActorBase, DistAPIBase

if TYPE_CHECKING:
    from .core import SchedulerTask  # pragma: no cover

logger = get_logger()


class RayAPI(DistAPIBase):
    def __init__(self):
        import ray
        from ray.exceptions import RayError, RayTaskError

        self._exc_cls = RayError
        self._task_exc = RayTaskError
        self._ray_module = ray

        ray_specs = ray.init(
            # resources=_limitset_to_ray_init(limit_set),
            log_to_driver=False,
            logging_level=logging.WARNING,
        )
        logger.info(f"ray dashboard: http://{ray_specs.get('webui_url')}")
        logger.info("launched ray with resources", **ray.cluster_resources())
        self._running = True

    @property
    def exception(self):
        return self._exc_cls

    def join(self):
        if self._running:
            self._ray_module.shutdown()
            self._running = False

    def kill(self, actor):
        self._ray_module.wait([actor.stop.remote()])
        self._ray_module.kill(actor)

    def get_running_actor(self, actor_cls: Type["ActorBase"]) -> "ActorBase":

        # ray should get the resources here...
        # not working with partial :
        if isinstance(actor_cls, partial):
            assert not actor_cls.args, "only kwargs in partials"
            root_cls = actor_cls.func
            actor_cls = type(
                root_cls.__name__,
                (ActorBase,),
                {
                    k: (
                        v
                        if k != "__init__"
                        else partialmethod(v, **actor_cls.keywords)
                    )
                    for k, v in root_cls.__dict__.items()
                },
            )

        return self._ray_module.remote(actor_cls).remote()

    @staticmethod
    def get_future(actor, next_task: "SchedulerTask") -> Future:
        return asyncio.wrap_future(
            actor.consume.remote(next_task.argument).future()
        )

    def parse_exception(self, e):
        return e.cause if isinstance(e, self._task_exc) else e


class SyncAPI(DistAPIBase):
    pass


class MultiProcAPI(DistAPIBase):
    def __init__(self) -> None:
        self.man = mp.Manager()

    def get_running_actor(self, actor_cls: Type["ActorBase"]) -> "ActorBase":
        return MPActorWrap(actor_cls, self.man)

    @staticmethod
    def get_future(actor, next_task: "SchedulerTask") -> Future:
        return asyncio.wrap_future(actor.consume(next_task.argument))

    def join(self):
        self.man.shutdown()


class MPActorWrap(ActorBase):
    def __init__(self, inner_actor_cls: Type["ActorBase"], man: mp.Manager):

        self._in_q = man.Queue(maxsize=1)
        self._out_q = man.Queue(maxsize=1)
        self.pool = ProcessPoolExecutor(1)
        self.proc = mp.Process(
            target=_work_mp_actor,
            args=(inner_actor_cls, self._in_q, self._out_q),
        )
        self.proc.start()

    def consume(self, task_arg):
        self.pool.submit(self._in_q.put, task_arg)
        return self.pool.submit(self._out_q.get)

    def stop(self):
        self.proc.kill()
        self.proc.join()
        self.pool.shutdown()


def _work_mp_actor(actor_cls, in_q, out_q):  # pragma: no cover
    actor = actor_cls()
    while True:
        arg = in_q.get()
        try:
            res = actor.consume(arg)
        except Exception as e:
            res = e
        out_q.put(res)


DIST_API_MAP = {"sync": SyncAPI, "ray": RayAPI, "mp": MultiProcAPI}
DEFAULT_DIST_API_KEY = "sync"


def get_dist_api(key) -> "DistAPIBase":
    try:
        return DIST_API_MAP[key]
    except KeyError:
        default = DIST_API_MAP[DEFAULT_DIST_API_KEY]
        err = f"unknown distributed system: {key}, defaulting {default}"
        logger.warning(err)
        return default
