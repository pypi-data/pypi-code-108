"""Sphinx extension adding semantic markup for metasyntactic variables."""

__version__ = "0.1"

from os import path

from docutils.nodes import emphasis
from sphinx.roles import EmphasizedLiteral
from sphinx.util.docutils import SphinxRole
from sphinx.writers.texinfo import TexinfoTranslator
from sphinx.writers.text import TextTranslator
from typing import Tuple, List


class metavar(emphasis):
    """Custom node for metasyntactic variables."""


class MetavarRole(SphinxRole):
    """Role for metasyntactic variables."""

    def run(self):
        return [metavar(self.rawtext, self.text, classes=["metavar"])], []


class MetavarAwareEmphasizedLiteral(EmphasizedLiteral):
    """Modified version of ``EmphasizedLiteral`` that outputs ``metavar`` nodes rather than emphasis."""

    def parse(self, text):
        parsed = super().parse(text)
        return [
            metavar(node.rawsource, *node.children, classes=["metavar"])
            if isinstance(node, emphasis)
            else node
            for node in parsed
        ]


class MetavarAwareTexinfoTranslator(TexinfoTranslator):
    """Modified Texinfo translator, outputting ``@var{}`` for metasyntactic variables."""

    def visit_metavar(self, node):
        self.body.append("@var{")


class MetavarAwareTextTranslator(TextTranslator):
    """Modified text translator, outputting metasyntactic variables in capital letters."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_metavar = False

    def visit_metavar(self, node):
        self.in_metavar = True

    def visit_Text(self, node):
        text = node.astext()
        if self.in_metavar:
            text = text.upper()
        self.add_text(text)

    def depart_metavar(self, node):
        self.in_metavar = False


def setup(app):
    app.set_translator("texinfo", MetavarAwareTexinfoTranslator)
    app.set_translator("text", MetavarAwareTextTranslator)
    app.add_role("samp", MetavarAwareEmphasizedLiteral(), override=True)
    app.add_role("metavar", MetavarRole())
