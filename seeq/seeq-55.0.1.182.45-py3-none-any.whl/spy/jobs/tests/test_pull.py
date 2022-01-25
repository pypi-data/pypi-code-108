import base64
import json
import os
import pickle

import mock
import pandas as pd
import pytest

from seeq.sdk import *
from seeq.spy.jobs import _pull
from seeq.spy.jobs.tests import test_schedule_system
from seeq.spy.tests import test_common

notebook_route = 'data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C863/notebooks/Path/To/Some/Notebook.ipynb'
test_notebook_url = f'{test_schedule_system.seeq_url}/{notebook_route}'
# noinspection HttpUrlsUsage
remote_notebook_url = f'http://remote.com/{notebook_route}'
test_df = pd.DataFrame(data={'Schedule': ['Daily'], 'Additional Info': ['What you need to know']})


def setup_module():
    test_common.initialize_sessions()


def requests_get_mock():
    mock_get_resp = mock.Mock()
    mock_get_resp.content = json.dumps({'content': base64.b64encode(pickle.dumps(test_df)).decode('utf-8')})
    mock_get_resp.status_code = 200
    return mock.Mock(return_value=mock_get_resp)


# noinspection PyUnusedLocal
def load_pickle_mock(pickle_path):
    return test_df


def get_project_from_api_mock():
    project_output = ProjectOutputV1(
        scheduled_notebooks=[
            ScheduledNotebookOutputV1(
                project='8A54CD8B-B47A-42DA-B8CC-38AD4204C863',
                file_path='Path/To/Some/Notebook.ipynb',
                label='run-in-executor-label',
                schedules=[
                    ScheduleOutputV1(key='0', stopped=False)
                ]
            )
        ]
    )
    return mock.Mock(return_value=project_output)


@pytest.mark.system
def test_pull_success_in_datalab():
    test_schedule_system.setup_run_in_datalab()
    with mock.patch('seeq.spy.jobs._common.requests_get', requests_get_mock()), \
            mock.patch('seeq.spy.jobs._pull.get_project_from_api', get_project_from_api_mock()), \
            mock.patch('seeq.spy.jobs._pull.load_pickle', load_pickle_mock):
        retrieved_job = _pull.pull(test_notebook_url, interactive_index=0, label='run-in-executor-label')
        assert 'Schedule' in retrieved_job
        assert 'What you need to know' in retrieved_job.values


@pytest.mark.system
def test_pull_success_all():
    test_schedule_system.setup_run_in_datalab()
    with mock.patch('seeq.spy.jobs._common.requests_get', requests_get_mock()), \
            mock.patch('seeq.spy.jobs._pull.get_project_from_api', get_project_from_api_mock()), \
            mock.patch('seeq.spy.jobs._pull.load_pickle', load_pickle_mock):
        retrieved_jobs = _pull.pull(test_notebook_url, all=True, label='run-in-executor-label')
        assert isinstance(retrieved_jobs, pd.DataFrame)
        assert len(retrieved_jobs) == 1
        assert 'Schedule' in retrieved_jobs.loc[0]
        assert 'What you need to know' in retrieved_jobs.loc[0].values


@pytest.mark.system
def test_pull_success_in_executor():
    test_schedule_system.setup_run_in_executor()
    mock_requests_get = requests_get_mock()
    with mock.patch('seeq.spy.jobs._common.requests_get', mock_requests_get), \
            mock.patch('seeq.spy.jobs._pull.get_project_from_api', get_project_from_api_mock()), \
            mock.patch('seeq.spy.jobs._pull.load_pickle', load_pickle_mock):
        retrieved_job = _pull.pull(test_notebook_url)
        assert 'Schedule' in retrieved_job
        assert 'What you need to know' in retrieved_job.values


@pytest.mark.system
def test_pull_success_outside_datalab():
    test_schedule_system.setup_run_outside_datalab()

    # Mark Derbecker (2021-12-31)
    # The following line doesn't seem correct but was necessary to get this test to run consistently in parallel
    os.environ['SEEQ_SDL_LABEL'] = 'run-in-executor-label'

    with mock.patch('seeq.spy.jobs._common.requests_get', requests_get_mock()), \
            mock.patch('seeq.spy.jobs._pull.get_project_from_api', get_project_from_api_mock()):
        retrieved_job = _pull.pull(remote_notebook_url, interactive_index=0)
        assert 'Schedule' in retrieved_job
        assert 'What you need to know' in retrieved_job.values


@pytest.mark.system
def test_pull_failure_outside_datalab():
    test_schedule_system.setup_run_outside_datalab()

    # Mark Derbecker (2021-12-31)
    # The following line doesn't seem correct but was necessary to get this test to run consistently in parallel
    os.environ['SEEQ_SDL_LABEL'] = 'run-in-executor-label'

    mock_get_resp_403 = mock.Mock()
    mock_get_resp_403.status_code = 403
    with mock.patch('seeq.spy.jobs._common.requests_get', mock.Mock(return_value=mock_get_resp_403)), \
            mock.patch('seeq.spy.jobs._pull.get_project_from_api', get_project_from_api_mock()):
        with pytest.raises(RuntimeError):
            _pull.pull(remote_notebook_url, interactive_index=0)
