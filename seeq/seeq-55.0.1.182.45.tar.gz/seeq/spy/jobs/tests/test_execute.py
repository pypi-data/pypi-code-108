import os
from pathlib import Path

import mock
import pytest

from seeq.base import system
from seeq.spy.jobs import _common as _jobs_common
from seeq.spy.jobs import _execute

execution_notebook_file = "data-lab/jupyter/scheduling/ExecutionNotebook.ipynb"
test_notebook_path = "sdk/pypi/seeq/spy/docs/Documentation"
test_notebook_file = "spy.pull.ipynb"
label = 'run-in-executor-label'
test_sched_index = '0'
job_key = '2ff2df94-a532-4f20-8864-959813ab4c17_7726F74691C5'

notebook_file_scheduled = system.cleanse_path(os.path.join(system.get_repo_root_dir(), test_notebook_path,
                                                           test_notebook_file))
scheduled_file_filename: str = Path(notebook_file_scheduled).name
scheduled_file_folder: Path = Path(notebook_file_scheduled).parent


def setup_module():
    # assume all the calls return successfully
    execution_notebook = system.cleanse_path(os.path.join(system.get_repo_root_dir(), execution_notebook_file))
    _jobs_common.get_execution_notebook = mock.Mock(return_value=execution_notebook)

    setup_run_in_executor()


def teardown_module():
    # reset values for other tests
    cleanup()


@pytest.mark.unit
def test_get_notebook_file_scheduled():
    assert _execute.get_notebook_file_scheduled() == notebook_file_scheduled


@pytest.mark.unit
def test_get_label():
    assert _execute.get_label() == label


@pytest.mark.unit
def test_get_index():
    assert _execute.get_index() == test_sched_index


@pytest.mark.unit
def test_get_label():
    assert _execute.get_job_key() == job_key


@pytest.mark.unit
def test_job_result_filename():
    _job_result_filename = _execute._compose_filename(test_sched_index, label, scheduled_file_filename,
                                                      scheduled_file_folder)

    expected_filename = os.path.join(system.get_repo_root_dir(), test_notebook_path, _jobs_common.get_results_folder(),
                                     f'spy.pull.executor.{test_sched_index}.{label}.html')
    assert system.cleanse_path(_job_result_filename) == system.cleanse_path(expected_filename)


def setup_run_in_executor():
    os.environ['SEEQ_SDL_FILE_PATH'] = notebook_file_scheduled
    os.environ['SEEQ_SDL_LABEL'] = label
    os.environ['SEEQ_SDL_SCHEDULE_INDEX'] = test_sched_index
    os.environ['SEEQ_SDL_JOB_KEY'] = job_key


def cleanup():
    del os.environ['SEEQ_SDL_FILE_PATH']
    del os.environ['SEEQ_SDL_LABEL']
    del os.environ['SEEQ_SDL_SCHEDULE_INDEX']
    del os.environ['SEEQ_SDL_JOB_KEY']
