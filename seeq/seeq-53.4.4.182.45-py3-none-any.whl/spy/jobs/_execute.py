import os
from pathlib import Path
from typing import Optional, Union

import nbconvert
import nbformat
from nbformat import NotebookNode

from seeq.spy.jobs import _common as _jobs_common

notebook_file_merged: Optional[str] = None
log_message_base: Optional[str] = None


def execute() -> None:
    """
    Execute a notebook. (Internal Seeq function: Not intended for end-users)
    """
    if not _jobs_common.running_in_executor():
        error_message = 'Execution of notebooks is not supported through SPy interface.'
        _get_logger().error(_log_message(error_message))
        return

    global notebook_file_merged

    # Executor container will have the notebook and job info needed to execute
    notebook_file_scheduled = get_notebook_file_scheduled()
    label = get_label()
    index = get_index()
    job_key = get_job_key()

    # Setup a base log message depending if coming from executor container or SPy user
    _set_log_message_base(notebook_file_scheduled, job_key)

    # Abort if scheduled notebook does not exist
    if not Path(notebook_file_scheduled).exists():
        # ToDo CRAB-25884 unschedule the notebook if no longer exists and notify the creator
        error_message = log_message_base + 'not found, aborting.'
        _get_logger().error(_log_message(error_message))
        return
    try:
        scheduled_file_filename: str = Path(notebook_file_scheduled).name
        scheduled_file_folder: Path = Path(notebook_file_scheduled).parent

        # notebook_file_merged is our new scheduled notebook with login cell
        notebook_file_merged = _compose_filename(index, label, scheduled_file_filename, scheduled_file_folder,
                                                 extension='.ipynb', result=False)
        # This is our resulting html file after execution
        _job_result_filename = _compose_filename(index, label, scheduled_file_filename, scheduled_file_folder)

        # Create the new scheduled notebook with login cell
        _merge_notebook(notebook_file_scheduled)

        # Execute the new scheduled notebook with login cell
        _execute(scheduled_file_folder)

        # Convert to html and save
        _convert(_job_result_filename)

        # Log success for executor
        _get_logger().info(_log_message('succeeded'))
    except BaseException as e:
        _get_logger().error(_log_message(e), exc_info=e)
    finally:
        # Cleanup
        _delete_notebook_file_merged()


def _merge_notebook(notebook_file_scheduled: Union[str, Path]) -> None:
    global notebook_file_merged

    try:
        # Open the notebook that has been scheduled for execution
        with open(notebook_file_scheduled) as f_notebook_scheduled:
            nb_notebook_scheduled = nbformat.read(f_notebook_scheduled, nbformat.NO_CONVERT)

        # Open the dummy notebook with spy.login cell
        with open(_jobs_common.get_execution_notebook()) as f_notebook_execution:
            nb_notebook_execution = nbformat.read(f_notebook_execution, nbformat.NO_CONVERT)

        # Create new notebook dynamically that includes login cell first
        nb_notebook_merged = NotebookNode(nb_notebook_execution.copy())

        # Add in cells from scheduled notebook
        nb_notebook_merged['cells'].extend(nb_notebook_scheduled.cells.copy())

        # Write out the new joined notebook as hidden notebook with the same name as scheduled notebook
        with open(notebook_file_merged, 'w') as f_notebook_merged:
            nbformat.write(nb_notebook_merged, f_notebook_merged)

        # Log to executor
        _get_logger().debug(_log_message('successfully merged execution notebook with scheduled notebook'))
    except BaseException as e:
        _get_logger().error(_log_message(e), exc_info=e)
        raise e


