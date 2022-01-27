# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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
import datetime
import itertools
import uuid
import time
import json
import pytz
import hashlib
import os
import contextlib
import typing
from . import version
from . import settings
from . import package
from . interfaces import user_statistics as interface
from .. utils import log
from .. platform import plugins


stats_logger = log.get_logger('app.stats')


timer_poll_interval = 60  # seconds
standard_sender_interval = timer_poll_interval * 5
post_timeout = 3  # seconds


def basic_hash(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True).encode('ascii')).hexdigest()


def api_url():
    application_url = version.application_url().rstrip('/')
    # Default URL for local server.
    # application_url = 'http://127.0.0.1:8000'
    return f'{application_url}/api'


def api_headers():
    return {'Accept': 'application/json;version=1.0'}


# TODO(erik): we need tests for collection of user statistics.
# Possibly using a local webserver to test HTTP posts.

@contextlib.contextmanager
def active(app):
    from Qt import QtCore
    timer = QtCore.QTimer(parent=app)
    statistics = _available_user_statistics()
    with contextlib.ExitStack() as stack:
        try:
            for s in statistics:
                instance = s.user_statistics()
                stack.enter_context(instance)
                _activated.append(instance)

            timer.setInterval(1000 * timer_poll_interval)
            timer.timeout.connect(user_running_sympathy)
            timer.start()
            yield statistics
            timer.timeout.disconnect(user_running_sympathy)
            timer.stop()
        finally:
            _activated.clear()


class DictEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return pytz.utc.localize(obj).isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()

        return super().default(obj)


class SyncPoster:

    def __init__(self, url, headers, ignore_ssl_errors=None):
        self._url = url
        self._headers = headers
        self._ignore_ssl_errors = ignore_ssl_errors
        self._stopped = False

    def _send(self, item):
        from .. platform.hooks import request_http

        if not self._stopped:
            data = json.dumps(item, cls=DictEncoder, sort_keys=True)
            data = data.encode('ascii')
            kwargs = {
                'headers': self._headers,
                'data': data,
                'verify': True
            }
            if self._ignore_ssl_errors:
                kwargs['verify'] = False

            try:
                res = request_http.value.post(self._url, timeout=post_timeout, **kwargs)
                res.raise_for_status()
                stats_logger.info('Successfully sent user statistics to %s.',
                                  self._url)
            except Exception as e:
                stats_logger.debug(
                    'Failed sending user statistics to %s.: %s', self._url, e)

    def send(self, data):
        try:
            self._send(data)
        except Exception as e:
            stats_logger.error(
                'Failed sending user statistics to %s.: %s', self._url, e)

    def send_and_exit(self, data):
        self.send(data)
        self._stopped = True


def _is_platform_node(node):
    res = False
    if node and node.library_node:
        res = node.library_node.is_platform_node
    return res


