import base64
import json
import pathlib
import pickle
from typing import Optional, Union

import pandas as pd

from seeq.sdk import *
from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.jobs import _common as _jobs_common
from seeq.spy.jobs import _push
from seeq.spy.jobs import _schedule


# noinspection PyShadowingBuiltins
def pull(datalab_notebook_url=None, label=None, interactive_index: Union[Optional[int], Optional[str]] = None,
         all: bool = False, session: Optional[Session] = None) -> Optional[pd.Series]:
    """
    Retrieves a jobs DataFrame previously created by a call to spy.jobs.push or
    spy.jobs.schedule.  The DataFrame will have been stored as a pickle (.pkl)
    file in the _Job DataFrames folder within the parent folder of the Notebook
    specified by the datalab_notebook_url, or of the current Notebook if no
    datalab_notebook_url is specified.

    Parameters
    ----------
    datalab_notebook_url : str, default None
        The URL of the Data Lab Notebook for which the scheduled jobs DataFrame
        is desired.  If the value is not specified, the URL of the
        currently-running notebook is used.

    label : str, default None
        The label that was used in scheduling, if any.  In most circumstances,
        this parameter should not be specified, since the scheduled Notebook
        will use the label that was provided during scheduling.

    interactive_index : int or str, default None
        Used during notebook development to control which row of jobs_df is
        returned when NOT executing as a job. Change this value if you want
        to test your notebook in the Jupyter environment with various rows
        of parameters.

        When the notebook is executed as a job, this parameter is ignored.

    all : bool, default False
        If true, the entire DataFrame is returned, regardless of call context
        or the value of interactive_index

    session : spy.Session, optional
        If supplied, the Session object (and its Options) will be used to
        store the login session state. This is useful to log in to different
        Seeq servers at the same time or with different credentials.

    Returns
    -------
    pandas.Series or pandas.DataFrame
        The requested row of the DataFrame that was pushed for the specified
        Notebook and label using the spy.jobs.push or spy.jobs.schedule method,
        if called with all=False.  If all=True, the entire DataFrame is
        returned

"""
    _common.validate_argument_types([
        (datalab_notebook_url, 'datalab_notebook_url', str),
        (label, 'label', str),
        (interactive_index, 'interactive_index', (int, str)),
        (all, 'all', bool),
        (session, 'session', Session)
    ])

    session = Session.validate(session)

    if interactive_index is None and not all and not _jobs_common.running_in_executor():
        raise SPyValueError(f'When not running in an executor, an interactive_index must be supplied for spy.jobs.pull '
                            f'unless all=True')

    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(session, datalab_notebook_url)

    if label is None:
        inferred_label = _jobs_common.get_label_from_executor() or None
    else:
        inferred_label = label

    project = get_project_from_api(session, project_id)
    scheduled_notebooks = [
        notebook for notebook in project.scheduled_notebooks
        if notebook.file_path == file_path and notebook.label == inferred_label
    ]

    if not scheduled_notebooks:
        return None
    elif len(scheduled_notebooks) != 1:
        raise SPyRuntimeError('There should be only one scheduled notebook')
    scheduled_notebook = scheduled_notebooks[0]

    file_path_path = pathlib.PurePosixPath(file_path)
    path_to_parent = _schedule.path_or_empty_string(file_path_path.parent)
    jobs_dfs_folder_path = pathlib.PurePosixPath(path_to_parent, _common.JOB_DATAFRAMES_FOLDER_NAME)
    with_label_text = f'.with.label.{inferred_label}' if inferred_label else ''
    jobs_df_pickle = f'{file_path_path.stem}{with_label_text}.pkl'
    get_pickle_path = pathlib.PurePosixPath(jobs_dfs_folder_path, jobs_df_pickle)
    if _schedule.is_referencing_this_project(datalab_notebook_url):
        jobs_df = load_pickle(get_pickle_path)
    else:
        cookies = {'sq-auth': session.client.auth_token}
        resp = _jobs_common.requests_get(session, f'{data_lab_url}/{project_id}/api/contents/{get_pickle_path}',
                                         cookies=cookies)
        if resp.status_code in [200, 201]:
            jobs_df = pickle.loads(base64.b64decode(json.loads(resp.content)['content']))
        else:
            raise SPyRuntimeError(f'Could not retrieve job due to error calling Jupyter Contents API: '
                                  f'({resp.status_code}) {resp.reason}')

    def typed_index(index):
        try:
            return int(index)
        except ValueError:
            return str(index)

    # N.B.: Python 3.7+ dicts are ordered by insertion order
    stopped = {typed_index(schedule.key): schedule.stopped for schedule in scheduled_notebook.schedules}
    jobs_df = jobs_df[jobs_df.index.isin(stopped.keys())]
    jobs_df['Stopped'] = jobs_df.apply(lambda x: stopped[x.name] if x.name in stopped.keys() else False, axis=1)
    if all:
        return jobs_df
    else:
        return _push.get_parameters(jobs_df, interactive_index, Status(quiet=True))


def load_pickle(pickle_path):
    full_path = pathlib.Path(_common.DATALAB_HOME, pickle_path)
    if not _schedule.path_exists(full_path):
        raise SPyRuntimeError(f'Schedule DataFrame pickle file not found for path {pickle_path}.')
    with open(pathlib.Path(_common.DATALAB_HOME, pickle_path), mode='rb') as pickle_file:
        return pickle.load(pickle_file)


def get_project_from_api(session: Session, project_id):
    projects_api = ProjectsApi(session.client)
    return projects_api.get_project(id=project_id)
