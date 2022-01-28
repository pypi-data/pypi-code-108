#Claudio Perez
import os
import re
import docutils.utils
from docutils.core import publish_doctree
import xml.etree.ElementTree as ElementTree
from .utils import norm_join

report_level = docutils.utils.Reporter.SEVERE_LEVEL + 1

def rst_to_xml(filename):
    with open(filename,"r") as f:
        doctree = publish_doctree(
                f.read(),
                settings_overrides={'report_level':report_level}
                )
    xml_representation = doctree.asdom().toxml()
    return ElementTree.fromstring(xml_representation)

def find_dependencies(src: str, base:str)->list:
    rst_tree = rst_to_xml(
        os.path.expandvars(
            norm_join(base,src)
        )
    )
    dependencies = []
    lit_includes = [
        i.text for i in rst_tree.findall(".//literal_block")
            if i.text and "literalinclude" in i.text
    ]
    paths = [
        i.split("\n")[0].split("literalinclude:: ")[1] for i in lit_includes
    ]
    dependencies.extend(paths)
    dependencies.extend([
        image.attrib["uri"] for image in rst_tree.findall(".//image")
        ])

    return dependencies, None


def parse_rst(text:str):
    doctree = publish_doctree(
            text,
            settings_overrides={'report_level':report_level}
            ).asdom()

    # Convert to etree.ElementTree since this is easier to work with than
    # xml.minidom
    doctree = ElementTree.fromstring(doctree.toxml())

    # Get all field lists in the document.
    field_lists = doctree.findall('field_list')

    fields = [f for field_list in field_lists \
        for f in field_list.findall('field')]

    field_names = [name.text for field in fields \
        for name in field.findall('field_name')]

    field_text = [ElementTree.tostring(element) for field in fields \
        for element in field.findall('field_body')]

    return dict(zip(field_names, field_text))

