import base64
import zlib
import xml.etree.ElementTree as ET
import urllib.parse

from drawio_parser.component import Component
from drawio_parser.diagram import Diagram

class Parser:

    def __init__(self, drawio_file) -> None:
        self.__diagrams = []
        self.__parse_drawio(ET.parse(drawio_file))

    def __extract_diagram_content(self, diagram) -> str:
        diagram_content: str = diagram.text or ""
        diagram_content_decoded: bytes = base64.b64decode(diagram_content)
        xml_content: bytes = zlib.decompress(diagram_content_decoded, -15)

        return urllib.parse.unquote(xml_content.decode())

    def __parse_drawio(self, drawio_file):
        
        for diagram in drawio_file.findall("diagram"):
            diagram_name: str = diagram.get("name", "")

            xml_content_str: str = self.__extract_diagram_content(diagram)
            
            xml_content: ET.Element = ET.fromstring(xml_content_str)
            xml_root = xml_content.findall('root')[0]
            diagram_elements = xml_root.findall('mxCell')
            components = []
            for e in diagram_elements:
                component = Component(e.get('id'), dict(e.items()))
                components.append(component)
            diagram = Diagram(diagram_name, components)
            self.__diagrams.append(diagram)

    def get_diagrams(self):
        return self.__diagrams
