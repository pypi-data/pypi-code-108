"""Useful common utility functions and classes used throughout the Finesse package."""

# TODO: sort out which things get imported at the module level here
from .components import refractive_index
from .homs import make_modes, insert_modes
from .logging import logs, tracebacks
from .text import (
    ngettext,
    option_list,
    format_section,
    format_bullet_list,
    add_linenos,
    stringify,
    stringify_graph_gml,
)
from .misc import (
    check_name,
    pairwise,
    valid_name,
    is_iterable,
    opened_file,
    graph_layouts,
    networkx_layouts,
    graphviz_layouts,
)
from .units import SI, SI_LABEL, SI_VALUE

__all__ = (
    "refractive_index",
    "make_modes",
    "insert_modes",
    "logs",
    "tracebacks",
    "ngettext",
    "option_list",
    "format_section",
    "format_bullet_list",
    "add_linenos",
    "stringify",
    "stringify_graph_gml",
    "check_name",
    "pairwise",
    "valid_name",
    "is_iterable",
    "opened_file",
    "graph_layouts",
    "networkx_layouts",
    "graphviz_layouts",
    "SI",
    "SI_LABEL",
    "SI_VALUE",
)
