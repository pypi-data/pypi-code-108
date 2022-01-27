# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""The agent itself.

"""

from __future__ import unicode_literals
import os
import shutil
import time
import re
import atexit
import signal
import sys
import threading

import appdynamics_bindeps.zmq.auth as zauth

from appdynamics import config, get_agent_version, get_proxy_version
from appdynamics.lang import str
from appdynamics.lib import get_ident, set_ident, get_ipc_addr, get_tcp_addr, mkdir

from appdynamics.agent.core import correlation, pb
from appdynamics.agent.core.timer import Timer
from appdynamics.agent.core.logs import setup_logger
from appdynamics.agent.core.registries import (BackendRegistry, NamingSchemeRegistry, ErrorConfigRegistry,
                                               DataGathererRegistry, TransactionRegistry, AnalyticsConfigRegistry)

from appdynamics.agent.models.transactions import make_transaction_factory

from appdynamics.agent.services.config import ConfigService
from appdynamics.agent.services.proxycontrol import ProxyControlService
from appdynamics.agent.services.snapshot import SnapshotService
from appdynamics.agent.services.transaction import TransactionService
from appdynamics.agent.services.stall_monitor import StallMonitorService
from appdynamics.agent.services.diagnostics import DiagnosticsService
from appdynamics.agent.services.analytics import AnalyticsService
from appdynamics.agent.services.http_transport import HttpTransportService


class Agent(object):
    """The entry point for the Python agent.

    """

    SIGNALS_TO_HANDLE = [signal.SIGTERM, signal.SIGINT, signal.SIGTSTP, signal.SIGHUP]

    def __init__(self):
        super(Agent, self).__init__()

        self.logger = setup_logger('appdynamics.agent')
        self.lock = threading.Lock()

        self.app_id = None
        self.tier_id = None
        self.node_id = None
        self.account_guid = None
        self.controller_guid = None

        self._tx_factory = None

        # Services
        self.proxy_control_svc = None
        self.config_svc = None
        self.tx_svc = None
        self.snapshot_svc = None
        self.analytics_svc = None
        self.http_transport_svc = None

        # Registries
        self.naming_registry = None
        self.bt_registry = None
        self.backend_registry = None
        self.error_config_registry = None
        self.data_gatherer_registry = None
        self.analytics_config_registry = None

        self.active_bts = set()
        self.current_bts = {}
        self.eum_config = None

        self.started = False
        self.last_forced_snapshot = 0

        # handle signal which cannot be handled by atexit
        self.handle_signals()

        if config.CURVE_ENABLED:
            self.setup_curve()

    def start(self):
        if self.proxy_control_svc is None:
            self.logger.info('Starting AppDynamics Python agent v%s (proxy v%s) ...' %
                             (get_agent_version(), get_proxy_version()))
            self.proxy_control_svc = ProxyControlService(self.on_start_node_response)
            self.proxy_control_svc.start()
            self.started = True

            # register shutdown hook when agent is started
            atexit.register(self.shutdown)

    def handle_signals(self):
        def signal_handler(signal, frame):
            """
            This function calls sys.exit(0) so that atexit handler can be executed.
            """
            sys.exit(0)

        for signal_num in self.SIGNALS_TO_HANDLE:
            signal.signal(signal_num, signal_handler)

    def setup_curve(self):
        self.logger.debug('CurveZMQ is enabled')
        mkdir(config.CURVE_SECRET_KEY_DIR)
        mkdir(config.CURVE_PUBLIC_KEY_DIR)

        secret_file_exists = os.path.exists(config.CURVE_AGENT_SECRET_KEY_FILE)
        public_file_exists = os.path.exists(config.CURVE_AGENT_PUBLIC_KEY_FILE)
        if secret_file_exists and public_file_exists:
            self.logger.debug('Certificates already exist. Skipping certificate creation ...')
            return

        if secret_file_exists != public_file_exists:
            self.logger.warning('Only one certificate exists. Please make sure that both public and private \
                certificates exist...')
            self.logger.warning('Disabling curve...')
            config.CURVE_ENABLED = False
            return

        public_file, secret_file = zauth.create_certificates(config.CURVE_SECRET_KEY_DIR, config.AGENT_NODE_NAME)
        shutil.move(os.path.join(config.CURVE_PUBLIC_KEY_DIR, public_file), config.CURVE_AGENT_PUBLIC_KEY_FILE)
        shutil.move(os.path.join(config.CURVE_SECRET_KEY_DIR, secret_file), config.CURVE_AGENT_SECRET_KEY_FILE)
        self.logger.debug('Certificates successfully created at {} & {}'.format(
            config.CURVE_AGENT_PUBLIC_KEY_FILE, config.CURVE_AGENT_SECRET_KEY_FILE))

    def shutdown(self):
        """Logs shutdown message, clear any active bts and stops the agent.

        This function is registered using atexit module when agent starts. It gets executed
        upon normal python interpreter termination.

        """
        try:
            self.logger.info('Shutting down AppDynamics Python agent...')
            self.active_bts.clear()
            self.stop()
        except Exception as ex:
            self.logger.info('Exception occurred during shutting down agent %s' % ex)

    def stop(self):
        """Stop the agent from doing anything else.

        Ideally this will stop any interceptors from doing anything, it will
        disconnect all ties to the proxy etc etc.

        """
        self.started = False

    def wait_for_start(self, timeout_ms=None):
        """Wait for the agent to start and get configured.

        Other Parameters
        ----------------
        timeout_ms : int, optional
            The maximum time to wait for the agent to start and be configured
            before returning.

        Returns
        -------
        bool
            Returns ``True`` if the agent is enabled after waiting, else
            ``False``.

        """
        if timeout_ms is not None:
            with self.timer() as timer:
                if self.proxy_control_svc is not None:
                    self.proxy_control_svc.wait_for_start(timeout_ms=timeout_ms)

                if self.config_svc is not None:
                    timeout_ms = max(0, timeout_ms - timer.duration_ms)
                    self.config_svc.wait_for_config(timeout_ms=timeout_ms)

                if self.tx_svc is not None:
                    timeout_ms = max(0, timeout_ms - timer.duration_ms)
                    self.tx_svc.wait_for_start(timeout_ms=timeout_ms)
        else:
            self.proxy_control_svc.wait_for_start()
            self.config_svc.wait_for_config()
            self.tx_svc.wait_for_start()

        return self.enabled

    def wait_for_end(self, timeout_ms=None):
        """Wait for the agent to finish reporting any pending BTs.

        """
        self.tx_svc.wait_for_end(timeout_ms=timeout_ms)

    @property
    def enabled(self):
        """Return true if the agent has started and is enabled.

        """
        return (
            self.started and
            self.config_svc and self.config_svc.enabled and
            self.tx_svc)

    def timer(self, *args, **kwargs):
        """Create a timer.

        Returns
        -------
        timer : appdynamics.agent.core.timer.Timer
            The newly created timer. Note the returned timer has not been
            started; you must start it with its
            :py:meth:`appdynamics.agent.core.timer.Timer.start()` method.

        """
        t = Timer(self.time, *args, **kwargs)
        return t

    @staticmethod
    def time():
        """Get the current time in ms from the agent's timer.

        Returns
        -------
        int
            The current time in milliseconds.

        """
        return int(1000 * time.time())

    def on_start_node_response(self, response):
        # Start node response is being handled inside lock to prevent race conditions where two threads simultaneously
        # entered the code block withing the self.config_svc check and resulted in proxy_control_service being shut down
        # because of 'threads can only be started once' runtime error
        with self.lock:
            if self.config_svc is None:
                self.logger.info('Starting AppDynamics agent services...')

                initial_config = response.configResponse if response.HasField('configResponse') else None
                self.bt_registry = TransactionRegistry()
                self.backend_registry = BackendRegistry()
                self.naming_registry = NamingSchemeRegistry()
                self.error_config_registry = ErrorConfigRegistry()
                self.data_gatherer_registry = DataGathererRegistry()
                self.analytics_config_registry = AnalyticsConfigRegistry()

                self._tx_factory = make_transaction_factory(self, self.timer, self.error_config_registry.is_bt_error)

                self.config_svc = ConfigService(self.update_config,
                                                self.proxy_control_svc.reconnect,
                                                initial_config)

                self.snapshot_svc = SnapshotService(self)
                self.stall_monitor_svc = StallMonitorService(self.active_bts, self.end_transaction, self.time)
                self.http_transport_svc = HttpTransportService()
                self.analytics_svc = AnalyticsService(self, self.http_transport_svc)

                self.tx_svc = TransactionService(self.snapshot_svc,
                                                 self.stall_monitor_svc,
                                                 self.analytics_svc)

                self.diagnostic_svc = DiagnosticsService(self)

                self.logger.info('Starting AppDynamics BT, config and snapshot threads...')
                self.stall_monitor_svc.start()
                self.tx_svc.start()
                self.config_svc.start()
                self.snapshot_svc.start()
                self.diagnostic_svc.start()
                self.http_transport_svc.start()
                self.analytics_svc.start()

            if config.TCP_COMM_PORT:
                response_port_array = re.findall("[0-9]+", response.dataSocketDirPath)
                # In a TCP setup, the agent expects 2 ports in the response from proxy. If 2 ports are not received,
                # something is wrong(Could happen if proxy is configured in IPC but the agent is configured with TCP).
                # To avoid exception in ZMQ while connecting to invalid ports, switch to default ports.
                if len(response_port_array) != 2:
                    self.logger.info('Communication ports were not received properly from the proxy. Make \
                        sure the proxy is running in TCP Mode.')
                    self.logger.info('Defaulting to {} and {} for config and reporting port respectively...'.format(
                        config.TCP_REQUEST_PORT, config.TCP_REPORTING_PORT))
                    response_port_array = [config.TCP_REQUEST_PORT, config.TCP_REPORTING_PORT]

                config_addr = info_addr = get_tcp_addr(config.TCP_COMM_HOST, response_port_array[0])
                reporting_addr = get_tcp_addr(config.TCP_COMM_HOST, response_port_array[1])
            else:
                config_addr = get_ipc_addr(response.dataSocketDirPath, config.PROXY_CONFIG_SOCKET_NAME)
                info_addr = get_ipc_addr(response.dataSocketDirPath, config.PROXY_INFO_SOCKET_NAME)
                reporting_addr = get_ipc_addr(response.dataSocketDirPath, config.PROXY_REPORTING_SOCKET_NAME)

            self.logger.info('Connecting AppDynamics services to %s...', "{} over {} and {} ports".format(
                config.TCP_COMM_HOST, response_port_array[0], response_port_array[1]) if config.TCP_COMM_PORT
                else response.dataSocketDirPath
            )
            self.config_svc.connect(config_addr)
            self.tx_svc.connect(info_addr, reporting_addr)

    def update_config(self, config):
        if self.app_id is None and config.HasField('agentIdentity'):
            identity = config.agentIdentity
            self.app_id = identity.appID
            self.tier_id = identity.tierID
            self.node_id = identity.nodeID
            self.account_guid = identity.accountGUID
            self.controller_guid = identity.controllerGUID

        self.bt_registry.update_config(config.txInfo)
        self.backend_registry.update_config(config.bckInfo, config.bckConfig)
        self.naming_registry.update_config(config.txConfig)
        self.error_config_registry.update_config(config.errorConfig)
        self.data_gatherer_registry.update_data_gatherers(config.dataGatherers)
        self.data_gatherer_registry.update_data_gatherer_bt_entries(config.dataGathererBTConfig.btConfig)
        self.analytics_config_registry.update_config(config.analyticsConfig)

        self.eum_config = config.eumConfig

    def start_transaction(self, entry_type, base_name=None, request=None, correlation_header=None):
        """Start a new business transaction.

        Parameters
        ----------
        entry_type : int
            An ENTRY_xxx from :py:mod:`appdynamics.agent.models.transactions`.
        base_name : str, optional
            The base name to give the transaction. If `None`, then the name is
            computed from `request`.
        request : object, optional
            The active, incoming HTTP request that caused this BT, if any.
            This must have fields `method`, `url`, `path`, `args` (the query
            parameters), `cookies`, and `headers`.
        correlation_header : str, optional
            The incoming correlation header as a string, if any. If this is
            `None` or not passed, and `request` is passed, then the header
            is extracted from the `request` object. (You can pass in an empty
            string if you want to explicitly disable correlation regardless
            of what is in the `request` header.)

        Returns
        -------
        bt : Transaction or None
            If a transaction was started, it is returned. A transaction will
            not be started and `None` will be returned if (1) the agent is
            disabled; (2) if the transaction that would've been started is
            excluded from reporting by the agent's configuration; (3) if
            there is an incoming correlation header that disables transaction
            detection.

        """
        bt = self.get_current_bt()
        if bt:
            # Already a current bt for this context;  do not start another.
            return bt

        if not self.started:
            self.start()
            return None

        if not self.enabled:
            return None

        entry_type_name = pb.EntryPointType.Name(entry_type)

        if request and correlation_header is None:
            correlation_header = request.headers.get(correlation.HEADER_NAME)

        bt_name = None

        try:
            bt_name, match = self._name_bt(base_name, entry_type, request)
            correlation_header = self.parse_correlation_header(correlation_header)
            # set_ident needs to be called before _start_bt and _continue_bt (PYTHON-772)
            set_ident()

            if correlation_header is None or correlation_header.is_cross_app:
                bt = self._start_bt(bt_name, entry_type, match)
                bt.cross_app_correlation = correlation_header

                self.logger.debug(
                    "BT:%s (name=%r) entry=%s start=new registered_id=%r %s",
                    bt.request_id, bt.name, entry_type_name, bt.registered_id,
                    '[x-app]' if correlation_header else '')
            else:  # In app correlation
                assert not correlation_header.is_cross_app
                bt = self._continue_bt(correlation_header)
                bt.is_continue = True
                self.logger.debug(
                    'BT:%s (name=%r) entry=%s/%s start=continuing header: %s',
                    bt.request_id, bt.name, entry_type_name, bt.entry_type, bt.incoming_correlation)
        except IgnoreTransaction as exc:
            self.logger.debug('BT:IGNORED (name=%r) entry=%s reason=%s', bt_name, entry_type_name, str(exc))
            return None

        bt.request = request
        self.active_bts.add(bt)
        self.set_current_bt(bt)
        self.tx_svc.start_transaction(bt)
        return bt

    def _name_bt(self, base_name, entry_type, request):
        if request:
            match = self.naming_registry.match(entry_type, request, base_name)

            if match is None:
                raise IgnoreTransaction('no name for BT -- discovery disabled or BT matched exclude rule')

            bt_name = match.name
        else:
            bt_name = base_name
            match = None

        # This makes using external APIs safe as the discovered names can be really long.
        bt_name = bt_name[:config.BT_NAME_MAX_SIZE]

        if self.bt_registry.is_excluded(entry_type, bt_name):
            raise IgnoreTransaction('excluded by rule')

        return bt_name, match

    def _continue_bt(self, correlation_header):
        if self.check_for_reresolution(correlation_header):
            raise IgnoreTransaction('reresolution, tier: %d, header: %s' % (self.tier_id, correlation_header))

        return self._tx_factory(incoming_correlation=correlation_header)

    def _start_bt(self, bt_name, entry_type, match):
        registered_id = self.bt_registry.get_registered_id(entry_type, bt_name)
        bt = self._tx_factory(entry_type=entry_type, name=bt_name, registered_id=registered_id)

        if match:
            bt.custom_match_id = match.custom_match_id
            bt.naming_scheme_type = match.naming_scheme

        return bt

    @property
    def can_cross_app_correlate(self):
        return self.controller_guid and self.account_guid

    def parse_correlation_header(self, correlation_header):
        if not correlation_header:
            return None

        hdr = correlation.parse_header(correlation_header, self.app_id)

        if hdr[correlation.DISABLE_TX_DETECTION_KEY]:
            raise IgnoreTransaction('notxdetect, header: %s' % correlation_header)

        incoming_controller_guid = hdr[correlation.CONTROLLER_GUID_KEY]
        incoming_account_guid = hdr[correlation.ACCOUNT_GUID_KEY]
        incoming_app_id = hdr[correlation.APP_ID_KEY]

        if incoming_controller_guid and incoming_controller_guid != self.controller_guid:
            self.logger.debug(
                'Do not correlate: controller GUID in header is %r but ours is %r',
                incoming_controller_guid, self.controller_guid)
            return None

        if incoming_account_guid and incoming_account_guid != self.account_guid:
            self.logger.debug(
                'Do not correlate: account GUID in header is %r but ours is %r',
                incoming_account_guid, self.account_guid)
            return None

        if hdr.is_cross_app and not self.can_cross_app_correlate:
            self.logger.debug(
                'Do not correlate: cross-app is disabled; app ID in header is %r but ours is %r',
                incoming_app_id, self.app_id)
            return None

        return hdr

    def check_for_reresolution(self, correlation_header):
        """Check if re-resolution is required.

        Parameters
        ----------
        correlation_header : correlation.CorrelationHeader

        Returns
        -------
        bool
            ``True`` if we re-resolved the backend, else ``False``.

        """
        try:
            backend_id = int(correlation_header[correlation.UNRESOLVED_EXIT_ID_KEY])
            doNotResolve = correlation_header[correlation.DO_NOT_RESOLVE_KEY]

            # Do not reresolve in case service proxy is detected,
            # Here it is tested based on doNotResolve flag
            if backend_id > 0 and not doNotResolve:
                last_tier_id = self.backend_registry.get_component_for_registered_backend(backend_id)

                if last_tier_id is not None and last_tier_id != self.tier_id:
                    self.tx_svc.reresolve(backend_id)
                    return True

                to_app_id = correlation_header.cross_app_to_component

                if to_app_id and to_app_id != self.app_id:
                    self.tx_svc.reresolve(backend_id)
                    return True
        except:
            pass

        return False

    def get_current_bt(self):
        """Get the currently active BT for the calling context.

        The calling context is the active greenlet or thread, depending on
        whether greenlets are in use or not. If the agent is disabled, or if
        there is no active transaction for the calling context, None is
        returned.

        Returns
        -------
        bt : appdynamics.agent.core.bt.Transaction or None
            the active business transaction (if any)

        """
        if not self.enabled:
            return None
        return self.current_bts.get(get_ident(), None)

    def set_current_bt(self, bt):
        if bt:
            self.current_bts[get_ident()] = bt

    def unset_current_bt(self):
        self.current_bts.pop(get_ident(), None)

    @staticmethod
    def start_exit_call(bt, start_frame_info, backend, **kwargs):
        """Start an exit call, taking a sample if the BT is snapshotting.

        """
        exit_call = bt.start_exit_call(start_frame_info, backend, **kwargs)
        if exit_call and bt.snapshotting:
            bt.sample_data.take_outer_frames(exit_call.timer.start_time_ms, bt.active_exit_calls)
        return exit_call

    @staticmethod
    def end_exit_call(bt, exit_call, end_frame_info, exc_info=None):
        """End an exit call.

        """
        bt.end_exit_call(exit_call, end_frame_info, exc_info=exc_info)

    def end_transaction(self, bt):
        """End the active transaction on this thread.

        Parameters
        ----------
        exc_info : (exc_type, exc_value, exc_tb) or None
            If an uncaught exception caused the transaction to end, then this
            contains the exception info (as returned by `sys.exc_info()`). If
            no exception occurred, then `None`.

        bt : appdynamics.agent.models.transactions.Transaction, optional
            A specific BT to end.

        """
        self.unset_current_bt()
        self.active_bts.discard(bt)
        if self.enabled and bt:
            self.stall_monitor_svc.end_bt_monitor(bt)
            self.tx_svc.end_transaction(bt)

    def end_active_bts(self):
        """End all the active BTs.

        """
        for bt in self.active_bts:
            self.end_transaction(bt)

    def report_custom_metric(self, metric, value):
        if not self.started:
            raise AgentNotStartedException

        if not self.enabled:
            raise AgentNotReadyException

        self.tx_svc.report_custom_metric(metric, value)


class AgentNotStartedException(Exception):
    pass


class AgentNotReadyException(Exception):
    pass


class IgnoreTransaction(Exception):
    pass
