"""Parsing and unparsing of Finesse kat files and models."""

import inspect
import textwrap
from functools import reduce
from ..utilities import opened_file
from ..env import TERMINAL_WIDTH, INDENT


def parse(text, model=None, spec=None):
    """Parse KatScript into a model.

    Parameters
    ----------
    text : str
        The KatScript to parse.

    model : :class:`.Model`, optional
        The Finesse model to add the parsed objects to. Defaults to a new, empty model.

    spec : :class:`.spec.BaseSpec`, optional
        The language specification to use. Defaults to :class:`.spec.KatSpec`.

    Returns
    -------
    :class:`.Model`
        The parsed model.
    """
    from .compiler import KatCompiler

    compiler = KatCompiler(spec=spec)
    return compiler.compile(text, model=model)


def parse_file(path, model=None, spec=None):
    """Parse KatScript from a file into a model.

    Parameters
    ----------
    path : str or :py:class:`io.FileIO`
        The path or file object to read KatScript from. If an open file object is
        passed, it will be read from and left open. If a path is passed, it will be
        opened, read from, then closed.

    model : :class:`.Model`, optional
        The Finesse model to add the parsed objects to. Defaults to a new, empty model.

    spec : :class:`.spec.BaseSpec`, optional
        The language specification to use. Defaults to :class:`.spec.KatSpec`.

    Returns
    -------
    :class:`.Model`
        The parsed model.
    """
    from .compiler import KatCompiler

    compiler = KatCompiler(spec=spec)
    with opened_file(path, "r") as fobj:
        return compiler.compile_file(fobj, model=model)


def parse_legacy(text, model=None, ignored_blocks=None):
    """Parse KatScript into a model.

    Parameters
    ----------
    text : str
        The KatScript to parse.

    model : :class:`.Model`
        The Finesse model to add the parsed objects to.

    ignored_blocks : list, optional
        A list of names of ``FTBLOCK`` sections in the kat code to leave out of the
        model; defaults to empty list.

    Returns
    -------
    :class:`.Model`
        The parsed model.

    Raises
    ------
    NotImplementedError
        If `model` contains any non-default elements. Parsing into existing models is
        unsupported.
    """
    from .legacy import KatParser

    if model:
        # Newly-created models contain an fsig, so we need to account for that
        if len(model.elements) > 1:
            raise NotImplementedError(
                "Legacy parsing of extra commands with an existing model is "
                "unsupported. Please switch to the new syntax, or only call "
                "'parse_legacy' on a complete kat file."
            )
    parser = KatParser()
    return parser.parse(text, model=model, ignored_blocks=ignored_blocks)


def parse_legacy_file(path, model=None, ignored_blocks=None):
    """Parse KatScript from a file into a model.

    Parameters
    ----------
    path : str or :py:class:`io.FileIO`
        The path or file object to read KatScript from. If an open file object is
        passed, it will be read from and left open. If a path is passed, it will be
        opened, read from, then closed.

    model : :class:`.Model`
        The Finesse model to add the parsed objects to.

    ignored_blocks : list, optional
        A list of names of ``FTBLOCK`` sections in the kat code to leave out of the
        model; defaults to empty list.

    Returns
    -------
    :class:`.Model`
        The parsed model.

    Raises
    ------
    NotImplementedError
        If `model` contains any non-default elements. Parsing into existing models is
        unsupported.
    """
    from .legacy import KatParser

    if model:
        # Newly-created models contain an fsig, so we need to account for that
        if len(model.elements) > 1:
            raise NotImplementedError(
                "Legacy parsing of extra commands with an existing model is "
                "unsupported. Please switch to the new syntax, or only call "
                "'parse_legacy' on a complete kat file."
            )

    parser = KatParser()
    with opened_file(path, "r") as fobj:
        return parser.parse(fobj.read(), model=model, ignored_blocks=ignored_blocks)


def unparse(item, **kwargs):
    """Serialise a Finesse object (such as a model) to KatScript.

    Parameters
    ----------
    item : object
        A Finesse object (such as a :class:`.Model`) to generate KatScript for.

    Returns
    -------
    str
        The generated KatScript.
    """
    from .generator import KatUnbuilder

    unbuilder = KatUnbuilder()
    return unbuilder.unbuild(item, **kwargs)


def unparse_file(path, item, **kwargs):
    """Serialise a model to KatScript in a file.

    Parameters
    ----------
    path : str
        The kat file path to parse.

    item : object
        A Finesse object (such as a :class:`.Model`) to generate KatScript for.

    Returns
    -------
    str
        The generated KatScript.
    """
    from .generator import KatUnbuilder

    unbuilder = KatUnbuilder()
    with opened_file(path, "w") as fobj:
        return unbuilder.unbuild_file(fobj, item, **kwargs)


