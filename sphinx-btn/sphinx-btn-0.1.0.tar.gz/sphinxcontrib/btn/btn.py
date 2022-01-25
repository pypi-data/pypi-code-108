# -*- coding: utf-8 -*-
from pathlib import Path
import re

from docutils import nodes
from .font_handler import Fontawesome
from sphinx.util import logging

# -- global variables ----------------------------------------------------------
font_handler = None
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------


class btn(nodes.General, nodes.Element):
    pass


def download_font_assets(app):
    """
    Download the fonts from the web assets and prepare them to be used in the documentation output directory
    :param app: the current Sphinx application
    """

    # start the font_handler
    font_handler = Fontawesome()

    # create a _font folder
    output_dir = Path(app.outdir)
    font_dir = output_dir / "_font"
    font_dir.mkdir(exist_ok=True)
    app.config.html_static_path.append(str(font_dir))

    # guess what need to be installed
    # based on the compiler
    if app.builder.format == "html":

        font_handler.download_asset("html", font_dir)
        app.add_css_file(font_handler.get_css())
        app.add_js_file(font_handler.get_js())

    elif app.builder.format == "latex":

        font_handler.download_asset("latex", font_dir)

    return


def get_glyph(icon):
    """
    get the glyph from text

    Return a tuple of (glyph, font) from the provided text. raise an error if one of them does not exist

    :param icon: The text to transform (e.g. "fa fa-folder")
    """

    # split the icon name to find the name inside
    m = re.match(r"^(fab|far|fa|fas) fa-([\w-]+)$", icon)
    if not m:
        raise ValueError(f'invalid icon name: "{icon}"')
    # if not m.group(2) in font_handler.get_metadata():
    #    raise ValueError(f'icon "{m.group(2)}" is not part of fontawesome 5.15.4')

    # return (font, glyph)
    return m.group(1), m.group(2)


def depart_btn_node(self, node):
    """
    Empty depart function, everything is handled in visit

    :param node: the btn node
    """
    pass


def visit_btn_node_html(self, node):
    """
    create the html output

    :param node: the btn node
    """

    # test if the icon exist in the metadata
    # only if an icon is actually set
    icon = node["icon"]
    if icon != "":
        try:
            get_glyph(icon)
        except ValueError as e:
            logger.warning(str(e), location=node)
            raise nodes.SkipNode

    # setup the margin using fontawsome class
    text = node["text"]
    margin = 'style="margin-right: .5em;"' if text and icon else ""

    self.body.append(
        f'<span class="guilabel"><i class="{icon}" {margin}></i>{text.strip()}</span>'
    )

    return


def visit_btn_node_latex(self, node):
    """
    create the latex output

    :param node: the btn node
    """

    # create the macro to display the btn in the latex document
    # install 2 packages tcolorbox and fontawesome5
    # create a sphinxbtn command
    macro = (
        "\\usepackage{fontawesome5}\n"
        + "\\usepackage{tcolorbox}\n"
        + "\\newtcbox{\\sphinxbtn}[1][]{box align=base, nobeforeafter, size=small, boxsep=2pt, #1}\n"
    )
    if macro not in self.elements["preamble"]:
        self.elements["preamble"] += macro

    # start building the content of the command
    content = ""

    # test if the icon exist in the metadata
    # only if an icon is actually set
    icon = node["icon"]
    if icon != "":
        try:
            font, glyph = get_glyph(icon)
        except ValueError as e:
            logger.warning(str(e), location=node)
            raise nodes.SkipNode

        # detect the font
        font_list = {"fa": None, "far": "regular", "fas": "solid", "fab": "brand"}
        font = font_list[font]

        # build the output
        content += "\\faIcon"
        if font is not None:
            content += f"[{font}]"
        content += f"{{{glyph}}}"

    # add a spacer if there is text afterward
    text = node["text"]
    if content != "" and text != "":
        content += " "

    # use the rest of the text to finish btn content
    text = node["text"]
    if text != "":
        content += text

    # write the final output
    self.body.append(f"\\sphinxbtn{{{content}}}")

    return


def visit_btn_node_unsuported(self, node):
    """
    raise error when the requested output is not supported

    :param node: the btn node
    """

    logger.warning("Unsupported output format (node skipped)", location=node)
    raise nodes.SkipNode


_NODE_VISITORS = {
    "html": (visit_btn_node_html, depart_btn_node),
    "latex": (visit_btn_node_latex, depart_btn_node),
    "man": (visit_btn_node_unsuported, None),
    "texinfo": (visit_btn_node_unsuported, None),
    "text": (visit_btn_node_unsuported, None),
}


def btn_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    add inline btn role

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """

    # get the icon parameters
    if text.find("<") != -1:
        start = text.find("<")
        end = text.find(">")
        icon = text[start + 1 : end]
        text = text[end + 1 :]
    else:
        icon = ""

    # create the node
    node = btn(icon=icon, text=text)

    return [node], []
