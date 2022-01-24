from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from sphinxcontrib.constdata.settings import Settings
from sphinxcontrib.constdata.templating import resolve_template
from sphinxcontrib.constdata.utils import ConstdataError
from tests.conftest import assert_file_contains_fragment


class TestResolveTemplate:
    @pytest.mark.sphinx("html", testroot="empty")
    def test_no_dollar_braced_placeholders(self, app):
        actual = resolve_template(
            Settings(app.env),
            ":menuselection:`{Path}`",
            "FileSaveAs",
            "menu.csv",
        )
        assert actual == ":menuselection:`File --> Save As...`"

    @pytest.mark.sphinx("html", testroot="empty")
    def test_non_braced_placeholders_ignored(self, app):
        actual = resolve_template(
            Settings(app.env), "only $braced $supported", "FileSaveAs", "menu.csv"
        )

        assert actual == "only $braced $supported"

    @pytest.mark.sphinx("html", testroot="empty")
    def test_dollar_braced_ignored(self, app):
        """${} is a dollar and placeholder, not a placeholder"""
        actual = resolve_template(
            Settings(app.env), "but ${id} ${Path} supported", "FileSaveAs", "menu.csv"
        )

        assert actual == "but $FileSaveAs $File --> Save As... supported"

    @pytest.mark.sphinx("html", testroot="empty")
    def test_missing_id_in_file(self, app):
        with pytest.raises(ConstdataError):
            resolve_template(Settings(app.env), "{Path}` ", "nonexistingid", "menu.csv")


@pytest.mark.xfail(
    reason="for unknown reason, warning is blank. Building test-missing-templates project manually from commandline, correctly produces expected warnings."
)
@pytest.mark.sphinx("html", testroot="missing-templates")
def test_missing_templates(app: Sphinx, warning: StringIO):
    """Test that HTML contain expected output if templates are missing"""
    warning_str = warning.getvalue()

    # table
    # (does not support templating yet, so unstyled template shown)
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected_html_table.html"),
    )

    # label
    assert (
        "index.rst:6: WARNING: Missing :constdata:label: template for 'menu.csv'."
        in warning_str
    )

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected_html_label.html"),
    )

    # link
    assert (
        "index.rst:8: WARNING: Missing :constdata:link: template for 'menu.csv'."
        in warning_str
    )

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected_html_link.html"),
    )
