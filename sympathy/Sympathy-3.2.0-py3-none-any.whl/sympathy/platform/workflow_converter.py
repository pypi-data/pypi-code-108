# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Convert workflow files between JSON and XML formats. This tool is intended
to be used internally by the Sympathy platform.
"""
from xml.etree import ElementInclude
import sys
import os
import json
import argparse
import inspect
import traceback
import functools
import itertools

from lxml import etree

from . import exceptions
from .. utils import uuid_generator
from .. utils import prim
from .. utils import log


logger = log.get_logger('core.syx')

ns = 'http://www.sysess.org/sympathyfordata/workflow/1.0'


def xml_format_detector(source):
    """Parse source file to discover file format."""
    text = source.read()
    source.seek(0)
    file_format = 'unknown'
    if text.find(ns) >= 0:
        file_format = 'xml-1.0'
    elif (text.find('sympathy-document') >= 0 and
          text.find('gui_graph') >= 0):
        file_format = 'xml-alpha'
    elif text.find('sympathy-document') >= 0:
        file_format = 'xml-0.4'
    print('Detected format {}'.format(file_format))
    return file_format


class ToJsonInterface(object):
    """Interface for converters from XML to JSON/dict"""

    def __init__(self, xml_file):
        self._xml_file = xml_file

    def json(self):
        """Return a JSON representation of the XML file"""
        raise NotImplementedError('Not implemented for interface.')

    def dict(self):
        """Return a dict representation of the XML file"""
        raise NotImplementedError('Not implemented for interface.')


class ToXmlInterface(object):
    """Interface for converters from dict to xml"""

    def xml(self):
        """Return a XML data representation"""
        raise NotImplementedError('Not implemented for interface.')


class JsonToXml(ToXmlInterface):
    """Convert from JSON structure to XML using xml.dom.miniom"""

    # Default values will not be written to xml.
    default_dict = {
        'optional': False
    }

    def __init__(self):
        super(JsonToXml, self).__init__()

    @classmethod
    def from_file(cls, json_file):
        """Create class instance from a JSON file"""
        instance = cls()
        instance._json_data = json.load(json_file)
        return instance

    @classmethod
    def from_dict(cls, dictionary):
        """Create class instance from a Python dictionary"""
        instance = cls()
        instance._json_data = dictionary
        return instance

    def xml(self):
        flow = self._flow_to_xml(None, self._json_data)
        return etree.tostring(
            flow, xml_declaration=True, pretty_print=True, encoding='US-ASCII')

    def _flow_to_xml(self, parent, data, depth=0):
        """
        Flow helper

        Parameters:
        depth: int
           The depth of the <flow> tag in the xml tree, with the root flow
           being at depth=0.
        """
        self_linked = data.get('is_linked', False)
        is_linked = self_linked and parent is not None

        # Determine the kind of flow. It will affect how it gets written.
        node_id = data.get('node_id')
        href = data.get('source')
        library_id = data.get('id')
        node_id = data.get('node_id')
        is_subflow = bool(depth or 0)

        # Validate consistency and fix issues up front.

        if is_subflow:
            if library_id and not node_id:
                logger.error(
                    'Only root flows can have library identifier.')

            if is_linked:
                if not (node_id or href):
                    logger.error('Linked subflow must have id or href.')
                    is_linked = False
            else:
                if node_id or href:
                    logger.error(
                        'Only linked flows should have a node identifier.')

            if node_id:
                href = None

            library_id = None
        else:
            if is_linked:
                logger.error('Root flow can not be linked.')
            elif not self_linked and (node_id or href):
                logger.error(
                    'Only linked flows should have a node identifier.')

            node_id = None
            href = None
            is_linked = False

        cls = data.get('cls')
        node_type = 'root_flow'

        if cls == 'flow':
            node_type = 'root_flow'
            if is_linked:
                node_type = 'linked_flow'
        else:
            node_type = 'cls'

        attribs_ = ['cls', 'uuid', 'tag']

        if parent is not None:
            # This is a subflow:
            attribs_ += ['x', 'y', 'source_uuid']

        if not is_linked and data.get('is_locked'):
            attribs_.append('is_locked')

        required_elements_ = ['label']
        optional_elements_ = [
            'description', 'documentation', 'author', 'copyright', 'version']

        if not is_linked:
            optional_elements_.append('icon')

        json_elements = ['libraries', 'pythonpaths', 'environment',
                         'overrides']
        if parent is not None:
            flow = etree.SubElement(parent, "flow")
        else:
            flow = etree.Element("flow", attrib={'xmlns': ns})
        self._add_attributes(flow, data, attribs_)

        if node_id:
            flow.set('id', str(node_id))

        if href:
            flow.set('href', str(href))

        if library_id:
            flow.set('id', str(library_id))

        self._add_text_elements(flow, data, required_elements_)
        self._add_text_elements(flow, data, optional_elements_, optional=True)

        if data.get('aggregation_settings'):
            self._json_element_to_xml(
                'aggregation', flow, data['aggregation_settings'],
                depth=depth+1)

        self._add_json_elements(flow, data, json_elements, depth=depth+1)

        # Environment is also sent inside parameters for legacy reasons, but we
        # don't want to write that.
        #
        # TODO(erik): data uses the same parameters dict as the flow itself,
        # and mutating it will also affect the flow! Either disallow mutations
        # or ensure that to_dict returns a deep copy.
        params = dict(data.get('parameters', {}))
        params.pop('environment', None)
        if not is_linked and params:
            param_data = {k: v for k, v in params.items() if v}
            if param_data:
                self._json_element_to_xml(
                    'parameters', flow, param_data, depth=depth+1)

        if 'ports' in data:
            self._ports_to_xml(flow, data['ports'], is_linked=is_linked)

        if is_subflow and 'basic_ports' in data:
            basic_ports = data['basic_ports']
            if basic_ports.get('inputs') or basic_ports.get('outputs'):
                self._ports_to_xml(flow, data['basic_ports'], 'basic_ports')

        if not is_linked:
            converters = (
                ('flows', functools.partial(self._flow_to_xml, depth=depth+1)),
                ('nodes', functools.partial(self._node_to_xml, depth=depth+1)),
                ('connections', self._connection_to_xml),
                ('textfields', self._textfield_to_xml))

            for field, converter in converters:
                if field == 'textfields':
                    # The textfields cannot be sorted according to uuid,
                    # since the ordering in the flow depends on the saved
                    # order.
                    elements = data.get(field, [])
                else:
                    elements = sorted(
                        data.get(field, []), key=lambda x: x['uuid'])
                for elem in elements:
                    converter(flow, elem)

        return flow

    def _add_text_elements(self, flow, data, element_list, optional=False):
        """Create text nodes"""
        for elem in element_list:
            elem_data = data.get(elem)
            if elem_data or not optional:
                text_node = etree.SubElement(flow, elem)
                text_node.text = elem_data

    def _add_json_elements(self, flow, data, element_list, depth):
        """Create cdata nodes only for existing stuff."""
        for elem in element_list:
            elem_data = data.get(elem)
            if elem_data:
                self._json_element_to_xml(elem, flow, data[elem], depth=depth)

    def _add_attribute(self, node, value, attrib):
        node.set(attrib, str(value))

    def _add_attributes(self, node, data, attribute_list, defaults=None):
        """Attriubute helper"""
        defaults = defaults or {}
        for attrib in sorted(attribute_list):
            if attrib in data:
                value = data[attrib]
                if not (attrib in defaults and defaults[attrib] == value):
                    self._add_attribute(node, value, attrib)

    def _ports_to_xml(self, flow, data, ports_ns='ports', is_linked=None):
        """Port helper"""
        ports = etree.SubElement(flow, ports_ns)

        attribs_ = ['uuid', 'source_uuid', 'index', 'type_base', 'type',
                    'x', 'y', 'key', 'scheme']

        if not is_linked:
            attribs_.extend(['parent', 'optional'])

        elements_ = ['label']

        for tag, port_data_list in zip(('input', 'output'),
                                       (data['inputs'], data['outputs'])):
            for port_data in port_data_list:
                port_data['label'] = port_data['description']
                port_data['key'] = port_data['name']
                port = etree.SubElement(ports, tag)
                self._add_attributes(
                    port, port_data, attribs_, defaults=self.default_dict)
                self._add_text_elements(port, port_data, elements_)

    def _node_to_xml(self, flow, data, depth):
        """
        Node helper

        Parameters:
        depth: int
           The depth of the <node> tag in the xml tree.
        """
        attribs_ = ['uuid', 'id', 'x', 'y', 'port_format', 'only_conf']
        elements_ = ['label', 'version', 'description', 'author', 'copyright']
        optional_elements = ['original_nodeid']

        node = etree.SubElement(flow, 'node')
        self._add_attributes(node, data, attribs_)
        self._add_text_elements(node, data, elements_)
        # Add version also as a min_version field. Keep writing 'version' field
        # only to satisfy older sympathy releases that require it.
        self._add_text_elements(
            node, {'min_version': data.get('version')}, ['min_version'])
        self._add_text_elements(node, data, optional_elements, optional=True)

        if 'parameters' in data:
            self._json_element_to_xml(
                'parameters', node, data['parameters']['data'], depth=depth+1)
        if 'ports' in data:
            self._ports_to_xml(node, data['ports'])

    def _connection_to_xml(self, flow, data):
        """Connection helper"""
        attribs_con = ['uuid']
        attribs_port = ['node', 'port']
        attribs_route = ['x', 'y']

        # TODO(erik): Check assumption, the type can be None.
        ctype = data.get('type')
        if ctype:
            attribs_con.append('type')
        else:
            logger.warning(
                "Invalid or missing connection type for %s is None",
                data.get('uuid'))

        connection = etree.SubElement(flow, 'connection')
        self._add_attributes(connection, data, attribs_con)
        for tag in ['source', 'destination']:
            port_data = data[tag]
            port = etree.SubElement(connection, tag)
            self._add_attributes(port, port_data, attribs_port)

        tag = 'route'
        for route_data in data[tag]:
            route = etree.SubElement(connection, tag)
            self._add_attributes(route, route_data, attribs_route)

    def _textfield_to_xml(self, flow, data):
        """Textfield helper"""
        attribs_ = ['uuid', 'width', 'height', 'x', 'y', 'color']
        textfield = etree.SubElement(flow, 'text')
        self._add_attributes(textfield, data, attribs_)
        if 'text' in data and data['text']:
            textfield.text = data['text']
        else:
            textfield.text = ''

    def _json_element_to_xml(self, name, parent, data, depth):
        """
        Pretty print and indent json data to fit into the xml document.

        Parameters:
        name: dict
           The name of the xml tag that should hold the json data
        data: dict
           The json data
        depth: int
           The depth of the <parameters> tag in the xml tree.
        """
        element = etree.SubElement(parent, name)
        element.set('type', 'json')

        # If the json structure is very small it should be printed on one line:
        plain_json_dump = json.dumps(data)
        if len(plain_json_dump) <= 80:
            element.text = plain_json_dump
            return

        def prettify_json_params(data, depth=0):
            """
            Pretty print parameter structures. Main differences from
            json.dumps(indent=2) is that lists are always printed on a single
            line and the key 'description' is skipped entirely.
            """
            base_indent = 2*depth*' '
            inner_indent = base_indent + '  '
            if isinstance(data, dict):
                type_ = data.get('type')
                lines = []
                for k, v in sorted(data.items()):
                    if k == 'description' and type_ != 'json':
                        continue
                    elif k == 'value' and type_ == 'json':
                        value_string = json.dumps(v)
                    else:
                        value_string = prettify_json_params(v, depth=depth+1)
                    lines.append('{}{}: {}'.format(
                        inner_indent, json.dumps(k), value_string))
                inner = ',\n'.join(lines)
                return '\n'.join(['{', inner, base_indent + '}'])
            else:
                return json.dumps(data)

        # Parameters get extra special treatment:
        if name in ['parameters', 'overrides']:
            prettify = prettify_json_params
        else:
            prettify = functools.partial(json.dumps, indent=2, sort_keys=True)

        # Extra new lines put the parameters on separate lines from the
        # surrounding xml tags. Extra indentation makes sure that it matches
        # the xml and that the closing xml tag is on the same level as the
        # opening one.
        text = '\n' + prettify(data) + '\n'
        indent = 2*depth*' '
        text = text.replace('\n', '\n' + indent)

        element.text = text


def update_broken_link_content(parent_dict):
    parent_dict['type'] = 'flow'
    parent_dict['parameters'] = {'type': 'json', 'data': {}}


def update_link_content(parent_dict, child_dict, child_filename,
                        rel_child_filename=None):
    child_dict['source_label'] = child_dict['label']
    child_dict['label'] = parent_dict.get('label', '')
    child_dict['overrides'] = parent_dict.get('overrides', {})

    if not rel_child_filename:
        rel_child_filename = child_filename

    child_dict['source'] = rel_child_filename
    child_dict['filename'] = child_filename
    child_dict['is_linked'] = True
    child_dict['basic_ports'] = parent_dict.get('basic_ports', {})
    update_link_ports(parent_dict, child_dict)


def update_link_ports(parent_dict, child_dict):
    def ports_iter(content_dict):
        return itertools.chain(
            content_dict['ports']['inputs'],
            content_dict['ports']['outputs'])

    child_lookup = {}
    for p in ports_iter(child_dict):
        child_lookup[p['uuid']] = p

    parent_lookup = {}
    for p in ports_iter(parent_dict):
        parent_lookup[p['source_uuid']] = p

    for child_port in ports_iter(child_dict):
        parent_port = parent_lookup.get(child_port.get('uuid'))

        child_port['source_uuid'] = child_port['uuid']

        if parent_port:
            child_port['uuid'] = parent_port['uuid']

            child_port['source_parent'] = child_port.get('parent', True)
            if child_port.get('optional'):
                child_port['parent'] = parent_port.get('parent', True)
        else:
            child_port['source_uuid'] = child_port['uuid']
            # Ensure generation of new UUID.
            child_port['uuid'] = uuid_generator.generate_uuid()

            child_port['source_parent'] = child_port.get('parent', True)

            if child_port.get('optional'):
                child_port['parent'] = False

    child_dict['source_uuid'] = child_dict['uuid']
    child_dict['uuid'] = parent_dict['uuid']


_dict_child_elements = ['flows', 'nodes', 'connections', 'textfields']
_xml_child_elements = ['flow', 'node', 'connection', 'text']


class XMLToJson(ToJsonInterface):
    """Convert from XML to JSON"""

    type_dict = {
        'uuid': str,
        'id': lambda x: str(x or ''),
        'label': lambda x: str(x).strip(),
        'description': lambda x: str(x).strip(),
        'documentation': lambda x: str(x).strip(),
        'author': lambda x: str(x).strip(),
        'only_conf': lambda x: x.lower() == 'true',
        'copyright': lambda x: str(x).strip(),
        'version': lambda x: str(x).strip(),
        'min_version': lambda x: str(x).strip(),
        'original_nodeid': lambda x: str(x).strip(),
        'icon': lambda x: str(x).strip(),
        'is_locked': lambda x: x.lower() == 'true',
        'source': lambda x: str(x).strip(),
        'source_uuid': str,
        'x': float,
        'y': float,
        'width': float,
        'height': float,
        'port_format': str,
        'color': str,
        'index': int,
        'type': str,
        'type_base': str,
        'key': lambda x: str(x).strip(),
        'scheme': str,
        'docs': str,
        'optional': lambda x: x.lower() == 'true',
        'parent': lambda x: x.lower() == 'true',
        'node': str,
    }

    def __init__(self, xml_file):
        super(XMLToJson, self).__init__(xml_file)
        etree.clear_error_log()
        try:
            parser = etree.XMLParser(huge_tree=True)
            self._doc = etree.parse(xml_file, parser)
        except etree.XMLSyntaxError as e:
            log_text = str(
                e.error_log.filter_from_level(etree.ErrorLevels.FATAL))
            raise exceptions.ReadSyxFileError(
                u"Corrupt flow file.", log_text)
        self._xml_filename = xml_file.name
        self._file_root = os.path.dirname(xml_file.name)
        self._root = self._doc.getroot()

        self._all_nodes = {}
        self._all_parameters = {}

    def _url_loader(self, href, parse, root, encoding=None):
        """
        Loader for ElementInclude that handles relative paths and http includes
        """
        try:
            return ElementInclude.default_loader(
                os.path.join(root, href), parse, encoding)
        except Exception:
            return None

    def _node_to_dict(self, node, path):
        """
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941b16",
            "x": 100,
            "y": 200,
            "id": "myid1",
            "label": "MyLabel",
            "author": "Greger Cronquist <greger.cronquist@combine.se>",
            "copyright": "(c) 2013 Combine Control Systems AB",
            "description": "Longer description should that be necessary",
            "docs": "file://document.html",
            "version": "1.0",
            "original_nodeid": "myid0",
            "ports": {
                "inputs": [...],
                "outputs": [..]
            }
            "parameters": ...
        }
        """
        contents = self._get_standard_node_data(node, path)
        # Ignore 'version' field, use 'min_version' field instead.
        contents['version'] = contents.pop('min_version', None)
        self._all_nodes['{}.{}'.format(path, contents['uuid'])] = contents
        return contents

    def _add_ns(self, tag):
        """Add XML namespace to tag"""
        return '{{{}}}{}'.format(ns, tag)

    def _get_standard_node_data(self, element, path):
        """Common attributes helper for nodes and flows."""
        contents = {}
        for tag in ['author', 'label', 'description', 'documentation',
                    'copyright', 'version', 'docs', 'min_version', 'icon',
                    'original_nodeid']:
            elems = element.findall(self._add_ns(tag))
            if len(elems) > 0:
                if elems[0].text:
                    text = self.type_dict[tag](elems[0].text)
                else:
                    text = ''
                contents[tag] = text

        for attribute in ['uuid', 'id', 'x', 'y', 'only_conf', 'port_format',
                          'is_locked']:
            if attribute in element.attrib:
                contents[attribute] = self.type_dict[
                    attribute](element.attrib[attribute])

        ports_ = element.findall(self._add_ns('ports'))
        if len(ports_) > 0:
            contents['ports'] = self._ports_to_dict(ports_[0])
        basic_ports_ = element.findall(self._add_ns('basic_ports'))
        if len(basic_ports_) > 0:
            contents['basic_ports'] = self._ports_to_dict(basic_ports_[0])
        params = element.findall(self._add_ns('parameters'))
        if len(params) > 0:
            contents['parameters'] = self._parameters_to_dict(
                params[0], '{}.{}'.format(path, contents['uuid']))

        return contents

    def _include_subflow(self, root, href):
        included_flow = self._url_loader(href, 'xml', root)
        return included_flow

    def _get_attrib(self, element, attrib):
        value = element.attrib.get(attrib)
        if value is not None:
            return self.type_dict[attrib](value)

    def _flow_to_dict(self, flow, path, root, is_subflow=False):
        """
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941b16",
            "x": 100.0,
            "y": 200.0,
            "id": "myid1",
            "label": "MyLabel",
            "author": "Greger Cronquist <greger.cronquist@combine.se>",
            "copyright": "(c) 2013 Combine Control Systems AB",
            "description": "Longer description should that be necessary",
            "docs": "file://document.html",
            "source": "file://OriginalSourceFile.syx",
            "is_linked": False,
            "version": "1.0",
            "parameters": {},
            "aggregation_settings": {},
            "overrides": {},
            "ports": {
                "inputs": [...],
                "outputs": [..]
            },
            "flows": [ flows... ],
            "nodes": [ nodes... ],
            "connections": [
                {
                    "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941c19",
                    "source": {
                        "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b17",
                        "port": "fbbdc405-bb8a-4ad7-b3ac-a52649941b17"
                    },
                    "destination": {
                        "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b11",
                        "index": 0
                    }
                }
            ]
            "parameters": ...
        }
        """

        def check_consistency(xml_flow):
            source_link = xml_flow.attrib.get('href')
            library_link = xml_flow.attrib.get('id')

            empty_source_link = not source_link and source_link is not None
            empty_library_link = not library_link and library_link is not None
            if empty_source_link:
                logger.warning("Flow contains empty href")
            if empty_library_link:
                # Commented to avoid excessive output for wide range of flows.
                # logger.debug("Flow contains empty id")
                pass

            is_linked = is_subflow and (source_link or library_link)

            res = []

            if is_linked:
                elems = []
                for k in _xml_child_elements:
                    if xml_flow.find(self._add_ns(k)) is not None:
                        elems.append(k)
                if elems:
                    res.append(
                        'Removed unexpected child elements from linked '
                        'subflow.')
                    logger.error(
                        'Inconsistent flow, linked flow xml contains: '
                        '%s elements', ', '.join(elems))
            else:
                if 'source_uuid' in flow.attrib:
                    res.append(
                        'Removed unexpected source_uuid from normal subflow')
                    logger.error(
                        'Inconsistent flow, source_uuid is set for '
                        'non-linked flow')

            if source_link and library_link:
                res.append(
                    'Removed file link from subflow linked as library node.')
                logger.error(
                    'Inconsistent flow, flow should be linked via id or '
                    'href, not both')

            return res

        new_root = root

        # Read linked flow.
        contents_ = self._get_standard_node_data(flow, path)
        contents_['xml_convert'] = check_consistency(flow)

        attrib_key = 'source_uuid'
        attrib_val = self._get_attrib(flow, attrib_key)
        if attrib_val is not None:
            contents_[attrib_key] = attrib_val

        contents_['tag'] = flow.get('tag', '')
        contents_['is_locked'] = (
            True if (flow.get('is_locked', 'False')) == 'True' else False)
        contents_['cls'] = flow.get('cls', 'Flow')

        source_link = flow.get('href')
        library_id = flow.get('id')
        library_link = library_id

        is_linked = is_subflow and (source_link or library_link)

        if is_linked:
            overrides = flow.findall(self._add_ns('overrides'))
            if len(overrides) > 0:
                contents_['overrides'] = self._json_element_to_dict(
                    overrides[0])

            if source_link and library_link:
                # Prefer library links.
                source_link = None

            for k in _dict_child_elements:
                contents_[k] = []
        else:
            contents_.pop('source_uuid', None)

        if source_link:
            linked_flow = self._include_subflow(root, source_link)

            if linked_flow is None:
                contents = contents_
                contents['broken_link'] = True
                contents['source'] = source_link
                contents['filename'] = os.path.normpath(
                    os.path.join(root, source_link))
                contents['is_linked'] = True
            else:
                new_root = os.path.join(root, os.path.dirname(source_link))
                contents = self._get_standard_node_data(linked_flow, path)

                for key in ('x', 'y'):
                    contents[key] = contents_[key]

                update_link_content(contents_, contents,
                                    os.path.normpath(
                                        os.path.join(root, source_link)),
                                    source_link)
                flow = linked_flow

                if contents['uuid'] in path:
                    raise exceptions.LinkLoopError(
                        u"Corrupt flow file.",
                        u"Corrupt flow file with duplicate uses of uuid {} in "
                        u"path, likely caused by linked subflow loops."
                        .format(contents['uuid']))
        else:
            contents = contents_

        aggregation_settings = flow.findall(self._add_ns('aggregation'))
        if len(aggregation_settings) > 0:
            contents['aggregation_settings'] = self._json_element_to_dict(
                aggregation_settings[0])

        for elem in ['libraries', 'pythonpaths', 'environment']:
            data = flow.findall(self._add_ns(elem))
            if len(data) > 0:
                contents[elem] = self._json_element_to_dict(data[0])

        if len(path) > 0:
            new_path = '{}.{}'.format(path, contents['uuid'])
        else:
            new_path = contents['uuid']

        try:
            flows = [self._flow_to_dict(flow_, new_path, new_root,
                                        is_subflow=True)
                     for flow_ in flow.findall(self._add_ns('flow'))]
        except exceptions.LinkLoopError:
            contents['broken_link'] = True

            for k in _dict_child_elements:
                contents[k] = []
        else:
            contents['flows'] = flows
            contents['nodes'] = [
                self._node_to_dict(node, new_path)
                for node in flow.findall(self._add_ns('node'))]

            contents['connections'] = [
                self._connection_to_dict(connection, new_path)
                for connection in flow.findall(
                        self._add_ns('connection'))]

            contents['textfields'] = [
                self._textfield_to_dict(textfield, new_path)
                for textfield in flow.findall(
                        self._add_ns('text'))]
        return contents

    def _ports_to_dict(self, ports):
        """
        "ports": {
            "inputs": [...],
            "outputs": [..]
        }

        input/output:
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941b16",
            "index": "0",
            "type": "table",
            "scheme": "hdf5",
            "optional": False,
            "label": "Input 1"
            "key": "Input 1"
        }
        """
        contents = {}
        inputs = []
        outputs = []

        for tag, list_ in zip(['input', 'output'], [inputs, outputs]):
            for value in ports.findall(self._add_ns(tag)):
                port = {}
                for attribute in ['uuid', 'type', 'type_base', 'scheme',
                                  'index', 'parent', 'optional', 'x', 'y',
                                  'width', 'height', 'key', 'source_uuid']:
                    if attribute in value.attrib:
                        port[attribute] = self.type_dict[
                            attribute](value.attrib[attribute])
                if 'key' in port:
                    port['name'] = port['key']

                label = value.findall(self._add_ns('label'))
                if len(label) > 0:
                    port['description'] = (
                        self.type_dict['label'](label[0].text))
                list_.append(port)

        contents['inputs'] = inputs
        contents['outputs'] = outputs
        return contents

    def _parameters_to_dict(self, parameters, path):
        """
        {
            "type": "json",
            "data": base64 blob
        }
        """
        contents = {}
        node_path = path
        if 'node' in parameters.attrib:
            node_path += '.{}'.format(parameters.attrib['node'])

        contents['type'] = parameters.attrib['type'].strip()
        data = parameters.text.strip()
        contents['data'] = json.loads(data)

        self._all_parameters[node_path] = contents

        return contents

    def _json_element_to_dict(self, json_element):
        data = json_element.text.strip()
        contents = json.loads(data)
        return contents

    def _connection_to_dict(self, connection, path):
        """
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941c19",
            "source": {
                "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b17",
                "port": "fbbdc405-bb8a-4ad7-b3ac-a52649941b18"
            },
            "destination": {
                "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b18",
                "port": "fbbdc405-bb8a-4ad7-b3ac-a52649981b16"
            }
        }
        """
        contents = {}
        source = {}
        destination = {}
        contents['uuid'] = connection.attrib['uuid']
        contents['type'] = connection.attrib.get('type')

        for dict_, tag in zip([source, destination],
                              ['source', 'destination']):
            port = connection.findall(self._add_ns(tag))[0]
            dict_['node'] = port.attrib['node']
            dict_['port'] = port.attrib['port']
            contents[tag] = dict_

        routes = []
        tag = 'route'
        contents[tag] = routes
        for route in connection.findall(self._add_ns(tag)):
            routes.append({'x': float(route.attrib['x']),
                           'y': float(route.attrib['y'])})
        return contents

    def _textfield_to_dict(self, textfield, path):
        """
        {
            "height", 10.0,
            "text": "Hello world",
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941c19",
            "width", 10.0,
            "x", 10.0,
            "y", 10.0,
            "color", "yellow"
        }
        """
        contents = {}
        for attrib in ['uuid', 'x', 'y', 'height', 'width', 'color']:
            if attrib in textfield.attrib:
                contents[attrib] = self.type_dict[
                    attrib](textfield.attrib[attrib])
        contents['text'] = textfield.text or ''
        return contents

    def _get_tag(self, element):
        """Tag split helper"""
        return element.tag.split('}', 1)[1]

    def _create_dictionary_from_xml(self, element):
        """Main XML parser loop"""
        tag = self._get_tag(element)
        if not tag == 'flow':
            raise RuntimeError('Not a proper workflow')
        all_contents = self._flow_to_dict(element, '', self._file_root)
        for node_path in self._all_parameters:
            if node_path in self._all_nodes:
                self._all_nodes[node_path]['parameters'] = (
                    self._all_parameters[node_path])
        return all_contents

    def json(self):
        return json.dumps(self._create_dictionary_from_xml(self._root),
                          sort_keys=True, separators=(',', ':'))

    def dict(self):
        return self._create_dictionary_from_xml(self._root)


def xml_file_to_xmltojson_converter(fq_xml_filename):
    """Simple XML to JSON parser helper"""
    to_json_converter = None
    with open(fq_xml_filename, 'r') as source_file:
        source_format = xml_format_detector(source_file)

        if source_format == 'xml-1.0':
            to_json_converter = XMLToJson(source_file)
        else:
            raise NotImplementedError(
                'XML {} not yet supported'.format(source_format))
    assert(to_json_converter is not None)
    return to_json_converter


TO_JSON_FORMAT_CLASSES = {
    'xml-1.0': XMLToJson}


def main():
    """
    Convert between different Sympathy workflow descriptions:

      - From JSON to XML)
      - From XML to JSON
    """
    parser = argparse.ArgumentParser(description=inspect.getdoc(main))
    parser.add_argument('--source-format', action='store',
                        choices=['json', 'xml-1.0',
                                 'detect'], required=True,
                        dest='source_format')
    parser.add_argument('--destination-format', action='store',
                        choices=['json', 'xml-1.0'], required=True,
                        dest='destination_format')
    parser.add_argument('source_file', action='store')
    parser.add_argument('destination_file', action='store')

    session = os.getenv('SY_TEMP_SESSION')
    if session is None:
        session = '.'
    return_code = 0
    with open(os.path.join(session, 'workflow_converter.log'), 'wb') as log:
        stdout = sys.stdout
        sys.stdout = log
        write_is_allowed = False
        arguments = parser.parse_args(sys.argv[1:])
        with open(arguments.source_file, 'rb') as source:
            source_format = arguments.source_format
            destination_format = arguments.destination_format
            try:
                if (source_format == 'detect' and
                        destination_format == 'json'):
                    source_format = xml_format_detector(source)

                if source_format == 'json':
                    if destination_format == 'xml-1.0':
                        to_xml_converter = JsonToXml.from_file(source)
                        output_data = to_xml_converter.xml()
                        write_is_allowed = True
                    else:
                        print('Conversion {} -> {} not yet supported'.
                              format(source_format, destination_format))
                elif destination_format == 'json':
                    if source_format in TO_JSON_FORMAT_CLASSES:
                        to_json_converter = TO_JSON_FORMAT_CLASSES[
                            source_format](source)
                    else:
                        print('Conversion {} -> {} not yet supported'.
                              format(source_format, destination_format))
                    output_data = to_json_converter.json()
                    write_is_allowed = True

                else:
                    print('Conversion {} -> {} not yet supported'.format(
                          source_format,
                          destination_format))

            except Exception as error:
                print('workflow_converter critical error {0}'.format(error))
                print(traceback.format_exc())
                return_code = 1

            if write_is_allowed:
                with open(arguments.destination_file, 'wb') as destination:
                    destination.write(output_data.encode('UTF-8'))

        sys.stdout = stdout
    sys.exit(return_code)


def icon_dirs_path(icon, icon_dirs):
    for icon_dir in icon_dirs:
        icon_path = os.path.join(icon_dir, icon)
        if os.path.exists(icon_path):
            return icon_path


def get_flow_data(syx_flow):
    """
    Get node data dict from flow.
    """
    properties = {}
    flow_dir = os.path.dirname(syx_flow)
    flow_name = os.path.basename(syx_flow)

    try:

        with open(syx_flow, 'rb') as f:
            flow_dict = XMLToJson(f).dict()
            icon = flow_dict.get('icon')
            name = flow_dict.get('label') or flow_name
            properties['label'] = name

            if icon:
                icon_path = icon_dirs_path(icon, [flow_dir])
                if icon_path:
                    properties['icon'] = prim.localuri(icon_path)
                else:
                    exceptions.sywarn(f"Couldn't find icon for node {name}")

            for key in ['author', 'copyright', 'description', 'version']:
                properties[key] = flow_dict.get(key)

            properties['file'] = prim.localuri(syx_flow)
            properties['type'] = 'flow'
            properties['id'] = flow_dict['id']
            # Empty values to conform better to node-library interface.
            properties['ports'] = dict(flow_dict.get('ports', {}))
            properties['parameters'] = {}
            properties['tags'] = [flow_dict.get('tag')]

        return properties
    except Exception:
        return None


if __name__ == '__main__':
    main()
