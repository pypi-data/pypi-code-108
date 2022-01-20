from docutils import nodes
from docutils.nodes import Element
from sphinx.util.docutils import SphinxDirective


def setup(app):
    app.add_directive('activity', Activity)
    app.add_node(ActivityNode,
                 html=(visit_activity_html, depart_activity_html),
                 latex=(visit_activity_latex, depart_activity_latex),)
    app.add_node(ActivityTitleNode,
                 html=(visit_activity_title_html, depart_activity_title_html),
                 latex=(visit_activity_title_latex, depart_activity_title_latex),)
    app.add_node(ActivityContentNode,
                 html=(visit_activity_content_html, depart_activity_content_html),
                 latex=(visit_activity_content_latex, depart_activity_content_latex),)
    app.add_directive('activity-answer', ActivityAnswer)
    app.add_node(ActivityAnswerNode,
                 html=(visit_activity_answer_html, depart_activity_answer_html),
                 latex=(visit_activity_answer_latex, depart_activity_answer_latex),)


class ActivityNode(Element):
    """The ActivityNode contains a single activity, consisting of the ActivityTitleNode and an
    ActivityContentNode."""

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('activity')


def visit_activity_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_activity_html(self, node):
    self.body.append('</div>')


def visit_activity_latex(self, node):
    pass


def depart_activity_latex(self, node):
    pass


class ActivityTitleNode(Element):
    """The ActivityTitleNode contains the title text for the ActivityNode."""

    pass


def visit_activity_title_html(self, node):
    self.body.append(self.starttag(node, 'h2'))


def depart_activity_title_html(self, node):
    self.body.append('</h2>')


def visit_activity_title_latex(self, node):
    pass


def depart_activity_title_latex(self, node):
    self.body.append('\n')


class ActivityContentNode(Element):
    """The ActivityContentNode contains the nested content for the ActivityNode."""

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('content')


def visit_activity_content_html(self, node):
    self.body.append(self.starttag(node, 'div'))


def depart_activity_content_html(self, node):
    self.body.append('</div>')


def visit_activity_content_latex(self, node):
    pass


def depart_activity_content_latex(self, node):
    pass


class ActivityAnswerNode(Element):
    """The ActivityAnswerNode can be placed inside the ActivityContentNode to provide an initially hidden
    answer to an activity.
    """

    def __init__(self, rawsource='', *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)
        self.set_class('answer')


def visit_activity_answer_html(self, node):
    self.body.append(self.starttag(node, 'div'))
    self.body.append('<div class="buttons"><button><span>Reveal answer</span><span>Hide answer</span></button></div>')
    self.body.append('<div class="content">')
    self.body.append('<h3>Answer</h3>')


def depart_activity_answer_html(self, node):
    self.body.append('</div>')
    self.body.append('</div>')


def visit_activity_answer_latex(self, node):
    pass


def depart_activity_answer_latex(self, node):
    pass


class Activity(SphinxDirective):
    """The Activity directive is used to generate an activity block."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        activity = ActivityNode()
        activity_title = ActivityTitleNode()
        activity += activity_title
        activity_title += nodes.Text(self.arguments[0], self.arguments[0])
        activity_content = ActivityContentNode()
        activity += activity_content
        self.state.nested_parse(self.content, self.content_offset, activity_content)
        return [activity]


class ActivityAnswer(SphinxDirective):
    """The ActivityAnswer directive is used to generate an answer block for an activity that is initially hidden."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        activity_answer = ActivityAnswerNode()
        self.state.nested_parse(self.content, self.content_offset, activity_answer)
        return [activity_answer]
