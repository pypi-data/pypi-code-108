import pytest


@pytest.mark.sphinx("html", testroot="naked-syntax")
def test_naked_syntax(app, status, warning):
    """
    Test naked syntax (without domain). It's actually the test of Sphinx itself, than if constdata.
    """
    app.build()

    warning_str = warning.getvalue()

    # the only two expected warning message
    assert (
        'index.rst:20: WARNING: Duplicate explicit target name: "constdata-menu-csv-filenew".'
        in warning_str
    )
    assert (
        'index.rst:20: WARNING: Duplicate explicit target name: "constdata-menu-csv-filesaveas".'
        in warning_str
    )
    # two warnings are two lines
    assert warning_str.count("\n") == 2
