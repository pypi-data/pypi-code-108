"""Text utilities."""


def ngettext(n, fsingle, fplural, sub=True):
    """Get the singular or plural form of the specified messages based on n.

    Simplified version of the Python standard library function :func:`gettext.ngettext`.

    Parameters
    ----------
    n : int
        The number to use to decide which form to return.

    fsingle, fplural : str
        Single and plural templates.

    sub : bool, optional
        Substitute `n` into the templates. Defaults to `True`.

    Examples
    --------
    >>> ngettext(1, "{n} item", "{n} items")
    '1 item'

    >>> ngettext(5, "{n} item", "{n} items")
    '5 items'

    The template doesn't have to contain `{n}`:
    >>> ngettext(5, "item", "items")
    'items'

    Setting `sub=False` turns off substitution:
    >>> ngettext(5, "{n} item", "{n} items", sub=False)
    '{n} items'
    """
    if n == 1:
        return fsingle.format(n=n) if sub else fsingle
    return fplural.format(n=n) if sub else fplural


def option_list(sequence, final_sep="or", quotechar=None):
    """Build a list from `sequence` with commas and a final "or".

    As in Python's error messages (e.g. "'func' missing 3 requied positional arguments:
    'a', 'b', and 'c'"), this function adds an Oxford comma for sequences of length > 2.

    Parameters
    ----------
    sequence : sequence
        The options to create a list with.

    final_sep : str, optional
        The final separator when `sequence` has more than one item. Defaults to `or`.

    quotechar : str, optional
        Quote the items in `sequence` with this character. Defaults to no quotes.
    """
    sequence = list(sequence)

    if quotechar:
        sequence = [f"{quotechar}{item}{quotechar}" for item in sequence]

    if len(sequence) <= 1:
        return "".join(sequence)
    elif len(sequence) == 2:
        return f"{sequence[0]} {final_sep} {sequence[1]}"
    sequence[-1] = f"{final_sep} {sequence[-1]}"
    return ", ".join(sequence)


def format_section(header, body, ruler=True, ruler_char="="):
    """Format text in sections."""
    text = f"{header}\n"

    if ruler:
        text += f"{ruler_char * len(header)}\n"

    if body:
        text += f"\n{body}\n"

    return text


def format_bullet_list(items, indent=4, bullet_char="-"):
    """Format items into a bullet list."""
    pre = " " * indent
    return "\n".join([f"{pre}{bullet_char} {item}" for item in items])


def add_linenos(linenos, lines):
    """Add line numbers to the start of lines.

    Parameters
    ----------
    linenos : sequence of int
        The line numbers, in the same order as `lines`.

    lines : sequence of str
        The lines.

    Returns
    -------
    sequence of str
        The lines with prepended line numbers.
    """
    # Use as many columns as required to fit the largest line number.
    wlinenocol = max([len(str(lineno)) for lineno in linenos])
    return [f"{lineno:>{wlinenocol}}: {line}" for lineno, line in zip(linenos, lines)]


def stringify(item):
    """Recursively stringify `item`.

    This is useful for when it doesn't make sense or isn't possible to override the
    __repr__ method of an object to get a compact string representation.
    """
    if isinstance(item, (list, tuple)):
        return f"[{', '.join(stringify(i) for i in item)}]"
    return str(item)


def stringify_graph_gml(graph):
    """Convert the specified NetworkX graph to string representation using GML
    markup."""
    from io import BytesIO
    import networkx as nx

    graphbytes = BytesIO()
    nx.write_gml(graph, graphbytes, stringify)
    graphbytes.seek(0)

    return graphbytes.read().decode("utf-8")