def help_(directive, spec=None):
    """Get help for `directive`, which can be any of a KatScript instruction, a
    KatScript path (e.g. `mirror.T`), or a Finesse or Python object or type.

    Like the Python builtin :func:`help`, this opens a pager containing the help text in
    the current console.

    Parameters
    ----------
    directive : any
        The directive to retrieve help for.

    spec : :class:`.KatSpec`, optional
        The KatScript specification to use. Defaults to :class:`.KatSpec`.

    Raises
    ------
    ValueError
        If `directive` cannot be recognised as a valid Finesse or KatScript item.
    """
    import pydoc

    if spec is None:
        from .spec import KatSpec

        spec = KatSpec()

    invalid_directive = ValueError(
        f"Cannot interpret {repr(directive)} as a valid Finesse or KatScript item."
    )

    extra = None

    if isinstance(directive, str):
        if pieces := directive.split("."):
            # This may refer to a model parameter or attribute.
            try:
                directive, extra = pieces[0], pieces[1:]
            except ValueError as e:
                raise invalid_directive from e

    try:
        adapter = spec.directives[directive]
    except KeyError:
        # This seems to be a Python object; use its docstring.
        pieces = []

        if inspect.isclass(directive):
            signature = str(inspect.signature(directive.__init__)).replace("self, ", "")
            pieces.append(f"{directive.__name__}{signature}")

            # Look for a KatScript directive producing this type.
            for key, adapter in spec.directives.items():
                if adapter is None or adapter.factory is None:
                    continue

                if directive != adapter.factory.item_type:
                    continue

                # Add the corresponding KatScript syntax.
                pieces.append(
                    (
                        f"KatScript (use 'finesse.help(\"{adapter.full_name}\")' for "
                        f"more information):\n"
                    )
                    + textwrap.indent(
                        adapter.documenter.syntax(spec, adapter), prefix=INDENT
                    )
                )

                break
        else:
            text = type(directive).__name__ + " object\n"
            text += repr(directive)
            pieces.append(text)

        # Add the object's docstring.
        pieces.append(inspect.getdoc(directive))

        return pydoc.pager("\n\n".join(pieces))

    if extra:
        # An attribute was specified. Return help for the parameter/attribute.
        try:
            obj = reduce(getattr, extra, adapter.documenter.item_type)
        except AttributeError as e:
            raise invalid_directive from e

        return pydoc.help(obj)

    # The directive is KatScript.
    pydoc.pager(syntax(directive))


def syntax(directive, spec=None, verbose=True, **kwargs):
    """Get the KatScript syntax for `directive`.

    Parameters
    ----------
    directive : str
        The directive to retrieve syntax for.

    spec : :class:`.KatSpec`, optional
        The KatScript specification to use. Defaults to :class:`.KatSpec`.

    verbose : bool
        Show documentation for the directive.

    Other Parameters
    ----------------
    kwargs : dict, optional
        Keyword arguments supported by :meth:`.ItemDocumenter.syntax`.

    Returns
    -------
    str
        The syntax for `directive`.

    Raises
    ------
    ValueError
        If `directive` cannot be recognised as a valid KatScript item.
    """
    if spec is None:
        from .spec import KatSpec

        spec = KatSpec()

    try:
        adapter = spec.directives[directive]
    except KeyError:
        raise ValueError(
            f"Cannot interpret {repr(directive)} as a valid KatScript directive."
        )

    syntax = adapter.documenter.syntax(spec, adapter, **kwargs)
    pieces = [syntax]

    if verbose:
        # Add the instruction summary and descriptions of its arguments.
        summary = adapter.documenter.summary()
        if summary is not None:
            pieces.append("\n".join(textwrap.wrap(summary, width=TERMINAL_WIDTH)))

        if params := adapter.documenter.argument_descriptions():
            paramsection = "Parameters\n----------\n"
            paramlines = []

            for name, (_, description) in params.items():
                paramlines.append(name)
                if description is not None:
                    wrapped = textwrap.wrap(
                        description,
                        initial_indent=INDENT,
                        subsequent_indent=INDENT,
                        width=TERMINAL_WIDTH - len(INDENT),  # Compensate for indent.
                    )
                    paramlines.append("\n".join(wrapped))
                else:
                    paramlines.append(
                        textwrap.indent("<no description>", prefix=INDENT)
                    )

            paramsection += "\n".join(paramlines)
            pieces.append(paramsection)

    return "\n\n".join(pieces)


__all__ = (
    "KatParserError",
    "KatReferenceError",
    "parse",
    "parse_file",
    "parse_legacy",
    "parse_legacy_file",
    "unparse",
    "unparse_file",
    "syntax",
)
