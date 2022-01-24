from docutils.parsers.rst.states import Inliner, Struct
from sphinx.errors import ExtensionError


class ConstdataError(ExtensionError):
    category = "Constdata extension"


def render_inline_rst(rst: str, lineno: int, inliner: Inliner):
    """Render and return (resulting nodes, system message)."""
    memo = Struct(
        document=inliner.document, reporter=inliner.reporter, language=inliner.language  # type: ignore
    )
    nodes, messages = inliner.parse(rst, lineno, memo, inliner.parent)  # type: ignore

    return nodes, messages
