""" Custom Sermos Scheduler and Celery Entry classes used for dynamic beat.
"""
import datetime
import os
import logging
from rhodb.redis_conf import RedisConnector
from celery.beat import Scheduler, ScheduleEntry
from celery import current_app
from celery.utils.time import is_naive
from celery.schedules import schedule as c_schedule, crontab as c_crontab
from sermos.utils.config_utils import retrieve_latest_schedule_config, \
    update_schedule_config
from sermos.constants import CONFIG_REFRESH_RATE, SCHEDULE_DATE_FORMAT, \
    USING_SERMOS_CLOUD

logger = logging.getLogger(__name__)
redis_conn = RedisConnector().get_connection()


def convert_to_datetime(
        datetime_str: str,
        datetime_format: str = SCHEDULE_DATE_FORMAT) -> datetime.datetime:
    """ Accept a string in the standard format and return a datetime object
    """
    return datetime.datetime.strptime(datetime_str, datetime_format)


def instantiate_celery_schedule(schedule_entry: dict) -> c_schedule:
    """ From a schedule entry and the full schedule from Sermos, create a
        celery `schedule` object.
    """
    scheduleType = schedule_entry['config']['scheduleType']

    if scheduleType == 'interval':
        # Create a timedelta object
        period = schedule_entry['config']['schedule']['period']
        every = schedule_entry['config']['schedule']['every']
        the_delta = datetime.timedelta(**{period: every})
        # Instantiate the celery schedule object
        return c_schedule(run_every=the_delta)

    if scheduleType == 'crontab':
        return c_crontab(
            minute=schedule_entry['config']['schedule']['minute'],
            hour=schedule_entry['config']['schedule']['hour'],
            day_of_week=schedule_entry['config']['schedule']['dayOfWeek'],
            day_of_month=schedule_entry['config']['schedule']['dayOfMonth'],
            month_of_year=schedule_entry['config']['schedule']['monthOfYear'])

    raise ValueError(f"Unsupported scheduleType ({scheduleType} ...")


class SermosEntry(ScheduleEntry):
    """ Create a beat entry with additional functionality for Sermos scheduler.

        https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
    """
    def __init__(self, schedule_entry: dict = None, **kwargs):
        schedule_entry = schedule_entry if schedule_entry else {}
        if schedule_entry:
            # This event is being instantiated directly with the Sermos
            # schedule entry
            celery_schedule = instantiate_celery_schedule(schedule_entry)

            # celery.beat.ScheduleEntry expects these keys in a dictionary
            # called `options`. See
            # https://docs.celeryproject.org/en/stable/userguide/calling.html
            # In the case of Sermos, we require the queue in the
            # ScheduleEntrySchema, others are all optional.
            options = dict()
            optional_keys = ('queue', 'exchange', 'routing_key', 'expires')
            for key in optional_keys:
                value = schedule_entry['config'].get(key, None)
                if value is not None:
                    options[key] = value

            last_run_at = schedule_entry.get('lastRunAt')
            if last_run_at is None:
                last_run_at = current_app.now()
                schedule_entry['lastRunAt'] = last_run_at
            if isinstance(schedule_entry['lastRunAt'], str):
                last_run_at = convert_to_datetime(
                    schedule_entry['lastRunAt'])

            # Verify times are accurate
            orig = last_run_at
            if not is_naive(last_run_at):
                last_run_at = last_run_at.replace(tzinfo=None)
            assert orig.hour == last_run_at.hour  # timezone sanity

            if USING_SERMOS_CLOUD:
                # We need to keep track of the id because this used to send
                # updates to sermos cloud.  The name can't be concatenated
                # with the sermos id or else it will be created as duplicate
                # celery beat task.
                name = schedule_entry['name']
                self.sermos_id = schedule_entry['id']
            else:
                name = schedule_entry['name']

            super().__init__(app=current_app._get_current_object(),
                             name=name,
                             task=schedule_entry['config']['task'],
                             args=schedule_entry.get('args', None),
                             kwargs=schedule_entry.get('kwargs', None),
                             options=options,
                             schedule=celery_schedule,
                             last_run_at=last_run_at,
                             total_run_count=schedule_entry.get(
                                 'totalRunCount', 0))
        else:
            # This is a task issued directly by celery's scheduler so won't
            # have the schedule_entry argument. Still not entirely clear why
            # this is seen.  Pop the id before initializing the super class.
            # Add it back after so we can keep sermos up to date w/ config.
            if USING_SERMOS_CLOUD:
                sermos_id = kwargs.pop('sermos_id')
                super().__init__(**kwargs)
                self.sermos_id = sermos_id
            else:
                super().__init__(**kwargs)

        # Ensure all events have 'event' key - this is populated by ChainedTask
        if 'event' not in self.kwargs.keys():
            self.kwargs['event'] = {}


