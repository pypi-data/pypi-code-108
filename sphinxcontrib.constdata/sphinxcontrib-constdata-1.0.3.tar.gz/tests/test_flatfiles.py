import os
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sphinx.application import Sphinx

from sphinxcontrib.constdata.flatfiles import (
    CACHEDB_FILENAME,
    AbstractFileToDb,
    AutodetectFileToDb,
    CsvFileToDb,
    FlatfileReader,
    JsonFileToDb,
    SqlCommand,
    YamlFileToDb,
)
from sphinxcontrib.constdata.settings import Settings
from sphinxcontrib.constdata.utils import ConstdataError

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

SAMPLES_DIR = os.path.join(dir_path, "samples")
"""Absolute path to a folder with sample flatfiles"""


class TestAbstractFileToDb:
    class MockFileToDb(AbstractFileToDb):
        def run(self):
            pass

    def test_convert_str_to_path(self):
        """Casts path passed as str to Path"""
        fftd = self.MockFileToDb(MagicMock(), "foo.csv")
        assert issubclass(type(fftd.rel_path), Path)

    def test_header_and_row_number_of_field_mismatch(self):
        """Raises exception of some row has different number than in header"""
        with pytest.raises(AssertionError):
            fftd = self.MockFileToDb(MagicMock(), "foo.csv")
            # third row contains only one field, but the header has two
            corrupted_file = [["h1", "h2"], ["v1.1", "v1.2"], ["v2.1"]]
            fftd.save_rows_to_db(corrupted_file)

    def test_table_name(self):
        """Table name is correctly based on a filename"""
        fftd = self.MockFileToDb(MagicMock(), "path/to/foo.csv")
        assert fftd.table_name == "path/to/foo.csv"

    def test_list_of_dicts_to_list_of_lists(self):
        fftd = self.MockFileToDb(MagicMock(), "foo.csv")

        original = [
            {"id": "FileNew", "Path": "File --> Create and &open new file"},
            {"id": "FileSaveAs", "Path": "File --> Save As..."},
        ]
        modified = [
            ["id", "Path"],
            ["FileNew", "File --> Create and &open new file"],
            ["FileSaveAs", "File --> Save As..."],
        ]

        assert fftd._list_of_dicts_to_list_of_lists(original) == modified


@pytest.mark.sphinx("html", testroot="empty")
class TestFileToDb:
    @pytest.mark.parametrize(
        "clazz, rel_path",
        (
            (CsvFileToDb, "conf.csv"),
            (JsonFileToDb, "conf.json"),
            (YamlFileToDb, "conf.yaml"),
        ),
    )
    def test_implementations(self, clazz, rel_path, app: Sphinx):
        """*FileToDb implementations writes specified file to cachedb"""
        mock_settings = Settings(app.env)
        clazz(mock_settings, rel_path).run()

        suffix = Path(rel_path).suffix
        self.assert_conf_file_cached(mock_settings, suffix)

    @pytest.mark.parametrize("rel_path", ("conf.csv", "conf.json", "conf.yaml"))
    def test_autodetection(self, rel_path, app: Sphinx):
        """AutodetectFileToDb writes specified files to cachedb"""
        mock_settings = Settings(app.env)

        AutodetectFileToDb(mock_settings, rel_path).run()

        suffix = Path(rel_path).suffix
        self.assert_conf_file_cached(mock_settings, suffix)

    def test_autodetection_unknown_extension(self, app: Sphinx):
        """AutodetectFileToDb crashes on unknown extension"""
        mock_settings = Settings(app.env)

        with pytest.raises(ValueError):
            AutodetectFileToDb(mock_settings, "conf.unknown_extension").run()

    def assert_conf_file_cached(self, settings: Settings, suffix):
        """conf.* files are really cached as tables with proper content

        :param extension: file extension including '.' ('.json', ...) used to construct table name"""
        con = settings.get_cachedb_conn()
        rows = con.execute(f'select * from "conf{suffix}"').fetchall()

        # total number of rows
        assert len(rows) == 2

        # column names
        first_row = rows[0]
        assert first_row.keys() == ["Variable", "Category", "Description"]

        # 1st row values
        assert first_row[0] == "author"
        assert first_row[1] == "Project information"
        assert (
            first_row[2]
            == """The author name(s) of the document.  The default value is ``'unknown'``."""
        )

        # 2nd row values
        second_row = rows[1]
        assert second_row[0] == "project_copyright"
        assert second_row[1] == "Project information"
        assert (
            second_row[2]
            == """An alias of ``copyright``.

.. versionadded:: 3.5"""
        )


