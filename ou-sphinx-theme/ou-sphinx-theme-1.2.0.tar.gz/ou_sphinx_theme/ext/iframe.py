from docutils.nodes import Element
from sphinx.util.docutils import SphinxDirective


def setup(app):
    app.add_directive('iframe', IFrame)
    app.add_node(IFrameNode,
                 html=(visit_iframe_html, depart_iframe_html),
                 latex=(visit_iframe_latex, depart_iframe_latex),)


class IFrameNode(Element):
    """The IFrameNode generates an iFrame."""

    pass


def visit_iframe_html(self, node):
    self.body.append(f'<iframe src="{node["source"]}"')
    if 'width' in node:
        self.body.append(f' width="{node["width"]}"')
    if 'height' in node:
        self.body.append(f' height="{node["height"]}"')
    if 'scrolling' in node:
        self.body.append(f' scrolling="{node["scrolling"]}"')
    self.body.append('>')


def depart_iframe_html(self, node):
    self.body.append('</iframe>')


def visit_iframe_latex(self, node):
    self.body.append(f'The embedded content can be found at \\url{{{node["source"]}}}')


def depart_iframe_latex(self, node):
    pass


class IFrame(SphinxDirective):
    """The IFrame directive is used to embed arbitrary URIs via an iframe.

    :param argument: The URI to load in the iframe
    :param width: Optional width for the iframe
    :param height: Optional height for the iframe
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'width': int,
                   'height': int,
                   'scrolling': str}

    def run(self):
        iframe = IFrameNode()
        iframe['source'] = self.arguments[0]
        if 'width' in self.options:
            iframe['width'] = self.options['width']
        if 'height' in self.options:
            iframe['height'] = self.options['height']
        if 'scrolling' in self.options:
            iframe['scrolling'] = self.options['scrolling']
        return [iframe]
