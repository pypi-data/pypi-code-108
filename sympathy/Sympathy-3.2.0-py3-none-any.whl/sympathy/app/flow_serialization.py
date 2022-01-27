# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import json
import os.path

import Qt.QtCore as QtCore
from packaging.version import Version

from sympathy.platform import workflow_converter, node_result
import sympathy.platform.exceptions as platform_exc
from sympathy.utils import uuid_generator, log
from sympathy.utils.prim import uri_to_path, absolute_paths
from sympathy.platform.migrations import epoch_version

from . import library
from . import version
from . flow.types import Type
from . flow.exceptions import SyInferTypeError
import sympathy.app.util
import sympathy.app.user_commands

logger = log.get_logger('core.flowdict')


def partial_dict(flow, element_list):
    """
    Serialize flow structure containing selected elements.

    Parameters
    ----------
    flow: sympathy flow
        Parent flow of the selected elements.
    element_list:
        Elements selected for inclusion in the output.

    Returns
    -------
    dict
        Serialization of the flow suitable for the clipboard,
        limited to the selected elements. Normally used as dictionary
        by the FlowDeserializer.
    """

    def in_port_uuid(port, uuids):
        return (
            uuid_generator.join_uuid(
                port['namespace_uuid'],
                port['uuid']) in uuids or
            uuid_generator.join_uuid(
                port['namespace_uuid'],
                port['source_uuid']) in uuids)

    x_min = x_max = y_min = y_max = 0
    if element_list:
        positions = [(e.position.x(), e.position.y())
                     for e in element_list]
        x_min = min([p[0] for p in positions])
        x_max = max([p[0] for p in positions])
        y_min = min([p[1] for p in positions])
        y_max = max([p[1] for p in positions])

    # Create a serialization (suitable for copying) of the entire flow
    # TODO(erik): remove unnecessary, or even harmful top-level elements. For
    # example, linked status or identifier. This can take place directly in
    # to_copy_dict.
    flow_dict = flow.to_copy_dict(base_node_params=False)
    element_uuids = []
    for e in element_list:
        if e.type == Type.Flow:
            element_uuids.append(e.full_link_uuid)
        else:
            if e.type in [Type.FlowInput, Type.FlowOutput]:
                element_uuids.append(e.port.full_uuid)
                if e.is_linked:
                    element_uuids.append(
                        uuid_generator.join_uuid(
                            e.namespace_uuid(), e.source_uuid))

            element_uuids.append(e.full_uuid)

    # Remove parts of the serialization that were not selected or can't be
    # copied (such as connections)
    flow_dict['nodes'] = [
        node for node in flow_dict['nodes']
        if node['full_uuid'] in element_uuids]
    flow_dict['flows'] = [
        node for node in flow_dict['flows']
        if node['full_uuid'] in element_uuids]
    flow_dict['textfields'] = [
        node for node in flow_dict['textfields']
        if node['full_uuid'] in element_uuids]
    flow_dict['connections'] = [
        connection for connection in flow_dict['connections']
        if (uuid_generator.join_uuid(
            connection['namespace_uuid'],
            connection['source']['node']) in element_uuids and
            uuid_generator.join_uuid(
                connection['namespace_uuid'],
                connection['destination']['node']) in element_uuids)]
    flow_dict['ports'] = {
        'inputs': [ip for ip in flow_dict['ports'].get('inputs', [])
                   if in_port_uuid(ip, element_uuids)],

        'outputs': [op for op in flow_dict['ports'].get('outputs', [])
                    if in_port_uuid(op, element_uuids)]}

    # TODO: Exclude items not used in paste, see _build_flow.
    # Might be easier to specify what to include than what to exclude.
    flow_dict.pop('basic_ports', None)
    return {
        'flow': flow_dict,
        'center': {
            'x': x_min + (x_max - x_min) / 2.0,
            'y': y_min + (y_max - y_min) / 2.0}}


def update_uuids_in_group(group, uuid_to_new_uuid, new_uuids):
    """
    Recursively traverse the 'group_structure' part of an aggregation settings
    dictionary and update all uuids.

    :param group: Dictionary with the group_structure part of the aggregation
    settings for a subflow.
    :param uuid_to_new_uuid: Dictionary mapping old node uuids to new uuids.
    Group uuids will be added to this dictionary.
    :param new_uuids: If True, generate new uuids for groups.
    """
    if group['type'] == 'group':
        if group['uuid']:
            # Group uuids are not in uuid_to_new_uuid
            if new_uuids:
                uuid_to_new_uuid[group['uuid']] = (
                    uuid_generator.generate_uuid())
            else:
                uuid_to_new_uuid[group['uuid']] = group['uuid']
            group['uuid'] = uuid_to_new_uuid[group['uuid']]
        for g in group['children']:
            update_uuids_in_group(g, uuid_to_new_uuid, new_uuids)
    elif group['type'] == 'node':
        # All node uuids should be in uuid_to_new_uuid
        if group['uuid'] in uuid_to_new_uuid:
            group['uuid'] = uuid_to_new_uuid[group['uuid']]


