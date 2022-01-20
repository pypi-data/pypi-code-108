from io import StringIO, BytesIO
from typing import Dict

import inflection
import six
from django.utils.encoding import smart_str, smart_bytes
from django.utils.xmlutils import SimplerXMLGenerator
from lxml import etree


def prettyPrintXml(xmlFilePathToPrettyPrint):
    assert xmlFilePathToPrettyPrint is not None


class XMLGenerator(SimplerXMLGenerator):
    def cdata(self, content):
        cdata = "<![CDATA[{}]]>".format(content)
        self.ignorableWhitespace(cdata)

    def startElement(self, name: str, attrs: Dict[str, str]) -> None:
        # Sort attrs for a deterministic output.
        sorted_attrs = dict(sorted(attrs.items())) if attrs else attrs
        super().startElement(name, sorted_attrs)


def tag_name(name):
    return inflection.camelize(name)


def list_name(name):
    return inflection.pluralize(tag_name(name))


def list_item_name(name):
    return inflection.singularize(tag_name(name))


def attribute_name(name):
    return inflection.camelize(name, uppercase_first_letter=False)


def is_to_attributes(data):
    if not isinstance(data, dict):
        return False
    if len(data) > 4:
        return False
    for key, value in six.iteritems(data):
        if isinstance(value, dict):
            return False
        if isinstance(value, (list, type)):
            return False
        if isinstance(value, str) and len(value) > 128:
            return False
    return True


class XMLRenderer:
    """
    Renderer which serializes to XML.
    """

    media_type = "application/xml"
    charset = "utf-8"
    item_tag_name = "list-item"
    root_tag_name = "root"
    xsd_schema = None
    indent = 4
    cdata = True

    text_name = "#text"
    attrs_name = "#attrs"
    # todo attrs startswith '@'

    def render(
        self, data, root_attrs=None, parent_tag_name=None, xsd_schema=None, indent=4
    ):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""

        stream = StringIO()

        root_attrs = root_attrs or {}
        if xsd_schema:
            root_attrs.update(
                {
                    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                    "xsi:schemaLocation": xsd_schema,
                }
            )

        xml = XMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, root_attrs)

        # if isinstance(data, list) and view:
        #     parent_tag_name = view.get_queryset().model._meta.model_name

        if parent_tag_name and isinstance(data, list):
            xml.startElement(list_name(parent_tag_name), {})
            self._to_xml(xml, data, parent_tag_name)
            xml.endElement(list_name(parent_tag_name))
        else:
            self._to_xml(xml, data, parent_tag_name)

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        text = stream.getvalue()
        if indent:

            parser = etree.XMLParser(
                resolve_entities=False, strip_cdata=False, encoding="utf-8"
            )
            stream = BytesIO(smart_bytes(text))
            document = etree.parse(stream, parser)
            stream = BytesIO()
            document.write(stream, pretty_print=True, encoding="utf-8")
            text = smart_str(stream.getvalue(), encoding="utf-8")
        # if view and view.request.GET.get('_xsd_validate') and xsd_schema:
        #     xsd = etree.XMLSchema(etree.parse(io.BytesIO(requests.get(xsd_schema).content)))
        #     list(etree.iterparse(io.BytesIO(smart_bytes(text)), schema=xsd))
        return text

    def _to_dict_attributes(self, xml, data, parent_tag_name):
        _data = {attribute_name(k): smart_str(v) for k, v in six.iteritems(data)}
        xml.startElement(list_item_name(parent_tag_name), _data)
        xml.endElement(list_item_name(parent_tag_name))

    def _split_attrs(self, data):
        value = dict(data)
        attrs = {}
        for k in list(value):
            if k.startswith("@"):
                attrs[k[1:]] = value.pop(k)

        return value, attrs

    def _to_list(self, xml, data, parent_tag_name):
        parent_tag_name = parent_tag_name or self.item_tag_name
        for item in data:
            self._to_xml(xml, item, parent_tag_name)

    def _to_xml(self, xml, data, parent_tag_name=None):
        if isinstance(data, (list, tuple)):
            self._to_list(xml, data, parent_tag_name)
        elif data is None:
            # Don't output any value
            pass
        elif isinstance(data, dict):
            _data, _attrs = self._split_attrs(data)
            _attrs.update(_data.pop(self.attrs_name, {}))
            if _attrs:
                _text = _data.pop(self.text_name, None)
                if _text:
                    _attrs.update(_data)
                elif _text is None:
                    _text = _data
                _attrs = {
                    attribute_name(k): smart_str(v) for k, v in six.iteritems(_attrs)
                }
                xml.startElement(tag_name(parent_tag_name), _attrs)
                self._to_xml(xml, _text, parent_tag_name=parent_tag_name)
                xml.endElement(tag_name(parent_tag_name))
            else:
                for key, value in six.iteritems(data):
                    attrs = {}
                    if isinstance(value, dict):
                        value, attrs = self._split_attrs(value)
                    if is_to_attributes(value):
                        _text = value.pop(self.text_name, None)
                        attrs = {
                            attribute_name(k): smart_str(v)
                            for k, v in six.iteritems(value)
                        }
                        value = _text
                    if key == self.attrs_name:
                        key = parent_tag_name
                    if isinstance(value, (list, tuple)) and len(data) == 1:
                        # Единственный список
                        self._to_list(xml, value, key)
                    else:
                        xml.startElement(tag_name(key), attrs)
                        self._to_xml(xml, value, parent_tag_name=key)
                        xml.endElement(tag_name(key))

        else:
            data = smart_str(data)
            need_cdata = self.cdata or "<" in data or ">" in data or "&" in data

            if need_cdata:
                xml.cdata(data)
            else:
                xml.characters(data)
