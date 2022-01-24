from io import StringIO

import pytest
from sphinx.application import Sphinx


@pytest.mark.sphinx("html", testroot="error-reporting")
def test_error_reporting(app: Sphinx, status, warning: StringIO):
    """Errors are reported in expected way (line number and message)"""
    app.build()

    # convert StringIO to str
    warning_str = warning.getvalue()

    assert (
        "index.rst:7: WARNING: Cache DB error (exception: no such table: nonexisting.csv)"
        in warning_str
    )
    assert (
        "index.rst:9: WARNING: Cache DB error (exception: no such table: nonexisting.csv)"
        in warning_str
    )
    assert (
        "index.rst:11: WARNING: Cache DB error (exception: no such table: nonexisting.csv)"
        in warning_str
    )
    assert (
        "index.rst:16: WARNING: Missing :constdata:label: template for 'menu.csv'."
        in warning_str
    )
    assert (
        "index.rst:18: WARNING: Missing :constdata:link: template for 'menu.csv'."
        in warning_str
    )
    assert (
        "index.rst:23: WARNING: Can't list a table because 'conf.json' has no ID column with name 'id'."
        in warning_str
    )
    assert (
        "index.rst:39: WARNING: File 'shortcuts.json' doesn't contain column 'PC' referred in template ':kbd:'{PC}'/:kbd:'{mac}' (Mac)' but only ['id', 'pc', 'mac'] columns."
        in warning_str
    )
    assert (
        "index.rst:44: WARNING: File 'shortcuts.json' doesn't contain a row with ID 'nonexisting'"
        in warning_str
    )
    assert (
        "index.rst:46: WARNING: File 'shortcuts.json' doesn't contain a row with ID 'nonexisting'"
        in warning_str
    )
    assert (
        'index.rst:53: WARNING: Duplicate explicit target name: "constdata-shortcuts-json-filenew".'
        in warning_str
    )
    assert (
        'index.rst:53: WARNING: Duplicate explicit target name: "constdata-shortcuts-json-filesaveas".'
        in warning_str
    )
