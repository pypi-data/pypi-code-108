"""
    pytest config for sphinxcontrib/constdata/tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2017 by Documatt Inc. <documatt@documatt.com>
    :license: BSD, see LICENSE for details.
"""
import sqlite3
from pathlib import Path
from typing import Union

import pytest
from sphinx.testing.path import path

# Needs Sphinx pytest fixtures
pytest_plugins = "sphinx.testing.fixtures"

# Exclude 'roots' dirs for pytest test collector
collect_ignore = ["roots"]


# Override fixture that says where is root of test Sphinx projects
@pytest.fixture(scope="session")
def rootdir():
    return path(__file__).parent.abspath() / "roots"


@pytest.fixture(scope="function")
def memory_sqlite_con():
    """
    Provide in-memory Sqlite connection and closes it after the test function.
    """
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    yield con
    con.close()


@pytest.fixture(scope="function")
def memory_sqlite_book_con(memory_sqlite_con):
    sql = """
        create table book
        (
            id text primary key not null,
            name text
        );
        insert into book (id, name) VALUES ('foo', 'Foo Book');
        insert into book (id, name) VALUES ('bar', 'Bar Book');
        """
    memory_sqlite_con.executescript(sql)
    return memory_sqlite_con


# @pytest.fixture
# def copy_sample_csv(rootdir, request):
#     """Copies SAMPLE_CSV_FOLDERNAME at this module level under "_const" within test Sphinx project (the default value of const_root setting). I.e., in test Sphinx project conf.py you don't have to specify ``const_root``."""
#     src = str(Path(__file__).parent / SAMPLE_CSV_FOLDERNAME)
#     test_project_name = "test-" + request.node.get_closest_marker("sphinx").kwargs["testroot"]
#     dst = str(Path(rootdir) / test_project_name / CONFIG_ROOT_DEFAULT)
#
#     # shutil.copytree(src, dst) in < Python 3.8 miss "dirs_exist_ok" param
#     # dist_utils' copy_tree() can handle existing dirs
#     copy_tree(src, dst)


def assert_file_contains_fragment(
    file_path: Union[Path, str],
    fragment_path: Union[Path, str],
    how_many_times: int = 1,
):
    """
    Reads file content and asserts it contains fragment.

    Usage::

        assert_file_contains_fragment(
            Path(app.outdir, "index.html"),
            Path(app.srcdir, "expected_link2.html")
        )

    :param file_path: absolute path to the file that should contain a fragment
    :param fragment_path: absolute path to a fragment
    :param how_many_times: by default, exactly one occurence is expected
    """
    content = Path(file_path).read_text(encoding="utf8")
    fragment = Path(fragment_path).read_text(encoding="utf8")

    assert content.count(fragment) == how_many_times
