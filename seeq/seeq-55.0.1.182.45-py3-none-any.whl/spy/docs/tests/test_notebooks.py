"""Smoke test ensuring that example notebooks run without error."""

import os
import pathlib
import re

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

from seeq.base import system
from seeq.spy.tests import test_common

THIS_DIR = pathlib.Path(__file__).absolute().parent
DOCUMENTATION_DIR = THIS_DIR / ".." / "Documentation"


def setup_module():
    test_common.initialize_sessions()


def run_notebook(notebook_name):
    # 7-bit C1 ANSI sequences
    def escape_ansi_control(error):
        ansi_escape = re.compile(r'''
            \x1B    # ESC
            [@-_]   # 7-bit C1 Fe
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        ''', re.VERBOSE)
        sanitized = ""
        for line in error:
            sanitized += ansi_escape.sub('', line) + "\n"
        return sanitized

    path = os.path.normpath(DOCUMENTATION_DIR / notebook_name)
    with open(path) as f:
        nb = nbformat.read(f, as_version=4)

    all_cells = nb['cells']

    for cell_index in range(len(all_cells)):
        # Replace cells that contain set_trace with print
        if 'set_trace()' in all_cells[cell_index]['source']:
            # Convert to dictionary to modify content
            content_to_modify = dict(all_cells[cell_index])
            content_to_modify['source'] = "#print('skip_cell_because_of_set_trace_function')"
            nb['cells'][cell_index] = nbformat.from_dict(content_to_modify)

    proc = ExecutePreprocessor(timeout=1200)
    proc.allow_errors = True
    system.do_with_retry(
        lambda: proc.preprocess(nb, {'metadata': {'path': os.path.dirname(path)}}),
        timeout_sec=1200)

    for cell in nb.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    pytest.fail("\nNotebook '{}':\n{}".format(notebook_name, escape_ansi_control(output.traceback)))


def cleanup_files(files_to_cleanup):
    for file_to_cleanup in files_to_cleanup:
        if os.path.exists(file_to_cleanup):
            if os.path.isfile(file_to_cleanup):
                os.remove(file_to_cleanup)
            else:
                system.removetree(file_to_cleanup)


@pytest.mark.system
def test_run_spy_assets_ipynb():
    run_notebook("spy.assets.ipynb")


@pytest.mark.system
def test_run_spy_push_ipynb():
    run_notebook("spy.push.ipynb")


@pytest.mark.system
def test_run_spy_search_ipynb():
    run_notebook("spy.search.ipynb")
    cleanup_files([DOCUMENTATION_DIR / 'pickled_search.pkl'])


@pytest.mark.system
def test_run_spy_widgets_ipynb():
    run_notebook("spy.widgets.ipynb")


@pytest.mark.system
def test_run_spy_workbooks_ipynb():
    run_notebook("spy.workbooks.ipynb")
    cleanup_files([DOCUMENTATION_DIR / '..' / 'My First Export'])


@pytest.mark.system
def test_run_tutorial_ipynb():
    run_notebook("Tutorial.ipynb")


@pytest.mark.system
def test_run_command_reference_ipynb():
    run_notebook("Command Reference.ipynb")


@pytest.mark.system
def test_run_advance_reports_and_dashboards_ipynb():
    run_notebook("Advanced Reports and Dashboards.ipynb")


@pytest.mark.system
def test_run_cooling_tower_health_ipynb():
    run_notebook(pathlib.Path("Cooling_Tower_Health", "Cooling_Tower_Health.ipynb"))
