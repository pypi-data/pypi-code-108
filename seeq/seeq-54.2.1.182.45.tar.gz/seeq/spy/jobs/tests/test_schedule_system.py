import os

import mock
import pandas as pd
import pytest
import requests

from seeq import spy
from seeq.spy import Session
from seeq.spy._config import Setting
from seeq.spy.jobs import _schedule
from seeq.spy.jobs.tests import test_schedule_unit
from seeq.spy.tests import test_common

seeq_url = 'http://localhost:34216'


def setup_module():
    test_common.initialize_sessions()
    test_schedule_unit.setup_mocks()


@pytest.mark.system
def test_schedule_in_datalab():
    setup_run_in_datalab()

    test_jobs_df = pd.DataFrame({'Schedule': ['0 */2 1 * * ? *', '0 0 2 * * ? *', '0 42 03 22 1 ? 2121']})
    test_status = spy.Status()
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=test_jobs_df, status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert 'notebook.ipynb' in test_status.message
    assert 'notebook.pkl' in test_status.message
    assert len(schedule_result.index) == 3

    # dataframe without the schedule column, but first column containing the schedules
    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    test_jobs_df = pd.DataFrame({'Other Name': ['0 */2 1 * * ? *', '0 0 2 * * ? *']})
    test_status = spy.Status()
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=test_jobs_df,
                                            datalab_notebook_url=datalab_notebook_url,
                                            status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert '1.ipynb' in test_status.message
    assert '1.pkl' in test_status.message
    assert len(schedule_result.index) == 2

    # schedule with a label
    label = 'This is a label!'
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=test_jobs_df,
                                            datalab_notebook_url=datalab_notebook_url,
                                            label=label, status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert '1.ipynb' in test_status.message
    assert f' with label <strong>{label}</strong> ' in test_status.message
    assert f'1.with.label.{label}.pkl' in test_status.message
    assert len(schedule_result.index) == 2

    # dataframe without the schedule column
    test_jobs_df = pd.DataFrame({'Some Name': ['abc'], 'Other Name': ['abc']})
    with pytest.raises(ValueError, match='Could not interpret "abc" as a schedule'):
        _schedule.schedule_df(spy.session, jobs_df=test_jobs_df, status=test_status)


@pytest.mark.system
def test_schedule_in_executor():
    setup_run_in_executor()

    test_jobs_df = pd.DataFrame({'Schedule': ['0 */5 * * * ?'], 'Param': ['val1']})
    test_status = spy.Status()
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=test_jobs_df, status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert 'test.ipynb' in test_status.message
    assert 'test.pkl' in test_status.message
    assert len(schedule_result.index) == 1


@pytest.mark.system
def test_schedule_outside_datalab():
    setup_run_outside_datalab()
    test_common.log_out_default_user()

    test_jobs_df = pd.DataFrame({'Schedule': ['0 0 2 * * ? *', '0 42 03 22 1 ? 2121']})
    test_status = spy.Status()
    with pytest.raises(RuntimeError) as err1:
        _schedule.schedule_df(spy.session, jobs_df=test_jobs_df, status=test_status)
    assert "Not logged in" in str(err1.value)

    test_common.log_in_default_user()

    # no datalab_notebook_url provided
    with pytest.raises(RuntimeError) as err2:
        _schedule.schedule_df(spy.session, jobs_df=test_jobs_df, status=test_status)
    assert "Provide a Seeq Data Lab Notebook URL" in str(err2.value)

    # noinspection HttpUrlsUsage
    datalab_notebook_url = f'http://remote.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=test_jobs_df,
                                            datalab_notebook_url=datalab_notebook_url,
                                            status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert '1.ipynb' in test_status.message
    assert '1.pkl' in test_status.message
    assert len(schedule_result.index) == 2


