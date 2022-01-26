from xml.dom.minidom import parseString as parse_xml

from pygments import highlight
from pygments.lexers.html import XmlLexer
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

from pyxb import ValidationError
from pyxb.utils.domutils import BindingDOMSupport

from schemas import eMeasure


def prettify(xml):
    return parse_xml(xml).toprettyxml(indent='  ', encoding='utf-8')


class QualityMeasureDocument(object):

    @classmethod
    def from_file(cls, path):
        qmd = cls()

        qmd.xml = open(path).read()
        qmd.document = eMeasure.CreateFromDocument(qmd.xml)

        return qmd

    @staticmethod
    def node_to_xml(node):
        try:
            dom = node.toDOM()

            # Specify the namespace of the binding class as the default for more compact XML (and
            # because this is how it appears in the example XML from Surescripts)
            dom = node.toDOM(bds=BindingDOMSupport(default_namespace=eMeasure.Namespace))

            return prettify(dom.toxml('utf-8'))
        except ValidationError as e:
            print(e.details())

            raise

    def to_xml(self):
        return self.node_to_xml(self.document)

    def print_node(self, node):
        self.print_xml(self.node_to_xml(node).decode())

    def print_document(self):
        self.print_xml(self.to_xml().decode())

    @staticmethod
    def print_xml(xml):
        highlighted = highlight(xml, XmlLexer(), TerminalTrueColorFormatter(style='paraiso-dark'))
        decorated = '\n'.join(line for line in highlighted.strip().split('\n'))

        print(decorated)
        print()
