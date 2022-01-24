from xml.parsers.expat import ExpatError
from xmltodict import parse as xmlparse

def safe_xml_parse(data):
    try:
        return xmlparse(data)
    except ExpatError:
        return {}