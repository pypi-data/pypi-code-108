from enum import Enum


class DiagramType(str, Enum):
    huffman_svg = "svg/~1"
    huffman_editor = "uml/~1"
    huffman_uml = "uml/~1"
    huffman_png = "png/~1"


DEFAULTS = {
    "url": "http://www.plantuml.com/plantuml",
    "type": DiagramType.huffman_uml
}