@pytest.mark.system
def test_unschedule_in_datalab():
    setup_run_in_datalab()

    test_status = spy.Status()
    schedule_result = _schedule.schedule_df(spy.session, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert 'notebook.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    schedule_result = _schedule.schedule_df(spy.session, datalab_notebook_url=datalab_notebook_url, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert '1.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    label = 'Labeled!'
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=pd.DataFrame(), label=label, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert 'notebook.ipynb' in test_status.message
    assert label in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    label = '*'
    schedule_result = _schedule.schedule_df(spy.session, jobs_df=pd.DataFrame(), label=label, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert 'notebook.ipynb' in test_status.message
    assert 'for all labels' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())


@pytest.mark.system
def test_unschedule_outside_datalab():
    setup_run_outside_datalab()
    test_common.log_out_default_user()

    test_status = spy.Status()

    with pytest.raises(RuntimeError) as err:
        _schedule.schedule_df(spy.session, status=test_status)
    assert "Not logged in" in str(err.value)

    test_common.log_in_default_user()

    # should provide a datalab_notebook_url
    with pytest.raises(RuntimeError):
        _schedule.schedule_df(spy.session, status=test_status)

    # noinspection HttpUrlsUsage
    datalab_notebook_url = f'http://remote.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    schedule_result = _schedule.schedule_df(spy.session, datalab_notebook_url=datalab_notebook_url, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert '1.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    schedule_result = _schedule.schedule_df(spy.session, jobs_df=pd.DataFrame(),
                                            datalab_notebook_url=datalab_notebook_url,
                                            status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert '1.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())


@pytest.mark.system
def test_validate_and_get_next_trigger():
    validate_result = _schedule.validate_and_get_next_trigger(spy.session, ['0 */5 * * * ? 2069'])
    assert '2069-01-01 00:00:00 UTC' == validate_result['0 */5 * * * ? 2069']

    with pytest.raises(RuntimeError) as err1:
        _schedule.validate_and_get_next_trigger(spy.session, ['0 */5 * * * ? 2001', '0 */5 * * * *'])
    assert "schedules are invalid" in str(err1.value)
    assert "0 */5 * * * ? 2001" in str(err1.value)
    assert "No future trigger" in str(err1.value)

    with pytest.raises(RuntimeError) as err2:
        _schedule.validate_and_get_next_trigger(spy.session, ['* */2 * * * '])
    assert "Unexpected end of expression" in str(err2.value)

    with pytest.raises(RuntimeError) as err3:
        _schedule.validate_and_get_next_trigger(spy.session, ['* abc * * * ? *'])
    assert "Illegal characters for this position" in str(err3.value)


@pytest.mark.system
def test_retrieve_notebook_path_in_datalab():
    setup_run_in_datalab()
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(spy.session)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C863'
    assert file_path == 'notebook.ipynb'

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(spy.session, datalab_notebook_url)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C865'
    assert file_path == '1.ipynb'


@pytest.mark.system
def test_retrieve_notebook_path_in_executor():
    setup_run_in_executor()
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(spy.session)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C863'
    assert file_path == 'test.ipynb'

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C866/notebooks/2.ipynb'
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(spy.session, datalab_notebook_url)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C866'
    assert file_path == '2.ipynb'


@pytest.mark.system
def test_retrieve_notebook_path_outside_sdl():
    setup_run_outside_datalab()
    with pytest.raises(RuntimeError) as err:
        _schedule.retrieve_notebook_path(spy.session)
    assert "Provide a Seeq Data Lab Notebook URL" in str(err.value)

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C867/notebooks/3.ipynb'
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(spy.session, datalab_notebook_url)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C867'
    assert file_path == '3.ipynb'


@pytest.mark.system
def test_verify_not_actually_existing_and_accessible():
    setup_run_outside_datalab()
    # noinspection HttpUrlsUsage
    datalab_notebook_url = f'http://nonce.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C867/notebooks/3.ipynb'
    # noinspection HttpUrlsUsage
    contents_request_url = f'http://nonce.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C867/api/contents/3.ipynb'
    mock_resp = requests.Response()
    mock_resp.status_code = 404
    mock_requests_get = mock.Mock(return_value=mock_resp)
    session = Session()
    session.client = mock.MagicMock()
    session.client.auth_token = 'some token'
    with mock.patch('seeq.spy.jobs._common.requests_get', mock_requests_get):
        with pytest.raises(RuntimeError) as err:
            _schedule._verify_existing_and_accessible(session, datalab_notebook_url)
        assert 'Notebook not found for URL' in str(err.value)
        mock_requests_get.assert_called_once_with(session,
                                                  contents_request_url,
                                                  params={'type': 'file', 'content': 0},
                                                  cookies={'sq-auth': 'some token'})


def setup_run_outside_datalab():
    os.environ.pop('SEEQ_SDL_CONTAINER_IS_DATALAB', None)
    os.environ.pop('SEEQ_SDL_CONTAINER_IS_EXECUTOR', None)
    os.environ.pop('SEEQ_PROJECT_UUID', None)
    os.environ.pop('SEEQ_SDL_FILE_PATH', None)
    os.environ.pop('SEEQ_SDL_LABEL', None)
    os.environ.pop('SEEQ_SDL_SCHEDULE_INDEX', None)


def setup_run_in_datalab():
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = 'true'
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = ''
    os.environ['SEEQ_PROJECT_UUID'] = '8A54CD8B-B47A-42DA-B8CC-38AD4204C863'
    Setting.set_seeq_url(seeq_url)
    Setting.SEEQ_PROJECT_UUID.set('8A54CD8B-B47A-42DA-B8CC-38AD4204C863')


def setup_run_in_executor():
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = ''
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = 'true'
    os.environ['SEEQ_PROJECT_UUID'] = '8A54CD8B-B47A-42DA-B8CC-38AD4204C864'
    os.environ['SEEQ_SDL_FILE_PATH'] = 'test.ipynb'
    os.environ['SEEQ_SDL_LABEL'] = 'run-in-executor-label'
    os.environ['SEEQ_SDL_SCHEDULE_INDEX'] = '0'
    Setting.set_seeq_url(seeq_url)
    Setting.SEEQ_PROJECT_UUID.set('8A54CD8B-B47A-42DA-B8CC-38AD4204C863')
