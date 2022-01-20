import asyncio
from enum import Enum
from typing import Optional
from apscheduler.schedulers.base import BaseScheduler, BaseJobStore
from apscheduler.jobstores.mongodb import MongoDBJobStore
from jcramda import from_import_as, depop
from .core import host_mac


__all__ = (
    'SchedulerType',
    'create_by_mongo',
    'scheduler',
    'job2dict',
    'default_store_opts',
)


ERR_MSG = 'scheduler is not created'


def job2dict(job):
    if not job:
        return {}
    return {
        'id': job.id,
        'name': job.name,
        'trigger': job.trigger,
        'func': job.func.__name__,
        'executor': job.executor,
        'args': job.args,
        'kwargs': job.kwargs,
        'max_instances': job.max_instances,
        'next_run_time': job.next_run_time,
        'misfire_grace_time': job.misfire_grace_time,
        'coalesce': job.coalesce,
    }


class SchedulerManager(object):
    instance: Optional[BaseScheduler]
    store: Optional[BaseJobStore]
    lock: asyncio.Lock

    def __init__(self, cron: BaseScheduler = None):
        self.lock = asyncio.Lock()
        self.instance = cron

    async def start(self):
        cron = self.instance
        assert cron, ERR_MSG
        assert not cron.running, 'scheduler is already running'
        await scheduler.lock.acquire()
        cron.start()
        while scheduler.lock.locked():
            await asyncio.sleep(1)

    def stop(self):
        assert self.instance, ERR_MSG
        assert self.instance.running, 'scheduler is not running'
        self.instance.shutdown()
        scheduler.lock.release()

    def jobs(self):
        assert self.instance, ERR_MSG
        if not self.instance.running:
            self.instance.start(True)
        r = list(map(job2dict, self.store.get_all_jobs()))
        return r

    def add_job(self, func, job_opts):
        """

        Parameters
        ----------
        func
        job_opts: dict
            "id": job id, Opitonal.
            "name": job name
            "args": func args
            "kwargs": func kwargs
            "trigger": ``date``, ``interval`` or ``cron``

            ## date params
                - datetime|str run_date: the date/time to run the job at
                - datetime.tzinfo|str timezone: time zone for ``run_date`` if it doesn't have one already

            ## interval params
               - int weeks: number of weeks to wait
               - int days: number of days to wait
               - int hours: number of hours to wait
               - int minutes: number of minutes to wait
               - int seconds: number of seconds to wait
               - datetime|str start_date: starting point for the interval calculation
               - datetime|str end_date: latest possible date/time to trigger on
               - datetime.tzinfo|str timezone: time zone to use for the date/time calculations
               - int|None jitter: advance or delay the job execution by ``jitter`` seconds at most.

            ## cron params
                - int|str year: 4-digit year
                - int|str month: month (1-12)
                - int|str day: day of the (1-31)
                - int|str week: ISO week (1-53)
                - int|str day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
                - int|str hour: hour (0-23)
                - int|str minute: minute (0-59)
                - int|str second: second (0-59)
                - datetime|str start_date: earliest possible date/time to trigger on (inclusive)
                - datetime|str end_date: latest possible date/time to trigger on (inclusive)
                - datetime.tzinfo|str timezone: time zone to use for the date/time calculations
                           (defaults to scheduler timezone)
                - int|None jitter: advance or delay the job execution by ``jitter`` seconds at most.

                .. note:: The first weekday is always **monday**.

        Returns
        -------

        """
        assert self.instance, 'scheduler is not created'
        return self.instance.add_job(func, **job_opts)

    def modify(self, job_id, change):
        job = self.store.lookup_job(job_id)
        assert job, f'not found job by id {job_id}'
        if 'args' in change or 'kw' in change:
            args, kw = depop(['args', 'kw'], change)
            job = self.instance.modify_job(job_id, args=args, kwargs=kw)
        if 'trigger' in change:
            job = self.instance.reschedule_job(job_id, **change)
        return job2dict(job)

    def remove(self, job_id):
        try:
            self.instance.remove_job(job_id)
        except RuntimeError:
            return False
        return True

    @property
    def running(self):
        return self.instance.running

    def find_job(self, job_id):
        return job2dict(self.store.lookup_job(job_id))


class SchedulerType(Enum):
    ASYNC = 'apscheduler.schedulers.asyncio:AsyncIOScheduler'
    BACKGROUND = 'apscheduler.schedulers.background:BackgroundScheduler'
    SYNC = 'apscheduler.schedulers.blocking:BlockingScheduler'


scheduler = SchedulerManager()


def create_by_mongo(s_type: SchedulerType = SchedulerType.BACKGROUND,
                    **mongo_store_opts) -> SchedulerManager:
    assert scheduler.instance is None, 'scheduler is already created'
    clazz = from_import_as(s_type.value)
    assert clazz, f'not found scheduler class named: {s_type.value}'
    instance: BaseScheduler = clazz()
    scheduler.store = MongoDBJobStore(**mongo_store_opts)
    instance.add_jobstore(scheduler.store)
    scheduler.instance = instance
    return scheduler


def default_store_opts(node=None) -> dict:
    node_id = node if node else host_mac()
    from .drivers import mongo
    mongo_client = mongo.conn()
    return {
        'collection': f'jobs.{node_id}',
        'database': mongo_client.get_default_database().name,
        'client': mongo_client
    }
