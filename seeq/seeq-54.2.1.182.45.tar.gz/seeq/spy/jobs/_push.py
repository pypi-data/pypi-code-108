import os
from typing import Optional, Union

import pandas as pd

from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.jobs import _common as _jobs_common
from seeq.spy.jobs import _schedule


def push(jobs_df: pd.DataFrame, spread: Optional[str] = None, datalab_notebook_url: Optional[str] = None,
         label: Optional[str] = None, user: Optional[str] = None,
         interactive_index: Union[Optional[int], Optional[str]] = None, suspend: bool = False, quiet: bool = False,
         status: Optional[Status] = None, session: Optional[Session] = None):
    """
    Schedules the automatic execution of a notebook and returns the row
    corresponding for the currently running schedule.

    When used inside a Data Lab notebook, the current notebook is scheduled
    for execution. A notebook can be scheduled also by specifying its URL, and
    the scheduling can be done on behalf of another user by a user with admin
    privileges.

    Successive calls to 'push()' for the same notebook and label but with
    different schedules will replace the previous schedule for that notebook-
    label combination.

    Removing the scheduling is accomplished via unschedule().

    A copy of the jobs DataFrame is automatically stored to a _Job DataFrames
    folder adjacent to the Notebook for which the job is scheduled.

    Parameters
    ----------
    jobs_df : pandas.DataFrame
        A DataFrame that contains the schedules in the form of schedule
        specification strings and optional parameters for each job.

        The DataFrame must have an integer index and a column named 'Schedule'
        containing the scheduling specifications. If no column named 'Schedule'
        is found, the first column is used.

        Examples of scheduling specification strings:

                  'every 15 minutes'
                  'every tuesday and friday at 6am'
                  'every fifth of the month'

        The timezone used for scheduling is the one specified in the logged-in
        user's profile.

        You can also use Quartz Cron syntax. Use the following site to
        construct it:
        https://www.freeformatter.com/cron-expression-generator-quartz.html

    spread : str, default None
        A time period over which to spread out the jobs. This should generally
        be the same value of the frequency of the jobs. For example, if you
        want the jobs to run every 6 hours, you should specify spread='6h'
        to dynamically space out the execution of the jobs throughout that
        6-hour period so that the load on Seeq services isn't concentrated
        at the same time.

    datalab_notebook_url : str, default None
        A datalab notebook URL. If the value is not specified the currently
        running notebook URL is used.

    label : str, default None
        A string used to enable scheduling of the Notebook by different users
        or from different Analysis Pages.  Labels may contain letters, numbers,
        spaces, and the following special characters: !@#$^&-_()[]{}

    user : str, default None
        Determines the user on whose behalf the notebook is executed. If the
        value is not specified the currently logged in user is used. The can be
        specified as username or a user's Seeq ID.

    interactive_index : int or str, default None
        Used during notebook development to control which row of jobs_df is
        returned when NOT executing as a job. Change this value if you want
        to test your notebook in the Jupyter environment with various rows
        of parameters.

        When the notebook is executed as a job, this parameter is ignored.

    suspend : bool default False
        If True, un-schedules all jobs for the specified notebook. This is used
        in scenarios where you wish to work with a notebook interactively and
        temporarily prevent job execution. Remove the argument (or change it
        to False) when you are ready to resume job execution.

    quiet : bool, default False
        If True, suppresses progress output. Note that when status is
        provided, the quiet setting of the Status object that is passed
        in takes precedent.

    status : spy.Status, optional
        If specified, the supplied Status object will be updated as the command
        progresses. It gets filled in with the same information you would see
        in Jupyter in the blue/green/red table below your code while the
        command is executed. The table itself is accessible as a DataFrame via
        the status.df property.

    session : spy.Session, optional
        If supplied, the Session object (and its Options) will be used to
        store the login session state. This is useful to log in to different
        Seeq servers at the same time or with different credentials.

    Returns
    -------
    pandas.Series
        The row that corresponds to the currently executing job. If not
        executing in the context of job, then the row is returned according
        to the interactive_index parameter.

    """
    _common.validate_argument_types([
        (jobs_df, 'jobs_df', pd.DataFrame),
        (spread, 'spread', str),
        (datalab_notebook_url, 'datalab_notebook_url', str),
        (label, 'label', str),
        (user, 'user', str),
        (interactive_index, 'interactive_index', (int, str)),
        (suspend, 'suspend', bool),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)

    try:
        _schedule.schedule_df(session, jobs_df=jobs_df, spread=spread, datalab_notebook_url=datalab_notebook_url,
                              label=label, user=user, suspend=suspend, status=status)
    except SchedulePostingError:
        # When the notebook is executed as a job, push will first re-schedule the notebook. If any errors will happen
        # during that reschedule, an exception forces an exit from the method, and the currently executing notebook will
        # not get the needed parameters and will have a failed execution (assuming it needs the parameters). Most of
        # the time, such transient errors are unnecessary to the running of a job. One example where a failed schedule
        # call is actually expected is when you schedule a notebook to run exactly once, with a fixed date. When the
        # notebook is executing on schedule, the date is already in the past, and that means the schedule will fail
        # because you cannot schedule something to run in the past.
        #
        # So we ignore the error here when running as a job and fall through to get_parameters(). Note that
        # schedule_df() will have filled in the status.message with an error and set it to FAILURE so that it appears in
        # red in the job result HTML.
        if not _jobs_common.running_in_executor():
            raise

    return get_parameters(jobs_df, interactive_index, status)


def get_parameters(jobs_df, interactive_index, status):
    if _jobs_common.running_in_executor():
        schedule_index = os.environ.get('SEEQ_SDL_SCHEDULE_INDEX')

        try:
            int_index = int(schedule_index)
        except (ValueError, TypeError):
            int_index = None

        if schedule_index is None:
            raise SPyRuntimeError('Job is being executed without a SEEQ_SDL_SCHEDULE_INDEX environment variable')
        if not (schedule_index in jobs_df.index or int_index in jobs_df.index):
            raise SPyValueError(f'Cannot execute job with index {schedule_index} because it is not in the '
                                f'index of the DataFrame for the job')

        status.update((status.message or '') +
                      f'\nParameters returned are for DataFrame row index <strong>{schedule_index}</strong>.')

        return jobs_df.loc[schedule_index if int_index is None else int_index]
    else:
        status.update((status.message or '') +
                      f'\nParameters returned are for DataFrame row index <strong>{interactive_index}</strong>. To '
                      'change the DataFrame row returned in the INTERACTIVE context, add/change the '
                      '<code>interactive_index</code> argument.')

        try:
            int_index = int(interactive_index)
        except (ValueError, TypeError):
            int_index = None

        if interactive_index is None:
            status.update((status.message or '') + '\nNot running in executor and interactive_index was None; ' +
                          'therefore return value is None')
            return None
        elif not (interactive_index in jobs_df.index or int_index in jobs_df.index):
            raise SPyValueError(f'Cannot schedule job with interactive_index {interactive_index} because it is not in '
                                f'the index of the DataFrame for the job')
        else:
            return jobs_df.loc[interactive_index if int_index is None else int_index]
