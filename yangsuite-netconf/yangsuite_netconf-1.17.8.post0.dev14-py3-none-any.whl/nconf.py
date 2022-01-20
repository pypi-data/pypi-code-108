# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Netconf API's for generating RPCs and communicating with devices."""
import select
import subprocess
import errno
import json
import traceback
import pkgutil
import re
import logging
import time
from collections import namedtuple, deque
from itertools import chain
from threading import Thread
import xml.dom.minidom
import lxml.etree as et
from jinja2 import Template
from time import sleep
from ncclient import manager, NCClientError
from ncclient.operations import RaiseMode
from ncclient.operations.retrieve import GetReply
from ncclient.transport.errors import SSHError
import ncclient.devices
from yangsuite.logs import get_logger
from ysdevices.devprofile import YSDeviceProfile
from .rpcbuilder import YSNetconfRPCBuilder, RpcInputError
from ysyangtree.tasks import TaskException


log = get_logger(__name__)


script_template = """#! /usr/bin/env python
import traceback
import lxml.etree as et
from argparse import ArgumentParser
from ncclient import manager
from ncclient.operations import RPCError

payload = [
{% for rpc in rpcs %}'''
{{ rpc }}''',{% endfor %}
]

if __name__ == '__main__':

    parser = ArgumentParser(description='Usage:')

    # script arguments
    parser.add_argument('-a', '--host', type=str, required=True,
                        help="Device IP address or Hostname")
    parser.add_argument('-u', '--username', type=str, required=True,
                        help="Device Username (netconf agent username)")
    parser.add_argument('-p', '--password', type=str, required=True,
                        help="Device Password (netconf agent password)")
    parser.add_argument('--port', type=int, default=830,
                        help="Netconf agent port")
    args = parser.parse_args()

    # connect to netconf agent
    with manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password,
                         timeout=90,
                         hostkey_verify=False,
                         device_params={'name': 'csr'}) as m:

        # execute netconf operation
        for rpc in payload:
            try:
                response = m.dispatch(et.fromstring(rpc))
                data = response.xml
            except RPCError as e:
                data = e.xml
                pass
            except Exception as e:
                traceback.print_exc()
                exit(1)

            # beautify output
            if et.iselement(data):
                data = et.tostring(data, pretty_print=True).decode()

            try:
                out = et.tostring(
                    et.fromstring(data.encode('utf-8')),
                    pretty_print=True
                ).decode()
            except Exception as e:
                traceback.print_exc()
                exit(1)

            print(out)

"""


class NetconfNotSupported(Exception):
    """Not in capabilities of server."""

    pass


class NetconfInvalidResponse(Exception):
    """No lxml element is returned."""

    pass


class SessionKey(namedtuple('SessionKey', ['user', 'device', 'stream'])):
    """Object used as index to store and look up NetconfSession instances.

    Note that 'stream' is an optional parameter."""

    __slots__ = ()

    def __new__(cls, user, device, stream=None):
        return super(SessionKey, cls).__new__(cls, user, device, stream)


class NetconfSession(object):
    """Representation of a NETCONF session by a user to a device.

    Do not instantiate directly; use get() API.

    Subclass this session class with library used to communcate NETCONF
    messages to the device.

    Can be used as a context manager to use an existing connection or
    create a temporary connection as appropriate::

      key1 = SessionKey("user1", "device1")
      key2 = SessionKey("user2", "device2")
      ncs1 = NetconfSession.get(key1)
      ncs2 = NetconfSession.get(key2)

      ncs1.connect()
      with ncs1:
        # ncs1 is already connected, remains connected
        # interact with session
      # ncs1 remains connected
      ncs1.connected == True
      # explicitly connected, need to explicitly disconnect as well
      ncs1.disconnect()

      with ncs2:
        # ncs2 was not previously connected, now connected temporarily
        # interact with session
      # ncs2 disconnects automatically after exiting the above block
      ncs2.connected == False
    """

    instances = {}

    class NotificationThread(Thread):
        """Thread listening for event notifications from the device."""

        def __init__(self, session):
            Thread.__init__(self)
            # Don't keep main process alive just because this thread is alive
            self.daemon = True

            self.session = session
            self.terminate = False

        def run(self):
            """Check for inbound notifications once per second."""
            log.info("Starting notification thread for %s", self.session.key)

            while not self.terminate:
                if not self.session.connected:
                    time.sleep(1)
                    continue
                notif = self.session.manager.take_notification(timeout=1)
                if not notif:
                    continue
                log.debug("Notification thread for %s received a notification",
                          self.session.key)
                self.session.log(et.tostring(notif.notification_ele,
                                             pretty_print=True,
                                             encoding="unicode"))

            log.info("Terminating notification thread for %s",
                     self.session.key)

    def __init__(self, key):
        """Do not call directly; use get() instead."""
        self.key = key
        self.dev_profile = YSDeviceProfile.get(key.device)
        if not self.dev_profile.netconf.enabled:
            raise NetconfNotSupported(
                'Device "{0}" is not marked as supporting NETCONF'
                .format(self.device_name))
        self.manager = None
        self._locked_datastores = []
        self.message_log = deque()
        self.notification_thread = None
        self.instances[key] = self
        self._disconnect_on_exit = False
        self.capabilities = []

    @property
    def with_defaults(self):
        """List of NETCONF "with-defaults" device capabilities.

        Used to apply RFC 6243 logic to determine "get-config" validity.
        """
        return self._with_defaults

    @property
    def datastore(self):
        """Device datastore capabilities."""
        return self._datastore

    @property
    def capabilities(self):
        """List of device NETCONF capabilities."""
        return self._capabilities

    @capabilities.setter
    def capabilities(self, caps=[]):
        self._capabilities = caps
        self._with_defaults = []
        self._datastore = []
        for cap in caps:
            if ':netconf:capability:' not in cap:
                continue
            if ':with-defaults:' in cap:
                self._with_defaults = cap[cap.find('=') + 1:].split(
                    '&also-supported='
                )
            elif ':candidate:' in cap:
                self._datastore.append('candidate')
            elif ':writable-running' in cap:
                self._datastore.append('running')

    def __enter__(self):
        if not self.connected:
            self.log("No session found. Creating a new temporary session")
            self._disconnect_on_exit = True
        return self.connect()

    def __exit__(self, *args):
        if self.connected and self._disconnect_on_exit:
            self.log("Ending temporary session")
            self.disconnect()
            self._disconnect_on_exit = False
        return False

    def __str__(self):
        return "user {0} session to {1}:{2} ({3}connected)".format(
            self.key.user, self.dev_profile.netconf.address,
            self.dev_profile.netconf.port, "" if self.connected else "not ")

    @classmethod
    def get(cls, key):
        """Retrieve or create the given NetconfSession instance.

        Raises:
          OSError: if the device identified in the key does not exist.
          NetconfNotSupported: if the device identified in the key
            does not support NETCONF.
        """
        if key not in cls.instances:
            dev_profile = YSDeviceProfile.get(key.device)

            if dev_profile.netconf.device_variant == 'iosenxr':
                cls.instances[key] = NetconfPipeSession(key)
            else:
                cls.instances[key] = NetconfSSHSession(key)

        return cls.instances[key]

    def connect(self, timeout=None):
        """Establish the connection to the device, if not already connected.

        ** Override this function in subclass. **

        Returns:
          NetconfSession: this instance if connection succeeded

        Raises:
          OSError: if SSH connection failed
        """
        pass

    @classmethod
    def destroy(cls, key):
        """Remove the session instance from the cache.
        The key can be a string or a device profile.
        Args:
          key (str): Device name or uses the base.profile_name as key.
        """
        if key in cls.instances:
            session = cls.instances[key]
            if session.connected:
                session.disconnect()
            del cls.instances[key]

    def disconnect(self):
        """Close the netconf session.

        ** Override this function in subclass. **

        Returns:
          NetconfSession: this instance if disconnect succeeded, else None
        """
        pass

    @property
    def connected(self):
        return (self.manager is not None and self.manager.connected)

    @property
    def locked_datastores(self):
        """List of datastore(s) that we have locked at present."""
        if not self.connected:
            self._locked_datastores = []
        return self._locked_datastores

    @locked_datastores.setter
    def locked_datastores(self, value):
        self._locked_datastores = value

    @property
    def device_name(self):
        return self.dev_profile.base.profile_name

    def log(self, message):
        """Log the given message to the internal log."""
        self.message_log.append(message)

    def clear_log(self):
        """Clear the log buffer."""
        self.message_log = deque()