class StandardUserStatistics(interface.UserStatistics):
    send_interval = standard_sender_interval

    def __init__(self):
        self._counter = itertools.count()
        self._workflow_enumerator = {}
        self._session = str(uuid.uuid4())
        self._started = False
        self._user = None
        self._messages = {}
        self._send_timer = time.time()

        self._poster = SyncPoster(
            f'{api_url()}/stat/',
            headers=api_headers())

    def _send_or_wait(self):
        if time.time() - self._send_timer > self.send_interval:
            self._send()
            self._send_timer = 0

    def _send(self):
        messages = self._pop_messages()
        # Prevent excessive data collection when running tests.
        test_run = os.environ.get('SY_TEST_RUN')

        if not test_run and messages and settings.instance()['send_stats']:
            self._poster.send(messages)

    def _send_and_exit(self):
        messages = self._pop_messages()
        # Prevent excessive data collection when running tests.
        test_run = os.environ.get('SY_TEST_RUN')

        if not test_run and messages and settings.instance()['send_stats']:
            self._poster.send_and_exit(messages)

    def _get_user(self):
        if self._user is None:
            self._user = settings.instance()['user_id']
        return self._user

    def _add_message(self, category, message):
        if self._started:
            self._messages.setdefault(category, []).append(message)

    def _aggregate(self, items, group_keys, reduce_fn=None):
        agg = []
        if items:
            for group_values, group_items in itertools.groupby(
                    items,
                    lambda x: tuple(x[gk] for gk in group_keys)):
                list_group_items = list(group_items)

                item = dict(zip(group_keys, group_values))
                item['n'] = len(list_group_items)

                if reduce_fn:
                    reduce_fn(item, list_group_items)
                agg.append(item)
        return agg

    def _aggregate_count_n_empty(self, items):
        agg = []
        if items:
            agg.append({'n': len(items)})
        return agg

    def _pop_messages(self):
        def duration_sum_reduce(item, items):
            e = datetime.timedelta(0)
            item['duration'] = sum(
                [v.get('duration') or e for v in items if v], e)

        res = self._messages
        if self._messages:
            res['session'] = [{'session_id': self._session}]
            # Aggregate configurations and executions.
            for category in ['configured_node', 'executed_node']:
                res[category] = self._aggregate(
                    res.get(category), ['node_id', 'status'],
                    reduce_fn=duration_sum_reduce)

            for category in ['created_connection']:
                res[category] = self._aggregate(
                    res.get(category), [
                        'dst_node_id', 'dst_port_id', 'dst_port_type',
                        'src_node_id', 'src_port_id', 'src_port_type'])

            for category in ['created_node', 'aborted_node']:
                res[category] = self._aggregate(
                    res.get(category), ['node_id'])

            for category in ['created_subflow']:
                res[category] = self._aggregate_count_n_empty(
                    res.get(category))

            # Filter emptys.
            res = {k: v for k, v in res.items() if v}

            self._messages = {}
        else:
            res = {}
        return res

    def user_created_connection(self, src, dst):
        try:
            src.node.node_identifier
            dst.node.node_identifier
        except AttributeError:
            # Port is likely flowio. Ignoring collection.
            # TODO(erik): traverse structure and find source, destination
            # ports.
            return

        if not (_is_platform_node(src.node) and _is_platform_node(dst.node)):
            return

        src_node_id = src.node.node_identifier
        dst_node_id = dst.node.node_identifier

        src_port_id = src.port_definition.name or src.port_definition.index
        dst_port_id = dst.port_definition.name or dst.port_definition.index

        src_port_type = str(src.datatype)
        dst_port_type = str(dst.datatype)

        self._add_message(
            'created_connection', {
                'src_node_id': src_node_id,
                'dst_node_id': dst_node_id,
                'src_port_id': src_port_id,
                'dst_port_id': dst_port_id,
                'src_port_type': src_port_type,
                'dst_port_type': dst_port_type,
            })

    def user_created_node(self, node):
        if not _is_platform_node(node):
            return

        self._add_message(
            'created_node', {
                'node_id': node.node_identifier,
            })

    def _result_duration(self, result):
        # Guard against errors when times for result are missing.
        done = result.times.get('done', datetime.datetime.now())
        try:
            duration = done - result.times['started']
        except Exception:
            duration = None
        return duration

    def user_configured_node(self, node, result):
        if not _is_platform_node(node):
            return

        self._add_message(
            'configured_node', {
                'node_id': node.node_identifier,
                'status': result.status,
                'duration': self._result_duration(result)
            })

    def user_created_subflow(self, subflow):
        self._add_message(
            'created_subflow', {
            })

        if subflow.library_node:
            self.user_created_node(subflow)

    def user_executed_node(self, node, result):
        if not _is_platform_node(node):
            return

        self._add_message(
            'executed_node', {
                'node_id': node.node_identifier,
                'status': result.status,
                'duration': self._result_duration(result),
            })

    def user_aborted_node(self, node):
        if not _is_platform_node(node):
            return

        self._add_message(
            'aborted_node', {
                'node_id': node.node_identifier,
            })

    def user_started_sympathy(self, interface):
        self._started = True
        system_dict = package.System.to_dict_from_settings()
        python_dict = package.Python.to_dict_from_settings()

        self._add_message(
            'started_sympathy', {
                'at_time': datetime.datetime.now(),
                'interface': interface,
                'user': self._get_user(),
                'system': system_dict,
                'system_hash': basic_hash(system_dict),
                'python': python_dict,
                'python_hash': basic_hash(python_dict),
            })

    def user_stopped_sympathy(self):
        self._add_message(
            'stopped_sympathy', {
                'at_time': datetime.datetime.now(),
            })
        self._started = False
        self._send_and_exit()

    def user_running_sympathy(self):
        # Discard previous unsent messages.
        self._messages['running_sympathy'] = []
        self._add_message(
            'running_sympathy', {
                'at_time': datetime.datetime.now(),
            })
        self._send_or_wait()

    def user_crashed_sympathy(self):
        self._add_message(
            'crashed_sympathy', {
                'at_time': datetime.datetime.now(),
            })

    def user_opened_workflow(self, flow):
        self._add_message(
            'opened_workflow', {
                'at_time': datetime.datetime.now(),
            })

    def user_closed_workflow(self, flow):
        self._add_message(
            'closed_workflow', {
                'at_time': datetime.datetime.now(),
            })

    def user_saved_workflow(self, flow):
        self._add_message(
            'saved_workflow', {
                'at_time': datetime.datetime.now(),
            })


def user_created_connection(src, dst):
    for collector in _activated:
        collector.user_created_connection(src, dst)


def user_created_node(node):
    for collector in _activated:
        collector.user_created_node(node)


def user_configured_node(node, result):
    for collector in _activated:
        collector.user_configured_node(node, result)


def user_created_subflow(subflow):
    for collector in _activated:
        collector.user_created_subflow(subflow)


def user_executed_node(node, result):
    for collector in _activated:
        collector.user_executed_node(node, result)


def user_aborted_node(node):
    for collector in _activated:
        collector.user_aborted_node(node)


def user_started_sympathy(interface):
    for collector in _activated:
        collector.user_started_sympathy(interface)


def user_stopped_sympathy():
    for collector in _activated:
        collector.user_stopped_sympathy()


def user_running_sympathy():
    for collector in _activated:
        collector.user_running_sympathy()


def user_crashed_sympathy():
    for collector in _activated:
        collector.user_crashed_sympathy()


def user_opened_workflow(flow):
    for collector in _activated:
        collector.user_opened_workflow(flow)


def user_closed_workflow(flow):
    for collector in _activated:
        collector.user_closed_workflow(flow)


def user_saved_workflow(flow):
    for collector in _activated:
        collector.user_saved_workflow(flow)


def user_unloaded_library(library_id, path, name, is_global):
    for collector in _activated:
        collector.user_unloaded_library(library_id, path, name, is_global)


def user_loaded_library(library_id, path, name, is_global):
    for collector in _activated:
        collector.user_loaded_library(library_id, path, name, is_global)


# Package interface:

_instance = None


def user_statistics() -> interface.UserStatistics:
    global _instance
    if _instance is None:
        _instance = StandardUserStatistics()
    return _instance


_activated = []
_statistics = plugins.Plugin(interface.identifier, typing.Any)


def _available_user_statistics():
    return _statistics.plugins().values()