def _overrides_extra_info(overrides_dict):
    """
    Read "extra_info" part of overrides and make it available in the normal
    overrides dict.
    """
    res = {}
    if overrides_dict is not None:
        extra_info_dict = overrides_dict.pop('__extra_info__', {})
        for id_, overrides in overrides_dict.items():
            res[id_] = {'data': overrides}
            res[id_].update(extra_info_dict.get(id_, {}))
    return res


class FlowDeserializer(object):

    def __init__(self, app_core):
        super(FlowDeserializer, self).__init__()
        self._app_core = app_core
        self._dictionary = {}
        self._xml_file = ''
        self._valid_file = True
        self._created_nodes = []
        self._created_connections = []
        self._init()

    def load_xml_file(self, xml_file):
        if not os.path.isfile(xml_file):
            raise platform_exc.ReadSyxFileError(
                u"File doesn't exist.",
                u"File {} doesn't exist.".format(xml_file))
        with open(xml_file, 'r') as source:
            converter = workflow_converter.XMLToJson(source)
            self._dictionary = converter.dict()
            self._dictionary['filename'] = xml_file

    def load_xml_data(self, xml_data):
        pass

    def load_json_data(self, json_data):
        self._dictionary = json.loads(json_data)

    @classmethod
    def from_dict(cls, dictionary, app_core):
        instance = cls(app_core)
        instance._dictionary = dictionary
        return instance

    @classmethod
    def from_json(cls, json_data, app_core):
        instance = cls(app_core)
        instance.load_json_data(json_data)
        return instance

    def is_valid(self):
        return self._valid_file

    def to_dict(self):
        return self._dictionary

    def created_nodes(self):
        return self._created_nodes

    def created_connections(self):
        return self._created_connections

    def _check_flow_libraries(self, flow_dict, flow, warn_on_errors=None,
                              parent_flow=None):
        def flow_libraries(flow_dict):
            """
            Returns
            -------
            list of dicts
                Flat dictionaries of top level (or linked) flows with
                libraries set. The dictionaries contain a limited set of
                fields relevant for resolving paths and user feedback.
            """

            def info_tree(flow_dict):
                res = {}
                for key in ['filename', 'source', 'libraries', 'label',
                            'source_label']:
                    res[key] = flow_dict.get(key)
                res['flows'] = [info_tree(sub_flow_dict)
                                for sub_flow_dict in flow_dict['flows']]
                return res

            def library_flows(flow_dict):
                res = []
                libraries = flow_dict.get('libraries')
                if 'filename' in flow_dict and libraries:
                    flow_dict_copy = dict(flow_dict)
                    flow_dict_copy.pop('flows', None)
                    flow_dict_copy['abs_libraries'] = absolute_paths(
                        os.path.dirname(flow_dict['filename']), libraries)

                    res.append(flow_dict_copy)

                for sub_flow_dict in flow_dict['flows']:
                    res.extend(library_flows(sub_flow_dict))
                return res

            info = info_tree(flow_dict)
            return library_flows(info)

        def error(exc_cls, libs):
            if libs:
                warn = False
                exc = exc_cls(libs)
                if warn_on_errors:
                    warn = type(exc) in warn_on_errors or any(
                        isinstance(exc, e) for
                        e in warn_on_errors)

                if warn:
                    result = node_result.NodeResult()
                    result.stderr = "Loading: {}. {}".format(
                        flow.display_name, exc.help_text)
                    self._app_core.display_message(
                        sympathy.app.util.NodeResult(flow, result))
                else:
                    raise exc

        warn_on_errors = warn_on_errors or []

        libraries = [sub_lib for lib in
                     flow_libraries(flow_dict)
                     for sub_lib in lib['abs_libraries']]

        parent_flow_libraries = []
        if parent_flow:
            parent_flow_libraries = sympathy.app.util.library_paths(
                flow=parent_flow)

        if libraries:
            conflicts = sympathy.app.util.library_conflicts(
                libraries, parent_flow_libraries=parent_flow_libraries)

            global_conflicts = conflicts.get('global')
            flow_conflicts = conflicts.get('flow')
            internal_conflicts = conflicts.get('internal')

            error(
                platform_exc.ConflictingInternalLibrariesError,
                internal_conflicts)

            error(platform_exc.ConflictingGlobalLibrariesError,
                  global_conflicts)

            error(platform_exc.ConflictingFlowLibrariesError,
                  flow_conflicts)

    def build_flow(self, flow, is_linked=False, warn_on_errors=None,
                   parent_flow=None):

        def inform_duplicate_identifiers(dup_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Duplicate element identifiers in flow:'
                '\n'
                'The flow contains duplicate elements identifiers and may '
                'not be fully recovered. '
                '\n\n'
                'BASIC:'
                '\n'
                'Remove nodes that have lost their connections '
                'or in other ways behave strangely '
                'and add them again redrawing the intended connections. '
                'Afterwards, save the flow.'
                '\n\n'
                'ADVANCED:'
                '\n'
                'Check the duplicate identifiers in the flow file.'
                '\n\n'
                'Duplicate identifiers of type(s): {}.'
                '\n\n'
                'Duplicate identifier(s): {}.'
            ).format(', '.join(dup_probs),
                     ', '.join(ident for v in dup_probs.values()
                               for ident in v))
            return nr

        def inform_lost_connections(conn_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Unable to create some flow connections: '
                'This could be the result of removed ports '
                'or changed port types.\n'
                '\n'
                'Be careful when changing types of ports that are '
                'in use on nodes or flows that are linked.'
                '\n\n'
                'Update affected workflows where connections are missing, '
                'and redraw the lost connections.'
                '\n\n'
                'Lost Connections: {}.'.format(', '.join(
                    "{} -> {}".format(*conn_prob)
                    for conn_prob in conn_probs)))
            return nr

        def inform_infer_lost_connections(conn_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Unable to infer type for some flow connections: '
                'This could be the result of removed ports '
                'or changed port types. '
                'The ports that lost connections may not be the ones '
                'that introduced the problem. This should not happen '
                'For flows saved in Sympathy version >= 1.3.1.'
                '\n'
                'Be careful when changing types of ports that are '
                'in use on nodes or flows that are linked.'
                '\n\n'
                'Update affected workflows and save them again.'
                '\n\n'
                'Lost Connections: {}.'.format(', '.join(
                    "{} -> {}".format(*conn_prob)
                    for conn_prob in conn_probs)))
            return nr

        def inform_lost_overrides(override_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Unable to restore some overrides: '
                'This could be the result of a bug. '
                'Please make a bug report to support@sympathyfordata.com. '
                '\n\n'
                'Lost overrides for node uuid: {}.'.format(', '.join(
                    override_probs)))
            return nr

        def inform_xml_convert_probs(xml_convert_probs):
            nr = node_result.NodeResult()
            nr.stderr = '\n'.join(xml_convert_probs)
            return nr

        def inform_cycle_lost_connections(conn_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Removed the following connections to avoid cycles in the '
                'flow:\n\n{}'.format(
                    '\n'.join(conn_probs)))
            return nr

        self._check_flow_libraries(self._dictionary,
                                   flow=flow,
                                   warn_on_errors=warn_on_errors,
                                   parent_flow=parent_flow)
        probs = {}
        infertype_ctx = None

        with flow.infertype_ctx() as ctx:
            result = self._build_flow(
                flow, self._dictionary, is_linked=is_linked, probs=probs)
            infertype_ctx = ctx

        ctx = infertype_ctx

        if ctx.errors:
            local_probs = probs.setdefault(flow.full_uuid, {})
            for src, dst in ctx.removed:
                logger.warning(
                    "Couldn't infer type for connection between "
                    "nodes %s and %s", src, dst)

                local_probs.setdefault('connection_infer_type', []).append(
                    (src, dst))

        for flow_full_uuid, flow_probs in probs.items():

            if flow_probs:
                override_probs = flow_probs.pop('overrides_exception', None)
                conn_probs = flow_probs.pop('connection_type', None)
                infer_conn_probs = flow_probs.pop(
                    'connection_infer_type', None)
                duplicate_probs = flow_probs.pop('duplicates', None)
                xml_convert_probs = flow_probs.pop('xml_convert', None)
                cycle_conn_probs = flow_probs.pop('removed_cycles', None)

                messages = []

                if override_probs:
                    messages.append(inform_lost_overrides(override_probs))

                if conn_probs:
                    messages.append(inform_lost_connections(conn_probs))

                if infer_conn_probs:
                    messages.append(inform_infer_lost_connections(
                        infer_conn_probs))

                if duplicate_probs:
                    messages.append(inform_duplicate_identifiers(
                        duplicate_probs))

                if xml_convert_probs:
                    messages.append(inform_xml_convert_probs(
                        xml_convert_probs))

                if cycle_conn_probs:
                    messages.append(inform_cycle_lost_connections(
                        cycle_conn_probs))

                for message in messages:
                    flode = self._app_core.get_flode(flow_full_uuid)
                    if flode:
                        for node_message in sympathy.app.util.node_messages(
                                flode, message):
                            self._app_core.display_message(node_message)
                    else:
                        for result_message in sympathy.app.util.result_messages(
                                flow_full_uuid, message):
                            self._app_core.display_message(result_message)
        return result

    def build_paste_flow(self, flow, anchor=QtCore.QPointF(0, 0), center=True,
                         warn_on_errors=None, parent_flow=None):
        if center:
            center = QtCore.QPointF(self._dictionary['center']['x'],
                                    self._dictionary['center']['y'])
        else:
            center = QtCore.QPointF(0, 0)

        self._check_flow_libraries(self._dictionary['flow'], flow=flow,
                                   warn_on_errors=warn_on_errors,
                                   parent_flow=parent_flow)

        with flow.infertype_ctx():
            result = self._build_flow(
                flow, self._dictionary['flow'], anchor - center,
                update_flow=False, create_copy=True)

        return result

    def _init(self):
        pass

    def _build_flow(self, flow, dictionary, anchor=QtCore.QPointF(0, 0),
                    update_flow=True, create_copy=False, is_linked=False,
                    parent_is_linked=False, unique_uuids=None, probs=None):
        """
        Add elements to a flow object from a dictionary representation.

        Parameters
        ----------
        flow : sympathy flow
            Parent flow.
        dictionary : dict
            Dictionary describing the flow elements to be added.
        anchor : QtCore.QPointF
            Origin position where the elements will be added. In scene
            coordinates.
        update_flow : bool
            If True, also modify the parent flow using the flow meta
            data in the dictionary.
        create_copy : bool
            If True, give most elements new uuids. Defaults to False.
        is_linked : bool
            Should be True when flow is linked. If True, don't elements new
            uuids. External ports in linked subflows will still get new uuids
            depending on the value of parent_is_linked. Defaults to False.
        parent_is_linked : bool
            If False, give external ports in linked subflows new
            uuids. Defaults to False.

        Returns
        -------
        tuple of two dictionaries
            The first dictionary contains a map from old uuids to new ones, the
            second dictionary is a map from new uuids to actual objects.
        """
        class StringKeyDict(dict):
            def __setitem__(self, key, value):
                if not isinstance(key, str):
                    logger.warning(
                        "Trying to add key with type %s: (%s, %s)", type(key),
                        key, value)
                super(StringKeyDict, self).__setitem__(key, value)

        def update_port_uuid(port_dict, port, uuid_to_class,
                             uuid_to_new_uuid, generate):
            if generate:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = port_dict['uuid']
                if uuid in unique_uuids:
                    logger.warning(
                        'Duplicate port: %s', uuid)
                    local_probs.setdefault('duplicates', {}).setdefault(
                        'port_dict', []).append(uuid)
            unique_uuids.add(uuid)

            port.uuid = uuid
            uuid_to_class[port.uuid] = port
            uuid_to_new_uuid[port_dict['uuid']] = port.uuid

        def update_port_uuids(dict_, instance, uuid_to_class,
                              uuid_to_new_uuid, kind, generate):
            if kind == 'input':
                port_from_index = instance.input
                maxlen = len(instance.inputs)
                ports = 'inputs'
            elif kind == 'output':
                port_from_index = instance.output
                maxlen = len(instance.outputs)
                ports = 'outputs'

            for index, port in enumerate(dict_.get(ports, [])):
                if index >= maxlen:
                    break
                p = port_from_index(index)

                update_port_uuid(port, p, uuid_to_class,
                                 uuid_to_new_uuid, generate)

        def valid_connection_ports(source, dest, conntype):
            if source and dest:
                if conntype is None:
                    return True
                else:
                    conntype = dest.datatype.from_str(conntype)
                    return (conntype.match(source.datatype) and
                            conntype.match(dest.datatype))
            return False

        local_probs = {}

        if probs is None:
            probs = {}

        if is_linked:
            unique_uuids = set()
        else:
            unique_uuids = set() if unique_uuids is None else unique_uuids

        update_uuids = create_copy and not is_linked and not parent_is_linked
        update_subflow_port_uuids = create_copy and not parent_is_linked
        update_node_port_uuids = create_copy and not is_linked and not parent_is_linked

        # Actual top-level cls is determined by the parent which is being built
        # or added to. For example, when pasting content copied from a Lambda to
        # a Flow, dict_cls is Lambda but flow_cls is Flow.
        # For lower-levels dict_cls equals flow_cls.
        dict_cls = dictionary.get('cls', 'Flow')
        flow_cls = type(flow).__name__

        ext_uuid_to_class = StringKeyDict()
        ext_uuid_to_new_uuid = StringKeyDict()

        uuid_to_class = StringKeyDict()
        uuid_to_new_uuid = StringKeyDict()
        broken = dictionary.get('broken_link', False)

        # Changes that modify flow should happen in here.  This will prevent,
        # for example, accidentally setting fields from the top-level
        # dictionary when performing paste operations.
        if update_flow:
            tag = dictionary.get('tag')
            flow.identifier = dictionary.get('id')
            flow.tag = tag

            label = dictionary.get('label', '')
            if label:
                flow.name = label

            # flow.set_properties ignores any keys that it isn't interested in.
            flow.set_properties(dictionary)

            if 'source' in dictionary:
                flow.source_uri = dictionary['source']
            if 'filename' in dictionary:
                flow.filename = dictionary['filename']
            flow.set_linked(dictionary.get('is_linked', False))
            flow.set_locked(dictionary.get('is_locked', False))
            flow.icon_filename = dictionary.get('icon')

            flow.set_broken_link(broken)
            if broken:
                if not dictionary.get('id'):
                    self._app_core.display_custom_node_message(
                        flow,
                        error="Can't open subflow file '{}'".format(
                            dictionary.get('source', '')))

            # We expect the flow parameters to be a dict such as
            # {'data': {...}, 'type': 'json'}, but let's not be too picky.
            parameters = dictionary.get('parameters', {})
            if 'data' in parameters:
                parameters = parameters['data']
                # Earlier versions of sympathy would create "recursive"
                # parameter dictionaries (i.e.
                # {type: json, environment: {}, data:
                #    {type: json, environment: {}, data: {...}}} ).
                # Let's try to fix that by dropping any "data" and "type" keys.
                for bad_key in ["data", "type"]:
                    parameters.pop(bad_key, None)
            environment = dictionary.get('environment', {})
            if environment:
                parameters['environment'] = environment
            flow.parameters = parameters

            flow.set_libraries_and_pythonpaths(
                libraries=dictionary.get('libraries', []),
                pythonpaths=dictionary.get('pythonpaths', []))
            flow.aggregation_settings = dictionary.get(
                'aggregation_settings', {})
            flow.source_uuid = dictionary.get('source_uuid')
            flow.source_label = dictionary.get('source_label')

        if ('source_uuid' in dictionary and
                dictionary['source_uuid'] is not None):
            uuid_to_new_uuid[dictionary['source_uuid']] = flow.uuid
            uuid_to_class[dictionary['source_uuid']] = flow
        uuid_to_new_uuid[dictionary['uuid']] = flow.uuid
        uuid_to_class[flow.uuid] = flow

        for node in dictionary['nodes']:
            pos = QtCore.QPointF(node['x'], node['y']) + anchor
            parameters = library.ParameterModel.from_dict(
                node.get('parameters'))

            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = node['uuid']
                if uuid in unique_uuids:
                    new_uuid = uuid_generator.generate_uuid()
                    logger.warning(
                        'Duplicate node: %s, replaced with: %s',
                        uuid, new_uuid)
                    local_probs.setdefault(
                        'identifier', {}).setdefault('node', []).append(uuid)
                    uuid = new_uuid
            unique_uuids.add(uuid)

            library_node = None
            root = flow.root_or_linked_flow()
            libraries = [os.path.normcase(l)
                         for l in sympathy.app.util.library_paths(root)]

            if not self._app_core.is_node_in_library(node['id'], libraries):
                node['type'] = 'node'
                library_node = self._app_core.library_node_from_definition(
                    node['id'], node)
                if library_node is None:
                    logger.error(
                        'Node %s (%s) is missing in libraries and flow lacks '
                        'required info',
                        uuid, node['id'])
                    continue

            version = node.get('version')
            if version is None:
                version = epoch_version
            else:
                version = Version(version)
            original_nodeid = node.get('original_nodeid') or None
            cmd = sympathy.app.user_commands.CreateNodeCommand(
                node_id=node['id'],
                position=pos,
                uuid=uuid,
                flow=flow,
                ports=node.get('ports', {}),
                port_format=node.get('port_format'),
                library_node=library_node,
                only_conf=node.get('only_conf'),
                version=version,
                name=node.get('label'),
                original_nodeid=original_nodeid,
            )
            cmd.redo()
            uuid_to_new_uuid[node['uuid']] = cmd.element_uuid()
            node_instance = cmd.created_element()
            uuid_to_class[cmd.element_uuid()] = node_instance
            if not parameters.is_empty():
                node_instance.parameter_model = parameters
            self._created_nodes.append(cmd)

            update_port_uuids(node.get('ports', {}), node_instance,
                              uuid_to_class, uuid_to_new_uuid, 'input',
                              update_node_port_uuids)

            update_port_uuids(node.get('ports', {}), node_instance,
                              uuid_to_class, uuid_to_new_uuid, 'output',
                              update_node_port_uuids)

        for subflow in dictionary['flows']:
            pos = QtCore.QPointF(subflow['x'], subflow['y']) + anchor
            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = subflow['uuid']
                if uuid in unique_uuids:
                    logger.warning('Duplicate flows: {}'.format(uuid))
                    local_probs.setdefault('duplicates', {}).setdefault(
                        'flow', []).append(uuid)
            unique_uuids.add(uuid)
            cls = subflow.get('cls', 'Flow')

            subflow_is_linked = subflow.get('is_linked', False)

            root = flow.root_or_linked_flow()
            libraries = [os.path.normcase(l)
                         for l in sympathy.app.util.library_paths(root)]

            content_dict = subflow
            library_node_id = subflow.get('node_id')
            node_id = subflow.get('id')
            library_node = None

            if library_node_id or (node_id and not subflow.get('source')):
                subflow_is_linked = True
                node_id = library_node_id or node_id
                if self._app_core.is_node_in_library(
                        node_id, libraries):
                    library_node = self._app_core.library_node(node_id)
                    deserializer = FlowDeserializer(self._app_core)
                    subflow_filename = uri_to_path(library_node.source_uri)
                    deserializer.load_xml_file(subflow_filename)
                    content_dict = deserializer.to_dict()

                    workflow_converter.update_link_content(
                        subflow, content_dict, subflow_filename)
                    content_dict['xml_convert'] = subflow.get(
                        'xml_convert', [])
                else:
                    if node_id:
                        workflow_converter.update_broken_link_content(content_dict)
                        library_node = self._app_core.library_node_from_definition(
                            node_id, content_dict)

                    content_dict['broken_link'] = True
                    content_dict['is_linked'] = True

            cmd = sympathy.app.user_commands.CreateSubflowCommand(
                position=pos, flow=flow, uuid=uuid, library_node=library_node,
                cls=cls)
            cmd.redo()
            self._created_nodes.append(cmd)
            uuid_to_new_uuid[subflow['uuid']] = cmd.element_uuid()
            uuid_to_class[cmd.element_uuid()] = cmd.created_element()

            uuid_to_new_uuid_, uuid_to_class_ = self._build_flow(
                cmd.created_element(), content_dict,
                create_copy=create_copy,
                parent_is_linked=(parent_is_linked or is_linked),
                is_linked=subflow_is_linked, unique_uuids=unique_uuids,
                probs=probs)

            uuid_to_new_uuid.update(uuid_to_new_uuid_)
            uuid_to_class.update(uuid_to_class_)

        if update_flow:
            # Subflow basic inputs and outputs
            basic_ports = dictionary.get('basic_ports', {})
            basic_inputs = basic_ports.get('inputs', [])
            basic_outputs = basic_ports.get('outputs', [])

            for ports, create_fn in [(basic_inputs, flow.create_input),
                                     (basic_outputs, flow.create_output)]:
                # TODO(erik): object created without user command. Might want
                # to change this.
                for port_dict in ports:
                    mapping = {}
                    type_base = port_dict.get('type_base')
                    if type_base:
                        port_dict['type'] = type_base
                    port = create_fn(
                        library.PortDefinition.from_definition(port_dict),
                        generics_map=mapping)

                    update_port_uuid(
                        port_dict, port, uuid_to_class, uuid_to_new_uuid,
                        update_subflow_port_uuids)
                    port.datatype_instantiate(mapping)

        # Subflow inputs and outputs
        inputs = dictionary.get('ports', {}).get('inputs', [])
        outputs = dictionary.get('ports', {}).get('outputs', [])

        new_input_order = []
        new_output_order = []
        for port in inputs + outputs:
            pos = QtCore.QPointF(port['x'], port['y']) + anchor
            old_parent_port_uuid = port['uuid']
            old_uuid = port.get('source_uuid', old_parent_port_uuid)
            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = old_uuid
                if uuid in unique_uuids:
                    logger.warning('Duplicate flow port: {}'.format(uuid))
                    probs.setdefault('identifier', {}).setdefault(
                        'flow_port', []).append(uuid)
            unique_uuids.add(uuid)

            if old_uuid == old_parent_port_uuid:
                parent_port_uuid = uuid
            elif update_subflow_port_uuids:
                # Also update uuids for parent port if we are copying stuff and
                # this is a link and no parent or ancestor flow is linked.
                parent_port_uuid = uuid_generator.generate_uuid()
            else:
                parent_port_uuid = old_parent_port_uuid
                if (parent_port_uuid in unique_uuids and
                        parent_port_uuid != uuid):
                    logger.warning(
                        'Duplicate flow port: {}'.format(parent_port_uuid))
                    local_probs.setdefault('duplicates', {}).setdefault(
                        'node', []).append(uuid)
            unique_uuids.add(parent_port_uuid)

            if port in inputs:
                cmdclass = sympathy.app.user_commands.CreateFlowInputCommand
            else:
                cmdclass = sympathy.app.user_commands.CreateFlowOutputCommand
            if broken:
                port_definition_tuple = (
                    port['name'], port['description'], port['type'],
                    port['scheme'], port['index'])
            else:
                port_definition_tuple = None

            optional = port.get('optional', False)

            if flow_cls == 'Lambda':
                create_parent_port = port.get('parent', False)
            else:
                if dict_cls == 'Lambda':
                    optional = True
                create_parent_port = port.get('parent', not optional)

            source_parent = port.get('source_parent', None)
            if source_parent is None:
                source_parent = create_parent_port

            cmd = cmdclass(position=pos, flow=flow, uuid=uuid,
                           port_definition_tuple=port_definition_tuple,
                           create_parent_port=create_parent_port,
                           parent_port_uuid=parent_port_uuid,
                           optional=optional,
                           source_parent=source_parent)
            cmd.redo()
            self._created_nodes.append(cmd)
            uuid_to_new_uuid[old_uuid] = uuid
            uuid_to_class[uuid] = cmd.created_element()

            # If parent port and port had different uuids, we need to add both
            # to uuid_to_new_uuid and uuid_to_class to be able to recreate
            # connections.
            if old_parent_port_uuid != old_uuid:
                uuid_to_new_uuid[old_parent_port_uuid] = parent_port_uuid
                uuid_to_class[parent_port_uuid] = (
                    cmd.created_element().parent_port)

            if 'description' in port:
                cmd.created_element().name = port['description']
            if port in inputs:
                new_input_order.append(port.get('index', len(new_input_order)))
            if port in outputs:
                new_output_order.append(
                    port.get('index', len(new_output_order)))

        if (new_input_order != sorted(new_input_order) or
                new_output_order != sorted(new_output_order)):
            logger.warning("Incorrect port order for flow %s", flow)

        for text_field in dictionary.get('textfields', []):
            rectangle = QtCore.QRectF(
                text_field['x'] + anchor.x(), text_field['y'] + anchor.y(),
                text_field['width'], text_field['height'])
            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = text_field['uuid']
                if uuid in unique_uuids:
                    logger.warning(
                        'Duplicate text field: {}'.format(uuid))
                    local_probs.setdefault('duplicates', {}).setdefault(
                        'text field', []).append(uuid)
                unique_uuids.add(uuid)

            cmd = sympathy.app.user_commands.CreateTextFieldCommand(
                rectangle, flow, uuid)
            cmd.redo()
            self._created_nodes.append(cmd)
            cmd.created_element().set_text(text_field['text'])
            if 'color' in text_field:
                cmd.created_element().set_color(text_field['color'])

        # And finally connections
        for connection in dictionary['connections']:

            logger.debug('Connection from {} {}'.format(
                connection['source']['node'],
                connection['source']['port']))
            logger.debug('Connection to {} {}'.format(
                connection['destination']['node'],
                connection['destination']['port']))
            if not connection['source']['node'] in uuid_to_new_uuid:
                logger.warning("Unknown source node")
                continue
            if not connection['destination']['node'] in uuid_to_new_uuid:
                logger.warning("Unknown destination node")
                continue

            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = connection['uuid']
                if uuid in unique_uuids:
                    logger.warning(
                        'Duplicate connection uuid: {}'.format(uuid))

                    local_probs.setdefault('duplicates', {}).setdefault(
                        'connection', []).append(uuid)
            unique_uuids.add(uuid)

            source_node_uuid = uuid_to_new_uuid.get(
                connection['source']['node'], None)
            source_port_uuid = uuid_to_new_uuid.get(
                connection['source']['port'], None)
            destination_node_uuid = uuid_to_new_uuid.get(
                connection['destination']['node'], None)
            destination_port_uuid = uuid_to_new_uuid.get(
                connection['destination']['port'], None)
            source_port = destination_port = None

            if (source_node_uuid in uuid_to_class and
                    destination_node_uuid in uuid_to_class):
                if source_node_uuid == flow.uuid:
                    flow_input = flow.flow_input(source_port_uuid)
                    if flow_input:
                        source_port = flow_input.output
                else:
                    source_port = uuid_to_class[source_node_uuid].output(
                        source_port_uuid)

                if destination_node_uuid == flow.uuid:
                    flow_output = flow.flow_output(destination_port_uuid)
                    if flow_output:
                        destination_port = flow_output.input
                else:
                    destination_port = (
                        uuid_to_class[destination_node_uuid].input(
                            destination_port_uuid))

                if valid_connection_ports(source_port, destination_port,
                                          connection['type']):
                    route_points = [
                        QtCore.QPointF(r['x'], r['y']) + anchor
                        for r in connection.get('route', [])]

                    logger.debug(
                        "Creating connection between nodes %s (%s) "
                        "and %s (%s)", source_node_uuid, source_port,
                        destination_node_uuid, destination_port)
                    cmd = sympathy.app.user_commands.CreateConnectionCommand(
                        source_port, destination_port, flow, uuid,
                        route_points=route_points)
                    try:
                        cmd.redo()
                        self._created_connections.append(cmd)
                    except SyInferTypeError:
                        logger.warning(
                            "Couldn't infer type for connection between "
                            "ports %s -> %s.",
                            source_port_uuid,
                            destination_port_uuid)
                        local_probs.setdefault(
                            'connection_infer_type', []).append((
                                source_port,
                                destination_port))
                    except Exception:
                        logger.warning(
                            "Failed to build connection between %s -> %s",
                            source_node_uuid, destination_node_uuid)

                else:
                    local_probs.setdefault('connection_type', []).append((
                        source_port,
                        destination_port))

                    logger.warning("Couldn't create a connection between "
                                   "ports %s and %s",
                                   source_port_uuid,
                                   destination_port_uuid)
            else:
                logger.warning(
                    "Failed to build connection between %s -> %s",
                    source_node_uuid, destination_node_uuid)

        if update_flow:
            # Update uuids in aggregation settings skipping settings
            # for any nodes that are no longer in the workflow.
            if flow.aggregation_settings:
                settings = flow.aggregation_settings
                for key in ('uuid_selected', 'selected_uuids'):
                    if key in settings:
                        settings[key] = [
                            uuid_to_new_uuid[uuid_]
                            for uuid_ in settings[key]
                            if uuid_ in uuid_to_new_uuid]
                if 'group_structure' in settings:
                    update_uuids_in_group(
                        settings['group_structure'], uuid_to_new_uuid,
                        update_uuids)

            # Set override parameters now that all nodes have been created.
            overrides_dict = dictionary.get('overrides', None)
            overrides_dict = _overrides_extra_info(overrides_dict)
            for tree_uuid, overrides_struct in overrides_dict.items():
                overrides = overrides_struct['data']
                version = overrides_struct.get('version', '0.0')
                try:
                    uuid_parts = uuid_generator.split_uuid(tree_uuid)
                    flow_ = flow
                    for i, uuid_part in enumerate(uuid_parts):
                        shallow_flodes = {
                            n.uuid: n for n in flow_.shallow_nodes()}

                        if uuid_part in shallow_flodes:
                            flow_ = shallow_flodes[uuid_part]
                            last_part = i == len(uuid_parts) - 1
                            is_node = flow_.type == Type.Node

                            if last_part and is_node:
                                node = flow_  # This part is actually a node.
                                overrides_nodeid = (
                                    overrides_struct.get('nodeid')
                                    or node.original_nodeid
                                    or node.identifier
                                )
                                parameter_model = (
                                    library.OverridesModel.from_dict(
                                        {'data': overrides,
                                         'type': 'json',
                                         'version': version,
                                         'nodeid': overrides_nodeid,
                                        }))
                                flow.set_node_override_parameters(
                                    node, parameter_model)
                            elif last_part or is_node:
                                # The last uuid part should always be a node,
                                # and all other parts should be
                                # flows. Otherwise, we discard these overrides.
                                break
                        else:
                            # This uuid_part doesn't exist in flow_. Discard
                            # these overrides.
                            break
                except Exception:
                    local_probs.setdefault('overrides_exception', []).append(
                        tree_uuid)

        removed_cycles = flow.remove_cycles()
        if removed_cycles:
            removed_connection_lines = []
            for conn in removed_cycles:
                src = ''
                dst = ''
                if conn.source:
                    src = conn.source.uuid
                if conn.destination:
                    dst = conn.destination.uuid
                removed_connection_lines.append(f'{src} -> {dst}')
            local_probs.setdefault('removed_cycles', []).extend(
                removed_connection_lines)

        xml_convert = dictionary.get('xml_convert', [])
        local_probs.setdefault('xml_convert', []).extend(xml_convert)
        probs[flow.full_uuid] = local_probs

        new_uuid_to_uuid = {new: old for old, new in uuid_to_new_uuid.items()}
        for port in flow.inputs + flow.outputs:
            ext_uuid_to_class[port.uuid] = port
            # When pasting FlowIO: no mapping exists.
            if port.uuid in new_uuid_to_uuid:
                ext_uuid_to_new_uuid[new_uuid_to_uuid[port.uuid]] = port.uuid
        return ext_uuid_to_new_uuid, ext_uuid_to_class

    def _debug_uuid_dicts(self, uuid_to_new_uuid, uuid_to_class):
        """
        Print uuid dictionaries to stdout in a readable format.

        This function is very useful for debugging the uuid substitutions.
        """
        from .common import RED

        def shorten(uuid):
            return uuid[:9] + uuid[-1]

        def no_color(s):
            return '  {}  '.format(s)

        def diff_colors_factory(*args):
            colors = [no_color]*len(args)
            for i, (a1, a2) in enumerate(zip(args[1:], args[:-1])):
                if a1 != a2:
                    colors[i:i+2] = [RED, RED]
            return colors

        for utnu_key, utnu_value in sorted(uuid_to_new_uuid.items()):
            if utnu_value in uuid_to_class:
                utc_value_uuid = uuid_to_class[utnu_value].uuid
                utc_value_name = uuid_to_class[utnu_value]
            else:
                utc_value_uuid = "N/A".ljust(10)
                utc_value_name = "N/A"
            c1, c2, c3 = diff_colors_factory(
                utnu_key, utnu_value, utc_value_uuid)
            print("{} -> {} -> {} ({})".format(
                c1(shorten(utnu_key)),
                c2(shorten(utnu_value)),
                c3(shorten(utc_value_uuid)),
                utc_value_name))
        print()

        utc_keys = set(uuid_to_class.keys()) - set(uuid_to_new_uuid.values())
        utnu_key = "N/A".ljust(10)
        for utc_key in utc_keys:
            utc_value = uuid_to_class[utc_key]
            c1, c2 = diff_colors_factory(
                utc_key, utc_value_uuid)
            print("{} -> {} -> {} ({})".format(
                no_color(shorten(utnu_key)),
                c1(shorten(utc_key)),
                c2(shorten(utc_value.uuid)),
                utc_value))
        print()
