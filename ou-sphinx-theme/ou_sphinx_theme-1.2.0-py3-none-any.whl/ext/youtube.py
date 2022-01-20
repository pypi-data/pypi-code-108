from docutils.nodes import Element
from sphinx.util.docutils import SphinxDirective

from .iframe import IFrameNode


def setup(app):
    app.add_directive('youtube', Youtube)
    app.add_node(VideoNode,
                 html=(visit_video_html, depart_video_html),
                 latex=(visit_video_latex, depart_video_latex),)
    app.add_node(PlayerNode,
                 html=(visit_player_html, depart_player_html),
                 latex=(visit_player_latex, depart_player_latex),)


class VideoNode(Element):
    """The VideoNode contains the PlayerNode and TranscriptNode that together make up the video."""

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('video')


def visit_video_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_video_html(self, node):
    self.body.append('</div>')


def visit_video_latex(self, node):
    pass


def depart_video_latex(self, node):
    pass


class PlayerNode(Element):
    """The PlayerNode represents the video player."""

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('player')


def visit_player_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_player_html(self, node):
    self.body.append('</div>')


def visit_player_latex(self, node):
    pass


def depart_player_latex(self, node):
    pass


class Youtube(SphinxDirective):
    """The Youtube directive supports embedding of YouTube videos.

    :param argument: The identifier of the YouTube video to embed
    :param width: Optional width for the video iframe
    :param height: Optional height for the video iframe
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'width': int,
                   'height': int}

    def run(self):
        video = VideoNode()
        player = PlayerNode()
        video += player
        iframe = IFrameNode()
        player += iframe
        iframe['source'] = f'https://www.youtube.com/embed/{self.arguments[0]}'
        if 'width' in self.options:
            iframe['width'] = self.options['width']
        if 'height' in self.options:
            iframe['height'] = self.options['height']
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, video)
        return [video]
