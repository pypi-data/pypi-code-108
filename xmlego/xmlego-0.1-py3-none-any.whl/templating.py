import imp
from lxml import etree
from .utils import copy_element, insert_after, remove_element

FOR_TAG = "t-for"
FOR_TAG_VALUE_ATTR = "values"
FOR_TAG_AS_ATTR = "as"

TRANSIENT_TAG = "t"
# This is meant to avoid name colision when injecting in exec_code
TEMP_VAR_NAME = "rewqrewvnkjvnkrntlwkqerjweholifuhlnrkjnqlrekwjcvhdlsiurenqwlfkjnfdasfsd"


# In case we need to filter
# Globals must contain __builtins__ entry 
def exec_code(code, globals=None, locals=None):
    if globals is None:
        globals = {}
    if locals is None:
        locals = {}
    exec(code, globals, locals)
    return globals, locals

def remove_transient_tags(xml):
    for t in xml.findall(TRANSIENT_TAG):
        children = t.getchildren()
        insert_after(t, children)
    remove_element(xml)

def eval_xml_for(xml, variables=None, globals=None):
    if variables is None:
        variables = {}

    # Retrieve data
    values_code = "({})".format(xml.attrib[FOR_TAG_VALUE_ATTR])
    values = exec_code(values_code, globals, locals=variables)
    as_attr = "({}) = {}".format(
        xml.attrib[FOR_TAG_AS_ATTR],
        TEMP_VAR_NAME
    )

    # We need a common parent and clear the current content
    tmp = etree.Element(TRANSIENT_TAG)
    tmp.extend(xml.getchildren())
    xml.clear()

    for it in values:
        loop_vars = {TEMP_VAR_NAME: it}
        exec_code(as_attr, globals=globals, locals=loop_vars)
        loop_vars.pop(TEMP_VAR_NAME)
        res = _eval_xml(copy_element(tmp), {**variables, **loop_vars}, globals=globals)
        xml.append(res)
    return xml

def _eval_xml(xml, variables=None, globals=None):
    if variables is None:
        variables = {}
    
    # Nb: Thoses functions will edit the tree IN-PLACE! Do a copy before any call if needed
    if xml.tag == FOR_TAG:
        eval_xml_for(xml, variables=variables, globals=globals)
        return xml, variables

    for child in xml.getchildren():
        _eval_xml(child, variables=variables, globals=globals)

    return xml, variables

def eval_xml(xml, variables=None, globals=None):
    if variables is None:
        variables = {}
    xml = _eval_xml(xml, variables=variables, globals=globals)
    remove_transient_tags(xml)
    return xml