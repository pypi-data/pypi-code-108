# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Converts snapshot information into data structures for reporting.

"""

from __future__ import unicode_literals
from collections import deque
import os

from appdynamics import config
from appdynamics.lang import bytes, filter, str, values
from appdynamics.lib import make_name_value_pairs

from appdynamics.agent.core import correlation, pb
from appdynamics.agent.models import callgraph, errors, exitcalls


REQUIRED = pb.SnapshotInfo.REQUIRED
ERROR = pb.SnapshotInfo.ERROR
SLOW = pb.SnapshotInfo.SLOW
CONTINUING = pb.SnapshotInfo.CONTINUING


def is_partial_snapshot(trigger, bt_started_on_time):
    if trigger == CONTINUING or (trigger == REQUIRED and bt_started_on_time):
        # REQUIRED triggers come from bt info response data. If the bt did not
        # 'start on time' (i.e. it timed out waiting for the response but
        # continued anyway), it's likely we missed frames in the snapshot.
        # Mark these types of REQUIRED snapshots as 'partial'.
        return False
    else:
        return True


def make_snapshot_info_dict(bt):
    return {
        'trigger': bt.snapshot_trigger,
        'snapshot': make_snapshot_dict(bt),
    }


def make_snapshot_dict(bt):
    call_graph = make_call_graph_dict(bt.sample_data, bt.timer.duration_ms, bt._exit_calls,
                                      include_internal_frames=config.INCLUDE_AGENT_FRAMES)
    snapshot = {
        'snapshotGUID': bt.snapshot_guid,
        'timestamp': bt.snapshot_start_time_ms,
        'callGraph': call_graph,
        'errorInfo': errors.make_error_info_dict(bt.errors),
        'exceptionInfo': errors.make_exception_info_dict(bt.exceptions),
        'processID': os.getpid(),
        'exitCalls': filter_redundant_exit_calls(values(bt._exit_calls))
    }

    if bt.request:
        snapshot['httpRequestData'] = make_snapshot_http_request_data(bt.request, bt.status_code, bt.http_data_gatherer)

    # Attach MIDC data to the snapshot
    snapshot['methodInvocationData'] = [{'name': name, 'value': value} for (name, value, enabled_for_snapshots, _)
                                        in bt.midc_data if enabled_for_snapshots]

    if bt.snapshot_user_data:
        snapshot['methodInvocationData'] += make_name_value_pairs(bt.snapshot_user_data)

    if bt.cross_app_correlation:
        snapshot['upstreamCrossAppSnapshotGUID'] = bt.cross_app_correlation[correlation.GUID_KEY]
        snapshot['upstreamCrossAppExitCallSequence'] = bt.cross_app_correlation[correlation.EXIT_GUID_KEY]

    if bt.eum_guid:
        snapshot['eumGUID'] = bt.eum_guid

    return snapshot


def make_snapshot_http_request_data(request, status_code, gatherer):
    http_data = {
        'url': request.path.encode('utf-8'),
        'requestMethod': request.method,
        'responseCode': status_code,
    }

    if gatherer:
        cookies = {}
        for key, enabled_for_apm, _ in gatherer.cookies:
            if key in request.cookies and enabled_for_apm:
                cookies[key] = request.cookies[key]
        http_data['cookies'] = make_name_value_pairs(cookies)

        headers = {}
        for key, enabled_for_apm, _ in gatherer.headers:
            if key in request.headers and enabled_for_apm:
                headers[key] = request.headers[key]
        http_data['headers'] = make_name_value_pairs(headers)

        http_params = {}
        for (key, name), enabled_for_apm, _ in gatherer.request_params:
            if key in request.args and enabled_for_apm:
                http_params[name] = request.args[key]
        http_data['httpParams'] = make_name_value_pairs(http_params)

    return http_data


def make_call_graph_dict(sample_data, total_time_taken_ms, exit_calls, include_internal_frames=False):
    """Make a dict representing a pb.CallGraph.

    This takes a SampleData, converts it into a call graph, then flattens that
    call graph using a level order traversal for packing into the protobuf.
    The call graph will have a synthetic root '{request}' that contains all of
    the time taken by the BT.

    If there are no samples in sample_data, then we return immediately.

    Parameters
    ----------
    sample_data : appdynamics.agent.models.callgraph.SampleData
        The sample data collected by the profiler
    total_time_taken_ms : int
        The precise time taken in the business transaction.

    Other Parameters
    ----------------
    include_internal_frames : bool, optional

    Returns
    -------
    dict
        A dict suitable for populating a ``pb.CallGraph``.

    """
    if not sample_data:
        return {}

    root = callgraph.make_call_graph(sample_data, total_time_taken_ms, include_internal_frames=include_internal_frames)

    # We always create a synthetic root that receives special treatment.
    # Add any unassigned exit calls to the root node.

    elements = [{
        'type': pb.CallElement.PY,
        'method': b'{request}',
        'numChildren': len(root.children),
        'timeTaken': root.time_taken_ms,
        'exitCalls': [
            make_snapshot_exit_call_dict(exit_call)
            for exit_call in values(exit_calls)
            if not exit_call.was_assigned
        ]
    }]

    q = deque(root.children)

    # Flatten the call graph using a level-order traversal.
    while q:
        node = q.popleft()
        q.extend(node.children)
        element = make_call_element_dict(node)
        elements.append(element)

    return {'callElements': elements}


def make_call_element_dict(call):
    frame = call.frame

    return {
        'type': pb.CallElement.PY,
        'numChildren': len(call.children),
        'timeTaken': call.time_taken_ms,
        'klass': bytes(frame.class_name),
        'method': bytes(frame.name),
        'fileName': bytes(frame.filename),
        'lineNumber': frame.lineno,
        'exitCalls': filter_redundant_exit_calls(call.exit_calls),
    }


def make_snapshot_exit_call_dict(exit_call):
    exit_call.was_added = True
    properties = make_name_value_pairs(exit_call.backend.identifying_properties, exit_call.optional_properties)

    result = {
        'backendIdentifier': exitcalls.make_backend_identifier_dict(exit_call.backend),
        'timeTaken': exit_call.time_taken_ms,
        'sequenceInfo': exit_call.sequence_info,
        'count': exit_call.num_calls,
        'properties': properties,
    }

    if exit_call.error_details:
        result['errorDetails'] = bytes(exit_call.error_details)

    if exit_call.operation:
        result['detailString'] = bytes(exit_call.operation)

    return result


def is_db_backend(exit_call):
    """
    method to figure out if exit call belongs to

    Parameters
    ----------
    exit_call: exit call

    Returns
    -------

    """
    return exit_call.backend.exit_point_type == exitcalls.EXIT_DB


def is_custom_backend(exit_call):
    return exit_call.backend.exit_point_type == exitcalls.EXIT_CUSTOM


def make_snapshot_db_calls_dicts(bt):
    return [
        {
            'backendIdentifier': exitcalls.make_backend_identifier_dict(db.backend),
            'sqlString': bytes(db.operation),
            'count': db.num_calls,
            'totalTimeTakenMS': db.time_taken_ms,
            'minTimeMS': db.min_time_taken_ms,
            'maxTimeMS': db.max_time_taken_ms,
            'sequenceInfo': str(db.id),
            'boundParameters': make_bound_parameters_dict(db.params),
        }
        for db in filter(is_db_backend, values(bt._exit_calls))
    ]


def filter_redundant_exit_calls(exit_calls_list):
    """
    Refer CORE-64926

    Following method ensures that the exit call information is NOT added
    redundantly to the BT details.

    It adds the exit call information to the dict iff.

    1. If the exit call is already not added to the call graph.
    (or)
    2. The exit call is of type EXIT_DB; since proxy expects snpshot info to
       have DB exit calls and treats them specially
       while parsing [look agent_proxy.java]

    Please also refer CORE-64926 for example payloads.

    """

    return [make_snapshot_exit_call_dict(exit_call) for exit_call in exit_calls_list
            if not exit_call.was_added or is_db_backend(exit_call) or is_custom_backend(exit_call)]


def make_bound_parameters_dict(params):
    return None  # TODO: Implement parameter tracking
