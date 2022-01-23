"""
Tests of the potluck_eval script.

test_eval.py
"""

import os
import json
import pathlib
import subprocess

import pytest
import importlib_resources

from .. import render
from .._version import __version__ as potluck_version

# Where to import potluck from so that we're testing the same potluck...
# (Note: potluck_eval script is just what's installed...)
IMPORT_FROM = str(pathlib.Path(__file__).parent.parent.parent)

# Expected strings in rubrics
# TODO: more detailed rubric expectations
RUBRIC_EXPECTS = {
    "debugTest": [ "<title>debugTest Rubric</title>" ],
    "interactiveTest": [ "<title>interactiveTest Rubric</title>" ],
    "sceneTest": [ "<title>sceneTest Rubric</title>" ],
    "functionsTest": [
        "<title>functionsTest Rubric</title>",
        "<h1>Rubric for functionsTest</h1>",
        "All functions are documented",
        "Define <code>indentMessage</code>",
        (
            "The <code>polygon</code> function must maintain"
            " invariants for the <code>position</code> and"
            " <code>heading</code> values"
        ),
        "<code>ellipseArea</code> must return the correct result",
    ],
    "freedomTest": [ "<title>freedomTest Rubric</title>" ],
    "snippetsTest": [
        "<title>snippetsTest Rubric</title>",
        "<h1>Rubric for snippetsTest</h1>",
        "Product Requirements",
        "Core goals",
        "processData",
        "must return the correct result",
        "Behavior Requirements",
        "Extra goals",
        "process.py",
        "must exhibit the correct behavior"
    ],
    "filesTest": [ "<title>filesTest Rubric</title>" ],
    "varsTest": [ "<title>varsTest Rubric</title>" ],
}

# Expectations about reports
REPORT_EXPECTS = {
    "functionsTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    },
    "debugTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "incomplete" },
    },
    "sceneTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    },
    "interactiveTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    },
    "freedomTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    },
    "snippetsTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "incomplete" },
    },
    "filesTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "incomplete" },
    },
    "varsTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    }
}

# Expectations about validation reports
VALIDATION_EXPECTS = {
    "functionsTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    },
    "synthTest": {
        "perfect": { "evaluation": "excellent" },
        "imperfect": { "evaluation": "partially complete" },
    }
}

# TODO: Expectations for instructions and for snippets!


@pytest.fixture(
    params=[
        "functionsTest",
        "debugTest",
        "interactiveTest",
        "sceneTest",
        "freedomTest",
        "snippetsTest",
        "filesTest",
        "varsTest",
    ]
)
def taskid(request):
    """
    Parameterized fixture that provides a task ID string.
    """
    return request.param


@pytest.fixture(params=["perfect", "imperfect"])
def username(request):
    """
    Parameterized fixture that provides a username string.
    """
    return request.param


@pytest.fixture
def in_evaldir():
    """
    Sets the current directory to the testarea evaluation directory.
    Yields that directory as a pathlib.Path.
    """
    with importlib_resources.path("potluck", "testarea") as testarea:
        evaldir = testarea / "test_course" / "fall2021"
        old_dir = os.getcwd()
        os.chdir(evaldir)
        yield evaldir
        os.chdir(old_dir)


@pytest.fixture
def logfile():
    """
    A fixture that yields a log filename and removes that file after the
    test is complete. The test must create the file.
    """
    result = pathlib.Path("logs", "pytest.log")
    yield result
    try:
        result.unlink()
    except Exception:
        pass


@pytest.fixture
def rubricfile(taskid):
    """
    A fixture that yields a rubric filename and removes that file after
    the test is complete. The test must create the file.
    """
    result = pathlib.Path("rubrics", f"rubric-{taskid}.html")
    yield result
    try:
        result.unlink()
    except Exception:
        pass


@pytest.fixture
def reportfiles(taskid, username):
    """
    A fixture that yields a pair of report JSON and HTML filenames and
    removes those files after the test is complete. The test must create
    the file.
    """
    r_json = pathlib.Path("reports", f"pytest-{username}-{taskid}.json")
    r_html = r_json.with_suffix(".html")
    yield (r_json, r_html)
    try:
        r_json.unlink()
    except Exception:
        pass
    try:
        r_html.unlink()
    except Exception:
        pass


