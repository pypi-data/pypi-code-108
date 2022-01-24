from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sphinx.application import Sphinx

from sphinxcontrib.constdata import CONFIG_FILES, CONFIG_ROOT, CONFIG_TEMPLATES_DEFAULT
from sphinxcontrib.constdata.settings import (
    _CONN_ATTR,
    CONFIG_ID_COL_NAME,
    CONFIG_TEMPLATES_LABEL,
    Settings,
)
from sphinxcontrib.constdata.utils import ConstdataError


class TestRoot:
    def test_root_not_set(self):
        """Not set root causes ValueError."""
        sphinx_env_mock = MagicMock()
        setattr(sphinx_env_mock.config, CONFIG_ROOT, None)

        with pytest.raises(ConstdataError):
            Settings(sphinx_env_mock).get_root()

    def test_root_set(self):
        """Correct value and type of (a Path) get_root()."""
        sphinx_env_mock = MagicMock()
        setattr(sphinx_env_mock.config, CONFIG_ROOT, "_foo")
        setattr(sphinx_env_mock.app, "confdir", "/path/to/project")

        assert Path("/path/to/project/_foo") == Settings(sphinx_env_mock).get_root()


class TestLabelTemplate:
    def test_label_default_settings(self):
        """Default settings"""
        sphinx_env_mock = MagicMock()
        setattr(sphinx_env_mock.config, CONFIG_FILES, CONFIG_TEMPLATES_DEFAULT)

        with pytest.raises(ConstdataError):
            Settings(sphinx_env_mock).get_label_template("foo.csv")

    def test_label_no_templates(self):
        """No "constdata_files" option"""
        sphinx_env_mock = MagicMock()
        setattr(sphinx_env_mock.config, CONFIG_FILES, None)

        with pytest.raises(ConstdataError):
            Settings(sphinx_env_mock).get_label_template("foo.csv")

    def test_label_empty_templates(self):
        """Empty "constdata_files" option"""
        sphinx_env_mock = MagicMock()
        setattr(sphinx_env_mock.config, CONFIG_FILES, {})

        with pytest.raises(ConstdataError):
            Settings(sphinx_env_mock).get_label_template("foo.csv")

    def test_label_no_filename(self):
        """Option "constdata_files" defined, but not for requested file"""
        sphinx_env_mock = MagicMock()
        setattr(sphinx_env_mock.config, CONFIG_FILES, {"bar.csv": {}})

        with pytest.raises(ConstdataError):
            Settings(sphinx_env_mock).get_label_template("foo.csv")

    def test_label(self):
        expected_template = ":menuselection:`{col_name}`"

        sphinx_env_mock = MagicMock()
        setattr(
            sphinx_env_mock.config,
            CONFIG_FILES,
            {"foo.csv": {CONFIG_TEMPLATES_LABEL: expected_template}},
        )
        template = Settings(sphinx_env_mock).get_label_template("foo.csv")
        assert expected_template == template


@pytest.mark.sphinx("html", testroot="empty")
def test_cachedb_conn_closed(monkeypatch, app: Sphinx):
    """Sqlite's Connection.close() has been called after the build"""
    mock_conn = MagicMock()
    monkeypatch.setattr(app, _CONN_ATTR, mock_conn)

    app.build()

    mock_conn.close.assert_called()


def test_get_id_col_name():
    mock_sphinx_env = MagicMock()
    setattr(
        mock_sphinx_env.config, CONFIG_FILES, {"foo.csv": {CONFIG_ID_COL_NAME: "bar"}}
    )
    assert "bar" == Settings(mock_sphinx_env).get_id_col_name("foo.csv")
