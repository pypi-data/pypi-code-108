from io import StringIO
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from tests.conftest import assert_file_contains_fragment


@pytest.mark.sphinx("html", testroot="link-role")
def test_links(app: Sphinx, status: StringIO, warning: StringIO):
    app.build()

    # index.rst

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"), Path(app.srcdir, "expected_link1.html")
    )
    assert_file_contains_fragment(
        Path(app.outdir, "index.html"), Path(app.srcdir, "expected_link2.html")
    )

    # second.rst

    assert_file_contains_fragment(
        Path(app.outdir, "second.html"), Path(app.srcdir, "expected_link3.html")
    )
    assert_file_contains_fragment(
        Path(app.outdir, "second.html"), Path(app.srcdir, "expected_link4.html")
    )

    # third.rst

    warning_str = warning.getvalue()

    assert (
        "third.rst:6: WARNING: Missing :constdata:link: template for 'menu.json'."
        in warning_str
    )

    assert (
        "third.rst:10: WARNING: Reference to non-existing row with ID 'FileSaveAs'. If you didn't make a typo, it usually means 'menu.json' showing 'FileSaveAs' is not anywhere listed with :constdata:table:: directive."
        in warning_str
    )

    assert_file_contains_fragment(
        Path(app.outdir, "third.html"), Path(app.srcdir, "expected_link5.html")
    )
    assert_file_contains_fragment(
        Path(app.outdir, "third.html"), Path(app.srcdir, "expected_link6.html")
    )

    # fourth.rst

    assert_file_contains_fragment(
        Path(app.outdir, "fourth.html"), Path(app.srcdir, "expected_link7.html")
    )
    assert_file_contains_fragment(
        Path(app.outdir, "fourth.html"), Path(app.srcdir, "expected_link8.html")
    )
    assert_file_contains_fragment(
        Path(app.outdir, "fourth.html"), Path(app.srcdir, "expected_link9.html")
    )
    assert_file_contains_fragment(
        Path(app.outdir, "fourth.html"), Path(app.srcdir, "expected_link10.html")
    )
