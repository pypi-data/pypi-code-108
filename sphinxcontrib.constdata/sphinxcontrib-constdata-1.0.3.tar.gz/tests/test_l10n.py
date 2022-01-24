import re
from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.testing.path import path

from tests.conftest import assert_file_contains_fragment


@pytest.mark.xfail(reason="Locally passes, on GitLab CI failed with 'assert 0 == 1'")
@pytest.mark.sphinx("gettext", testroot="l10n")
def test_pot_generation(app: Sphinx, status, warning):
    """Properly extract translatable from all flatfiles messages to .pot, not only those used in documents"""
    app.build()

    assert_file_contains_fragment(
        Path(app.outdir, "constdata.pot"),
        Path(app.srcdir, "expected_pot_fragment.pot"),
    )


@pytest.mark.xfail(
    reason="""Sometimes causes
            sphinx.errors.SphinxError: This environment is incompatible with the selected builder, please choose another doctree directory.
        Sometimes not. Asked in sphinx-dev
        https://groups.google.com/u/1/g/sphinx-dev/c/ybAgTEl4GyU, but still not sure how to fix it.
    """
)
@pytest.mark.sphinx("html", testroot="l10n", confoverrides={"language": "cs"})
def test_translation(app: Sphinx, status, warning):
    """Translation works. Test that translatable CSV/JSON/YAML table/link/label produce the same output."""
    app.build()

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"), Path(app.srcdir, "expected_html_tables.html")
    )

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected_html_links.html"),
    )

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected_html_labels.html"),
    )


@pytest.mark.sphinx(
    "gettext",
    testroot="l10n-separate-layout/source",
    builddir=path("tests/roots/l10n-separate-layout/build/"),
)
def test_separate_layout(app: Sphinx, warning: StringIO, sphinx_test_tempdir):
    """Tests that bug causing 'does not start with' error has been fixed' exception"""
    sphinx_test_tempdir
    app.build()

    warning_str = warning.getvalue()

    # e.g.
    # ValueError: '/Users/libor/git/documatt/sphinxcontrib-constdata/tests/roots/test-l10n-separate-layout/build/gettext/constdata.pot' does not start with '/Users/libor/git/documatt/sphinxcontrib-constdata/tests/roots/test-l10n-separate-layout/source'
    r = r"^ValueError: '.+constdata\.pot' does not start with '.+'$"
    assert not re.match(r, warning_str)
