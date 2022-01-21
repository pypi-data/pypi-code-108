"""
Collection of pre-configured snippets for re-use.

"""

from .stylers import Style, TableStyler


style_header_generic = TableStyler(
    rows=[0],
    styles=[Style.BOLD, Style.CENTER],
    context='light'
)

style_even_rows = TableStyler(
    rows=[slice(2, None, 2)],
    context='light'
)