nccl = logging.getLogger("ncclient")
# The 'Sending' and 'Received' messages are logged at level INFO.
nccl.setLevel("INFO")


class NetconfSessionLogHandler(logging.Handler):
    """Logging handler that logs to a NetconfSession's log."""

    parser = et.XMLParser(recover=True)

    def emit(self, record):
        if hasattr(record, 'session'):
            # Strip leading "[host foo session-id bar] " from the
            # msg as it's redundant for our purposes
            msg = re.sub(r'^\[[^]]+\] ', r'', record.msg)

            # If the message contains XML, pretty-print it
            record.args = list(record.args)
            for i in range(len(record.args)):
                arg = None
                if isinstance(record.args[i], str):
                    arg = record.args[i].encode("utf-8")
                elif isinstance(record.args[i], bytes):
                    arg = record.args[i]
                if not arg:
                    continue
                start = arg.find(b"<")
                end = arg.rfind(b"]]>]]>")    # NETCONF 1.0 message terminator
                if end == -1:
                    end = arg.rfind(b">")
                    if end != -1:
                        # Include the '>' character in our range
                        end += 1
                if start != -1 and end != -1:
                    elem = et.fromstring(arg[start:end], self.parser)
                    if elem is None:
                        continue
                    # Hello messages are quite long and are,
                    # from an end user's perspective, often just noise.
                    # Therefore, abridge them unless the user has opted in
                    # to high verbosity.
                    if (et.QName(elem.tag).localname == "hello" and
                            nccl.level != logging.DEBUG):
                        for child in list(elem):
                            elem.remove(child)
                        elem.text = "..."

                    text = et.tostring(elem, pretty_print=True,
                                       encoding="utf-8")
                    record.args[i] = (arg[:start] +
                                      text +
                                      arg[end:]).decode()
            record.args = tuple(record.args)

            for ncs in NetconfSession.instances.values():
                # Message for an established session
                if ncs.manager and ncs.manager._session == record.session:
                    ncs.log(msg % record.args)
                    return
            for ncs in NetconfSession.instances.values():
                # Message for a session not yet fully established
                if ((not ncs.connected) and
                        ncs.dev_profile.base.address == record.session.host):
                    ncs.log(msg % record.args)
                    return


nccl.addHandler(NetconfSessionLogHandler())


class NetconfSSHSession(NetconfSession):
    """Subclass using ncclient library for NETCONF messaging."""

    def connect(self, timeout=None):
        """Establish the connection to the device, if not already connected.

        Returns:
          NetconfSession: this instance if connection succeeded

        Raises:
          OSError: if SSH connection failed
        """
        if self.connected:
            return self

        try:
            if (self.dev_profile.netconf.device_variant
                    not in ncclient_supported_platforms()):
                log.warning(
                    "Unrecognized platform {0}. Using 'default'".format(
                        self.dev_profile.netconf.device_variant))
            _manager = manager.connect(
                **ncclient_manager_kwargs(self.dev_profile, timeout))
            _manager.raise_mode = RaiseMode.NONE
            self.notification_thread = self.NotificationThread(self)
            self.manager = _manager
            self.capabilities = list(_manager.server_capabilities)
            self.notification_thread.start()
            self.log("NETCONF CONNECTED {0}:{1}".format(
                self.dev_profile.netconf.address,
                self.dev_profile.netconf.port))
            return self
        except SSHError as exc:
            log.error('Connection refused with SSHError by device: %s', exc)
            self.log('Connection refused with SSHError by device: %s' % exc)
            # Translate ncclient error into more generic Python exception
            raise OSError(errno.ECONNREFUSED,
                          'SSH connection refused by device "{0}"'
                          .format(self.device_name))

    def disconnect(self):
        """Close the netconf session.

        Returns:
          NetconfSession: this instance if disconnect succeeded, else None
        """
        if not self.connected:
            return self

        try:
            self.manager.close_session()
            self.manager = None
            if self.notification_thread is not None:
                self.notification_thread.terminate = True
                self.notification_thread.join()
            self.log("NETCONF DISCONNECT {0}:{1}".format(
                self.dev_profile.netconf.address,
                self.dev_profile.netconf.port))
            return self
        except ValueError:
            # TODO: what can cause this?
            log.error('Error occurred while closing the session')
            self.log('Error occurred while closing the session.')
            return None


