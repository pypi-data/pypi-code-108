# Copyright (c) 2017 Red Hat
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import cherrypy
import socket
from collections import defaultdict
from contextlib import suppress

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import codecs
import copy
from datetime import datetime
import json
import logging
import os
import time
import select
import ssl
import threading

import zuul.executor.common
from zuul import exceptions
from zuul.configloader import ConfigLoader
from zuul.connection import BaseConnection
import zuul.lib.repl
from zuul.lib import commandsocket, encryption, streamer_utils
from zuul.lib.ansible import AnsibleManager
from zuul.lib.jsonutil import ZuulJSONEncoder
from zuul.lib.keystorage import KeyStorage
from zuul.lib.monitoring import MonitoringServer
from zuul.lib.re2util import filter_allowed_disallowed
from zuul.model import (
    Abide,
    Branch,
    ChangeQueue,
    DequeueEvent,
    EnqueueEvent,
    HoldRequest,
    PromoteEvent,
    QueueItem,
    SystemAttributes,
    UnparsedAbideConfig,
    WebInfo,
)
from zuul.version import get_version_string
from zuul.zk import ZooKeeperClient
from zuul.zk.components import ComponentRegistry, WebComponent
from zuul.zk.config_cache import SystemConfigCache
from zuul.zk.event_queues import (
    TenantManagementEventQueue,
    TenantTriggerEventQueue,
    PipelineManagementEventQueue,
    PipelineResultEventQueue,
    PipelineTriggerEventQueue,
)
from zuul.zk.executor import ExecutorApi
from zuul.zk.layout import LayoutStateStore
from zuul.zk.locks import tenant_read_lock
from zuul.zk.nodepool import ZooKeeperNodepool
from zuul.zk.system import ZuulSystem
from zuul.zk.zkobject import LocalZKContext, ZKContext
from zuul.lib.auth import AuthenticatorRegistry
from zuul.lib.config import get_default

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
cherrypy.tools.websocket = WebSocketTool()

COMMANDS = ['stop', 'repl', 'norepl']


class SaveParamsTool(cherrypy.Tool):
    """
    Save the URL parameters to allow them to take precedence over query
    string parameters.
    """
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.saveParams)

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_handler',
                                      self.restoreParams)

    def saveParams(self, restore=True):
        cherrypy.request.url_params = cherrypy.request.params.copy()
        cherrypy.request.url_params_restore = restore

    def restoreParams(self):
        if cherrypy.request.url_params_restore:
            cherrypy.request.params.update(cherrypy.request.url_params)


cherrypy.tools.save_params = SaveParamsTool()


def handle_options(allowed_methods=None):
    if cherrypy.request.method == 'OPTIONS':
        methods = allowed_methods or ['GET', 'OPTIONS']
        if allowed_methods and 'OPTIONS' not in allowed_methods:
            methods = methods + ['OPTIONS']
        # discard decorated handler
        request = cherrypy.serving.request
        request.handler = None
        # Set CORS response headers
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] =\
            ', '.join(['Authorization', 'Content-Type'])
        resp.headers['Access-Control-Allow-Methods'] =\
            ', '.join(methods)
        # Allow caching of the preflight response
        resp.headers['Access-Control-Max-Age'] = 86400
        resp.status = 204


cherrypy.tools.handle_options = cherrypy.Tool('on_start_resource',
                                              handle_options)


# Custom JSONEncoder that combines the ZuulJSONEncoder with cherrypy's
# JSON functionality.
class ZuulWebJSONEncoder(ZuulJSONEncoder):

    def iterencode(self, value):
        # Adapted from cherrypy/_json.py
        for chunk in super().iterencode(value):
            yield chunk.encode("utf-8")


json_encoder = ZuulWebJSONEncoder()


def json_handler(*args, **kwargs):
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return json_encoder.iterencode(value)


class ChangeFilter(object):
    def __init__(self, desired):
        self.desired = desired

    def filterPayload(self, payload):
        status = []
        for pipeline in payload['pipelines']:
            for change_queue in pipeline['change_queues']:
                for head in change_queue['heads']:
                    for change in head:
                        if self.wantChange(change):
                            status.append(copy.deepcopy(change))
        return status

    def wantChange(self, change):
        return change['id'] == self.desired


class LogStreamHandler(WebSocket):
    log = logging.getLogger("zuul.web")

    def __init__(self, *args, **kw):
        kw['heartbeat_freq'] = 20
        super(LogStreamHandler, self).__init__(*args, **kw)
        self.streamer = None

    def received_message(self, message):
        if message.is_text:
            req = json.loads(message.data.decode('utf-8'))
            self.log.debug("Websocket request: %s", req)
            if self.streamer:
                self.log.debug("Ignoring request due to existing streamer")
                return
            try:
                self._streamLog(req)
            except Exception:
                self.log.exception("Error processing websocket message:")
                raise

    def closed(self, code, reason=None):
        self.log.debug("Websocket closed: %s %s", code, reason)
        if self.streamer:
            try:
                self.streamer.zuulweb.stream_manager.unregisterStreamer(
                    self.streamer)
            except Exception:
                self.log.exception("Error on remote websocket close:")

    def logClose(self, code, msg):
        self.log.debug("Websocket close: %s %s", code, msg)
        try:
            self.close(code, msg)
        except Exception:
            self.log.exception("Error closing websocket:")

    def _streamLog(self, request):
        """
        Stream the log for the requested job back to the client.

        :param dict request: The client request parameters.
        """
        for key in ('uuid', 'logfile'):
            if key not in request:
                return self.logClose(
                    4000,
                    "'{key}' missing from request payload".format(
                        key=key))

        try:
            port_location = streamer_utils.getJobLogStreamAddress(
                self.zuulweb.executor_api, self.zuulweb.component_registry,
                request['uuid'], source_zone=self.zuulweb.zone)
        except exceptions.StreamingError as e:
            return self.logClose(4011, str(e))

        if not port_location:
            return self.logClose(4011, "Error with log streaming")

        self.streamer = LogStreamer(
            self.zuulweb, self,
            port_location['server'], port_location['port'],
            request['uuid'], port_location.get('use_ssl'))


class LogStreamer(object):
    log = logging.getLogger("zuul.web")

    def __init__(self, zuulweb, websocket, server, port, build_uuid, use_ssl):
        """
        Create a client to connect to the finger streamer and pull results.

        :param str server: The executor server running the job.
        :param str port: The executor server port.
        :param str build_uuid: The build UUID to stream.
        """
        self.log.debug("Connecting to finger server %s:%s", server, port)
        Decoder = codecs.getincrementaldecoder('utf8')
        self.decoder = Decoder()
        self.zuulweb = zuulweb
        self.finger_socket = socket.create_connection(
            (server, port), timeout=10)
        if use_ssl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = self.zuulweb.finger_tls_verify_hostnames
            context.load_cert_chain(
                self.zuulweb.finger_tls_cert, self.zuulweb.finger_tls_key)
            context.load_verify_locations(self.zuulweb.finger_tls_ca)
            self.finger_socket = context.wrap_socket(
                self.finger_socket, server_hostname=server)

        self.finger_socket.settimeout(None)
        self.websocket = websocket
        self.uuid = build_uuid
        msg = "%s\n" % build_uuid    # Must have a trailing newline!
        self.finger_socket.sendall(msg.encode('utf-8'))
        self.zuulweb.stream_manager.registerStreamer(self)

    def __repr__(self):
        return '<LogStreamer %s uuid:%s>' % (self.websocket, self.uuid)

    def errorClose(self):
        self.websocket.logClose(4011, "Unknown error")

    def handle(self, event):
        if event & select.POLLIN:
            data = self.finger_socket.recv(1024)
            if data:
                data = self.decoder.decode(data)
                if data:
                    self.websocket.send(data, False)
            else:
                # Make sure we flush anything left in the decoder
                data = self.decoder.decode(b'', final=True)
                if data:
                    self.websocket.send(data, False)
                self.zuulweb.stream_manager.unregisterStreamer(self)
                self.finger_socket.close()
                return self.websocket.logClose(1000, "No more data")
        else:
            self.zuulweb.stream_manager.unregisterStreamer(self)
            self.finger_socket.close()
            return self.websocket.logClose(1000, "Remote error")


