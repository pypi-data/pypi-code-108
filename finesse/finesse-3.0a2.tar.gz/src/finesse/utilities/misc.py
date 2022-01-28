"""Miscellaneous utility functions for any part of Finesse."""

import functools
import re
from itertools import tee
from contextlib import contextmanager
from pathlib import Path
from functools import partial, reduce

import numpy as np


def reduce_getattr(obj, key: str, delimiter: str = "."):
    """Applies a nested getattr with reduce to select an attribute of a nested object
    within `obj`.

    Parameters
    ----------
    obj : object
        Object to search

    key : str
        Delimited string of attributes

    delimiter : str, optional
        Delimiter character of key

    Returns
    -------
    Attribute of object
    """
    attrs = key.strip().split(delimiter)
    return reduce(getattr, attrs, obj)


def calltracker(func):
    """Decorator used for keeping track of whether the current state is inside the
    decorated function or not.

    Sets an attribute `has_been_called` on the function which gets switched on when the
    function is being executed and switched off after the function has returned. This
    allows you to query ``func.has_been_called`` for determining whether the code being
    executed has been called from within `func`.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        out = func(*args, **kwargs)
        wrapper.has_been_called = False

        return out

    wrapper.has_been_called = False
    return wrapper


def valid_name(name):
    """Validate the specified name."""
    return re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$").match(name)


def check_name(name):
    """Checks the validity of a component or node name.

    A name is valid if it contains only alphanumeric characters and underscores, and is
    not empty.

    Parameters
    ----------
    name : str
        The name to check.

    Returns
    -------
    name : str
        The name passed to this function if valid.

    Raises
    ------
    ValueError
        If `name` contains non-alphanumeric / underscore characters.
    """
    if not valid_name(name):
        raise ValueError(
            f"'{name}' can only contain alphanumeric and underscore characters"
        )
    return name


def pairwise(iterable):
    """Iterates through each pair in a iterable.

    Parameters
    ----------
    iterable : :py:class:`collections.abc.Iterable`
        An iterable object.

    Returns
    -------
    zip
        A zip object whose `.next()` method returns a tuple where the i-th
        element comes from the i-th iterable argument.
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def find(x, value):
    """Finds `value` in the list `x` and returns its index, returning `None` if `value`
    is not in the list."""
    try:
        return x.index(value)
    except ValueError:
        return None


def find_nearest(x, value, index=False):
    idx = np.argmin(np.abs(x - value))
    if index:
        return idx
    return x[idx]


def is_iterable(obj):
    """Reliable check for whether an object is iterable.

    Note that strings are treated as non-iterable objects
    when performing this check. This will only return true
    for iterable non-str objects.

    Returns
    -------
    flag : bool
        True if `obj` is iterable, False otherwise.
    """
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return not isinstance(obj, str)


@contextmanager
def opened_file(fobj, mode):
    """Get an open file regardless of whether a string or an already open file is
    passed.

    Parameters
    ----------
    fobj : str, :class:`pathlib.Path`, or file-like
        The path or file object to ensure is open. If `fobj` is an already open file
        object, its mode is checked to be correct but is otherwise returned as-is. If
        `fobj` is a string, it is opened with the specified `mode` and yielded, then
        closed once the wrapped context exits. Note that passed open file objects are
        *not* closed.

    mode : str
        The mode to ensure `fobj` is opened with.

    Yields
    ------
    :class:`io.FileIO`
        The open file with the specified `mode`.

    Raises
    ------
    ValueError
        If `fobj` is not a string nor open file, or if `fobj` is open but with a
        different `mode`.
    """
    close = False

    if isinstance(fobj, (str, Path)):
        fobj = open(fobj, mode)
        close = True  # Close the file we just opened once we're done.
    else:
        try:
            # Ensure mode agrees.
            if fobj.mode != mode:
                raise ValueError(
                    f"Unexpected mode for '{fobj.name}' (expected '{mode}', got "
                    f"'{fobj.mode}')"
                )
        except AttributeError:
            raise ValueError(f"'{fobj}' is not an open file or path.")

    try:
        yield fobj
    finally:
        if close:
            fobj.close()