class NetconfPipeSession(NetconfSession):
    """Subclass using POSIX pipes to Communicate NETCONF messaging."""

    class NetconfPipeManager():
        """Netconf client using process pipes."""

        chunk = re.compile('(\n#+\\d+\n)')
        rpc_pipe_err = """
            <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <rpc-error>
                <error-type>transport</error-type>
                <error-tag>resource-denied</error-tag>
                <error-severity>error</error-severity>
                <error-message>No pipe data returned</error-message>
            </rpc-error>
            </rpc-reply>"""

        def __init__(self, proc, log, data):
            self.proc = proc
            self.log = log
            self.buf = ''
            elements = et.fromstring(data)
            self.server_capabilities = [e.text for e in elements.iter()
                                        if hasattr(e, 'text')]

        def get_rpc(self, elements):
            """Return string representation of lxml element with rpc."""
            rpc_element = et.Element(
                'rpc',
                attrib={'message-id': '101'},
                nsmap={None: "urn:ietf:params:xml:ns:netconf:base:1.0"}
            )
            rpc_element.append(elements)
            return et.tostring(rpc_element,
                               pretty_print=True).decode()

        def recv_data(self):
            """Retrieve data from process pipe."""
            if not self.proc:
                self.log('Not connected.')
            else:
                buf = ''
                while True:
                    # TODO: Could be better...1 byte at a time...
                    # but, too much buffer and it deadlocks!!
                    data = self.proc.stdout.read(1)

                    if not data:
                        return GetReply(self.rpc_pipe_err)

                    buf += data

                    if buf.endswith('\n##'):
                        buf = buf[:-3]
                        break

                self.log(buf)
                buf = buf[buf.find('<'):]
                reply = re.sub(self.chunk, '', buf)
                return GetReply(reply)

        def send_cmd(self, rpc):
            """Send a message to process pipe."""
            if not self.proc:
                self.log('Not connected.')
            else:
                if et.iselement(rpc):
                    if not rpc.tag.endswith('rpc'):
                        rpc = self.get_rpc(rpc)
                    else:
                        rpc = et.tostring(rpc, pretty_print=True).decode()
                rpc_str = '\n#' + str(len(rpc)) + '\n' + rpc + '\n##\n'
                self.log(rpc_str)
                self.proc.stdin.write(rpc_str)
                self.proc.stdin.flush()

                return self.recv_data()

        def edit_config(self, target=None, config=None, **kwargs):
            """Send edit-config."""
            target = target
            config = config
            target_element = et.Element('target')
            et.SubElement(target_element, target)
            edit_config_element = et.Element('edit-config')
            edit_config_element.append(target_element)
            edit_config_element.append(config)
            return self.send_cmd(self.get_rpc(edit_config_element))

        def get_config(self, source=None, filter=None, **kwargs):
            """Send get-config."""
            source = source
            filter = filter
            source_element = et.Element('source')
            et.SubElement(source_element, source)
            get_config_element = et.Element('get-config')
            get_config_element.append(source_element)
            get_config_element.append(filter)
            return self.send_cmd(self.get_rpc(get_config_element))

        def get(self, filter=None, **kwargs):
            filter_arg = filter
            get_element = et.Element('get')
            if isinstance(filter_arg, tuple):
                type, filter_content = filter_arg
                if type == "xpath":
                    get_element.attrib["select"] = filter_content
                elif type == "subtree":
                    filter_element = et.Element('filter')
                    filter_element.append(filter_content)
                    get_element.append(filter_element)
            else:
                get_element.append(filter_arg)
            return self.send_cmd(self.get_rpc(get_element))

        def commit(self, **kwargs):
            commit_element = et.Element('commit')
            return self.send_cmd(self.get_rpc(commit_element))

        def discard_changes(self, **kwargs):
            discard_element = et.Element('discard-changes')
            return self.send_cmd(self.get_rpc(discard_element))

        def lock(self, target=None, **kwargs):
            target = target
            store_element = et.Element(target)
            target_element = et.Element('target')
            target_element.append(store_element)
            lock_element = et.Element('lock')
            lock_element.append(target_element)
            return self.send_cmd(self.get_rpc(lock_element))

        def unlock(self, target=None, **kwargs):
            target = target
            store_element = et.Element(target)
            target_element = et.Element('target')
            target_element.append(store_element)
            unlock_element = et.Element('unlock')
            unlock_element.append(target_element)
            return self.send_cmd(self.get_rpc(unlock_element))

        def dispatch(self, rpc_command=None, **kwargs):
            rpc = rpc_command
            return self.send_cmd(rpc)

    class NotificationPipeThread(Thread):
        """Notification listener for process pipe.

        TODO: Not operational and may not be end design
        """

        def __init__(self, session):
            Thread.__init__(self)
            # Don't keep main process alive just because this thread is alive
            self.daemon = True

            self.session = session
            self.terminate = False

        def run(self):
            """Check for inbound notifications when select activates."""
            log.info("Starting notification thread for %s", self.session.key)

            while not self.terminate:
                if not self.session.connected:
                    time.sleep(1)
                    continue

                rfd, wfd, efd = select.select(
                    [self.session.manager.proc.stdout],
                    [], [], 10
                )

                self.session.manager.recv_data()

                log.debug("Notification thread for %s received a notification",
                          self.session.key)

            log.info("Terminating notification thread for %s",
                     self.session.key)

    @property
    def connected(self):
        """Check for active connection."""
        return (self.manager is not None and self.manager.proc.poll() is None)

    def connect(self, timeout=None):
        """Connect to ENXR pipe."""
        if self.connected:
            return self

        if (self.dev_profile.netconf.device_variant != "iosenxr"):
            self.log("Unrecognized TCP platform {0}.".format(
                self.dev_profile.netconf.device_variant))

        CMD = ['netconf_sshd_proxy', '-i', '0', '-o', '1', '-u', 'lab']
        BUFSIZE = 8192

        p = subprocess.Popen(CMD, bufsize=BUFSIZE,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             universal_newlines=True)

        buf = ''
        while True:
            data = p.stdout.read(1)
            if not data:
                self.log('No data received for hello')
                p.terminate()
                return

            buf += data
            if buf.endswith(']]>]]>'):
                buf = buf[buf.find('<'):-6]
                self.log('Hello received')
                break

        p.stdin.write(
            '<?xml version="1.0" encoding="UTF-8"?><hello '
            'xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><capabilities>'
            '<capability>urn:ietf:params:netconf:base:1.1</capability>'
            '</capabilities></hello>]]>]]>'
        )
        p.stdin.flush()
        self.manager = self.NetconfPipeManager(p, self.log, buf)
        # TODO: Notification stream interferes with get-schema
        self.log("NETCONF CONNECTED PIPE")
        return self

    def disconnect(self):
        """Disconnect from ENXR pipe."""
        if self.connected:
            self.manager.proc.terminate()
            self.manager = None
            self.log("NETCONF DISCONNECT PIPE")
        return self


def gen_ncclient_rpc(cfgd, prefix_namespaces="always"):
    """Construct the XML Element(s) needed for the given config dict.

    Helper function to :func:`gen_rpc_api`.

    Creates lxml Element instances specific to what :mod:`ncclient` is looking
    for per netconf protocol operation.

    .. note::
       Unlike :func:`gen_raw_rpc`, the XML generated here will NOT be declared
       to the netconf 1.0 namespace but instead any NETCONF XML elements
       will be left un-namespaced.

       This is so that :mod:`ncclient` can select the appropriate
       namespace (1.0, 1.1, etc.) as needed for the session.

    Args:
       cfgd (dict): Relevant keys - 'proto-op', 'dsstore', 'modules'.
       prefix_namespaces (str): One of "always" (prefer namespace prefixes) or
         "minimal" (prefer unprefixed namespaces)

    Returns:
       list: of lists [protocol operation, kwargs], or None

    Raises:
       ysnetconf.RpcInputError: if cfgd is invalid;
         see :meth:`YSNetconfRPCBuilder.get_payload`.
    """
    if not cfgd:
        log.warning("No configuration sent for RPC generation")
        return None

    dsstore = cfgd.get('dsstore')
    prt_op = cfgd['proto-op']
    with_defaults = cfgd.get('with-defaults', '')

    rpcbuilder = YSNetconfRPCBuilder(prefix_namespaces=prefix_namespaces)

    container = None

    if prt_op == 'edit-config':
        container = rpcbuilder.netconf_element('config')
    elif prt_op == 'get-config':
        container = rpcbuilder.netconf_element('filter')
    elif prt_op == 'get':
        container = rpcbuilder.netconf_element('filter')
    elif prt_op == 'action':
        container = rpcbuilder.yang_element('action')
    else:
        container = rpcbuilder.netconf_element('TEMPORARY')

    for modcfgd in cfgd.get('modules', {}).values():
        rpcbuilder = YSNetconfRPCBuilder(
            prefix_namespaces=prefix_namespaces,
            nsmap=modcfgd.get('namespace_prefixes'),
            netconf_ns=None)

        rpcbuilder.get_payload(modcfgd['configs'], container)

    kwargs = {}
    if prt_op == "rpc":
        # The outer container is temporary - the child element(s) created
        # should be the actual raw RPC(s), which is what we want to return
        return [[prt_op, {'rpc_command': elem}] for elem in container]

    if prt_op == 'edit-config':
        kwargs['target'] = dsstore
        if len(container):
            kwargs['config'] = container
    elif prt_op == 'get-config':
        kwargs['source'] = dsstore
        if len(container):
            kwargs['filter'] = container
        if with_defaults:
            kwargs['with_defaults'] = with_defaults
    elif prt_op == 'get':
        if len(container):
            kwargs['filter'] = container
        if with_defaults:
            kwargs['with_defaults'] = with_defaults
    elif prt_op in ['get-data', 'edit-data', 'action']:
        kwargs['rpc_command'] = container

    return [[prt_op, kwargs]]


