from pathlib import Path

import pytest

from tests.conftest import assert_file_contains_fragment


@pytest.mark.sphinx("html", testroot="label-role")
def test_label_role(app, status, warning):
    app.build()

    assert_file_contains_fragment(
        Path(app.outdir, "index.html"),
        Path(app.srcdir, "expected1.html"),
    )
