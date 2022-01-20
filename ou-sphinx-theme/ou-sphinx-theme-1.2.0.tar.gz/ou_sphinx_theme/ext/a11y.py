from docutils.nodes import Element
from sphinx.util.docutils import SphinxDirective

from .iframe import IFrameNode


def setup(app):
    app.add_directive('transcript', Transcript)
    app.add_node(TranscriptNode,
                 html=(visit_transcript_html, depart_transcript_html),
                 latex=(visit_transcript_latex, depart_transcript_latex),)
    app.add_directive('description', Description)
    app.add_node(DescriptionNode,
                 html=(visit_description_html, depart_description_html),
                 latex=(visit_description_latex, depart_description_latex),)


class TranscriptNode(Element):
    """The TranscriptNode represents the transcript of a video."""

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('transcript')


def visit_transcript_html(self, node):
    self.body.append(self.starttag(node, 'div'))
    self.body.append('<div class="buttons">')
    self.body.append('<button><span>Show transcript</span><span>Hide transcript</span></button>')
    self.body.append('</div>')
    self.body.append('<div class="content">')


def depart_transcript_html(self, node):
    self.body.append('</div>')
    self.body.append('</div>')


def visit_transcript_latex(self, node):
    self.body.append('\n')


def depart_transcript_latex(self, node):
    pass


class DescriptionNode(Element):
    """The DescriptionNode represents the description of a visual element."""

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('description')


def visit_description_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_description_html(self, node):
    self.body.append('</div>')


def visit_description_latex(self, node):
    self.body.append('\n')


def depart_description_latex(self, node):
    pass


class Transcript(SphinxDirective):
    """The Transcript directive supports providing a transcription of an audio element.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        transcript = TranscriptNode()
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, transcript)
        return [transcript]


class Description(SphinxDirective):
    """The Description directive supports providing a text description of a visual element.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        description = DescriptionNode()
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, description)
        return [description]