def ncclient_send(key, rpc, timeout=None):
    """Use :mod:`ncclient` to send given RPC/s to the given device.

    Loops though the rpc list and deposits results into the
    collections.deque result stream cache.

    Args:
      key (SessionKey): Used as index to cached result stream.
      rpc (list): List of tuples (nc_op, kwargs), where nc_op is
          a str indicating the protocol operation requested and
          kwargs is a dict of parameters for this operation.
      timeout (int): RPC reply timeout value in seconds.

    Raises:
      NetconfNotSupported: if the key points to a non-NETCONF device

    Returns:
      list: of ``[nc_op, output]`` from the device.
    """
    result = []
    disconnect = False

    # May raise NetconfNotSupported
    nconf_session = NetconfSession.get(key)

    if not nconf_session.connected:
        nconf_session.log("No session found. Creating a new temporary session")
        nconf_session.connect(timeout)
        disconnect = True

    session_manager = nconf_session.manager
    commit_ok = False
    nc_raw = ''

    try:

        for nc_op, kwargs in rpc:

            try:

                nconf_session.log("NETCONF SEND {0}".format(nc_op))
                ret = ''

                if nc_op == 'edit-config':
                    ret = session_manager.edit_config(**kwargs)
                    if ret.ok:
                        commit_ok = True

                elif nc_op == 'commit':
                    if commit_ok:
                        ret = session_manager.commit()
                        if check_lock_reject(ret):
                            nconf_session.log(
                                "Running datastore is locked for commit"
                            )
                            if try_lock(session_manager, 'running'):
                                ret = session_manager.commit()
                                unlock_datastore(key, 'running')

                elif nc_op == 'get-config':
                    ret = session_manager.get_config(**kwargs)

                elif nc_op == 'get':
                    ret = session_manager.get(**kwargs)

                elif nc_op == 'rpc' or nc_op == 'action':
                    rpccom = kwargs['rpc_command']
                    if rpccom.tag.endswith('rpc'):
                        # Drop the outer rpc element
                        kwargs['rpc_command'] = rpccom[0]
                    rpcmsg = et.tostring(
                        kwargs['rpc_command']).decode("utf-8")
                    if '<commit' in rpcmsg:
                        if commit_ok:
                            ret = session_manager.dispatch(**kwargs)
                        else:
                            nconf_session.log(
                                "EDIT-CONFIG Failed, Cannot send COMMIT.")
                    else:
                        ret = session_manager.dispatch(**kwargs)
                        if ret.ok:
                            if 'edit-config' and 'candidate/>' in rpcmsg:
                                commit_ok = True
                if ret:
                    nc_raw = xml.dom.minidom.parseString(ret.xml).toprettyxml(
                        indent='  '
                    )
                    nconf_session.log(nc_raw)
                    result.append((nc_op, nc_raw))
                    if not ret.ok:
                        if nc_op == 'commit':
                            nconf_session.log("NETCONF discarding commit")
                            ret = session_manager.discard_changes()
                else:
                    nconf_session.log("{0} RPC Execution Failed".format(nc_op))

            except NCClientError as e:
                result.append((nc_op, str(e)))
                log.error(str(result))
                log.debug(traceback.format_exc())
                nconf_session.log("ERROR - {0}".format(str(e)))

            except UnicodeDecodeError as e:
                OFFSET = 30   # display 30 characters to each side of the error
                start = e.start - OFFSET if e.start >= OFFSET else 0
                end = e.start + OFFSET
                if end > len(e.object):
                    end = len(e.object)
                msg = ('UnicodeDecodeError: {0}\n'
                       'Data surrounding the error: {1}'
                       .format(e, e.object[start:end]))
                result.append((nc_op, msg))
                log.error(str(result))
                nconf_session.log("ERROR - {0}".format(msg))

            except Exception as e:
                result.append((nc_op, str(e)))
                log.error(str(result))
                log.debug(traceback.format_exc())
                nconf_session.log("ERROR - {0}".format(str(e)))

            nconf_session.log("NETCONF {0} COMPLETE".format(nc_op))
    finally:
        if disconnect:
            nconf_session.disconnect()

    return result


def check_lock_reject(rpc_reply):
    """Check if rpc-reply has lock related error.

    Args:
      rpc_reply (ncclient.RPC): rpc-reply class
    Returns:
      bool: True means error is related to datastore being locked
    """
    lock_retry_errors = ['lock-denied', 'resource-denied',
                         'in-use']
    if isinstance(rpc_reply, ncclient.operations.rpc.RPCReply) or \
       isinstance(rpc_reply, ncclient.operations.retrieve.GetReply):
        if rpc_reply.error:
            if rpc_reply.error.tag in lock_retry_errors:
                return True
    elif not et.iselement(rpc_reply):
        try:
            rpc_reply = et.fromstring(rpc_reply, encoding='utf-8')
            check_lock_reject(rpc_reply)
        except et.XMLSyntaxError:
            return False
    elif 'rpc-error' in rpc_reply[0].tag:
        for error in rpc_reply.iter():
            if error.text in lock_retry_errors:
                return True
    return False


def try_lock(session, target, timer=30, sleeptime=1):
    """Tries to lock the datastore to perform edit-config operation.

    Attempts to acquire the lock on the datastore. If exception thrown,
    retries the lock on the datastore till the specified timer expires.

    Helper function to :func:`lock_datastore`.

    Args:
        session (NetconfSession): active session
        target (str): Datastore to be locked
        timer: lock retry counter.
        sleeptime: sleep timer.

    Returns:
        bool: True if datastore was successfully locked, else False.
    """
    for counter in range(1, timer+1):
        ret = session.manager.lock(target=target)
        if ret.ok:
            return True
        retry = False
        for rpcerror in ret.errors:
            session.log("LOCK FAILED - MESSAGE - {0}".format(
                rpcerror.message))
        retry = check_lock_reject(ret)

        if not retry:
            session.log('ERROR - CANNOT ACQUIRE LOCK - {0}'.format(
                ret.error.tag))
            break
        elif counter < timer:
            session.log("RETRYING LOCK - {0}".format(counter))
            sleep(sleeptime)
        else:
            session.log('ERROR - LOCKING FAILED. RETRY TIMER EXCEEDED!!!')
    return False


