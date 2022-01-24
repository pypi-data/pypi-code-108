import copy
from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from sphinxcontrib.constdata import table_directive
from sphinxcontrib.constdata.table_directive import (
    make_csv_table_content,
    translate_table,
)
from sphinxcontrib.constdata.utils import ConstdataError
from tests.conftest import assert_file_contains_fragment


class TestMakeCsvTableContent:
    """make_csv_table_content() tests"""

    @pytest.fixture
    def patch_make_url_safe_target_id(self, monkeypatch):
        # make_csv_table_content() depends on make_url_safe_target_id() from
        # sphinxcontrib.constdata.directives module to generate
        # URL safe target ID. To exclude make_url_safe_target_id() from test of
        # make_csv_table_content(), we will patch it to return predicable string.
        monkeypatch.setattr(
            table_directive,
            "make_url_safe_target_id",
            lambda rel_path, row_id: f"constdata-menu-csv-{row_id}",
        )

    def test_make_csv_table_content(self, patch_make_url_safe_target_id):
        table = [
            {"id": "FileNew", "Path": 'File --> Create and "open" new file'},
            {"id": "FileSaveAs", "Path": "File --> Save As..."},
        ]

        lines = make_csv_table_content("menu.csv", "id", table)
        assert lines == [
            '"id","Path"',
            '".. _constdata-menu-csv-FileNew:\n\nFileNew","File --> Create and ""open"" new file"',
            '".. _constdata-menu-csv-FileSaveAs:\n\nFileSaveAs","File --> Save As..."',
        ]

    def test_make_csv_table_content_no_id_col(self, patch_make_url_safe_target_id):
        """make_csv_table_content() raises ConstdataError if passed file has no passed ID column"""
        table = [
            {"id": "FileNew", "Path": 'File --> Create and "open" new file'},
            {"id": "FileSaveAs", "Path": "File --> Save As..."},
        ]

        with pytest.raises(
            ConstdataError,
            match="Can't list a table because 'menu.csv' has no ID column with name 'nonexisting-id-col'.",
        ):
            make_csv_table_content("menu.csv", "nonexisting-id-col", table)

    def test_make_csv_table_content_doesnt_modify_table(
        self, patch_make_url_safe_target_id
    ):
        """make_csv_table_content() doesn't modify ID columns in passed in table parameter."""
        # There was a bug that adds RST label (``.. _label:``) to row[<id_col_name>]. E.g. ``foo`` became ``.. _foo-label: foo``.
        table = [
            {"id": "FileNew", "Path": 'File --> Create and "open" new file'},
            {"id": "FileSaveAs", "Path": "File --> Save As..."},
        ]
        orig_table = copy.deepcopy(table)
        make_csv_table_content("menu.csv", "id", table)
        assert table == orig_table


def test_translate_table():
    # gettext that puts everything into parenthesis
    gettext = lambda original: f"({original})"

    table = [
        {"id": "FileNew", "Path": 'File --> Create and "open" new file'},
        {"id": "FileSaveAs", "Path": "File --> Save As..."},
    ]

    new_table = translate_table(gettext, table)
    assert new_table == [
        {"(id)": "(FileNew)", "(Path)": '(File --> Create and "open" new file)'},
        {"(id)": "(FileSaveAs)", "(Path)": "(File --> Save As...)"},
    ]

    # original table was not modified
    assert table != new_table


@pytest.mark.sphinx("html", testroot="table-directive")
def test_table_directive(app: Sphinx, status: StringIO, warning: StringIO):
    app.build()
    warning_str = warning.getvalue()

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected1.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected2.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected3.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected4.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected5.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected6.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected7.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected8.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected9.html"),
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected10.html"),
    )

    # renaming and omitting ID column
    assert (
        "index.rst:30: WARNING: Can't list a table because 'menu4.csv' has no ID column with name 'id'."
        in warning_str
    )
    assert (
        "index.rst:40: WARNING: Can't list a table because 'menu6.csv' has no ID column with name 'id'"
        in warning_str
    )

    # Query with no result
    assert "index.rst:71: WARNING: Query returns no rows" in warning_str

    # The same table again
    assert (
        'WARNING: Duplicate explicit target name: "constdata-menu1-csv-filenew".'
        in warning_str
    )
    assert (
        'WARNING: Duplicate explicit target name: "constdata-menu1-csv-filesaveas".'
        in warning_str
    )
