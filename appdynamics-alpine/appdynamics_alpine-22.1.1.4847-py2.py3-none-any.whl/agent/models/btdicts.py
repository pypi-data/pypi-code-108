from appdynamics.agent.core import correlation, pb, snapshot
from appdynamics.agent.models import errors, exitcalls
from appdynamics.lang import bytes, values, long


def make_bt_info_request_dict(bt):
    if bt.incoming_correlation:
        correlation_header = bt.incoming_correlation.pb_dict
    else:
        correlation_header = None

    bt_info_request = {
        'requestID': bt.request_id,
        'messageID': 0,
        'btIdentifier': make_bt_identifier_dict(bt),
        'correlation': correlation_header,
    }

    if bt.cross_app_correlation:
        cross_app = make_cross_app_correlation_dict(bt.cross_app_correlation)
        bt_info_request.update(cross_app)

    return bt_info_request


def make_cross_app_correlation_dict(hdr):
    cross_app = {}

    backend_id = hdr.cross_app_correlation_backend

    if backend_id:
        cross_app['crossAppCorrelationBackendId'] = backend_id

    snap_enabled = bool(hdr[correlation.GUID_KEY] and hdr[correlation.SNAPSHOT_ENABLED_KEY])
    cross_app['incomingCrossAppSnapshotEnabled'] = snap_enabled

    EMPTY_STRING = ''

    cross_app_correlation = {
        'fromAccountGuid': hdr.get(correlation.ACCOUNT_GUID_KEY, EMPTY_STRING),
        'fromAppId': hdr.get(correlation.APP_ID_KEY, EMPTY_STRING),
        'btId': hdr.get(correlation.BT_ID_KEY, EMPTY_STRING),
        'fromComponentID': hdr.get(correlation.FROM_COMPONENT_ID_KEY, EMPTY_STRING),
        'exitPointType': hdr.get(correlation.EXIT_TYPE_ORDER_KEY, EMPTY_STRING),
        'backendId':
            long(hdr.get(correlation.UNRESOLVED_EXIT_ID_KEY)) if hdr.get(correlation.UNRESOLVED_EXIT_ID_KEY) else None
    }

    cross_app['crossAppCorrelation'] = cross_app_correlation

    return cross_app


def make_bt_identifier_dict(bt):
    if bt.registered_id:
        if bt.incoming_correlation:
            identifier_type = pb.BTIdentifier.REMOTE_REGISTERED
        else:
            identifier_type = pb.BTIdentifier.REGISTERED

        return {
            'type': identifier_type,
            'btID': bt.registered_id,
        }

    if bt.incoming_correlation:
        return make_remote_unregistered_bt_identifier_dict(bt)

    return {
        'type': pb.BTIdentifier.UNREGISTERED,
        'unregisteredBT': {
            'btInfo': {
                'entryPointType': bt.entry_type,
                'internalName': bytes(bt.name),
            },
            'customMatchPointDefinitionId': bt.custom_match_id,
        }
    }


def make_remote_unregistered_bt_identifier_dict(bt):
    if bt.naming_scheme_type:
        match_type = pb.UnRegisteredRemoteBT.DISCOVERED
        naming_scheme = bt.naming_scheme_type
    else:
        match_type = pb.UnRegisteredRemoteBT.CUSTOM
        naming_scheme = None

    return {
        'type': pb.BTIdentifier.REMOTE_UNREGISTERED,
        'unregisteredRemoteBT': {
            'entryPointType': bt.entry_type,
            'btName': bytes(bt.name),
            'matchCriteriaType': match_type,
            'namingSchemeType': naming_scheme,
        }
    }


def make_bt_details_dict(bt):
    if bt.bt_info_response:
        bt_info_state = pb.BTDetails.RESPONSE_RECEIVED
    else:
        bt_info_state = pb.BTDetails.MISSING_RESPONSE

    bt_details = {
        'btInfoRequest': bt.bt_info_request,
        'btMetrics': {
            'isError': bt.has_errors,
            'timeTaken': bt.timer.duration_ms,
            'timestamp': bt.timer.start_time_ms,
        },
        'btInfoState': bt_info_state,
    }

    if bt._exit_calls:
        bt_details['btMetrics']['backendMetrics'] = exitcalls.make_backend_metrics_dicts(values(bt._exit_calls))

    if bt.snapshot_guid:
        bt_details['snapshotInfo'] = snapshot.make_snapshot_info_dict(bt)

    bt_errors = bt.errors
    if bt_errors or bt.exceptions:
        bt_details['errors'] = errors.make_bt_errors_dict(bt_errors, bt.exceptions)

    if bt.is_stalled:
        bt_details['btMetrics']['isStalled'] = bt.is_stalled
        if bt.stall_message:
            bt_details['btMetrics']['stallMessage'] = bt.stall_message

    return bt_details


def make_custom_metrics_dict(metric, value):
    return {
        'name': metric.name,
        'value': value,
        'timeRollup': metric.time_rollup_type,
        'clusterRollup': metric.cluster_rollup_type,
        'holeHandling': metric.hole_handling_type,
    }