def get_datastore_state(target, device):
    """Apply datastore rules according to device and desired datastore.

    - If no target is passed in and device has candidate, choose candidate.
    - If candidate is chosen, allow commit.
    - If candidate is chosen and writable-running exists, allow lock on running
      prior to commit.
    - If running, allow lock, no commit.
    - If startup, allow lock, no commit.
    - If intent, no lock, no commit.
    - If operational, no lock, no commit.
    - Default: running

    Args:
     target (str): Target datastore for YANG interaction.
     device (NetconfSession): Class containing runtime capabilities.
    Returns:
     (tuple): Target datastore (str): assigned according to capabilities
              Datastore state (dict):
                commit - can apply a commit to datastore
                lock_ok - can apply a lock to datastore
                lock_running - apply lock to running datastore prior to commit
    """
    target_state = {}

    for store in device.datastore:
        if store == 'candidate':
            if not target:
                target = 'candidate'
            target_state['candidate'] = ['commit', 'lock_ok']
            if 'running' in target_state:
                target_state['candidate'].append('lock_running')
            continue
        if store == 'running':
            if 'candidate' in target_state:
                target_state['candidate'].append('lock_running')
            target_state['running'] = ['lock_ok']
            continue
        if store == 'startup':
            target_state['startup'] = ['lock_ok']
            continue
        if store == 'intent':
            # read only
            target_state['intent'] = []
            continue
        if store == 'operational':
            # read only
            target_state['operational'] = []
            continue

    if not target:
        target = 'running'

    return target, target_state


def lock_datastore(key, target, timer):
    """Helper function to Lock the datastore.

    Checks for the open session associated with the device
    and uses the same to acquire the lock on the datastore.
    If no session found then creates one and acquires the lock.

    Args:
        key (SessionKey): Used to look up the NETCONF session
        target (str): datastore to lock
        timer (int): lock retry counter in seconds

    Returns:
        dict: ``{'reply': <message>}``
    """
    result = {'reply': 'Unknown Reason'}
    locked = False
    try:
        nconf_session = NetconfSession.get(key)
    except NetconfNotSupported:
        result['reply'] = "The device doesn't support netconf"
        return result

    session_manager = nconf_session.manager
    if session_manager is not None:
        locked = try_lock(nconf_session, target, timer)
        if locked:
            nconf_session.locked_datastores.append(target)
            result['reply'] = "Datastore Locked"
            nconf_session.log('Datastore ' + target + ' Locked successfully')
        else:
            nconf_session.log("Lock operation failed")
            result['reply'] = "Lock failed"
        return result
    else:
        nconf_session.log(
            'No active session found. Start a session to acquire lock')
        result['reply'] = \
            "No active session found. Start a session to acquire lock"
    return result


def unlock_datastore(key, target):
    """Function to unlock the datastore.

    Tries to unlock the datastore and removes the corresponding
    datastore entry association with the device.

    Args:
        key (SessionKey): key to locate session object
        target (str): datastore to unlock

    Returns:
        dict: ``{'reply': <message>}``
    """
    result = {'reply': 'Unknown Reason'}
    try:
        nconf_session = NetconfSession.get(key)
    except NetconfNotSupported:
        result['reply'] = "The device doesn't support netconf"
        return result

    session_manager = nconf_session.manager
    if session_manager is not None:
        if target in nconf_session.locked_datastores:
            ret = session_manager.unlock(target=target)
            if ret.ok:
                nconf_session.locked_datastores.remove(target)
                nconf_session.log('Datastore ' + target +
                                  ' unlocked successfully')
                result['reply'] = "Datastore unlocked successfully"
            else:
                error = ret.error.tag
                log.error('Error: unlock failed with ' + error + ' error')
                nconf_session.log('ERROR: unlock failed with ' + error +
                                  ' error')
                result['reply'] = 'Unlock failed with ' + error + ' error'
        else:
            nconf_session.log('Already Unlocked')
            result['reply'] = "Already Unlocked"
    else:
        nconf_session.log('No active session found')
        result['reply'] = "No active session found"
    return result


def start_session(key, timeout=None):
    """Starts a new NETCONF session.

    Args:
        key (SessionKey): Index to locate/store the session.
        timeout (int): RPC reply timeout value in seconds.

    Returns:
        bool: True if session was successfully started (or already exists),
          else False
    """
    try:
        nconf_session = NetconfSession.get(key)
    except NetconfNotSupported:
        return False

    return bool(nconf_session.connect(timeout))


def end_session(key):
    """Closes the netconf session.

    Args:
        key (SessionKey): Index to locate the session.

    Returns:
        bool: True if session is closed (or was already closed), else False.
    """
    result = False
    try:
        nconf_session = NetconfSession.get(key)
        NetconfSession.destroy(key)
    except NetconfNotSupported:
        return result

    return bool(nconf_session.disconnect())


def set_logging(loglevel):
    """Set the logging level for ncclient module

    Args:
        loglevel (str): logging level to be set.
    """
    logger1 = logging.getLogger('yangsuite')
    logger2 = logging.getLogger('ncclient')
    handlers = logger1.handlers

    for handler in handlers:
        if handler not in logger2.handlers:
            logger2.addHandler(handler)

    if loglevel == 'debug':
        logger2.setLevel(logging.DEBUG)
    else:
        # Don't permit any level less verbose than INFO, because the RPCs
        # sent and received are logged at INFO level and we need to see those.
        logger2.setLevel(logging.INFO)

    return True


