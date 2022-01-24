"""
extools - Python tools for Orchid Extender

This package provides a number of utility functions designed to make working
with Extender for Sage 300 easier.

A View-like object is any object which responds to .put, .get, .recordClear,
.browse, .fetch, .update, .insert.
"""
try:
    from accpac import *
except ImportError as e:
    # This happens when the tools are imported outside of the Extender env.
    # We can pass to let the tool do its work (likely sphinx making docs).
    pass

def lines_in(ds):
    """Generator that yields all records in a datasource.

    :param ds: an instance of an accpac.UIDataSource
    """
    ds.recordClear()
    ds.browse("")

    while ds.fetch() == 0:
        yield ds

def lines_in_view(viewid):
    """Generator that yields all records in a view.

    :param viewid: The identifier of the datastore (i.e. dsOEORDH)
    """
    view = openView(viewid)
    view.recordClear()
    view.browse("")

    while view.fetch() == 0:
        yield view

def success(*args):
    """Check if the return values from view actions indicate success.

    Extender view calls return 0 on success and non-zero on failure. Use this
    function to check whether a collection of view calls have been successful.

    :param \*args: any number of return values.
    :rtype: bool

    .. code-block:: python

        view = openView("EX0001")
        rc = view.recordClear()
        br = view.browse("")
        fe = view.fetch()
        if not success(rc, br, fe):
            showMessage("Failed to open EX0001 and seek to the first record.")
    """
    if sum(args) > 0:
        return False
    return True

def open_and_fetch_row(viewid):
    """Open the view and fetch the first row.

    :param view: RotoID of the view to open and fetch from
    :rtype: accpack.View or None
    """
    view = openView(viewid)
    browsed = view.browse('')
    fetched = view.fetch()

    if not success(browsed, fetched):
        return None

    return view