@pytest.fixture
def validationreportfiles(taskid, username):
    """
    A fixture that yields a pair of validation report JSON and HTML
    filenames and removes those files after the test is complete. The
    test must create the file.
    """
    r_json = pathlib.Path(
        "reports",
        f"pytest-{username}-{taskid}-validation.json"
    )
    r_html = r_json.with_suffix(".html")
    yield (r_json, r_html)
    try:
        r_json.unlink()
    except Exception:
        pass
    try:
        r_html.unlink()
    except Exception:
        pass


def check_log_is_clean(logfile):
    """
    Helper that checks for a clean log file.
    """
    assert logfile.is_file()
    with logfile.open() as fin:
        log = fin.read()
    assert log.splitlines()[0] == (
        f"This is potluck version {potluck_version}"
    )
    assert render.ERROR_MSG not in log
    assert render.DONE_MSG in log


def test_rubric_creation(in_evaldir, taskid, logfile, rubricfile):
    """
    Tests rubric creation for a particular task.
    """
    assert not logfile.exists()
    assert not rubricfile.exists()
    result = subprocess.run(
        [
            "potluck_eval",
            "--import-from", IMPORT_FROM,
            "-t", taskid,
            "--rubric",
            "--log", str(logfile)
        ]
    )
    assert result.returncode == 0
    check_log_is_clean(logfile)

    assert rubricfile.is_file()

    # Look for expected strings in created rubric
    if taskid in RUBRIC_EXPECTS:
        with rubricfile.open() as fin:
            contents = fin.read()

        for expected in RUBRIC_EXPECTS[taskid]:
            assert expected in contents


def test_evaluation(in_evaldir, taskid, username, reportfiles, logfile):
    """
    Tests the potluck_eval script for a certain task/user example.
    """
    assert not logfile.exists()
    r_json, r_html = reportfiles
    assert not r_json.exists()
    assert not r_html.exists()
    result = subprocess.run(
        [
            "potluck_eval",
            "--import-from", IMPORT_FROM,
            "-t", taskid,
            "-u", username,
            "--log", str(logfile),
            "--outfile", str(r_json)
        ]
    )
    assert result.returncode == 0
    check_log_is_clean(logfile)

    assert r_json.is_file()
    assert r_html.is_file()

    with r_json.open() as fin:
        report = json.load(fin)

    if taskid in REPORT_EXPECTS:
        if username in REPORT_EXPECTS[taskid]:
            expectations = REPORT_EXPECTS[taskid][username]
            for key in expectations:
                assert key in report
                assert report[key] == expectations[key]


def test_specifications_checks(in_evaldir, taskid, logfile):
    """
    A meta-meta test that runs the build-in specifications tests on the
    example specifications to make sure they test clean.
    """
    assert not logfile.exists()
    result = subprocess.run(
        [
            "potluck_eval",
            "--import-from", IMPORT_FROM,
            "-t", taskid,
            "--check",
            "--log", str(logfile)
        ]
    )
    assert result.returncode == 0
    check_log_is_clean(logfile)

    # Look for expected strings in the log file
    with logfile.open() as fin:
        log = fin.read()

    assert "All examples met expectations." in log
    assert "Check of solution code passed." in log


def test_validation(
    in_evaldir,
    taskid,
    username,
    validationreportfiles,
    logfile
):
    """
    Tests the potluck_eval script validation mode for a certain
    task/user example.
    """
    # Skip this test if there aren't any expectations for it: not all
    # tasks can be validated (they may not define any validation goals).
    if taskid not in VALIDATION_EXPECTS:
        return
    assert not logfile.exists()
    r_json, r_html = validationreportfiles
    assert not r_json.exists()
    assert not r_html.exists()
    result = subprocess.run(
        [
            "potluck_eval",
            "--validate",
            "--import-from", IMPORT_FROM,
            "-t", taskid,
            "-u", username,
            "--log", str(logfile),
            "--outfile", str(r_json)
        ]
    )
    assert result.returncode == 0
    check_log_is_clean(logfile)

    assert r_json.is_file()
    assert r_html.is_file()

    with r_json.open() as fin:
        report = json.load(fin)

    if taskid in VALIDATION_EXPECTS:
        if username in VALIDATION_EXPECTS[taskid]:
            expectations = VALIDATION_EXPECTS[taskid][username]
            for key in expectations:
                assert key in report
                assert report[key] == expectations[key]