def gen_raw_rpc(cfgd, prefix_namespaces="always"):
    """Construct the XML Element(s) needed for the given config dict.

    Creates lxml Element instances containing all required XML needed to
    run a netconf protocol operation using the ncclient run_command option.

    Helper function to :func:`gen_rpc_api`.

    Args:
       cfgd (dict): Relevant keys are 'proto-op', 'dsstore', 'namespace',
         'prefix', 'configs', 'with-defaults'.
       prefix_namespaces (str): Either 'always' or 'minimal', affecting whether
         prefixed or unprefixed namespaces are preferred.

    Returns:
       lxml.etree.Element: or None in case of failure

    Raises:
       ysnetconf.RpcInputError: if cfgd is invalid;
         see :meth:`YSNetconfRPCBuilder.get_payload`.
    """
    if not cfgd:
        return None

    rpcbuilder = YSNetconfRPCBuilder(prefix_namespaces=prefix_namespaces)

    proto_op_cfg = {
        'get-config': {
            'direction': rpcbuilder.netconf_element('source'),
            'payload': rpcbuilder.netconf_element('filter'),
        },
        'get': {
            'direction': None,
            'payload': rpcbuilder.netconf_element('filter'),
        },
        'edit-config': {
            'direction': rpcbuilder.netconf_element('target'),
            'payload': rpcbuilder.netconf_element('config'),
        },
        'action': {
            'direction': None,
            'payload': None,
        },
        'rpc': {
            'direction': None,
            'payload': None,
        }
    }

    prt_op = cfgd['proto-op']

    log.debug("Constructing raw RPC for %s", prt_op)

    rpc = rpcbuilder.netconf_element('rpc')
    rpcbuilder.add_netconf_attr(rpc, 'message-id', str(101))

    poc = proto_op_cfg[prt_op]

    direction = poc['direction']

    payload = poc['payload']

    if prt_op == 'action':
        action = rpcbuilder.yang_element(prt_op)
        rpc.append(action)
        container = action
    elif prt_op == 'rpc':
        # generic RPC
        container = rpc
    else:
        proto_op = rpcbuilder.netconf_element(prt_op)
        rpc.append(proto_op)
        if direction is not None:
            dsstore = cfgd['dsstore']
            store = rpcbuilder.netconf_element(dsstore)
            direction.append(store)
            proto_op.append(direction)

        proto_op.append(payload)

        if prt_op in ['get', 'get-config']:
            with_defaults = cfgd.get('with-defaults', '')
            if with_defaults:
                wd = rpcbuilder.ncwd_element('with-defaults')
                wd.text = with_defaults
                proto_op.append(wd)

        container = payload

    for modcfgd in cfgd.get('modules', {}).values():
        rpcbuilder = YSNetconfRPCBuilder(
            prefix_namespaces=prefix_namespaces,
            nsmap=modcfgd.get('namespace_prefixes'),
        )

        container = rpcbuilder.get_payload(modcfgd['configs'], container)

    # get-config and get can get by just fine without a <filter> element,
    # but edit-config must have a <config> even if it's empty
    if prt_op in ['get-config', 'get'] and len(container) == 0:
        container.getparent().remove(container)

    return rpc


def _commit_rpc(gentype, prefix_namespaces='always'):
    """Helper function to build commit RPC.

    Args:
      gentype (str): One of 'raw', 'basic', 'run', 'script'
      prefix_namespaces (str): Either 'always' or 'minimal', affecting whether
        prefixed or unprefixed namespaces are preferred.
    Returns:
      str: commit RPC
    """
    if gentype == 'raw':
        rpcbuilder = YSNetconfRPCBuilder(prefix_namespaces=prefix_namespaces)
        rpc = rpcbuilder.netconf_element('rpc')
        rpcbuilder.add_netconf_attr(rpc, 'message-id', str(102))
        rpc.append(rpcbuilder.netconf_element('commit'))
    elif gentype == 'script':
        rpcbuilder = YSNetconfRPCBuilder(prefix_namespaces=prefix_namespaces)
        rpc = rpcbuilder.netconf_element('commit')
    elif gentype == 'basic' or gentype == 'run':
        rpc = et.Element('commit')
    else:
        raise ValueError("Unexpected gentype string '{0}'".format(gentype))
    return et.tostring(rpc, encoding='unicode', pretty_print=True)


def gen_rpc_api(request):
    """Construct the XML string and ncclient ops for the given request.

    Args:
      request (dict): relevant keys are:

        - 'gentype' - one of 'raw', 'basic', 'run', or 'script'
        - 'prefix_namespaces' - one of 'always' or 'minimal'
        - 'commit' - "add", or any other value to not add
        - 'cfgd' (data) **or** 'cfg' (JSON representation of cfgd)

          - For any gentype other than 'script', this is a dict representing
            a single RPC. See :func:`gen_ncclient_rpc` and :func:`gen_raw_rpc`
            for the expectations of this dict's keys.
          - For gentype 'script', this is a **list** of dicts each with key
            'cfg' or 'cfgd' and value corresponding to a dict to pass to
            :func:`gen_raw_rpc`.

    Returns:
      dict: with format::

        {'rpc': <XML string or error message>,
         'ncrpcs': [[nc_op, kwargs], [nc_op, kwargs]...]}
    """
    result = {'rpc': 'Failed to generate RPC', 'ncrpcs': []}
    rpctext = ''

    if 'cfg' in request:
        cfgs = request.get("cfg")
        cfgd = json.loads(cfgs)
    else:
        cfgd = request.get("cfgd", {})

    if not cfgd:
        log.warning("No configuration sent for RPC generation")
        return result

    commit = request.get('commit', False)
    prefix_namespaces = request.get('prefix_namespaces', 'minimal')
    gentype = request.get('gentype', None)

    if gentype == 'raw':
        try:
            elem = gen_raw_rpc(cfgd, prefix_namespaces=prefix_namespaces)
        except RpcInputError as exc:
            result['rpc'] = str(exc)
            return result
        rpctext = et.tostring(elem, encoding='unicode', pretty_print=True)
        if commit and cfgd['dsstore'] == 'candidate':
            rpctext += "\n" + _commit_rpc(gentype,
                                          prefix_namespaces=prefix_namespaces)
        result['rpc'] = rpctext
    elif gentype == 'script':
        rpcs = []
        # For the other gentypes, cfg -> cfgd is a dict (an RPC)
        # For 'script', cfgd is a list of dicts (all RPCs to include in script)
        for rpc in cfgd:
            rpc_cfgd = rpc.get('cfgd') or json.loads(rpc['cfg'])
            try:
                elem = gen_raw_rpc(rpc_cfgd,
                                   prefix_namespaces=prefix_namespaces)
            except RpcInputError as exc:
                result['rpc'] = str(exc)
                return result
            # Unlike the 'raw' case above, here we don't want the outer <rpc>
            # element, we just want its contents, its first/only child element
            rpctext = et.tostring(elem[0], encoding='unicode',
                                  pretty_print=True)
            rpcs.append(rpctext)
            if rpc.get('commit', False) and rpc_cfgd['dsstore'] == 'candidate':
                rpcs.append(_commit_rpc(gentype,
                                        prefix_namespaces=prefix_namespaces))
        tplt = Template(script_template)
        result['rpc'] = tplt.render({'rpcs': rpcs})
    elif gentype in ['basic', 'run']:
        try:
            ncrpcs = gen_ncclient_rpc(cfgd,
                                      prefix_namespaces=prefix_namespaces)
        except RpcInputError as exc:
            result['rpc'] = str(exc)
            return result

        if not ncrpcs:
            return result
        # ncrpc = [proto_op, {option: value, option: value}] - get values
        elems = [value for ncrpc in ncrpcs for value in ncrpc[1].values()]
        for elem in elems:
            if not et.iselement(elem):
                continue
            try:
                rpctext += et.tostring(elem,
                                       encoding='unicode',
                                       pretty_print=True)
            except Exception:
                log.error(
                    "Problem forming return string for RPC\n{0}".format(
                        traceback.format_exc()))
        if commit and cfgd['dsstore'] == 'candidate':
            ncrpcs += [['commit', {}]]
            rpctext += "\n" + _commit_rpc(gentype,
                                          prefix_namespaces=prefix_namespaces)

        result['ncrpcs'] = ncrpcs
        result['rpc'] = rpctext

    return result