# noinspection PyBroadException
def _execute(target_file_folder: Union[str, Path]) -> NotebookNode:
    global notebook_file_merged

    try:
        # Open the notebook for execution
        with open(notebook_file_merged, 'r+') as f_notebook_merged:
            nb_notebook_merged = nbformat.read(f_notebook_merged, nbformat.NO_CONVERT)

        # Configure the execute processor to allow errors and the output path
        proc = nbconvert.preprocessors.ExecutePreprocessor(timeout=_jobs_common.get_cell_execution_timeout(),
                                                           allow_errors=True)
        proc.preprocess(nb_notebook_merged, {'metadata': {'path': target_file_folder}})

        # Log to executor
        _get_logger().debug(_log_message('successfully executed merged notebook'))

        # Remove login cell from notebook
        del nb_notebook_merged['cells'][0]

        # Decrement the "execution_count" by 1 to correct notebook cell numbering
        # "execution_count" can have 'None' as value so just pass on any exception to continue
        for cell in nb_notebook_merged['cells']:
            try:
                if 'execution_count' in cell:
                    execution_count = int(cell['execution_count'])
                    execution_count -= 1
                    cell['execution_count'] = execution_count
            except BaseException:
                pass

            if 'outputs' in cell:
                for output in cell['outputs']:
                    try:
                        if 'execution_count' in output:
                            execution_count = int(output['execution_count'])
                            execution_count -= 1
                            output['execution_count'] = execution_count
                    except BaseException:
                        pass

        # Write the scheduled notebook
        with open(notebook_file_merged, 'w') as f_notebook_merged:
            nbformat.write(nb_notebook_merged, f_notebook_merged)

        # Log to executor
        _get_logger().debug(_log_message('successfully edited merged notebook'))

        # The executed notebook will be returned if spy.jobs.execute was called by a user
        return nb_notebook_merged
    except BaseException as e:
        _get_logger().error(_log_message(e), exc_info=e)
        raise e


# noinspection DuplicatedCode
def _convert(job_result_file: str) -> None:
    global notebook_file_merged

    try:
        # Open the modified notebook that has been scheduled for execution
        with open(notebook_file_merged) as f_notebook_merged:
            nb_notebook_merged = nbformat.read(f_notebook_merged, nbformat.NO_CONVERT)

        # Configure the HTML exporter and export
        html_exporter = nbconvert.HTMLExporter()
        job_result_html, _ = html_exporter.from_notebook_node(nb_notebook_merged)

        # Create parent folder if not existing and write out the exported html to file
        Path(job_result_file).parent.mkdir(parents=True, exist_ok=True)
        with open(job_result_file, 'w') as f_job_result_file:
            f_job_result_file.write(job_result_html)

        # Log to executor
        _get_logger().debug(_log_message('successfully exported merged notebook'))
    except BaseException as e:
        _get_logger().error(_log_message(e), exc_info=e)
        raise e


def _delete_notebook_file_merged():
    # unlink(missing_ok=True) handles if file doesnt exist, but IntelliJ is not recognizing this parameter
    # https://youtrack.jetbrains.com/issue/PY-38852
    if Path(notebook_file_merged).exists():
        Path(notebook_file_merged).unlink()


def _compose_filename(index, label, scheduled_file_filename, scheduled_file_folder, extension='.html', result=True):
    folder: Union[str, Path] = Path(scheduled_file_folder, _jobs_common.get_results_folder()) if result else \
        scheduled_file_folder
    filename_no_ext: str = Path(scheduled_file_filename).stem

    # Build up the job result html file name
    folder = str(folder)
    executor = ".executor"
    index = '.' + index if len(index) > 0 else ''
    label = '.' + label if len(label) > 0 else ''

    result_filename = f'{folder}/{filename_no_ext}{executor}{index}{label}{extension}'
    return result_filename


def _get_logger():
    return _jobs_common.get_executor_logger()


def _set_log_message_base(notebook_file_scheduled, job_key: str) -> None:
    global log_message_base

    log_message_base = f'Notebook {notebook_file_scheduled} with jobKey {job_key} '


def _log_message(message: Union[str, BaseException]) -> str:
    return log_message_base + str(message)


def get_notebook_file_scheduled():
    return os.environ.get('SEEQ_SDL_FILE_PATH', '')


def get_label():
    return os.environ.get('SEEQ_SDL_LABEL', '')


def get_index():
    return os.environ.get('SEEQ_SDL_SCHEDULE_INDEX', '')


def get_job_key():
    return os.environ.get('SEEQ_SDL_JOB_KEY', '')
