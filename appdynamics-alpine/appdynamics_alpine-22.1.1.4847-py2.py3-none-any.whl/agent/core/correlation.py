# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Utilities for correlation between apps and tiers.

"""

from __future__ import unicode_literals

from appdynamics.lang import long, map, str, zip, native_str
from appdynamics.lib import make_uuid
from appdynamics.agent.core import pb
from appdynamics import config
import appdynamics.agent

HEADER_NAME = native_str('singularityheader')
ACCOUNT_GUID_KEY = 'acctguid'
CONTROLLER_GUID_KEY = 'ctrlguid'
DISABLE_TX_DETECTION_KEY = 'notxdetect'
APP_ID_KEY = 'appId'
BT_ID_KEY = 'btid'
BT_NAME_KEY = 'btname'
BT_TYPE_KEY = 'bttype'
TIER_ID_KEY = 'btcomp'
BT_MATCH_TYPE_KEY = 'mctype'
BT_MATCH_VALUE_KEY = 'mcvalue'
SNAPSHOT_ENABLED_KEY = 'snapenable'
GUID_KEY = 'guid'
UNRESOLVED_EXIT_ID_KEY = 'unresolvedexitid'
EXIT_GUID_KEY = 'exitguid'
FROM_COMPONENT_ID_KEY = 'cidfrom'
TO_COMPONENT_ID_KEY = 'cidto'
EXIT_TYPE_ORDER_KEY = 'etypeorder'
EXIT_CALL_SUBTYPE_KEY = 'esubtype'
DEBUG_KEY = 'debug'
TIMESTAMP_KEY = 'ts'
DO_NOT_RESOLVE_KEY = 'donotresolve'


class CorrelationHeader(object):
    """A convenient representation of the correlation header.

    """
    BOOLEAN_KEYS = set([DISABLE_TX_DETECTION_KEY, DEBUG_KEY, SNAPSHOT_ENABLED_KEY, DO_NOT_RESOLVE_KEY])
    COMMA_SEPARATED_KEYS = set([FROM_COMPONENT_ID_KEY, TO_COMPONENT_ID_KEY, EXIT_TYPE_ORDER_KEY, EXIT_CALL_SUBTYPE_KEY])
    COMMA_SEPERATOR = ','
    UNRESOLVED_PREFIX = '{[UNRESOLVED]['
    UNRESOLVED_PREFIX_LEN = len(UNRESOLVED_PREFIX)
    UNRESOLVED_SUFFIX = ']}'
    UNRESOLVED_SUFFIX_LEN = len(UNRESOLVED_SUFFIX)
    CROSS_APP_CIDTO_PREFIX = 'A'
    CROSS_APP_CIDTO_PREFIX_LEN = len(CROSS_APP_CIDTO_PREFIX)

    def __init__(self, local_app_id):
        super(CorrelationHeader, self).__init__()
        self.local_app_id = local_app_id
        self.ordering = []
        self.values = {}

    def __getitem__(self, key):
        value = self.values.get(key, '')
        if key in self.BOOLEAN_KEYS:
            try:
                value = value.lower() == 'true'
            except AttributeError:
                value = bool(value)
        return value

    def __setitem__(self, key, value):
        if key not in self.values:
            self.ordering.append(key)
        self.values[key] = str(value) if value else ''

    def append(self, key, value):
        if key in self.COMMA_SEPARATED_KEYS:
            self[key] = self[key] + (self.COMMA_SEPERATOR if self[key] else '') + str(value)
        else:
            raise AttributeError("Key can't be appended to.")

    def get(self, key, default=None):
        return self.values.get(key, default)

    @property
    def is_cross_app(self):
        return str(self.local_app_id) != self[APP_ID_KEY]

    @property
    def cross_app_correlation_backend(self):
        if not self.is_cross_app:
            return None

        backend_id = None

        try:
            last_component = self[TO_COMPONENT_ID_KEY].split(self.COMMA_SEPERATOR)[-1]
            backend_id = _get_unresolved_backend_id(last_component)

            if not backend_id:
                app_id = _get_app_id(last_component)

                if app_id != self.local_app_id:
                    # X-app reresolution when upstream tier sends a header that assumes we are:
                    # 1. A different application (cidto=...,A123), or
                    # 2. A tier inside the same application (cidto=...,42).
                    backend_id = long(self[UNRESOLVED_EXIT_ID_KEY])
            raise Exception('backend_id = %r' % backend_id)
        except:
            pass

        return backend_id

    @property
    def cross_app_to_component(self):
        last_component = self[TO_COMPONENT_ID_KEY].split(self.COMMA_SEPERATOR)[-1]
        app_id = _get_app_id(last_component)
        return app_id

    def add_unregistered_bt(self, bt, tier_id):
        if bt.is_auto_discovered:
            match_type = 'auto'
            match_value = bt.naming_scheme_type
        else:
            match_type = 'custom'
            match_value = ''

        self[BT_NAME_KEY] = bt.name

        if bt.incoming_correlation and not bt.incoming_correlation.is_cross_app:
            self[BT_TYPE_KEY] = bt.entry_type
        else:
            self[BT_TYPE_KEY] = pb.EntryPointType.Name(bt.entry_type)

        self[TIER_ID_KEY] = tier_id
        self[BT_MATCH_TYPE_KEY] = match_type
        self[BT_MATCH_VALUE_KEY] = match_value

    def add_component_link(self, exit_type, exit_subtype, tier_id):
        last_component = self[TO_COMPONENT_ID_KEY].split(self.COMMA_SEPERATOR)[-1]
        self.append(FROM_COMPONENT_ID_KEY, last_component)
        self.append(TO_COMPONENT_ID_KEY, str(tier_id))
        self.append(EXIT_TYPE_ORDER_KEY, exit_type)
        self.append(EXIT_CALL_SUBTYPE_KEY, exit_subtype)

    def __str__(self):
        pairs = []
        for key in self.ordering:
            value = self[key]

            # Skip booleans that are set to False.
            if isinstance(value, bool):
                if value is False:
                    continue
                else:
                    value = 'true'
            pairs.append('%s=%s' % (key, value))

        header_value = '*'.join(pairs)
        return header_value

    @property
    def pb_dict(self):
        """Make a dict for populating a :py:class:`appdynamics.agent.pb.Correlation`.

        """
        from_components = self[FROM_COMPONENT_ID_KEY].split(self.COMMA_SEPERATOR)
        to_components = self[TO_COMPONENT_ID_KEY].split(self.COMMA_SEPERATOR)
        exit_point_types = self[EXIT_TYPE_ORDER_KEY].split(self.COMMA_SEPERATOR)

        if not self[EXIT_CALL_SUBTYPE_KEY]:
            exit_point_subtypes = exit_point_types
        else:
            exit_point_subtypes = self[EXIT_CALL_SUBTYPE_KEY].split(self.COMMA_SEPERATOR)

        links = [
            {
                'fromComponentID': from_component_id,
                'toComponentID': to_component_id,
                'exitPointType': exit_point_type,
                'exitPointSubtype': exit_point_subtype,
            }
            for from_component_id, to_component_id, exit_point_type, exit_point_subtype in
            zip(from_components, to_components, exit_point_types, exit_point_subtypes)
        ]
        """
        In case of service proxy detection, we are adding one more component link
        from service proxy to downstream server with specific exit point type and sub type
        """
        if self[DO_NOT_RESOLVE_KEY]:
            links.append(
                {
                    'fromComponentID': to_components[-1],
                    'toComponentID': str(appdynamics.agent.get_agent_instance().tier_id),
                    'exitPointType': exit_point_types[-1],
                    'exitPointSubtype': exit_point_subtypes[-1],
                }
            )

        unresolved_exit_id = None

        if to_components:
            last_component = to_components[-1]
            unresolved_exit_id = _get_unresolved_backend_id(last_component)

        if unresolved_exit_id is None:
            try:
                unresolved_exit_id = long(self[UNRESOLVED_EXIT_ID_KEY])
            except (TypeError, ValueError):
                return {}

        return {
            'incomingBackendId': unresolved_exit_id,
            'incomingSnapshotEnabled': self[SNAPSHOT_ENABLED_KEY],
            'doNotSelfResolve': self[DO_NOT_RESOLVE_KEY],
            'componentLinks': links,
            'exitCallSequence': self[EXIT_GUID_KEY],
        }


class NoTxDetectException(Exception):
    pass


def _get_unresolved_backend_id(component):
    try:
        if (component.startswith(CorrelationHeader.UNRESOLVED_PREFIX) and
                component.endswith(CorrelationHeader.UNRESOLVED_SUFFIX)):
            return long(component[CorrelationHeader.UNRESOLVED_PREFIX_LEN:-CorrelationHeader.UNRESOLVED_SUFFIX_LEN])
    except:
        pass

    return None


def _get_app_id(component):
    try:
        if component.startswith(CorrelationHeader.CROSS_APP_CIDTO_PREFIX):
            return long(component[CorrelationHeader.CROSS_APP_CIDTO_PREFIX_LEN:])
    except:
        pass

    return None


def make_header(agent, bt, exit_call, do_not_resolve=False):
    try:
        if not bt:
            raise NoTxDetectException('no active BT')

        if exit_call is None or exit_call.backend.registered_id is None:
            raise NoTxDetectException('backend not yet registered')

        if not exit_call.backend.correlation_enabled:
            return None

        incoming = bt.incoming_correlation or {}

        if incoming.get(DISABLE_TX_DETECTION_KEY):
            raise NoTxDetectException('incoming header has notxdetect=true')
    except NoTxDetectException as exc:
        if bt:
            agent.logger.debug('BT:%s (name=%r) created notxdetect header: %s', bt.request_id, bt.name, str(exc))
        elif not config.NO_TX_DETECT_HEADER_DISABLE:
            agent.logger.debug('Created notxdetect header: no active BT')
        else:
            agent.logger.debug('Disabled notxdetect header: no active BT')
        return make_notxdetect_header() if not config.NO_TX_DETECT_HEADER_DISABLE else None

    hdr = CorrelationHeader(agent.app_id)
    backend = exit_call.backend
    hdr[APP_ID_KEY] = agent.app_id
    hdr[ACCOUNT_GUID_KEY] = agent.account_guid
    hdr[CONTROLLER_GUID_KEY] = agent.controller_guid

    if bt.registered_id:
        hdr[BT_ID_KEY] = bt.registered_id
        hdr[BT_NAME_KEY] = bt.name
    else:
        hdr.add_unregistered_bt(bt, agent.tier_id)

    if bt.wait_for_bt_info_response() and (bt.bt_info_response.isSnapshotRequired or bt.continuing_snapshot_enabled):
        hdr[SNAPSHOT_ENABLED_KEY] = 'true'

    if backend.component_id:
        if backend.is_foreign_app:
            backend_tier_id = 'A%d' % backend.component_id
        else:
            backend_tier_id = backend.component_id
    else:
        backend_tier_id = '{[UNRESOLVED][%d]}' % backend.registered_id

    # If header is created before bt.snapshot_guid is set by snapshot service, we need to sync the snapshot_guid
    if bt.snapshot_guid is None:
        hdr[GUID_KEY] = make_uuid()
        bt.correlation_hdr_snapshot_guid = hdr[GUID_KEY]
    else:
        hdr[GUID_KEY] = bt.snapshot_guid

    hdr[UNRESOLVED_EXIT_ID_KEY] = backend.registered_id or 0
    hdr[EXIT_GUID_KEY] = exit_call.sequence_info

    if incoming:
        hdr[FROM_COMPONENT_ID_KEY] = incoming[FROM_COMPONENT_ID_KEY]
        hdr[TO_COMPONENT_ID_KEY] = incoming[TO_COMPONENT_ID_KEY]
        hdr[EXIT_TYPE_ORDER_KEY] = incoming[EXIT_TYPE_ORDER_KEY]
        hdr[EXIT_CALL_SUBTYPE_KEY] = incoming[EXIT_CALL_SUBTYPE_KEY]

        # Older agents do not have exit point subtypes.
        if not hdr[EXIT_CALL_SUBTYPE_KEY]:
            hdr[EXIT_CALL_SUBTYPE_KEY] = hdr[EXIT_TYPE_ORDER_KEY]

    hdr.append(FROM_COMPONENT_ID_KEY, agent.tier_id)
    hdr.append(TO_COMPONENT_ID_KEY, backend_tier_id)
    hdr.append(EXIT_TYPE_ORDER_KEY, backend.backend_type_name)
    hdr.append(EXIT_CALL_SUBTYPE_KEY, backend.exit_point_subtype)

    if do_not_resolve:
        hdr[DO_NOT_RESOLVE_KEY] = 'true'

    agent.logger.debug('BT:%s (name=%r) created correlation header: %s', bt.request_id, bt.name, hdr)
    return HEADER_NAME, native_str(hdr)


def parse_header(correlation_header_value, app_id):
    """Parse a correlation header from its string format.

    Parameters
    ----------
    correlation_header_value : str
        The value of the correlation header as a string.

    Returns
    -------
    CorrelationHeader
        The parsed correlation header.

    """
    hdr = CorrelationHeader(app_id)

    try:
        parts = correlation_header_value.split('*')

        for part in parts:
            try:
                # Get key and value, killing spaces around them
                key, value = map(lambda x: x.strip(), part.split('='))
            except:
                # No equals sign for some reason
                continue

            hdr[key] = value
    except:
        pass

    return hdr


def make_notxdetect_header():
    hdr = CorrelationHeader(None)
    hdr[DISABLE_TX_DETECTION_KEY] = 'true'
    return HEADER_NAME, str(hdr)