def gen_task_api(replay, request):
    """Given a replay task, construct XML request with the given options.

    Args:
      replay (dict): contains data from a stored task (see task.py)
      request (dict):
        -  prefixes (str): Namespace prefix setting
        -  dsstore (str): Target datastore. Ignored for custom RPCs.
        -  gentype (str): 'basic', 'raw', or 'run'.

    Returns:
      dict: of the form::
        - ncrpcs (lxml.Element): lxml objects if "basic" gentype
        - segments (str): RPC's or Python script, "custom" or "script" gentype
        - info (str): Modules with revisions used for RPC's
        - error (str): Any errors encountered
    """
    dsstore = request.get('dsstore')
    if not dsstore:
        raise TaskException('No datastore sent for task')

    prefixes = request.get('prefixes', 'minimal')
    gentype = request.get('gentype', 'basic')

    segments = ''
    errors = ''
    mods = []
    ncrpcs = []
    task = replay['task']
    for seg in task['segments']:
        try:
            commit = seg['commit']
            cfgd = seg['yang']
            cfgd['dsstore'] = dsstore

            # need this format for rpcbuilder
            for mod, data in cfgd.get('modules', {}).items():
                if 'revision' in list(data.keys()):
                    if [mod, data['revision']] not in mods:
                        mods.append([mod, data['revision']])

            if cfgd['proto-op'] == 'custom':
                segments += cfgd['rpc']
                if gentype == 'run':
                    rpc = et.fromstring(cfgd['rpc'])
                    ncrpcs.append(['rpc', {'rpc_command': rpc}])
                continue

            if gentype in ['raw', 'basic']:
                res = gen_rpc_api({'commit': commit,
                                   'cfgd': cfgd,
                                   'prefix_namespaces': prefixes,
                                   'gentype': gentype})
                segments += res['rpc'] + '\n'
            elif gentype == 'script':
                res = gen_rpc_api({'commit': commit,
                                   'cfgd': cfgd,
                                   'prefix_namespaces': prefixes,
                                   'gentype': 'raw'})
                ncrpcs.append(res['rpc'])
            elif gentype == 'run':
                res = gen_rpc_api({'commit': commit,
                                   'cfgd': cfgd,
                                   'prefix_namespaces': prefixes,
                                   'gentype': gentype})
                ncrpcs += res['ncrpcs']
            else:
                ncrpcs = ''

        except Exception:
            log.error("Failed to gen segment %s", seg['segment'])
            log.debug(traceback.format_exc())
            errors += "Failed to gen segment {0}\n{1}\n".format(
                str(seg['segment']), traceback.format_exc())

    if gentype == 'script':
        tplt = Template(script_template)
        segments = tplt.render({'rpcs': ncrpcs})

    return {'ncrpcs': ncrpcs,
            'segments': segments,
            'info': mods,
            'error': errors}


def ncclient_supported_platforms():
    """Look up submodules of :mod:`ncclient.devices` to find supported devices.

    The :mod:`ncclient` library doesn't publish a list of platforms, but when
    the user specifies a platform name, it looks up
    ``ncclient.devices.<name>``, so, we just need to find these submodules.

    Returns:
       list: of name strings
    """
    return list(modinfo[1] for modinfo in
                pkgutil.walk_packages(ncclient.devices.__path__))


def ncclient_manager_kwargs(dev_profile, timeout=None):
    """Populate the device parameters needed for :mod:`ncclient.manager`.

    Args:
        dev_profile (ysdevices.YSDeviceProfile): Device to send the RPC to.
        timeout (int): RPC reply timeout value in seconds. If not specified,
            will use the default timeout provided by the device profile.

    Returns:
        dict: populated parameters for :mod:`ncclient.manager`.
    """
    if dev_profile.netconf.device_variant in ncclient_supported_platforms():
        params = {'name': dev_profile.netconf.device_variant}
    else:
        params = {'name': 'default'}

    kwargs = {
        'host': dev_profile.netconf.address,
        'port': dev_profile.netconf.port,
        'username': dev_profile.netconf.username,
        'password': dev_profile.netconf.password,
        'device_params': params,
        'timeout': timeout or dev_profile.netconf.timeout,
    }

    if dev_profile.netconf.ignore_keys:
        kwargs['hostkey_verify'] = False
        kwargs['look_for_keys'] = False
        kwargs['allow_agent'] = False

    return kwargs


def ncclient_server_capability_uris(key):
    """Get list of URIs identifying server capabilities.

    Args:
      key (SessionKey): Used to locate the device session

    Returns:
      list: of URI strings
    """
    with NetconfSession.get(key) as ncs:
        capabilities = list(ncs.manager.server_capabilities)

    # Capability can be of the form uri?module=foo&revision=bar&...
    # We just want the uri
    return [cap.split('?')[0].strip() for cap in capabilities]


def ncclient_server_capabilities(key, filter):
    """Check server capabilities from session_manager.

    Args:
        key (SessionKey): Used to locate the device session
        filter (str): String containing the urn we're interested in
            e.g "urn:ietf:params:netconf:capability:candidate:1.0"

    Returns:
        bool: True/False based on if the device supports it
    """
    return (filter in ncclient_server_capability_uris(key))


def ncclient_server_capabilities_report(key):
    """Provide a structured report of NETCONF server reported capabilities.

    Args:
      key (SessionKey): Used to locate the device session

    Returns:
      list: of dicts, each with key 'capability' and possibly others
    """
    with NetconfSession.get(key) as ncs:
        capabilities = list(ncs.manager.server_capabilities)

    result = []
    # Capability can be of the form uri?module=foo&revision=bar&...
    for cap_entry in capabilities:
        capability = cap_entry.split('?')[0].strip()
        attributes = cap_entry.split('?')[1] if '?' in cap_entry else ''
        entry = {'capability': capability}
        for attr in attributes.split('&'):
            if not attr:
                continue
            name, value = attr.split("=") if '=' in attr else (attr, None)
            if ',' in value:
                value = value.split(',')
            entry[name] = value
        result.append(entry)

    def sort_order(cap_entry):
        """Sort capabilities more intelligently than alphabetical alone."""
        capability = cap_entry['capability']
        if capability.startswith("urn:ietf:params:netconf:"):
            # core NETCONF capability
            return (0, capability)
        elif (capability.startswith("http://tail-f.com/ns/netconf") or
              capability.startswith("http://tail-f.com/ns/common")):
            # tail-f protocol capability
            return (1, capability)
        elif capability.startswith("urn:ietf:params:xml:ns:yang:smiv2:"):
            # SNMP MIB
            return (100, capability)
        elif capability.startswith("urn:ietf:params:xml:ns:"):
            # IETF module other than an SNMP MIB
            return (10, capability)
        elif capability.startswith("http://openconfig.net/yang/"):
            # OpenConfig YANG module
            return (11, capability)
        elif capability.startswith("http://tail-f.com/yang/"):
            # tail-f YANG module
            return (12, capability)
        else:
            # Native YANG module, etc.
            return (50, capability)

    return sorted(result, key=sort_order)