class TestSqlCommand:
    def test_make_create_table_sql(self, memory_sqlite_con):
        sql = SqlCommand(memory_sqlite_con).make_create_table_sql(
            "foo", ["col1", "col2", "col3"]
        )
        assert (
            sql
            == 'create table "foo" ("col1" text primary key not null, "col2" text, "col3" text)'
        )

    def test_make_insert_sql(self, memory_sqlite_con):
        sql = SqlCommand(memory_sqlite_con).make_insert_sql(
            "foo", {"col1": "val1", "col2": "val2", "col3": "val3"}
        )
        assert (
            sql
            == 'insert into "foo" ("col1", "col2", "col3") values (:col1, :col2, :col3)'
        )

    class TestSelectOne:
        def test_ok(self, memory_sqlite_book_con):
            book = SqlCommand(memory_sqlite_book_con).select_one(
                "select * from book where id = :id", {"id": "foo"}
            )

            assert book == {"id": "foo", "name": "Foo Book"}

        def test_return_none_if_nothing_found(self, memory_sqlite_book_con):
            book = SqlCommand(memory_sqlite_book_con).select_one(
                "select * from book where id = :id", {"id": "nonexisting"}
            )

            assert book == {}

        def test_crash_for_multiple_rows(self, memory_sqlite_book_con):
            with pytest.raises(ValueError):
                SqlCommand(memory_sqlite_book_con).select_one("select * from book")

        def test_crash_for_invalid_sql_syntax(self, memory_sqlite_book_con):
            with pytest.raises(ConstdataError):
                SqlCommand(memory_sqlite_book_con).select_one("select where from foo")

    class TestSelect:
        def test(self, memory_sqlite_book_con):
            actual = SqlCommand(memory_sqlite_book_con).select("select * from book")
            expected = [
                {"id": "foo", "name": "Foo Book"},
                {"id": "bar", "name": "Bar Book"},
            ]

            assert 2 == len(actual)
            assert expected == actual

        def test_returns_none_if_nothing_found(self, memory_sqlite_book_con):
            actual = SqlCommand(memory_sqlite_book_con).select(
                "select * from book where id = :id", {"id": "nonexisting"}
            )

            assert [] == actual

        def test_crash_for_invalid_sql_syntax(self, memory_sqlite_book_con):
            with pytest.raises(ConstdataError):
                SqlCommand(memory_sqlite_book_con).select("select where from foo")


@pytest.mark.sphinx("html", testroot="empty")
class TestFlatfileReader:
    @pytest.fixture
    def flatfile(self, app: Sphinx):
        """Fixture injecting Flatfile pointing to ``menu.csv`` sample file."""
        mock_settings = Settings(app.env)
        rel_path = "menu.csv"
        # upload test sample file menu.csv to temp cachedb
        AutodetectFileToDb(mock_settings, rel_path).run()

        return FlatfileReader(mock_settings, rel_path)

    def test_get_row_by_id(self, flatfile):
        row = flatfile.get_row_by_id("FileNew")

        assert row == {"id": "FileNew", "Path": "File --> Create and &open new file"}

    def test_iterate_rows_all(self, flatfile):
        """iterate_rows() returns all rows if no query is passed"""
        rows = flatfile.iterate_rows()

        assert rows == [
            {"id": "FileNew", "Path": "File --> Create and &open new file"},
            {"id": "FileSaveAs", "Path": "File --> Save As..."},
        ]

    def test_iterate_rows_query(self, flatfile):
        """iterate_rows() returns rows matching passed query"""
        rows = flatfile.iterate_rows(
            """select * from "menu.csv" where id = 'FileNew\'"""
        )

        assert rows == [{"id": "FileNew", "Path": "File --> Create and &open new file"}]

    def test_iterate_rows_invalid_query(self, flatfile):
        """iterate_rows() returns raise ConstdataError on underlying SQL error"""
        with pytest.raises(ConstdataError):
            rows = flatfile.iterate_rows('select * from "nonexisting.csv"')

    def test_iterate_rows_no_result(self, flatfile):
        """iterate_rows() returns empty [] on to result to a query"""
        rows = flatfile.iterate_rows(
            """select * from "menu.csv" where id = 'nonexisting\'"""
        )
        assert rows == []


@pytest.mark.sphinx("html", testroot="lot-of-flatfiles")
def test_cache_flatfiles_on_start(app: Sphinx):
    app.build()

    # cannot
    #   sql_command = SqlCommand(Settings(app.env).get_cachedb_conn())
    # because it returns closed connection (was closed at the end of build)
    cachedb_path = os.path.join(app.outdir, CACHEDB_FILENAME)
    sql_command = SqlCommand(sqlite3.connect(cachedb_path))

    sql = "select name from sqlite_master where type = 'table'"
    tables = sql_command.select(sql)

    assert tables == [
        {"name": "menu.csv"},
        {"name": "subfolder/conf.csv"},
        {"name": "subfolder/conf.json"},
        {"name": "subfolder/conf.yaml"},
    ]
    assert "subfolder/conf.unknown_extension" not in tables