class ZuulWebAPI(object):
    log = logging.getLogger("zuul.web")

    def __init__(self, zuulweb):
        self.zk_client = zuulweb.zk_client
        self.system = ZuulSystem(self.zk_client)
        self.zk_nodepool = ZooKeeperNodepool(self.zk_client,
                                             enable_node_cache=True)
        self.zuulweb = zuulweb
        self.cache = {}
        self.cache_time = {}
        self.cache_expiry = 1
        self.static_cache_expiry = zuulweb.static_cache_expiry
        self.status_lock = threading.Lock()

    def _basic_auth_header_check(self):
        """make sure protected endpoints have a Authorization header with the
        bearer token."""
        token = cherrypy.request.headers.get('Authorization', None)
        # Add basic checks here
        if token is None:
            status = 401
            e = 'Missing "Authorization" header'
            e_desc = e
        elif not token.lower().startswith('bearer '):
            status = 401
            e = 'Invalid Authorization header format'
            e_desc = '"Authorization" header must start with "Bearer"'
        else:
            return None
        error_header = '''Bearer realm="%s"
       error="%s"
       error_description="%s"''' % (self.zuulweb.authenticators.default_realm,
                                    e,
                                    e_desc)
        cherrypy.response.status = status
        cherrypy.response.headers["WWW-Authenticate"] = error_header
        return {'description': e_desc,
                'error': e,
                'realm': self.zuulweb.authenticators.default_realm}

    def _auth_token_check(self):
        rawToken = \
            cherrypy.request.headers['Authorization'][len('Bearer '):]
        try:
            claims = self.zuulweb.authenticators.authenticate(rawToken)
        except exceptions.AuthTokenException as e:
            for header, contents in e.getAdditionalHeaders().items():
                cherrypy.response.headers[header] = contents
            cherrypy.response.status = e.HTTPError
            return ({},
                    {'description': e.error_description,
                     'error': e.error,
                     'realm': e.realm})
        return (claims, None)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['POST', ])
    def dequeue(self, tenant_name, project_name):
        basic_error = self._basic_auth_header_check()
        if basic_error is not None:
            return basic_error
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405)
        # AuthN/AuthZ
        claims, token_error = self._auth_token_check()
        if token_error is not None:
            return token_error
        self.isAuthorizedOrRaise(claims, tenant_name)
        msg = 'User "%s" requesting "%s" on %s/%s'
        self.log.info(
            msg % (claims['__zuul_uid_claim'], 'dequeue',
                   tenant_name, project_name))

        tenant = self._getTenantOrRaise(tenant_name)
        project = self._getProjectOrRaise(tenant, project_name)

        body = cherrypy.request.json
        if 'pipeline' in body and (
                ('change' in body and 'ref' not in body) or
                ('change' not in body and 'ref' in body)):
            # Validate the pipeline so we can enqueue the event directly
            # in the pipeline management event queue and don't need to
            # take the detour via the tenant management event queue.
            pipeline_name = body['pipeline']
            pipeline = tenant.layout.pipelines.get(pipeline_name)
            if pipeline is None:
                raise cherrypy.HTTPError(400, 'Unknown pipeline')

            event = DequeueEvent(
                tenant_name, pipeline_name, project.canonical_hostname,
                project.name, body.get('change', None), body.get('ref', None))
            self.zuulweb.pipeline_management_events[tenant_name][
                pipeline_name].put(event)
            resp = cherrypy.response
            resp.headers['Access-Control-Allow-Origin'] = '*'
        else:
            raise cherrypy.HTTPError(400, 'Invalid request body')
        return True

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['POST', ])
    def enqueue(self, tenant_name, project_name):
        basic_error = self._basic_auth_header_check()
        if basic_error is not None:
            return basic_error
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405)
        # AuthN/AuthZ
        claims, token_error = self._auth_token_check()
        if token_error is not None:
            return token_error
        self.isAuthorizedOrRaise(claims, tenant_name)
        msg = 'User "%s" requesting "%s" on %s/%s'
        self.log.info(
            msg % (claims['__zuul_uid_claim'], 'enqueue',
                   tenant_name, project_name))

        tenant = self._getTenantOrRaise(tenant_name)
        project = self._getProjectOrRaise(tenant, project_name)

        body = cherrypy.request.json
        if 'pipeline' not in body:
            raise cherrypy.HTTPError(400, 'Invalid request body')

        # Validate the pipeline so we can enqueue the event directly
        # in the pipeline management event queue and don't need to
        # take the detour via the tenant management event queue.
        pipeline_name = body['pipeline']
        pipeline = tenant.layout.pipelines.get(pipeline_name)
        if pipeline is None:
            raise cherrypy.HTTPError(400, 'Unknown pipeline')

        if 'change' in body:
            return self._enqueue(tenant, project, pipeline, body['change'])
        elif all(p in body for p in ['ref', 'oldrev', 'newrev']):
            return self._enqueue_ref(tenant, project, pipeline, body['ref'],
                                     body['oldrev'], body['newrev'])
        else:
            raise cherrypy.HTTPError(400, 'Invalid request body')

    def _enqueue(self, tenant, project, pipeline, change):
        event = EnqueueEvent(tenant.name, pipeline.name,
                             project.canonical_hostname, project.name,
                             change, ref=None, oldrev=None, newrev=None)
        self.zuulweb.pipeline_management_events[tenant.name][
            pipeline.name].put(event)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return True

    def _enqueue_ref(self, tenant, project, pipeline, ref, oldrev, newrev):
        event = EnqueueEvent(tenant.name, pipeline.name,
                             project.canonical_hostname, project.name,
                             change=None, ref=ref, oldrev=oldrev,
                             newrev=newrev)
        self.zuulweb.pipeline_management_events[tenant.name][
            pipeline.name].put(event)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return True

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['POST', ])
    def promote(self, tenant_name):
        basic_error = self._basic_auth_header_check()
        if basic_error is not None:
            return basic_error
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405)
        # AuthN/AuthZ
        claims, token_error = self._auth_token_check()
        if token_error is not None:
            return token_error
        self.isAuthorizedOrRaise(claims, tenant_name)

        body = cherrypy.request.json
        pipeline_name = body.get('pipeline')
        changes = body.get('changes')

        msg = 'User "%s" requesting "%s" on %s/%s'
        self.log.info(
            msg % (claims['__zuul_uid_claim'], 'promote',
                   tenant_name, pipeline_name))

        tenant = self._getTenantOrRaise(tenant_name)

        # Validate the pipeline so we can enqueue the event directly
        # in the pipeline management event queue and don't need to
        # take the detour via the tenant management event queue.
        pipeline = tenant.layout.pipelines.get(pipeline_name)
        if pipeline is None:
            raise cherrypy.HTTPError(400, 'Unknown pipeline')

        event = PromoteEvent(tenant_name, pipeline_name, changes)
        self.zuulweb.pipeline_management_events[tenant_name][
            pipeline_name].put(event)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return True

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def autohold_list(self, tenant_name, *args, **kwargs):
        # we don't use json_in because a payload is not mandatory with GET
        if cherrypy.request.method != 'GET':
            raise cherrypy.HTTPError(405)
        # filter by project if passed as a query string
        project_name = cherrypy.request.params.get('project', None)
        return self._autohold_list(tenant_name, project_name)

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['GET', 'POST', ])
    def autohold(self, tenant_name, project_name=None):
        # we don't use json_in because a payload is not mandatory with GET
        # Note: GET handling is redundant with autohold_list
        # and could be removed.
        if cherrypy.request.method == 'GET':
            return self._autohold_list(tenant_name, project_name)
        elif cherrypy.request.method == 'POST':
            basic_error = self._basic_auth_header_check()
            if basic_error is not None:
                return basic_error
            # AuthN/AuthZ
            claims, token_error = self._auth_token_check()
            if token_error is not None:
                return token_error
            self.isAuthorizedOrRaise(claims, tenant_name)
            msg = 'User "%s" requesting "%s" on %s/%s'
            self.log.info(
                msg % (claims['__zuul_uid_claim'], 'autohold',
                       tenant_name, project_name))

            length = int(cherrypy.request.headers['Content-Length'])
            body = cherrypy.request.body.read(length)
            try:
                jbody = json.loads(body.decode('utf-8'))
            except ValueError:
                raise cherrypy.HTTPError(406, 'JSON body required')

            # Validate the payload
            jbody['change'] = jbody.get('change', None)
            jbody['ref'] = jbody.get('ref', None)
            count = jbody.get('count')
            if jbody['change'] and jbody['ref']:
                raise cherrypy.HTTPError(
                    400, 'change and ref are mutually exclusive')
            if not all(p in jbody for p in [
                    'job', 'count', 'change', 'ref', 'reason',
                    'node_hold_expiration']):
                raise cherrypy.HTTPError(400, 'Invalid request body')
            if count < 0:
                raise cherrypy.HTTPError(400, "Count must be greater 0")

            tenant = self._getTenantOrRaise(tenant_name)
            project = self._getProjectOrRaise(tenant, project_name)

            project_name = project.canonical_name

            if jbody['change']:
                ref_filter = project.source.getRefForChange(jbody['change'])
            if jbody['ref']:
                ref_filter = str(jbody['ref'])
            else:
                ref_filter = ".*"

            self._autohold(tenant_name, project_name, jbody['job'], ref_filter,
                           jbody['reason'], jbody['count'],
                           jbody['node_hold_expiration'])
            resp = cherrypy.response
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return True
        else:
            raise cherrypy.HTTPError(405)

    def _autohold(self, tenant_name, project_name, job_name, ref_filter,
                  reason, count, node_hold_expiration):
        key = (tenant_name, project_name, job_name, ref_filter)
        self.log.debug("Autohold requested for %s", key)

        request = HoldRequest()
        request.tenant = tenant_name
        request.project = project_name
        request.job = job_name
        request.ref_filter = ref_filter
        request.reason = reason
        request.max_count = count

        zuul_globals = self.zuulweb.globals
        # Set node_hold_expiration to default if no value is supplied
        if node_hold_expiration is None:
            node_hold_expiration = zuul_globals.default_hold_expiration

        # Reset node_hold_expiration to max if it exceeds the max
        elif zuul_globals.max_hold_expiration and (
                node_hold_expiration == 0 or
                node_hold_expiration > zuul_globals.max_hold_expiration):
            node_hold_expiration = zuul_globals.max_hold_expiration

        request.node_expiration = node_hold_expiration

        # No need to lock it since we are creating a new one.
        self.zk_nodepool.storeHoldRequest(request)

    def _autohold_list(self, tenant_name, project_name=None):
        result = []
        for request_id in self.zk_nodepool.getHoldRequests():
            request = self.zk_nodepool.getHoldRequest(request_id)
            if not request:
                continue

            if tenant_name != request.tenant:
                continue

            if project_name is None or request.project.endswith(project_name):
                result.append({
                    'id': request.id,
                    'tenant': request.tenant,
                    'project': request.project,
                    'job': request.job,
                    'ref_filter': request.ref_filter,
                    'max_count': request.max_count,
                    'current_count': request.current_count,
                    'reason': request.reason,
                    'node_expiration': request.node_expiration,
                    'expired': request.expired,
                    'nodes': request.nodes,
                })

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return result

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['GET', 'DELETE', ])
    def autohold_by_request_id(self, tenant_name, request_id):
        if cherrypy.request.method == 'GET':
            return self._autohold_info(tenant_name, request_id)
        elif cherrypy.request.method == 'DELETE':
            return self._autohold_delete(tenant_name, request_id)
        else:
            raise cherrypy.HTTPError(405)

    def _autohold_info(self, tenant_name, request_id):
        request = self._get_autohold_request(tenant_name, request_id)
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return {
            'id': request.id,
            'tenant': request.tenant,
            'project': request.project,
            'job': request.job,
            'ref_filter': request.ref_filter,
            'max_count': request.max_count,
            'current_count': request.current_count,
            'reason': request.reason,
            'node_expiration': request.node_expiration,
            'expired': request.expired,
            'nodes': request.nodes,
        }

    def _autohold_delete(self, tenant_name, request_id):
        # We need tenant info from the request for authz
        request = self._get_autohold_request(tenant_name, request_id)
        basic_error = self._basic_auth_header_check()
        if basic_error is not None:
            return basic_error
        # AuthN/AuthZ
        claims, token_error = self._auth_token_check()
        if token_error is not None:
            return token_error
        self.isAuthorizedOrRaise(claims, request.tenant)
        msg = 'User "%s" requesting "%s" on %s/%s'
        self.log.info(
            msg % (claims['__zuul_uid_claim'], 'autohold-delete',
                   request.tenant, request.project))

        # User is authorized, so remove the autohold request
        self.log.debug("Removing autohold %s", request)
        try:
            self.zk_nodepool.deleteHoldRequest(request)
        except Exception:
            self.log.exception(
                "Error removing autohold request %s:", request)

        cherrypy.response.status = 204

    def _get_autohold_request(self, tenant_name, request_id):
        hold_request = None
        try:
            hold_request = self.zk_nodepool.getHoldRequest(request_id)
        except Exception:
            self.log.exception("Error retrieving autohold ID %s", request_id)

        if hold_request is None:
            raise cherrypy.HTTPError(
                404, f'Hold request {request_id} not found.')

        if tenant_name != hold_request.tenant:
            # return 404 rather than 403 to avoid leaking tenant info
            raise cherrypy.HTTPError(
                404, 'Hold request {request_id} not found.')

        return hold_request

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def index(self):
        return {
            'info': '/api/info',
            'connections': '/api/connections',
            'components': '/api/components',
            'tenants': '/api/tenants',
            'tenant_info': '/api/tenant/{tenant}/info',
            'status': '/api/tenant/{tenant}/status',
            'status_change': '/api/tenant/{tenant}/status/change/{change}',
            'jobs': '/api/tenant/{tenant}/jobs',
            'job': '/api/tenant/{tenant}/job/{job_name}',
            'projects': '/api/tenant/{tenant}/projects',
            'project': '/api/tenant/{tenant}/project/{project:.*}',
            'project_freeze_jobs': '/api/tenant/{tenant}/pipeline/{pipeline}/'
                                   'project/{project:.*}/branch/{branch:.*}/'
                                   'freeze-jobs',
            'pipelines': '/api/tenant/{tenant}/pipelines',
            'labels': '/api/tenant/{tenant}/labels',
            'nodes': '/api/tenant/{tenant}/nodes',
            'key': '/api/tenant/{tenant}/key/{project:.*}.pub',
            'project_ssh_key': '/api/tenant/{tenant}/project-ssh-key/'
                               '{project:.*}.pub',
            'console_stream': '/api/tenant/{tenant}/console-stream',
            'badge': '/api/tenant/{tenant}/badge',
            'builds': '/api/tenant/{tenant}/builds',
            'build': '/api/tenant/{tenant}/build/{uuid}',
            'buildsets': '/api/tenant/{tenant}/buildsets',
            'buildset': '/api/tenant/{tenant}/buildset/{uuid}',
            'config_errors': '/api/tenant/{tenant}/config-errors',
            # TODO(mhu) remove after next release
            'authorizations': '/api/user/authorizations',
            'tenant_authorizations': ('/api/tenant/{tenant}'
                                      '/authorizations'),
            'autohold': '/api/tenant/{tenant}/project/{project:.*}/autohold',
            'autohold_list': '/api/tenant/{tenant}/autohold',
            'autohold_by_request_id': ('/api/tenant/{tenant}'
                                       '/autohold/{request_id}'),
            'autohold_delete': ('/api/tenant/{tenant}'
                                '/autohold/{request_id}'),
            'enqueue': '/api/tenant/{tenant}/project/{project:.*}/enqueue',
            'dequeue': '/api/tenant/{tenant}/project/{project:.*}/dequeue',
            'promote': '/api/tenant/{tenant}/promote',
        }

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def info(self):
        return self._handleInfo(self.zuulweb.info)

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def tenant_info(self, tenant):
        info = self.zuulweb.info.copy()
        info.tenant = tenant
        tenant_config = self.zuulweb.unparsed_abide.tenants.get(tenant)
        if tenant_config is not None:
            # TODO: should we return 404 if tenant not found?
            tenant_auth_realm = tenant_config.get('authentication-realm')
            if tenant_auth_realm is not None:
                if (info.capabilities is not None and
                    info.capabilities.toDict().get('auth') is not None):
                    info.capabilities.capabilities['auth']['default_realm'] =\
                        tenant_auth_realm
        return self._handleInfo(info)

    def _handleInfo(self, info):
        ret = {'info': info.toDict()}
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        if self.static_cache_expiry:
            resp.headers['Cache-Control'] = "public, max-age=%d" % \
                self.static_cache_expiry
        resp.last_modified = self.zuulweb.start_time
        return ret

    def isAuthorizedOrRaise(self, claims, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        authorized = self._is_authorized(tenant, claims)
        if not authorized:
            raise cherrypy.HTTPError(403)

    def _is_authorized(self, tenant, claims):
        # First, check for zuul.admin override
        override = claims.get('zuul', {}).get('admin', [])
        if (override == '*' or
            (isinstance(override, list) and tenant.name in override)):
            return True

        for rule_name in tenant.authorization_rules:
            rule = self.zuulweb.abide.admin_rules.get(rule_name)
            if not rule:
                self.log.error('Undefined rule "%s"', rule_name)
                continue
            self.log.debug('Applying rule "%s" from tenant "%s" to claims %s',
                           rule_name, tenant.name, json.dumps(claims))
            authorized = rule(claims, tenant)
            if authorized:
                if '__zuul_uid_claim' in claims:
                    uid = claims['__zuul_uid_claim']
                else:
                    uid = json.dumps(claims)
                self.log.info('%s authorized on tenant "%s" by rule "%s"',
                              uid, tenant.name, rule_name)
                return True
        return False

    # TODO(mhu) deprecated, remove next version
    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['GET', ])
    def authorizations(self):
        basic_error = self._basic_auth_header_check()
        if basic_error is not None:
            return basic_error
        # AuthN/AuthZ
        claims, token_error = self._auth_token_check()
        if token_error is not None:
            return token_error
        try:
            admin_tenants = self._authorizations()
        except exceptions.AuthTokenException as e:
            for header, contents in e.getAdditionalHeaders().items():
                cherrypy.response.headers[header] = contents
            cherrypy.response.status = e.HTTPError
            return {'description': e.error_description,
                    'error': e.error,
                    'realm': e.realm}
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return {'zuul': {'admin': admin_tenants}, }

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    @cherrypy.tools.handle_options(allowed_methods=['GET', ])
    def tenant_authorizations(self, tenant):
        basic_error = self._basic_auth_header_check()
        if basic_error is not None:
            return basic_error
        # AuthN/AuthZ
        claims, token_error = self._auth_token_check()
        if token_error is not None:
            return token_error
        try:
            admin_tenants = self._authorizations()
        except exceptions.AuthTokenException as e:
            for header, contents in e.getAdditionalHeaders().items():
                cherrypy.response.headers[header] = contents
            cherrypy.response.status = e.HTTPError
            return {'description': e.error_description,
                    'error': e.error,
                    'realm': e.realm}
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return {'zuul': {'admin': tenant in admin_tenants,
                         'scope': [tenant, ]}, }

    def _authorizations(self):
        rawToken = cherrypy.request.headers['Authorization'][len('Bearer '):]
        claims = self.zuulweb.authenticators.authenticate(rawToken)

        if 'zuul' in claims and 'admin' in claims.get('zuul', {}):
            return claims['zuul']['admin']

        return [n for n, t in self.zuulweb.abide.tenants.items()
                if self._is_authorized(t, claims)]

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def tenants(self):
        result = []
        for tenant_name, tenant in sorted(self.zuulweb.abide.tenants.items()):
            queue_size = 0
            for pipeline in tenant.layout.pipelines.values():
                status = pipeline.summary.refresh(self.zuulweb.zk_context)
                for queue in status["change_queues"]:
                    for head in queue["heads"]:
                        for item in head:
                            if item["live"]:
                                queue_size += 1

            result.append({
                'name': tenant_name,
                'projects': len(tenant.untrusted_projects),
                'queue': queue_size,
            })

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return result

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def connections(self):
        ret = [s.connection.toDict()
               for s in self.zuulweb.connections.getSources()]
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type="application/json; charset=utf-8")
    def components(self):
        ret = {}
        for kind, components in self.zuulweb.component_registry.all():
            for comp in components:
                comp_json = {
                    "hostname": comp.hostname,
                    "state": comp.state,
                    "version": comp.version,
                }
                ret.setdefault(kind, []).append(comp_json)
        resp = cherrypy.response
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return ret

    def _getStatus(self, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        with self.status_lock:
            if tenant not in self.cache or \
               (time.time() - self.cache_time[tenant]) > self.cache_expiry:
                self.cache[tenant_name] = self.formatStatus(tenant)
                self.cache_time[tenant_name] = time.time()

        payload = self.cache[tenant_name]
        resp = cherrypy.response
        resp.headers["Cache-Control"] = f"public, max-age={self.cache_expiry}"
        last_modified = datetime.utcfromtimestamp(self.cache_time[tenant_name])
        last_modified_header = last_modified.strftime('%a, %d %b %Y %X GMT')
        resp.headers["Last-modified"] = last_modified_header
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return payload

    def formatStatus(self, tenant):
        data = {}
        data['zuul_version'] = self.zuulweb.component_info.version

        data['trigger_event_queue'] = {}
        data['trigger_event_queue']['length'] = len(
            self.zuulweb.trigger_events[tenant.name])
        data['management_event_queue'] = {}
        data['management_event_queue']['length'] = len(
            self.zuulweb.management_events[tenant.name]
        )
        data['connection_event_queues'] = {}
        for connection in self.zuulweb.connections.connections.values():
            queue = connection.getEventQueue()
            if queue is not None:
                data['connection_event_queues'][connection.connection_name] = {
                    'length': len(queue),
                }

        layout_state = self.zuulweb.tenant_layout_state[tenant.name]
        data['last_reconfigured'] = layout_state.last_reconfigured * 1000

        pipelines = []
        data['pipelines'] = pipelines

        trigger_event_queues = self.zuulweb.pipeline_trigger_events[
            tenant.name]
        result_event_queues = self.zuulweb.pipeline_result_events[tenant.name]
        management_event_queues = self.zuulweb.pipeline_management_events[
            tenant.name]
        for pipeline in tenant.layout.pipelines.values():
            status = pipeline.summary.refresh(self.zuulweb.zk_context)
            status['trigger_events'] = len(trigger_event_queues[pipeline.name])
            status['result_events'] = len(result_event_queues[pipeline.name])
            status['management_events'] = len(
                management_event_queues[pipeline.name])
            pipelines.append(status)
        return data

    def _getTenantOrRaise(self, tenant_name):
        tenant = self.zuulweb.abide.tenants.get(tenant_name)
        if tenant:
            return tenant
        if tenant_name not in self.zuulweb.unparsed_abide.tenants:
            raise cherrypy.HTTPError(404, "Unknown tenant")
        self.log.warning("Tenant %s isn't loaded", tenant_name)
        raise cherrypy.HTTPError(204, f"Tenant {tenant_name} isn't ready")

    def _getProjectOrRaise(self, tenant, project_name):
        _, project = tenant.getProject(project_name)
        if not project:
            raise cherrypy.HTTPError(404, "Unknown project")
        return project

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def status(self, tenant):
        return self._getStatus(tenant)

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def status_change(self, tenant, change):
        payload = self._getStatus(tenant)
        result_filter = ChangeFilter(change)
        return result_filter.filterPayload(payload)

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(
        content_type='application/json; charset=utf-8', handler=json_handler,
    )
    def jobs(self, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        result = []
        for job_name in sorted(tenant.layout.jobs):
            desc = None
            tags = set()
            variants = []
            for variant in tenant.layout.jobs[job_name]:
                if not desc and variant.description:
                    desc = variant.description.split('\n')[0]
                if variant.tags:
                    tags.update(list(variant.tags))
                job_variant = {}
                if not variant.isBase():
                    if variant.parent:
                        job_variant['parent'] = str(variant.parent)
                    else:
                        job_variant['parent'] = tenant.default_base_job
                branches = variant.getBranches()
                if branches:
                    job_variant['branches'] = branches
                if job_variant:
                    variants.append(job_variant)

            job_output = {"name": job_name}
            if desc:
                job_output["description"] = desc
            if variants:
                job_output["variants"] = variants
            if tags:
                job_output["tags"] = list(tags)
            result.append(job_output)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return result

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def config_errors(self, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        ret = [
            {'source_context': e.key.context.toDict(),
             'error': e.error}
            for e in tenant.layout.loading_errors.errors
        ]
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(
        content_type='application/json; charset=utf-8', handler=json_handler)
    def job(self, tenant_name, job_name):
        tenant = self._getTenantOrRaise(tenant_name)
        job_variants = tenant.layout.jobs.get(job_name)
        result = []
        for job in job_variants:
            result.append(job.toDict(tenant))

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return result

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def projects(self, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        result = []
        for project in tenant.config_projects:
            pobj = project.toDict()
            pobj['type'] = "config"
            result.append(pobj)
        for project in tenant.untrusted_projects:
            pobj = project.toDict()
            pobj['type'] = "untrusted"
            result.append(pobj)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return sorted(result, key=lambda project: project["name"])

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(
        content_type='application/json; charset=utf-8', handler=json_handler)
    def project(self, tenant_name, project_name):
        tenant = self._getTenantOrRaise(tenant_name)
        project = self._getProjectOrRaise(tenant, project_name)

        result = project.toDict()
        result['configs'] = []
        configs = tenant.layout.getAllProjectConfigs(project.canonical_name)
        for config_obj in configs:
            config = config_obj.toDict()
            config['pipelines'] = []
            for pipeline_name, pipeline_config in sorted(
                    config_obj.pipelines.items()):
                pipeline = pipeline_config.toDict()
                pipeline['name'] = pipeline_name
                pipeline['jobs'] = []
                for jobs in pipeline_config.job_list.jobs.values():
                    job_list = []
                    for job in jobs:
                        job_list.append(job.toDict(tenant))
                    pipeline['jobs'].append(job_list)
                config['pipelines'].append(pipeline)
            result['configs'].append(config)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return result

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def pipelines(self, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        ret = []
        for pipeline, pipeline_config in tenant.layout.pipelines.items():
            triggers = []
            for trigger in pipeline_config.triggers:
                if isinstance(trigger.connection, BaseConnection):
                    name = trigger.connection.connection_name
                else:
                    # Trigger not based on a connection doesn't use this attr
                    name = trigger.name
                triggers.append({
                    "name": name,
                    "driver": trigger.driver.name,
                })
            ret.append({"name": pipeline, "triggers": triggers})

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def labels(self, tenant_name):
        tenant = self._getTenantOrRaise(tenant_name)
        allowed_labels = tenant.allowed_labels or []
        disallowed_labels = tenant.disallowed_labels or []
        labels = set()
        for launcher in self.zk_nodepool.getRegisteredLaunchers():
            labels.update(filter_allowed_disallowed(
                launcher.supported_labels,
                allowed_labels, disallowed_labels))
        ret = [{'name': label} for label in sorted(labels)]
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def nodes(self, tenant):
        ret = []
        for node_id in self.zk_nodepool.getNodes(cached=True):
            node = self.zk_nodepool.getNode(node_id)
            # This returns all nodes; some of which may not be
            # intended for use by Zuul, so be extra careful checking
            # user_data.
            if not (node.user_data and
                    isinstance(node.user_data, dict) and
                    node.user_data.get('zuul_system') ==
                    self.system.system_id and
                    node.user_data.get('tenant_name') == tenant):
                continue
            node_data = {}
            for key in ("id", "type", "connection_type", "external_id",
                        "provider", "state", "state_time", "comment"):
                node_data[key] = getattr(node, key, None)
            ret.append(node_data)
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    @cherrypy.expose
    @cherrypy.tools.save_params()
    def key(self, tenant_name, project_name):
        tenant = self._getTenantOrRaise(tenant_name)
        project = self._getProjectOrRaise(tenant, project_name)

        key = encryption.serialize_rsa_public_key(project.public_secrets_key)
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'text/plain'
        return key

    @cherrypy.expose
    @cherrypy.tools.save_params()
    def project_ssh_key(self, tenant_name, project_name):
        tenant = self._getTenantOrRaise(tenant_name)
        project = self._getProjectOrRaise(tenant, project_name)

        key = f"{project.public_ssh_key}\n"
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'text/plain'
        return key

    def buildToDict(self, build, buildset=None):
        start_time = build.start_time
        if build.start_time:
            start_time = start_time.strftime(
                '%Y-%m-%dT%H:%M:%S')
        end_time = build.end_time
        if build.end_time:
            end_time = end_time.strftime(
                '%Y-%m-%dT%H:%M:%S')
        if build.start_time and build.end_time:
            duration = (build.end_time -
                        build.start_time).total_seconds()
        else:
            duration = None

        ret = {
            '_id': build.id,
            'uuid': build.uuid,
            'job_name': build.job_name,
            'result': build.result,
            'held': build.held,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'voting': build.voting,
            'log_url': build.log_url,
            'nodeset': build.nodeset,
            'error_detail': build.error_detail,
            'final': build.final,
            'artifacts': [],
            'provides': [],
        }

        if buildset:
            ret.update({
                'project': buildset.project,
                'branch': buildset.branch,
                'pipeline': buildset.pipeline,
                'change': buildset.change,
                'patchset': buildset.patchset,
                'ref': buildset.ref,
                'newrev': buildset.newrev,
                'ref_url': buildset.ref_url,
                'event_id': buildset.event_id,
                'buildset': {
                    'uuid': buildset.uuid,
                },
            })

        for artifact in build.artifacts:
            art = {
                'name': artifact.name,
                'url': artifact.url,
            }
            if artifact.meta:
                art['metadata'] = json.loads(artifact.meta)
            ret['artifacts'].append(art)
        for provides in build.provides:
            ret['provides'].append({
                'name': provides.name,
            })
        return ret

    def _get_connection(self):
        return self.zuulweb.connections.connections['database']

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def builds(self, tenant, project=None, pipeline=None, change=None,
               branch=None, patchset=None, ref=None, newrev=None,
               uuid=None, job_name=None, voting=None, nodeset=None,
               result=None, final=None, held=None, complete=None,
               limit=50, skip=0, idx_min=None, idx_max=None):
        connection = self._get_connection()

        if tenant not in self.zuulweb.abide.tenants.keys():
            raise cherrypy.HTTPError(404, 'Tenant %s does not exist.' % tenant)

        # If final is None, we return all builds, both final and non-final
        if final is not None:
            final = final.lower() == "true"

        if complete is not None:
            complete = complete.lower() == 'true'

        try:
            _idx_max = idx_max is not None and int(idx_max) or idx_max
            _idx_min = idx_min is not None and int(idx_min) or idx_min
        except ValueError:
            raise cherrypy.HTTPError(400, 'idx_min, idx_max must be integers')

        builds = connection.getBuilds(
            tenant=tenant, project=project, pipeline=pipeline, change=change,
            branch=branch, patchset=patchset, ref=ref, newrev=newrev,
            uuid=uuid, job_name=job_name, voting=voting, nodeset=nodeset,
            result=result, final=final, held=held, complete=complete,
            limit=limit, offset=skip, idx_min=_idx_min, idx_max=_idx_max)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return [self.buildToDict(b, b.buildset) for b in builds]

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def build(self, tenant, uuid):
        connection = self._get_connection()

        data = connection.getBuilds(tenant=tenant, uuid=uuid, limit=1)
        if not data:
            raise cherrypy.HTTPError(404, "Build not found")
        data = self.buildToDict(data[0], data[0].buildset)
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return data

    def buildsetToDict(self, buildset, builds=[]):
        ret = {
            '_id': buildset.id,
            'uuid': buildset.uuid,
            'result': buildset.result,
            'message': buildset.message,
            'project': buildset.project,
            'branch': buildset.branch,
            'pipeline': buildset.pipeline,
            'change': buildset.change,
            'patchset': buildset.patchset,
            'ref': buildset.ref,
            'newrev': buildset.newrev,
            'ref_url': buildset.ref_url,
            'event_id': buildset.event_id,
        }
        if builds:
            ret['builds'] = []
        for build in builds:
            ret['builds'].append(self.buildToDict(build))
        return ret

    @cherrypy.expose
    @cherrypy.tools.save_params()
    def badge(self, tenant, project=None, pipeline=None, branch=None):
        connection = self._get_connection()

        buildsets = connection.getBuildsets(
            tenant=tenant, project=project, pipeline=pipeline,
            branch=branch, complete=True, limit=1)
        if not buildsets:
            raise cherrypy.HTTPError(404, 'No buildset found')

        if buildsets[0].result == 'SUCCESS':
            file = 'passing.svg'
        else:
            file = 'failing.svg'
        path = os.path.join(self.zuulweb.static_path, file)

        # Ensure the badge are not cached
        cherrypy.response.headers['Cache-Control'] = "no-cache"

        return cherrypy.lib.static.serve_file(
            path=path, content_type="image/svg+xml")

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def buildsets(self, tenant, project=None, pipeline=None, change=None,
                  branch=None, patchset=None, ref=None, newrev=None,
                  uuid=None, result=None, complete=None, limit=50, skip=0,
                  idx_min=None, idx_max=None):
        connection = self._get_connection()

        if complete:
            complete = complete.lower() == 'true'

        try:
            _idx_max = idx_max is not None and int(idx_max) or idx_max
            _idx_min = idx_min is not None and int(idx_min) or idx_min
        except ValueError:
            raise cherrypy.HTTPError(400, 'idx_min, idx_max must be integers')

        buildsets = connection.getBuildsets(
            tenant=tenant, project=project, pipeline=pipeline, change=change,
            branch=branch, patchset=patchset, ref=ref, newrev=newrev,
            uuid=uuid, result=result, complete=complete,
            limit=limit, offset=skip, idx_min=_idx_min, idx_max=_idx_max)

        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return [self.buildsetToDict(b) for b in buildsets]

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def buildset(self, tenant, uuid):
        connection = self._get_connection()

        data = connection.getBuildset(tenant, uuid)
        if not data:
            raise cherrypy.HTTPError(404, "Buildset not found")
        data = self.buildsetToDict(data, data.builds)
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return data

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.websocket(handler_cls=LogStreamHandler)
    def console_stream(self, tenant):
        cherrypy.request.ws_handler.zuulweb = self.zuulweb

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def project_freeze_jobs(self, tenant_name, pipeline_name, project_name,
                            branch_name):
        item = self._freeze_jobs(
            tenant_name, pipeline_name, project_name, branch_name)

        output = []
        for job in item.current_build_set.job_graph.getJobs():
            output.append({
                'name': job.name,
                'dependencies':
                    list(map(lambda x: x.toDict(), job.dependencies)),
            })

        ret = output
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    @cherrypy.expose
    @cherrypy.tools.save_params()
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def project_freeze_job(self, tenant_name, pipeline_name, project_name,
                           branch_name, job_name):
        # TODO(jhesketh): Allow a canonical change/item to be passed in which
        # would return the job with any in-change modifications.
        item = self._freeze_jobs(
            tenant_name, pipeline_name, project_name, branch_name)
        job = item.current_build_set.jobs.get(job_name)
        if not job:
            raise cherrypy.HTTPError(404)

        uuid = "0" * 32
        params = zuul.executor.common.construct_build_params(
            uuid, self.zuulweb.connections, job, item, item.pipeline)
        params['zuul'].update(zuul.executor.common.zuul_params_from_job(job))
        del params['job_ref']
        params['job'] = job.name
        params['zuul']['buildset'] = None
        params['timeout'] = job.timeout
        params['post_timeout'] = job.post_timeout
        params['override_branch'] = job.override_branch
        params['override_checkout'] = job.override_checkout
        params['ansible_version'] = job.ansible_version
        params['workspace_scheme'] = job.workspace_scheme
        if job.name != 'noop':
            params['playbooks'] = job.run
            params['pre_playbooks'] = job.pre_run
            params['post_playbooks'] = job.post_run
            params['cleanup_playbooks'] = job.cleanup_run
        params["nodeset"] = job.nodeset.toDict()
        params['vars'] = job.combined_variables
        params['extra_vars'] = job.extra_variables
        params['host_vars'] = job.host_variables
        params['group_vars'] = job.group_variables
        params['secret_vars'] = job.secret_parent_data

        ret = params
        resp = cherrypy.response
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return ret

    def _freeze_jobs(self, tenant_name, pipeline_name, project_name,
                     branch_name):

        tenant = self._getTenantOrRaise(tenant_name)
        project = self._getProjectOrRaise(tenant, project_name)
        pipeline = tenant.layout.pipelines.get(pipeline_name)
        if not pipeline:
            raise cherrypy.HTTPError(404, 'Unknown pipeline')

        change = Branch(project)
        change.branch = branch_name or "master"
        context = LocalZKContext(self.log)
        queue = ChangeQueue.new(context, pipeline=pipeline)
        item = QueueItem.new(context, queue=queue, change=change,
                             pipeline=queue.pipeline)
        item.freezeJobGraph(tenant.layout, context,
                            skip_file_matcher=True,
                            redact_secrets_and_keys=True)

        return item


class StaticHandler(object):
    def __init__(self, root):
        self.root = root

    def default(self, path, **kwargs):
        # Try to handle static file first
        handled = cherrypy.lib.static.staticdir(
            section="",
            dir=self.root,
            index='index.html')
        if not path or not handled:
            # When not found, serve the index.html
            return cherrypy.lib.static.serve_file(
                path=os.path.join(self.root, "index.html"),
                content_type="text/html")
        else:
            return cherrypy.lib.static.serve_file(
                path=os.path.join(self.root, path))


class StreamManager(object):
    log = logging.getLogger("zuul.web")

    def __init__(self):
        self.streamers = {}
        self.poll = select.poll()
        self.bitmask = (select.POLLIN | select.POLLERR |
                        select.POLLHUP | select.POLLNVAL)
        self.wake_read, self.wake_write = os.pipe()
        self.poll.register(self.wake_read, self.bitmask)

    def start(self):
        self._stopped = False
        self.thread = threading.Thread(
            target=self.run,
            name='StreamManager')
        self.thread.start()

    def stop(self):
        self._stopped = True
        os.write(self.wake_write, b'\n')
        self.thread.join()

    def run(self):
        while True:
            for fd, event in self.poll.poll():
                if self._stopped:
                    return
                if fd == self.wake_read:
                    os.read(self.wake_read, 1024)
                    continue
                streamer = self.streamers.get(fd)
                if streamer:
                    try:
                        streamer.handle(event)
                    except Exception:
                        self.log.exception("Error in streamer:")
                        streamer.errorClose()
                        self.unregisterStreamer(streamer)
                else:
                    try:
                        self.poll.unregister(fd)
                    except KeyError:
                        pass

    def registerStreamer(self, streamer):
        self.log.debug("Registering streamer %s", streamer)
        self.streamers[streamer.finger_socket.fileno()] = streamer
        self.poll.register(streamer.finger_socket.fileno(), self.bitmask)
        os.write(self.wake_write, b'\n')

    def unregisterStreamer(self, streamer):
        self.log.debug("Unregistering streamer %s", streamer)
        try:
            self.poll.unregister(streamer.finger_socket)
        except KeyError:
            pass
        try:
            del self.streamers[streamer.finger_socket.fileno()]
        except KeyError:
            pass


class ZuulWeb(object):
    log = logging.getLogger("zuul.web.ZuulWeb")

    def __init__(self,
                 config,
                 connections,
                 authenticators: AuthenticatorRegistry,
                 info: WebInfo = None):
        self.start_time = time.time()
        self.config = config
        self.listen_address = get_default(self.config,
                                          'web', 'listen_address',
                                          '127.0.0.1')
        self.listen_port = get_default(self.config, 'web', 'port', 9000)
        self.server = None
        self.static_cache_expiry = get_default(self.config, 'web',
                                               'static_cache_expiry',
                                               3600)
        self.info = info
        self.static_path = os.path.abspath(
            get_default(self.config, 'web', 'static_path', STATIC_DIR)
        )
        self.hostname = socket.getfqdn()

        self.zk_client = ZooKeeperClient.fromConfig(self.config)
        self.zk_client.connect()

        self.executor_api = ExecutorApi(self.zk_client, use_cache=False)

        self.component_info = WebComponent(
            self.zk_client, self.hostname, version=get_version_string())
        self.component_info.register()

        self.monitoring_server = MonitoringServer(self.config, 'web',
                                                  self.component_info)
        self.monitoring_server.start()

        self.component_registry = ComponentRegistry(self.zk_client)

        self.system_config_cache_wake_event = threading.Event()
        self.system_config_cache = SystemConfigCache(
            self.zk_client,
            self.system_config_cache_wake_event.set)

        self.keystore = KeyStorage(
            self.zk_client, password=self._get_key_store_password())
        self.globals = SystemAttributes.fromConfig(self.config)
        self.ansible_manager = AnsibleManager(
            default_version=self.globals.default_ansible_version)
        self.abide = Abide()
        self.unparsed_abide = UnparsedAbideConfig()
        self.tenant_layout_state = LayoutStateStore(
            self.zk_client, self.system_config_cache_wake_event.set)
        self.local_layout_state = {}

        self.connections = connections
        self.authenticators = authenticators
        self.stream_manager = StreamManager()
        self.zone = get_default(self.config, 'web', 'zone')

        self.management_events = TenantManagementEventQueue.createRegistry(
            self.zk_client)
        self.pipeline_management_events = (
            PipelineManagementEventQueue.createRegistry(self.zk_client)
        )
        self.trigger_events = TenantTriggerEventQueue.createRegistry(
            self.zk_client, self.connections
        )
        self.pipeline_trigger_events = (
            PipelineTriggerEventQueue.createRegistry(
                self.zk_client, self.connections
            )
        )
        self.pipeline_result_events = PipelineResultEventQueue.createRegistry(
            self.zk_client
        )

        self.zk_context = ZKContext(self.zk_client, None, None, self.log)

        command_socket = get_default(
            self.config, 'web', 'command_socket',
            '/var/lib/zuul/web.socket'
        )

        self.command_socket = commandsocket.CommandSocket(command_socket)

        self.repl = None

        self.command_map = {
            'stop': self.stop,
            'repl': self.start_repl,
            'norepl': self.stop_repl,
        }

        self.finger_tls_key = get_default(
            self.config, 'fingergw', 'tls_key')
        self.finger_tls_cert = get_default(
            self.config, 'fingergw', 'tls_cert')
        self.finger_tls_ca = get_default(
            self.config, 'fingergw', 'tls_ca')
        self.finger_tls_verify_hostnames = get_default(
            self.config, 'fingergw', 'tls_verify_hostnames', default=True)

        route_map = cherrypy.dispatch.RoutesDispatcher()
        api = ZuulWebAPI(self)
        route_map.connect('api', '/api',
                          controller=api, action='index')
        route_map.connect('api', '/api/info',
                          controller=api, action='info')
        route_map.connect('api', '/api/connections',
                          controller=api, action='connections')
        route_map.connect('api', '/api/components',
                          controller=api, action='components')
        route_map.connect('api', '/api/tenants',
                          controller=api, action='tenants')
        route_map.connect('api', '/api/tenant/{tenant}/info',
                          controller=api, action='tenant_info')
        route_map.connect('api', '/api/tenant/{tenant}/status',
                          controller=api, action='status')
        route_map.connect('api', '/api/tenant/{tenant}/status/change/{change}',
                          controller=api, action='status_change')
        route_map.connect('api', '/api/tenant/{tenant_name}/jobs',
                          controller=api, action='jobs')
        route_map.connect('api', '/api/tenant/{tenant_name}/job/{job_name}',
                          controller=api, action='job')
        # if no auth configured, deactivate admin routes
        if self.authenticators.authenticators:
            # route order is important, put project actions before the more
            # generic tenant/{tenant}/project/{project} route
            route_map.connect('api', '/api/user/authorizations',
                              controller=api, action='authorizations')
            route_map.connect('api', '/api/tenant/{tenant}/authorizations',
                              controller=api,
                              action='tenant_authorizations')
            route_map.connect('api', '/api/tenant/{tenant_name}/promote',
                              controller=api, action='promote')
            route_map.connect(
                'api',
                '/api/tenant/{tenant_name}/project/{project_name:.*}/autohold',
                controller=api, action='autohold')
            route_map.connect(
                'api',
                '/api/tenant/{tenant_name}/project/{project_name:.*}/enqueue',
                controller=api, action='enqueue')
            route_map.connect(
                'api',
                '/api/tenant/{tenant_name}/project/{project_name:.*}/dequeue',
                controller=api, action='dequeue')
        route_map.connect('api', '/api/tenant/{tenant_name}/autohold/'
                          '{request_id}',
                          controller=api, action='autohold_by_request_id')
        route_map.connect('api', '/api/tenant/{tenant_name}/autohold',
                          controller=api, action='autohold_list')
        route_map.connect('api', '/api/tenant/{tenant_name}/projects',
                          controller=api, action='projects')
        route_map.connect('api', '/api/tenant/{tenant_name}/project/'
                          '{project_name:.*}',
                          controller=api, action='project')
        route_map.connect(
            'api',
            '/api/tenant/{tenant_name}/pipeline/{pipeline_name}'
            '/project/{project_name:.*}/branch/{branch_name:.*}/freeze-jobs',
            controller=api, action='project_freeze_jobs'
        )
        route_map.connect(
            'api',
            '/api/tenant/{tenant_name}/pipeline/{pipeline_name}'
            '/project/{project_name:.*}/branch/{branch_name:.*}'
            '/freeze-job/{job_name}',
            controller=api, action='project_freeze_job'
        )
        route_map.connect('api', '/api/tenant/{tenant_name}/pipelines',
                          controller=api, action='pipelines')
        route_map.connect('api', '/api/tenant/{tenant_name}/labels',
                          controller=api, action='labels')
        route_map.connect('api', '/api/tenant/{tenant}/nodes',
                          controller=api, action='nodes')
        route_map.connect('api', '/api/tenant/{tenant_name}/key/'
                          '{project_name:.*}.pub',
                          controller=api, action='key')
        route_map.connect('api', '/api/tenant/{tenant_name}/'
                          'project-ssh-key/{project_name:.*}.pub',
                          controller=api, action='project_ssh_key')
        route_map.connect('api', '/api/tenant/{tenant}/console-stream',
                          controller=api, action='console_stream')
        route_map.connect('api', '/api/tenant/{tenant}/builds',
                          controller=api, action='builds')
        route_map.connect('api', '/api/tenant/{tenant}/badge',
                          controller=api, action='badge')
        route_map.connect('api', '/api/tenant/{tenant}/build/{uuid}',
                          controller=api, action='build')
        route_map.connect('api', '/api/tenant/{tenant}/buildsets',
                          controller=api, action='buildsets')
        route_map.connect('api', '/api/tenant/{tenant}/buildset/{uuid}',
                          controller=api, action='buildset')
        route_map.connect('api', '/api/tenant/{tenant_name}/config-errors',
                          controller=api, action='config_errors')

        for connection in connections.connections.values():
            controller = connection.getWebController(self)
            if controller:
                cherrypy.tree.mount(
                    controller,
                    '/api/connection/%s' % connection.connection_name)

        # Add fallthrough routes at the end for the static html/js files
        route_map.connect(
            'root_static', '/{path:.*}',
            controller=StaticHandler(self.static_path),
            action='default')

        conf = {
            '/': {
                'request.dispatch': route_map
            }
        }
        cherrypy.config.update({
            'global': {
                'environment': 'production',
                'server.socket_host': self.listen_address,
                'server.socket_port': int(self.listen_port),
            },
        })

        cherrypy.tree.mount(api, '/', config=conf)

    @property
    def port(self):
        return cherrypy.server.bound_addr[1]

    def start(self):
        self.log.debug("ZuulWeb starting")

        self.component_info.state = self.component_info.INITIALIZING
        # Wait for system config and layouts to be loaded
        while not self.system_config_cache.is_valid:
            self.system_config_cache_wake_event.wait()

        # Initialize the system config
        self.updateSystemConfig()

        # Wait until all layouts/tenants are loaded
        while True:
            self.system_config_cache_wake_event.clear()
            self.updateLayout()
            if (set(self.unparsed_abide.tenants.keys())
                != set(self.abide.tenants.keys())):
                self.system_config_cache_wake_event.wait()
            else:
                break

        self.stream_manager.start()
        self.wsplugin = WebSocketPlugin(cherrypy.engine)
        self.wsplugin.subscribe()
        cherrypy.engine.start()

        self.log.debug("Starting command processor")
        self._command_running = True
        self.command_socket.start()
        self.command_thread = threading.Thread(target=self.runCommand,
                                               name='command')
        self.command_thread.daemon = True
        self.command_thread.start()
        self.component_info.state = self.component_info.RUNNING

        self.system_config_thread = threading.Thread(
            target=self.updateConfig,
            name='system_config')
        self._system_config_running = True
        self.system_config_thread.daemon = True
        self.system_config_thread.start()

    def stop(self):
        self.log.debug("ZuulWeb stopping")
        self.component_info.state = self.component_info.STOPPED
        cherrypy.engine.exit()
        # Not strictly necessary, but without this, if the server is
        # started again (e.g., in the unit tests) it will reuse the
        # same host/port settings.
        cherrypy.server.httpserver = None
        self.wsplugin.unsubscribe()
        self.stream_manager.stop()
        self._system_config_running = False
        self.system_config_cache_wake_event.set()
        self.system_config_thread.join()
        self.zk_client.disconnect()
        self.stop_repl()
        self._command_running = False
        self.command_socket.stop()
        self.monitoring_server.stop()

    def join(self):
        self.command_thread.join()
        self.monitoring_server.join()

    def runCommand(self):
        while self._command_running:
            try:
                command = self.command_socket.get().decode('utf8')
                if command != '_stop':
                    self.command_map[command]()
            except Exception:
                self.log.exception("Exception while processing command")

    def start_repl(self):
        if self.repl:
            return
        self.repl = zuul.lib.repl.REPLServer(self)
        self.repl.start()

    def stop_repl(self):
        if not self.repl:
            return
        self.repl.stop()
        self.repl = None

    def _get_key_store_password(self):
        try:
            return self.config["keystore"]["password"]
        except KeyError:
            raise RuntimeError("No key store password configured!")

    def updateConfig(self):
        while self._system_config_running:
            try:
                self.system_config_cache_wake_event.wait()
                self.system_config_cache_wake_event.clear()
                if not self._system_config_running:
                    return
                self.updateSystemConfig()
                self.updateLayout()
            except Exception:
                self.log.exception("Exception while updating system config")

    def updateSystemConfig(self):
        self.log.debug("Updating system config")
        self.unparsed_abide, self.globals = self.system_config_cache.get()
        self.ansible_manager = AnsibleManager(
            default_version=self.globals.default_ansible_version)

        loader = ConfigLoader(
            self.connections, self.zk_client, self.globals,
            keystorage=self.keystore)

        loader.loadTPCs(self.abide, self.unparsed_abide)
        loader.loadAdminRules(self.abide, self.unparsed_abide)

    def updateLayout(self):
        self.log.debug("Updating layout state")
        loader = ConfigLoader(
            self.connections, self.zk_client, self.globals,
            keystorage=self.keystore)

        min_ltimes = defaultdict(lambda: defaultdict(lambda: -1))
        for tenant_name in self.unparsed_abide.tenants:
            # Reload the tenant if the layout changed.
            if (self.local_layout_state.get(tenant_name)
                    == self.tenant_layout_state.get(tenant_name)):
                continue
            self.log.debug("Reloading tenant %s", tenant_name)
            with tenant_read_lock(self.zk_client, tenant_name):
                layout_state = self.tenant_layout_state.get(tenant_name)
                layout_uuid = layout_state and layout_state.uuid

                if layout_state:
                    branch_cache_min_ltimes = (
                        layout_state.branch_cache_min_ltimes)
                else:
                    # Consider all project branch caches valid if
                    # we don't have a layout state.
                    branch_cache_min_ltimes = defaultdict(lambda: -1)

                # The tenant will be stored in self.abide.tenants after
                # it was loaded.
                tenant = loader.loadTenant(
                    self.abide, tenant_name, self.ansible_manager,
                    self.unparsed_abide, min_ltimes=min_ltimes,
                    layout_uuid=layout_uuid,
                    branch_cache_min_ltimes=branch_cache_min_ltimes)
                if tenant is not None:
                    self.local_layout_state[tenant_name] = layout_state
                else:
                    with suppress(KeyError):
                        del self.local_layout_state[tenant_name]
        self.log.debug("Done updating layout state")