CAP_CANDIDATE = 'urn:ietf:params:netconf:capability:candidate:1.0'
CAP_WRITABLE_RUN = 'urn:ietf:params:netconf:capability:writable-running:1.0'
CAP_STARTUP = 'urn:ietf:params:netconf:capability:startup:1.0'


def ncclient_server_datastores(key, operation):
    """Get the list of datastores applicable to a given device and operation.

    Args:
      key (SessionKey): Used to locate the device session
      operation (str): 'get-config', 'edit-config' are presently supported;
        any other value will be treated as the union of these two operations
        (i.e., any datastore supported by either operation will be returned).

    Returns:
      list: such as ('running', 'candidate', 'startup')
    """
    capabilities = ncclient_server_capability_uris(key)
    datastores = []
    if CAP_WRITABLE_RUN in capabilities or operation != 'edit-config':
        datastores.append('running')
    if CAP_CANDIDATE in capabilities:
        datastores.append('candidate')
    if operation != 'edit-config' and CAP_STARTUP in capabilities:
        datastores.append('startup')
    log.debug('Datastores for "%s" on device "%s": %s',
              operation, key.device, datastores)
    return sorted(datastores)


NOTIFY_CAP_NS = 'urn:ietf:params:netconf:capability:notification:1.0'
NOTIFICATION_NS = "urn:ietf:params:xml:ns:netmod:notification"


def get_schema_list_via_capabilities(key):
    """Get list of schema capabilities via NETCONF.

    This is a helper method to
    :func:`~ysnetconf.views.download.get_schema_list`; calling this presumes
    that the caller has already confirmed that the device is reachable and that
    it does **NOT** support ietf-netconf-monitoring.

    (If ietf-netconf-monitoring is supported, use
    :func:`get_schema_list_via_ietf_netconf_monitoring` instead!)

    Args:
      key (SessionKey): used to look up the device session

    Returns:
      list: List of ``{'name': NAME, 'revision': REVISION}`` items.

    Raises:
      OSError: ECONNREFUSED if unable to connect to the device.
    """
    with NetconfSession.get(key) as ncs:
        caps = ncs.manager.server_capabilities

    schemas = []
    # Capability can be of the form uri?module=foo&revision=bar&...
    # We just want the module + revision, if present
    MOD_RE = re.compile(r"module=([^&]+)")
    REV_RE = re.compile(r"revision=([^&]+)")
    for cap in caps:
        m = re.search(MOD_RE, cap)
        if not m:
            # It's a capability, but not a module
            continue
        mod = m.group(1)

        rev = "unknown"
        m = re.search(REV_RE, cap)
        if m:
            rev = m.group(1)

        schemas.append({'name': mod, 'revision': rev})

    return schemas


YANG_LIBRARY_CAP_NS = "urn:ietf:params:netconf:capability:yang-library:1.0"
YANG_LIBRARY_NS = "urn:ietf:params:xml:ns:yang:ietf-yang-library"


def get_schema_list_via_ietf_yang_library(key):
    """Get list of supported schemas using the ietf-yang-library API.

    This is a helper method to
    :func:`~ysnetconf.views.download.get_schema_list`; calling this
    presumes that the caller has already confirmed that the device
    supports this feature.

    Args:
      key (SessionKey): used to identify the device session

    Returns:
      list: List of ``{'name': NAME, 'revision': REVISION}`` items.

    Raises:
      OSError: ECONNREFUSED if unable to connect to the device.
    """
    getlist = et.Element("modules-state", xmlns=YANG_LIBRARY_NS)
    module = et.SubElement(getlist, 'module')
    et.SubElement(module, 'name')
    et.SubElement(module, 'revision')
    submodule = et.SubElement(module, 'submodule')
    et.SubElement(submodule, 'name')
    et.SubElement(submodule, 'revision')

    with NetconfSession.get(key) as ncs:
        reply = ncs.manager.get(filter=('subtree', getlist))

    schemas = []
    if not hasattr(reply, 'data_ele') or reply.data_ele is None:
        return schemas

    data_ele = reply.data_ele
    # Reply content is of the form:
    # <data>
    #  <modules-state xmlns="urn:ietf:params:xml:ns:yang:ietf-yang-library">
    #   <module>
    #     <name>Cisco-IOS-XE-native</name>
    #     <revision>2018-08-10</revision>
    #     <submodule>
    #       <name>Cisco-IOS-XE-interfaces</name>
    #       <revision>2018-09-28</revision>
    #     </submodule>
    #     <submodule>...</submodule>
    #     ...
    #   </module>
    #   <module>...</module>
    #   ...
    #  </modules-state>
    # </data>
    module_xpath = "{0}/{1}".format(et.QName(YANG_LIBRARY_NS, "modules-state"),
                                    et.QName(YANG_LIBRARY_NS, "module"))
    submodule_xpath = "{0}/{1}".format(module_xpath,
                                       et.QName(YANG_LIBRARY_NS, "submodule"))

    for mod in chain(data_ele.iterfind(module_xpath),
                     data_ele.iterfind(submodule_xpath)):
        if len(mod):
            name = mod[0].text
            revision = mod[1].text

            schemas.append({'name': name, 'revision': revision})

    return schemas


MONITORING_NS = "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"


def get_schema_list_via_ietf_netconf_monitoring(key):
    """Get list of supported schemas using the ietf-netconf-monitoring API.

    This is a helper method to
    :func:`~ysnetconf.views.download.get_schema_list`; calling this
    presumes that the caller has already confirmed that the device
    supports this feature.

    Args:
      key (SessionKey): used to identify the device session

    Returns:
      list: List of ``{'name': NAME, 'revision': REVISION}`` items.

    Raises:
      OSError: ECONNREFUSED if unable to connect to the device.
    """
    getlist = et.Element('netconf-state', xmlns=MONITORING_NS)
    et.SubElement(getlist, 'schemas')

    with NetconfSession.get(key) as ncs:
        reply = ncs.manager.get(filter=('subtree', getlist))

    schemas = []
    if not hasattr(reply, 'data_ele') or reply.data_ele is None:
        return schemas

    data_ele = reply.data_ele
    # Reply content is of the form:
    # <data>
    #   <netconf-state xmlns="...ietf-netconf-monitoring">
    #     <schemas>
    #       <schema> ... </schema>
    #       <schema> ... </schema>
    #       <schema> ... </schema>
    #     </schema>
    #   </netconf-state>
    # </data>
    xpath = "{0}/{1}/{2}".format(et.QName(MONITORING_NS, "netconf-state"),
                                 et.QName(MONITORING_NS, "schemas"),
                                 et.QName(MONITORING_NS, "schema"))
    for sc in data_ele.iterfind(xpath):
        if len(sc):
            # <schema>
            #   <identifier>openconfig-yang-types</identifier>
            #   <version>2017-01-26</version>
            #   <format>yang</format>
            #   <namespace>http://openconfig.net/yang/types/yang</namespace>
            #   <location>NETCONF</location>
            # </schema>
            identifier = sc[0].text
            version = sc[1].text

            schemas.append({'name': identifier, 'revision': version})

    return schemas