class SermosScheduler(Scheduler):
    """ Sermos' implementation of a Celery Scheduler. Leverages a Sermos
    configuration server to provide the up-to-date schedule and provides to
    this scheduler for in-memory tracking.
    """
    Entry = SermosEntry
    _last_refresh = None  # Internal time keeper for Sermos syncing
    _refresh_rate = CONFIG_REFRESH_RATE * 1000000  # Turn to microseconds
    _schedule = None  # Holds latest Celery schedule with only enabled tasks
    _schedule_full = None  # Holds latest schedule, regardless of enabled
    _initial_read = True  # Set to False upon initial bootstrapping

    def __init__(self, *args, **kwargs):
        logger.info("Initializing SermosScheduler ...")
        # This step ensures the latest schedule is pulled from Sermos/cache
        # and bootstraps the local time checker we use.
        self.set_under_schedule()
        self._last_refresh = datetime.datetime.utcnow()

        # Default 60 second max interval here so our schedule is always
        # forced to be up to date.
        max_interval = int(
            os.environ.get('CELERY_BEAT_SYNC_MAX_INTERVAL',
                           CONFIG_REFRESH_RATE))
        kwargs['max_interval'] = max_interval

        kwargs['schedule'] = self._schedule
        Scheduler.__init__(self, *args, **kwargs)

    def set_under_schedule(self):
        """ Parse the latest schedule config and set self._schedule with parsed
        schedule including only those that are enabled.
        """
        s = {}
        s_full = []
        s_full_orig = [s.copy() for s in self._schedule_full
                       ] if self._schedule_full else []
        latest_schedule = retrieve_latest_schedule_config()
        for sched in latest_schedule:
            s_full.append(sched)  # Append to full list regardless of enabled
            if sched['enabled']:
                s[sched['name']] = SermosEntry(sched)
        self._schedule = s
        self._schedule_full = s_full

        # Report if schedule changed
        if self._schedule_full != s_full_orig:
            logger.info("SermosScheduler: Schedule updated ...")
            logger.info(f"SermosScheduler: {self._schedule}")

    def get_current_sermos_schedule(self):
        """ Unpack Celery's current representation of the schedule into Sermos
        format. This is used to send updates back to Sermos related to dynamic
        properties such as last_run_at and total_run_count.
        """

        sched = {'schedules': []}
        for entry_name, entry in self.schedule.items():
            sched['schedules'].append({
                'id': entry.sermos_id,
                'lastRunAt': entry.last_run_at.isoformat(),
                'totalRunCount': entry.total_run_count
            })

        return sched

    def setup_schedule(self):
        self.install_default_entries(self.data)
        # Overload default behavior and instead bootstrap with our _schedule
        # instead of app.conf.beat_schedule.
        self.merge_inplace(self._schedule)

    def should_refresh(self):
        """ Determine if enough time has elapsed to perform a schedule refresh.

        We turn everything into microseconds so we don't spam external services
        intra-second as most of the time, more than one task exists in the
        schedule and therefore we need to check the scheduler's `schedule`
        on each task very rapidly when issuing tasks.
        """
        now = datetime.datetime.utcnow()
        microseconds_since_last_refresh = float(
            str((now - self._last_refresh).seconds) + "." +
            str((now - self._last_refresh).microseconds)) * 1000000
        res = bool(microseconds_since_last_refresh > self._refresh_rate)
        if res is True:
            self._last_refresh = now - datetime.timedelta(milliseconds=1)
        return res

    def sync(self):
        """ Sync local schedule with Sermos and update Celery's representation
        TODO check this vis-a-vis local vs cloud
        """
        if self.schedule and USING_SERMOS_CLOUD:
            update_schedule_config(self.get_current_sermos_schedule())
        self.set_under_schedule()  # Internal representation
        self.merge_inplace(self._schedule)  # Celery representation

    def get_schedule(self):
        """ Overload default Scheduler get_schedule method to check for updates

        Note: Celery uses a property function, e.g.:
        https://www.tutorialsteacher.com/python/property-function
        for getting/setting the schedule internally. We only override the
        get_schedule method here.
        """
        update = False
        if self._initial_read:
            logger.info('SermosScheduler: Initial read ...')
            update = True
            self._initial_read = False
        elif self.should_refresh():
            logger.info('SermosScheduler: Refreshing schedule ...')
            update = True

        if update:
            self.sync()

        return self._schedule

    def set_schedule(self, schedule):
        """ Redefine Celery set_schedule method
        """
        self.data = schedule

    # Redefine Celery schedule property()
    schedule = property(get_schedule, set_schedule)
