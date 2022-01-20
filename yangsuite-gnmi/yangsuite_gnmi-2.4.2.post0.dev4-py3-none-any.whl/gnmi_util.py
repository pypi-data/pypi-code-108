import logging
import base64
import json
import traceback
from xml.etree.ElementPath import xpath_tokenizer_re
from google.protobuf import json_format
from six import string_types

from cisco_gnmi import proto
from ysgnmi.device_plugin import GnmiNotification


log = logging.getLogger(__name__)


class GnmiMessageException(Exception):
    pass


class GnmiMessage:
    """Class to prepare and return gMNI messages"""

    def __init__(self, message_type, cfg):
        self.msg_type = message_type
        self.cfg = cfg

    @classmethod
    def run_set(self, device, payload, **kwargs):
        """Run gNMI set service.

        Args:
          device (ysgnmi.device_plugin.GnmiSession): Target device.
          user (str): YANG Suite username.
          payload (proto.gnmi_pb2.SetRequest): SetRequest.
          payload (str): JSON representing a SetRequest.
        """
        if isinstance(payload, proto.gnmi_pb2.SetRequest):
            gnmi_string = str(payload)
        else:
            try:
                payload = GnmiMessageConstructor.json_to_gnmi('set', payload)
                gnmi_string = str(payload)
            except Exception:
                log.error(traceback.format_exc())
                raise GnmiMessageException("Invalid payload\n{0}".format(
                    str(payload))
                )

        device.log.info('gNMI SET\n' + '=' * 8 + '\n{0}'.format(
            gnmi_string
        ))
        try:
            response = device.gnmi.service.Set(payload)
            device.log.info(
                'gNMI SET Response\n' + '=' * 17 + '\n{0}'.format(
                    str(response)
                )
            )

            decode_result = self.decode_notification(
                response,
                kwargs.get('namespace', {})
            )
            device.log.info(
                'gNMI SET Response decoded\n' + '=' * 25 + '\n'
            )
            device.results.append(decode_result)
        except Exception as exc:
            log.error(traceback.format_exc())
            if hasattr(exc, 'details'):
                device.log.error('ERROR: {0}'.format(exc.details()))
            else:
                device.log.error(str(exc))

    @classmethod
    def run_get(self, device, payload):
        """Run gNMI get service.

        Args:
          device (ysgnmi.device_plugin.GnmiSession): Target device.
          user (str): YANG Suite username.
          payload (proto.gnmi_pb2.SetRequest): SetRequest.
          payload (str): JSON representing a SetRequest.
        """
        if isinstance(payload, proto.gnmi_pb2.GetRequest):
            gnmi_string = str(payload)
        else:
            try:
                payload = GnmiMessageConstructor.json_to_gnmi('get', payload)
                gnmi_string = str(payload)
            except Exception:
                log.error(traceback.format_exc())
                raise GnmiMessageException("Invalid payload\n{0}".format(
                    str(payload)
                ))

        device.log.info('gNMI GET\n' + '=' * 8 + '\n{0}'.format(
            gnmi_string
        ))
        try:
            response = device.gnmi.service.Get(payload)
            device.log.info(
                'gNMI GET Response\n' + '=' * 17 + '\n{0}'.format(
                    str(response)
                )
            )
            # Decoder works for JSON or base64 encoded JSON.
            decode_result = self.decode_notification(response, {})
            device.log.info(
                'Get Response JSON value decoded\n' + '=' * 31 + '\n'
            )
            device.log.info(decode_result)
        except Exception as exc:
            log.error(traceback.format_exc())
            if hasattr(exc, 'details'):
                device.log.error('ERROR: {0}'.format(exc.details()))
            else:
                device.log.error(str(exc))

    @classmethod
    def iter_subscribe_request(self, payload):
        """Generator passed to Subscribe service to handle stream payloads.

        Args:
          payload (proto.gnmi_pb2.SubscribeRequest)
        """
        subscribe_request = proto.gnmi_pb2.SubscribeRequest()
        subscribe_request.subscribe.CopyFrom(payload.subscribe)
        yield subscribe_request

    @staticmethod
    def decode_notification(update={}, namespace={}):
        """Convert JSON return to python dict for display or processing.

        Args:
          update (dict): Could also be a gNMI response.
          namespace (dict): Can be used if verifier is implemented.

        Returns:
          str
        """
        # Try to cover different return formats.
        results = []
        log.info('Decoding notification')
        if not isinstance(update, dict):
            try:
                update = json_format.MessageToDict(update)
            except Exception:
                return str(update)
        if 'notification' in update:
            update = update['notification']
            notify_list = []
            if isinstance(update, list):
                for upd in update:
                    if 'update' in upd:
                        notify_list += upd['update']
                    elif 'path' in upd:
                        notify_list.append(upd)
                update = notify_list
        if 'update' in update:
            update = update['update']
            if not isinstance(update, list):
                update = [update]
        elif 'path' in update and 'val' in update:
            val = update.get('val', {}).get('jsonIetfVal', '')
            if not val:
                val = update.get('val', {}).get('jsonVal', '')
            json_val = base64.b64decode(val).decode('utf-8')
            msg = 'JSON Decoded\n' + '=' * 12 + '\n' + json.dumps(
                json.loads(json_val, strict=False), indent=2
            )
            return msg
        msg = ''
        for upd in update:
            val = upd.get('val', {}).get('jsonIetfVal', '')
            if not val:
                val = upd.get('val', {}).get('jsonVal', '')
            if not val:
                log.error('Update has no value')
                return []
            json_val = base64.b64decode(val).decode('utf-8')
            msg += 'JSON Decoded\n' + '=' * 12 + '\n' + json.dumps(
                json.loads(json_val, strict=False), indent=2
            )
            results.append(msg)
        return '\n'.join(results)

    @classmethod
    def run_subscribe(self, device, payload, request):
        """Run gNMI subscribe service.

        Args:
          device (ysgnmi.device_plugin.GnmiSession): Target device.
          user (str): YANG Suite username.
          payload (proto.gnmi_pb2.SetRequest): SetRequest.
          payload (str): JSON representing a SetRequest.
          request (dict): gNMI subscribe settings for thread.
        """
        if isinstance(payload, proto.gnmi_pb2.SubscribeRequest):
            gnmi_string = str(payload)
        else:
            try:
                payload = GnmiMessageConstructor.json_to_gnmi(
                    'subscribe', payload
                )
                gnmi_string = str(payload)
            except Exception:
                log.error(traceback.format_exc())
                raise GnmiMessageException("Invalid payload\n{0}".format(
                    str(payload)
                ))
        device.log.info('gNMI SUBSCRIBE\n' + '=' * 14 + '\n{0}'.format(
            gnmi_string
        ))
        try:
            response = device.gnmi.service.Subscribe(
                self.iter_subscribe_request(payload)
            )

            def verify(data, returns={}):
                return data
            # TODO: add verify option for user?
            request['returns'] = {'empty': 'returns'}
            request['verifier'] = verify
            request['decode'] = self.decode_notification
            request['log'] = device.log
            subscribe_thread = GnmiNotification(
                response,
                **request
            )
            if request['request_mode'] == 'ONCE':
                subscribe_thread.event_triggered = True
            subscribe_thread.log = device.log
            subscribe_thread.start()
            device.active_notifications[device] = subscribe_thread
        except Exception as exc:
            log.error(traceback.format_exc())
            if hasattr(exc, 'details'):
                device.log.error('ERROR: {0}'.format(exc.details()))
            else:
                device.log.error(str(exc))

    def get_modules(self, cfg):
        """Helper function for get_entries."""
        return cfg.get('modules', {})

    def get_entries(self, cfg):
        """Helper function for get_messages."""
        entries = []
        modules = self.get_modules(cfg)

        for mod in modules.keys():
            entries.append({
                'module': mod,
                'namespace_modules': modules[mod].get('namespace_modules'),
                'namespace_prefixes': modules[mod].get('namespace_prefixes'),
                'nodes': modules[mod]['configs']
            })
        return entries

    def get_messages(self):
        """Using request, instantiate GnmiMessageConstuctor class.

        Returns:
          list: GnmiMessageConstructor classes.
        """
        gmcs = []
        entries = self.get_entries(self.cfg)
        for entry in entries:
            gmc = GnmiMessageConstructor(self.msg_type, entry, **self.cfg)
            gmcs.append(gmc)
        return gmcs


