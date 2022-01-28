import logging
import xml
from xml.dom import Node
from xml.dom.minicompat import NodeList

logger = logging.getLogger(__name__)

def _get_elements_by_part_tagName_helper(parent, name, rc):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            logging.debug(f' node.tagName: {node.tagName}')
            if (name == "*" or node.tagName == name or node.tagName.find(name) != -1):
                rc.append(node)
        _get_elements_by_part_tagName_helper(node, name, rc)
    return rc


class Document(xml.dom.minidom.Document):
    def getElementsByPartTagName(self, name):
        return _get_elements_by_part_tagName_helper(self, name, NodeList())