def graph_layouts():
    """Available NetworkX and graphviz (if installed) graph plotting layouts."""
    return {**networkx_layouts(), **graphviz_layouts()}


def networkx_layouts():
    """Available NetworkX graph plotting layouts."""
    import inspect
    import networkx

    # Excluded layouts.
    excluded = (
        "rescale",
        # These layouts need the network to first be grouped into sets.
        "bipartite",
        "multipartite_layout",
    )

    layouts = {}
    suffix = "_layout"

    def find_layouts(members):
        for name, func in members:
            if name.startswith("_") or not name.endswith(suffix):
                # Not a public layout.
                continue

            # Strip the "_layout" part.
            name = name[: -len(suffix)]

            if name in excluded:
                continue

            layouts[name] = func

    find_layouts(inspect.getmembers(networkx.drawing.layout, inspect.isfunction))

    return layouts


def graphviz_layouts():
    """Available graphviz graph plotting layouts."""
    import networkx
    from ..env import has_pygraphviz

    layouts = {}

    if has_pygraphviz():
        for layout in ["neato", "dot", "fdp", "sfdp", "circo"]:
            # Returns callable that can be called like `networkx.drawing.layout` members.
            layouts[layout] = partial(
                networkx.drawing.nx_agraph.pygraphviz_layout, prog=layout
            )

    return layouts


def doc_element_parameter_table(cls):
    """Prints table for a particular element class."""
    import finesse
    import tabulate
    from IPython.core.display import HTML
    from functools import partial
    from types import SimpleNamespace

    # object counter to keep track of odd and even rows
    i = SimpleNamespace()
    i.current = -1

    def my_html_row_with_attrs(celltag, cell_values, colwidths, colaligns, **kwargs):
        alignment = {
            "left": ' style="text-align: left;"',
            "right": ' style="text-align: right;"',
            "center": ' style="text-align: center;"',
            "decimal": ' style="text-align: right;"',
        }
        values_with_attrs = [
            "<{0}{1}>{2}</{0}>".format(celltag, alignment.get(a, ""), c)
            for c, a in zip(cell_values, colaligns)
        ]
        kwargs["i"].current += 1
        return (
            f"<tr style=\"vertical-align: middle;\" class=\"row-{'even' if kwargs['i'].current % 2 else 'odd'}\">"
            + "".join(values_with_attrs).rstrip()
            + "</tr>"
        )

    def process_changeable(pinfo):
        if pinfo.changeable_during_simulation:
            return "<div style='color:green;'>✓</div>"
        else:
            return "<div style='color:red;'>✗</div>"

    SphinxTable = tabulate.TableFormat(
        lineabove=tabulate.Line(
            '<table class="docutils align-default"><thead>', "", "", ""
        ),
        linebelowheader=tabulate.Line("</thead>", "", "", ""),
        linebetweenrows=None,
        linebelow=tabulate.Line("</table>", "", "", ""),
        headerrow=partial(my_html_row_with_attrs, "th", i=i),
        datarow=partial(my_html_row_with_attrs, "td", i=i),
        padding=0,
        with_header_hide=None,
    )
    tbl = [
        (p.name, p.description, p.units, p.dtype.__name__, process_changeable(p))
        for p in finesse.element.ModelElement._param_dict[cls][::-1]
    ]
    if len(tbl) == 0:
        raise RuntimeError(f"{cls} has no model parameters to display.")

    a = tabulate.tabulate(
        tbl,
        tablefmt=SphinxTable,
        colalign=("left", "left", "center", "center", "center"),
        headers=(
            "Name",
            "Description",
            "Units",
            "Data type",
            "Can change during simualation",
        ),
    )
    return HTML(a)
