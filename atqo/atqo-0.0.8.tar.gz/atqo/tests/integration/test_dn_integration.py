from enum import Enum

import pytest

from atqo import ActorBase, Capability, CapabilitySet, Scheduler, SchedulerTask
from atqo.distributed_apis import DIST_API_MAP


class REnum(Enum):
    CPU = 0
    CONN = 1
    MEM = 2


LIMIT_DIC = {REnum.CPU: 6, REnum.CONN: 2000, REnum.MEM: 3500}

file_uploader = Capability(
    {REnum.CPU: 1, REnum.CONN: 400, REnum.MEM: 1000}, name="ul"
)
bigfile_handling = Capability({REnum.CONN: 100, REnum.MEM: 1000}, name="big")
file_downloader = Capability(
    {REnum.CPU: 1, REnum.CONN: 500, REnum.MEM: 750}, name="dl"
)


class _TestBase(ActorBase):

    prefix = "nofing"

    def __init__(self) -> None:
        self._log("TEST intited")

    def consume(self, task_arg):
        self._log(f"TEST consuming {task_arg}")
        if task_arg == "fing":
            raise ValueError("oh-oh")
        return f"{self.prefix} {task_arg}"

    def stop(self):
        self._log("TEST stopping")


class Uploader(_TestBase):
    prefix = "uploaded"


class Downloader(_TestBase):
    prefix = "downloaded"


actor_dict = {
    CapabilitySet([file_uploader, bigfile_handling]): Uploader,
    CapabilitySet([file_uploader]): Uploader,
    CapabilitySet([file_downloader, bigfile_handling]): Downloader,
    CapabilitySet([file_downloader]): Downloader,
}


class _Producer:
    def __init__(self, *task_sets) -> None:
        self.task_sets = task_sets
        self._i = -1

    def __call__(self):
        self._i += 1
        try:
            return self.task_sets[self._i]
        except IndexError:
            return []


@pytest.mark.parametrize("dist_sys", [*DIST_API_MAP.keys(), "wrong"])
def test_minor_integration(dist_sys):
    reorg = True

    scheduler = Scheduler(
        actor_dict=actor_dict,
        resource_limits=LIMIT_DIC,
        distributed_system=dist_sys,
        reorganize_after_every_task=reorg,
        verbose=True,
    )

    tasks = [
        SchedulerTask("small file", requirements=[file_uploader]),
        SchedulerTask(
            "bigger file", requirements=[file_uploader, bigfile_handling]
        ),
        SchedulerTask(
            "complex", requirements=[file_downloader, bigfile_handling]
        ),
    ]

    out = []
    errs = []

    def _processor(results):
        for r in results:
            if isinstance(r, ValueError):
                errs.append(r)
            else:
                out.append(r)

    scheduler.process(
        _Producer(
            tasks, tasks, [SchedulerTask("fing", [file_downloader])], tasks
        ),
        _processor,
    )
    scheduler.join()

    assert sorted(out) == sorted(
        ["uploaded small file", "uploaded bigger file", "downloaded complex"]
        * 3
    )
    assert errs
    assert (
        "Upload"
        in scheduler._actor_sets[CapabilitySet([file_uploader])].__repr__()
    )
