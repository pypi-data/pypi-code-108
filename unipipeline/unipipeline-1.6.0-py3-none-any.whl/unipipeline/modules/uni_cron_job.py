from datetime import datetime
from typing import NamedTuple, List, Tuple, Optional, Iterable, TYPE_CHECKING

from crontab import CronTab  # type: ignore

from unipipeline.message.uni_cron_message import UniCronMessage
from unipipeline.definitions.uni_cron_task_definition import UniCronTaskDefinition

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator


class UniCronJob(NamedTuple):
    id: int
    task: UniCronTaskDefinition
    crontab: Optional[CronTab]
    every_sec: Optional[int]
    mediator: 'UniMediator'
    message: UniCronMessage

    def next_sec(self) -> int:
        if self.crontab is not None:
            return int(self.crontab.next(default_utc=False))
        sec = datetime.now().second
        mod = sec % self.every_sec  # type: ignore
        return 0 if mod == 0 else (self.every_sec - mod)  # type: ignore

    @staticmethod
    def mk_jobs_list(tasks: Iterable[UniCronTaskDefinition], mediator: 'UniMediator') -> List['UniCronJob']:
        res = list()
        for i, task in enumerate(tasks):
            res.append(UniCronJob(
                id=i,
                task=task,
                crontab=CronTab(task.when) if task.when is not None else None,
                every_sec=task.every_sec,
                mediator=mediator,
                message=UniCronMessage(task_name=task.name)
            ))
        return res

    @staticmethod
    def search_next_tasks(all_tasks: List['UniCronJob']) -> Tuple[Optional[int], List['UniCronJob']]:
        min_delay: Optional[int] = None
        notification_list: List[UniCronJob] = []
        for cj in all_tasks:
            sec = cj.next_sec()
            if min_delay is None:
                min_delay = sec
            if sec < min_delay:
                notification_list.clear()
                min_delay = sec
            if sec <= min_delay:
                notification_list.append(cj)

        return min_delay, notification_list

    def send(self) -> None:
        self.mediator.send_to(self.task.worker.name, self.message, alone=self.task.alone)