class GnmiMessageConstructor:
    """Construct a single gNMI message based on request."""

    def __init__(self, message_type, entry, **cfg):
        self.request = entry
        self.cfg = cfg
        self.prefix = cfg.get('prefix')
        self.origin = cfg.get('origin')
        self.encoding = cfg.get('encoding', 'JSON_IETF').upper()
        self.get_type = cfg.get('get_type', 'ALL').upper()
        self.base64 = cfg.get('base64', False)
        self.nodes = None
        self.update = []
        self.replace = []
        self.delete = []
        self.subscribe = []
        self.get = []
        self.json_val = {}
        self.msg_type = message_type
        self.xml_xpath_to_gnmi_xpath()
        self.nodes_to_dict()

    @property
    def msg_type(self):
        return self._msg_type

    @msg_type.setter
    def msg_type(self, msg_type):
        self.payload = None
        self._msg_type = msg_type
        if msg_type == 'set':
            self.payload = proto.gnmi_pb2.SetRequest()
        elif msg_type == 'get':
            self.payload = proto.gnmi_pb2.GetRequest()
            self.payload.type = proto.gnmi_pb2.GetRequest.DataType.Value(
                self.get_type
            )
            self.payload.encoding = proto.gnmi_pb2.Encoding.Value(
                self.encoding
            )
        elif msg_type == 'subscribe':
            self.payload = proto.gnmi_pb2.SubscribeRequest()
        if msg_type != 'subscribe' and self.prefix:
            # TODO: calculate prefix paths
            prefix_path = proto.gnmi_pb2.Path()
            prefix_path.origin = self.origin
            self.payload.prefix.CopyFrom(prefix_path)

    @classmethod
    def _upd_rpl(self, upd_rpl, base64_encode):
        updates = []
        for upd in upd_rpl:
            val = None
            if 'val' in upd:
                val = upd.pop('val', {})
            gnmi_update = json_format.ParseDict(
                upd,
                proto.gnmi_pb2.Update()
            )
            if val is not None:
                if 'jsonIetfVal' in val:
                    if base64_encode:
                        jval = bytes(
                            json.dumps(val['jsonIetfVal']), encoding='utf-8'
                        )
                        gnmi_update.val.json_ietf_val = base64.b64encode(jval)
                    else:
                        gnmi_update.val.json_ietf_val = json.dumps(
                            val['jsonIetfVal']
                        ).encode('utf-8')
                elif 'jsonVal' in val:
                    if base64_encode:
                        jval = bytes(
                            json.dumps(val['jsonVal']), encoding='utf-8'
                        )
                        gnmi_update.val.json_val = base64.b64encode(jval)
                    else:
                        gnmi_update.val.json_val = json.dumps(
                            val['jsonVal']
                        ).encode('utf-8')
            updates.append(gnmi_update)
        return updates

    @classmethod
    def json_to_gnmi(self, action, payload, **kwargs):
        """Given a JSON payload, convert it to a gNMI message.

        Expected JSON format is similar to a string __repr__ of the
        proto.gnmi_pb2 class with the exception of the "val" member.
        The "val" is passed in normal JSON format in the payload parameter
        but then gets converted to base64 encoding in the returned
        associated proto.gnmi_pb2 class.

        Args:
          action (str): set | get | subscribe.
          payload (str): Properly formated JSON string.
        Raises:
          GnmiMessageException
        Returns:
          gNMI proto.gnmi_pdb2 class
        """
        base64_encode = kwargs.get('base64', False)
        try:
            gnmi_dict = json.loads(payload)
        except Exception as exc:
            log.error(traceback.format_exc())
            raise GnmiMessageException('JSON parse failed: {0}'.format(
                str(exc)
            ))
        try:
            if action == 'set':
                updates = gnmi_dict.pop('update', [])
                replaces = gnmi_dict.pop('replace', [])
                gnmi_pld = json_format.ParseDict(
                    gnmi_dict,
                    proto.gnmi_pb2.SetRequest()
                )
                if updates:
                    gnmi_upd = self._upd_rpl(updates, base64_encode)
                    if gnmi_upd:
                        gnmi_pld.update.extend(gnmi_upd)
                if replaces:
                    gnmi_upd = self._upd_rpl(replaces, base64_encode)
                    if gnmi_upd:
                        gnmi_pld.replace.extend(gnmi_upd)
            elif action == 'get':
                gnmi_pld = json_format.Parse(
                    payload,
                    proto.gnmi_pb2.GetRequest()
                )
            elif action == 'subscribe':
                gnmi_pld = json_format.Parse(
                    payload,
                    proto.gnmi_pb2.SubscribeRequest()
                )
            return gnmi_pld
        except Exception as exc:
            log.error(traceback.format_exc())
            raise GnmiMessageException('Message parse failed: {}'.format(
                str(exc)
            ))

    def _manage_paths(self, path_req, gnmi_req):
        # Get initial gnmi path for gnmi message
        short_xp = self.get_shortest_common_path(path_req)
        gnmi_path = self.parse_xpath_to_gnmi_path(
            short_xp, self.origin
        )

        ext_xpaths = []
        for n in path_req:
            xp = n['xpath']
            n['xpath'] = xp[len(short_xp):]
            ext_xpaths.append(n)

        gnmi_req.path.CopyFrom(gnmi_path)

        return self.get_payload(ext_xpaths)

    def _gnmi_update_request(self, upd_req, gnmi_upd_req):
        # Construct an Update structure for a SetRequest gNMI message.
        json_val = self._manage_paths(upd_req, gnmi_upd_req)
        # Human readable for logs
        self.json_val = json_val

        json_val = json.dumps(json_val).encode('utf-8')
        if self.base64:
            json_val = base64.b64encode(json_val)

        if self.encoding and self.encoding.lower() == 'json_ietf':
            gnmi_upd_req.val.json_ietf_val = json_val
        else:
            gnmi_upd_req.val.json_val = json_val

        return [gnmi_upd_req]

    def nodes_to_dict(self, nodes=None, origin=None):
        """Construct full gNMI request message to be sent through service.

        Args:
          nodes (list): dicts with xpath in gNMI format, nodetypes, values.
          origin (string): gNMI origin for message.
        """
        # TODO: classmethod?
        if not self.nodes:
            self.nodes = nodes
        if origin:
            self.origin = origin

        update = self.nodes.get('update', [])
        replace = self.nodes.get('replace', [])
        delete = self.nodes.get('delete', [])
        get = self.nodes.get('get', [])
        subscribes = self.nodes.get('subscribe', [])

        if update:
            gnmi_update = proto.gnmi_pb2.Update()
            self.update = self._gnmi_update_request(update, gnmi_update)
            self.payload.update.extend(self.update)

        if replace:
            gnmi_replace = proto.gnmi_pb2.Update()
            self.replace = self._gnmi_update_request(replace, gnmi_replace)
            self.payload.replace.extend(self.replace)

        if delete:
            gnmi_delete_paths = []
            for xp in delete:
                gnmi_delete_paths.append(
                    self.parse_xpath_to_gnmi_path(xp, self.origin)
                )
            self.payload.delete.extend(gnmi_delete_paths)

        if get:
            for xp in get:
                self.payload.path.append(
                    self.parse_xpath_to_gnmi_path(xp, self.origin)
                )

        if subscribes:
            # Create subscribe list.
            subscribe_list = proto.gnmi_pb2.SubscriptionList()
            subscribe_list.encoding = proto.gnmi_pb2.Encoding.Value(
                self.encoding
            )
            mode = self.cfg.get('request_mode')
            subscribe_list.mode = proto.gnmi_pb2.SubscriptionList.Mode.Value(
                mode
            )
            if self.prefix:
                # TODO: calculate prefix paths
                prefix_path = proto.gnmi_pb2.Path()
                prefix_path.origin = self.origin
                subscribe_list.prefix.CopyFrom(prefix_path)

            # Create subscriptions for the list.
            for subscribe in subscribes:
                subscription = proto.gnmi_pb2.Subscription()
                if mode != 'ONCE':
                    sub_mode = self.cfg.get('sub_mode')
                    subscription.mode = proto.gnmi_pb2.SubscriptionMode.Value(
                        sub_mode
                    )
                    subscription.sample_interval = self.cfg.get(
                        'sample_interval'
                    )
                gnmi_path = self.parse_xpath_to_gnmi_path(subscribe)
                subscription.path.CopyFrom(gnmi_path)

                # Add the subscription to the list.
                subscribe_list.subscription.extend([subscription])

            # Add list to the subscribe request.
            self.payload.subscribe.CopyFrom(subscribe_list)

        return self.payload

    def _trim_xpaths(self, xpaths, short_xp):
        # Helper function for get_shortest_common_path.
        for xpath in xpaths:
            if short_xp not in xpath:
                xp = short_xp[:short_xp.rfind('/')]
                short_xp = self._trim_xpaths(xpaths, xp)
        return short_xp

    def get_shortest_common_path(self, nodes):
        """Find the shortest common path in a collection of nodes.

        Args:
          nodes (list): dicts with xpath in gNMI format, nodetypes, values.

        Return:
          str
        """
        xpaths = [n['xpath'] for n in nodes]
        short_xp = min(set(xpaths), key=len)
        short_xp = self._trim_xpaths(xpaths, short_xp)
        short_node = [n for n in nodes if n['xpath'] == short_xp]
        if short_node:
            if short_node[0]['nodetype'] not in ['list', 'container']:
                short_xp = short_xp[:short_xp.rfind('/')]
        return short_xp

    def get_payload(self, update):
        """Construct dict that will be converted to json_val in Update.

        Args:
          update (list): dicts with xpath in gNMI format, nodetypes, values.

        Returns:
          dict
        """
        json_val = {}
        processed_xp = []
        for node in update:
            xp = node['xpath']
            if xp.endswith(']'):
                continue
            if xp in processed_xp:
                continue
            jval = json_val
            collect_key = False
            key_elem = None
            tokenized = xpath_tokenizer_re.findall(xp)
            for i, seg in enumerate(tokenized, 1):
                token, elem = seg
                if token in ['/', '=']:
                    continue
                if not token and not collect_key and elem:
                    if len(tokenized) == i:
                        jval[elem] = node['value']
                    else:
                        if elem not in jval:
                            jval[elem] = {}
                        jval = jval[elem]
                    continue
                if token == '[':
                    collect_key = True
                    continue
                if token == ']':
                    collect_key = False
                    continue
                if key_elem is not None and token:
                    jval[key_elem] = token.strip('"')
                    key_elem = None
                    continue
                if collect_key and elem:
                    key_elem = elem
                    continue
            processed_xp.append(xp)

        return json_val

    def _trim_nodes(self, nodes):
        # Prune list nodes if already in other nodes xpath
        if nodes:
            xps = [n['xpath'] for n in nodes]
            long_xp = max(xps, key=len)
        for i in range(len(nodes)):
            if nodes[i]['xpath'] == long_xp:
                continue
            if nodes[i]['xpath'] in long_xp:
                nodes.remove(nodes[i])
                return self._trim_nodes(nodes)
        return nodes

    def xml_xpath_to_gnmi_xpath(self):
        """Convert XML Path Language 1.0 Xpath to gNMI Xpath.

        Input modeled after YANG/NETCONF Xpaths.
        References:
        * https://www.w3.org/TR/1999/REC-xpath-19991116/#location-paths
        * https://www.w3.org/TR/1999/REC-xpath-19991116/#path-abbrev
        * https://tools.ietf.org/html/rfc6020#section-6.4
        * https://tools.ietf.org/html/rfc6020#section-9.13
        * https://tools.ietf.org/html/rfc6241

        Parameters
        ---------
        request: dict containing request namespace and nodes to be worked on.
            namespace: dict of <prefix>: <namespace>
            nodes: list of dict
                    <xpath>: Xpath pointing to resource
                    <nodetype>: YANG statement type
                    <value>: value to set resource to
                    <edit-op>: equivelant NETCONF edit-config operation

        Returns
        -------
        tuple: namespace_modules, message dict
            namespace_modules: dict of <prefix>: <module name>
            message dict: 4 lists containing possible updates, replaces,
                deletes, or gets derived form input nodes.
        """
        message = {
            "update": [],
            "replace": [],
            "delete": [],
            "get": [],
            "subscribe": []
        }
        if "nodes" not in self.request:
            # TODO: raw rpc?
            return message
        if not self.request.get('namespace_modules'):
            log.info("No prefix-to-module mapping in request")
            namespace = {}
            module = ''
            namespace_prefixes = self.request.get("namespace_prefixes", {})
            for prefix, nspace in namespace_prefixes.items():
                if "/Cisco-IOS-" in nspace:
                    module = nspace[nspace.rfind("/") + 1:]
                elif "/cisco-nx" in nspace:  # NXOS lowercases namespace
                    module = "Cisco-NX-OS-device"
                elif "/openconfig.net" in nspace:
                    module = "openconfig-"
                    module += nspace[nspace.rfind("/") + 1:]
                elif "urn:ietf:params:xml:ns:yang:" in nspace:
                    module = nspace.replace("urn:ietf:params:xml:ns:yang:", "")
                if module:
                    namespace[prefix] = module
            self.request['namespace_modules'] = namespace

        nodes = self.request.get("nodes", [])
        if self.msg_type == 'set':
            # Prune key nodes without edit-op assigned.
            nodes = [n for n in nodes if not (
                n['xpath'].endswith(']') and
                not n.get('edit-op')
            )]
        if self.msg_type in ['get', 'subscribe'] and len(nodes) > 1:
            # Prune nodes with xpaths already in other node's xpath.
            nodes = self._trim_nodes(nodes)

        module = self.request.get('module')
        self.namespace_modules = self.request.get("namespace_modules", {})

        for node in nodes:
            if "xpath" not in node:
                log.error("Xpath is not in message")
            else:
                xpath = node["xpath"]
                value = node.get("value", "")
                datatype = node.get('datatype', 'string')
                edit_op = node.get("edit-op", "")

                if datatype == 'boolean':
                    if isinstance(value, string_types):
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                elif datatype.startswith('int') or \
                        datatype.startswith('uint'):
                    if value:
                        value = int(value)
                elif datatype == 'decimal64':
                    if value:
                        value = float(value)

                if xpath.startswith('/'):
                    xp = xpath.split('/')[1:]
                else:
                    node['xpath'] = '/' + xpath
                    xp = xpath.split('/')

                if not module:
                    # First segment of xpath has prefix of module.
                    if ':' in xp[0]:
                        pfx = xp[0].split(':')[0]
                        module = self.namespace_modules[pfx]
                    else:
                        module = ''
                    if self.prefix is None:
                        # Should be in format so this is an older test
                        if 'Cisco-IOS-XE' in module:
                            self.prefix = True
                            self.origin = 'rfc7951'
                        elif 'openconfig' in module:
                            self.origin = 'openconfig'

                for pfx, mod in self.namespace_modules.items():
                    if isinstance(value, string_types) and pfx in value:
                        if mod != module:
                            value = value.replace(pfx + ":", mod + ':')
                        else:
                            value = value.replace(pfx + ":", '')
                    # gNMI prefixes require entire module name.
                    for i, seg in enumerate(xp):
                        if pfx not in xpath:
                            continue
                        if i == 0 and self.prefix:
                            # Only needed for first path elem.
                            seg = seg.replace(pfx + ":", module + ':')
                            xp[i] = seg
                            continue
                        if mod != module:
                            # From another module so this is required.
                            seg = seg.replace(pfx + ":", mod + ':')
                        else:
                            seg = seg.replace(pfx + ':', '')
                        xp[i] = seg

                    if not xpath.endswith(']'):
                        node['name'] = xp[-1:][0]
                    else:
                        node['name'] = ''
                    node['xpath'] = '/'.join(xp)

                node['value'] = value

                if self.msg_type == 'set':
                    if not edit_op:
                        edit_op = 'update'

                    if edit_op in ["update", "replace"]:
                        if edit_op == "replace":
                            message["replace"] += [node]
                        elif edit_op == "update":
                            message["update"] += [node]
                    elif edit_op == "delete":
                        message["delete"].append(node['xpath'])

                elif self.msg_type in ['get', 'subscribe']:
                    if not message[self.msg_type]:
                        message[self.msg_type] = [node['xpath']]
                    elif node['xpath'] not in message[self.msg_type]:
                        message[self.msg_type].append(node['xpath'])
                else:
                    log.error('gNMI message type "{0}" is invalid.'.format(
                        str(self.msg_type)
                    ))

        self.nodes = message

    @classmethod
    def parse_xpath_to_gnmi_path(cls, xpath, origin=None):
        """Parses an XPath to proto.gnmi_pb2.Path.

        Effectively wraps the std XML XPath tokenizer and traverses
        the identified groups. Parsing robustness needs to be validated.
        Probably best to formalize as a state machine sometime.
        TODO: Formalize tokenizer traversal via state machine.
        """
        if not isinstance(xpath, string_types):
            raise Exception("xpath must be a string!")
        path = proto.gnmi_pb2.Path()
        if origin:
            if not isinstance(origin, string_types):
                raise Exception("origin must be a string!")
            path.origin = origin
        curr_elem = proto.gnmi_pb2.PathElem()
        in_filter = False
        just_filtered = False
        curr_key = None
        # TODO: Lazy
        xpath = xpath.strip("/")
        xpath_elements = xpath_tokenizer_re.findall(xpath)
        path_elems = []
        for element in xpath_elements:
            # stripped initial /, so this indicates a completed element
            if element[0] == "/":
                if not curr_elem.name:
                    # Trying to append to path without a name.
                    raise Exception(
                        "Current PathElem has no name! Invalid XPath?"
                    )
                path_elems.append(curr_elem)
                curr_elem = proto.gnmi_pb2.PathElem()
                continue
            # We are entering a filter
            elif element[0] == "[":
                in_filter = True
                continue
            # We are exiting a filter
            elif element[0] == "]":
                in_filter = False
                continue
            # If we're not in a filter then we're a PathElem name
            elif not in_filter:
                curr_elem.name = element[1]
            # Skip blank spaces
            elif not any([element[0], element[1]]):
                continue
            # If we're in the filter and just completed a filter expr,
            # "and" as a junction should just be ignored.
            elif in_filter and just_filtered and element[1] == "and":
                just_filtered = False
                continue
            # Otherwise we're in a filter and this term is a key name
            elif curr_key is None:
                curr_key = element[1]
                continue
            # Otherwise we're an operator or the key value
            elif curr_key is not None:
                if element[0] in [">", "<"]:
                    raise Exception("Only = supported as filter operand!")
                if element[0] == "=":
                    continue
                else:
                    # We have a full key here, put it in the map
                    if curr_key in curr_elem.key.keys():
                        raise Exception("Key already in key map!")
                    curr_elem.key[curr_key] = element[0].strip("'\"")
                    curr_key = None
                    just_filtered = True
        # Keys/filters in general should be totally cleaned up at this point.
        if curr_key:
            raise Exception("Hanging key filter! Incomplete XPath?")
        # If we have a dangling element that hasn't been completed due to no
        # / element then let's just append the final element.
        if curr_elem:
            path_elems.append(curr_elem)
            curr_elem = None
        if any([curr_elem, curr_key, in_filter]):
            raise Exception("Unfinished elements in XPath parsing!")

        path.elem.extend(path_elems)
        return path
