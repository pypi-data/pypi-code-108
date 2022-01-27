""" Service for reporting data to Analytics agent.
This service sends data to the Analytics Agent every 30 seconds or 10k requests whichever happens earlier.

"""


from __future__ import unicode_literals

import threading
from datetime import datetime
from uuid import uuid4
from appdynamics.agent.core.logs import setup_logger
from appdynamics.lang import queue, values
from appdynamics import config, get_agent_version, get_python_version
from appdynamics.agent.models.exitcalls import make_backend_metrics_dicts
from appdynamics.agent.models.errors import make_bt_errors_dict
from appdynamics.agent.core import pb


class AnalyticsService(threading.Thread):

    NORMAL = 'NORMAL'
    SLOW = 'SLOW'
    VERY_SLOW = 'VERY_SLOW'
    ERROR = 'ERROR'
    STALL = 'STALL'

    # This needs to be updated if there is any change in the exitpoint types defined in protobuf files
    EXIT_POINT_TYPES = ['HTTP', 'DB', 'CACHE', 'RABBITMQ', 'WEB_SERVICE', 'CUSTOM', 'JMS']

    def __init__(self, agent, analytics_transport_svc):
        super(AnalyticsService, self).__init__()
        self.name = 'AnalyticsService'
        self.running = False
        self.agent = agent
        self.service_activated = threading.Event()
        self.report_event = threading.Event()
        self.logger = setup_logger('appdynamics.agent')
        self.daemon = True
        # queue of dictionary objects corresponding to each event to be sent to Analytics Agent
        self.event_queue = queue.Queue()
        self.analytics_transport_svc = analytics_transport_svc
        self.analytics_agent_url = self._get_analytics_agent_url()
        self.default_analytics_request_headers = self._create_default_headers_for_analytics_request()
        # PYTHON-930 Keeping thresholds in cache and updating it as btInfoResponse
        # might not contain thresholds for all BTs
        self.stall_threashold_cache = {}
        self.very_slow_threshold_cache = {}
        self.slow_threshold_cache = {}

    @property
    def enabled(self):
        return self.agent.analytics_config_registry.enabled

    def analytics_enabled_for_bt(self, bt_id):
        return self.enabled and bt_id in self.agent.analytics_config_registry.get_analytics_bt_ids()

    def _is_running(self):
        return self.running

    def _get_analytics_agent_url(self):
        scheme = 'https' if config.ANALYTICS_SSL_ENABLED else 'http'
        url = scheme + '://' + config.ANALYTICS_HOSTNAME + ':' + \
            str(config.ANALYTICS_PORT) + config.ANALYTICS_AGENT_API_PATH
        self.logger.debug('Analytics agent url is: {}'.format(url))
        return url

    def _create_default_headers_for_analytics_request(self):
        headers = {
            'User-Agent': 'Python-Agent/{} (python {})'.format(get_agent_version(), get_python_version()),
            'Content-Type': 'application/json',
            'X-Analytics-Agent-Access-Key': config.AGENT_ACCOUNT_ACCESS_KEY,
            'Connection': 'close',
        }
        return headers

    def run(self):
        try:
            self.running = True
            while self._is_running():
                self.service_activated.wait()
                self.report_event.wait(config.ANALYTICS_REPORT_DATA_TIMEOUT)
                self.logger.debug('Analytics service is reporting data...')
                self.report_data()
        except:
            self.logger.exception('Failure in Analytics Service thread to report data to Analytics agent')

    def _get_event_timestamp(self, bt):
        start_time = bt.timer.start_time_ms / 1000
        date_obj = datetime.fromtimestamp(start_time)
        date_string = date_obj.utcnow().isoformat() + 'Z'
        return date_string

    def _update_thresholds(self, bt):
        bt_info_response = bt.bt_info_response

        if bt_info_response:
            if bt_info_response.currentStallThreshold and bt_info_response.currentStallThreshold > 0:
                self.stall_threashold_cache[bt.registered_id] = bt_info_response.currentStallThreshold
            if bt_info_response.currentVerySlowThreshold and bt_info_response.currentVerySlowThreshold > 0:
                self.very_slow_threshold_cache[bt.registered_id] = bt_info_response.currentVerySlowThreshold
            if bt_info_response.currentSlowThreshold and bt_info_response.currentSlowThreshold > 0:
                self.slow_threshold_cache[bt.registered_id] = bt_info_response.currentSlowThreshold

    def _get_request_experience(self, bt):
        """Internal method to get request experience by comparing time taken by BT against various thresholds.
        """
        self._update_thresholds(bt)
        request_experience = self.NORMAL

        if bt.has_errors:
            request_experience = self.ERROR
        elif bt.registered_id in self.stall_threashold_cache and \
                bt.timer.duration_ms > self.stall_threashold_cache.get(bt.registered_id):
            request_experience = self.STALL
        elif bt.registered_id in self.very_slow_threshold_cache and \
                bt.timer.duration_ms > self.very_slow_threshold_cache.get(bt.registered_id):
            request_experience = self.VERY_SLOW
        elif bt.registered_id in self.slow_threshold_cache and \
                bt.timer.duration_ms > self.slow_threshold_cache.get(bt.registered_id):
            request_experience = self.SLOW
        return request_experience

    def _is_entry_point(self, bt):
        """Entry point is False if BT is continuing, otherwise True

        """
        return not bt.is_continue

    def _get_request_guid(self, bt):
        if bt.snapshot_guid is not None:
            return str(bt.snapshot_guid)
        if bt.correlation_hdr_snapshot_guid is not None:
            return str(bt.correlation_hdr_snapshot_guid)
        return str(uuid4())

    def record_transaction(self, current_bt):
        """This method creates an event to be send to analytics agent by extracting and processing
        required data from BT. Finally, storing the event into the event_queue.
        """
        request_experience = self._get_request_experience(current_bt)
        segment = {
            'tier': config.AGENT_TIER_NAME,
            'tierId': str(self.agent.tier_id),
            'node': config.AGENT_NODE_NAME,
            'nodeId': str(self.agent.node_id),
            'requestExperience': request_experience,
            'entryPoint': self._is_entry_point(current_bt),
            'transactionTime': current_bt.timer.duration_ms,
        }
        exit_calls = self._get_exit_call_details_dict(current_bt)
        if exit_calls:
            segment['exitCalls'] = exit_calls

        error_list = self._get_error_list_dict(current_bt)
        if error_list:
            segment['errorList'] = error_list

        segment['httpData'] = self._get_http_data_dict(current_bt)

        # Adding MIDC data to analytics event
        MIDC_data = {}
        # MIDC data tuple format: (key, value, enabled_for_snapshots, enabled_for_analytics)
        for key, value, _, enabled_for_analytics in current_bt.midc_data:
            if enabled_for_analytics:  # if data is enabled for anlytics
                MIDC_data[key] = value

        if MIDC_data:
            segment['userData'] = MIDC_data

        event = {
            'eventTimestamp': self._get_event_timestamp(current_bt),
            'application': config.AGENT_APPLICATION_NAME,
            'applicationId': str(self.agent.app_id),
            'requestGUID': self._get_request_guid(current_bt),
            'transactionName': current_bt.name,
            'transactionId': current_bt.registered_id,
            'userExperience': request_experience,
            'responseTime': current_bt.timer.duration_ms,
            'segments': [segment]
        }

        self.logger.debug('Event recorded is {}'.format(event))
        self.event_queue.put(event, block=False)

    def report_data(self):
        """This method reports analytics data by adding request to the transport queue. Transport service then
        sends the data with a POST request.
        """
        if not self.event_queue.empty():
            event_list = []
            while not self.event_queue.empty():
                event_list.append(self.event_queue.get())

            analytics_request = (self.analytics_agent_url, iter(event_list), self.default_analytics_request_headers)
            self.analytics_transport_svc.transport_queue.put(analytics_request, block=False)
            self.report_event.clear()

    def _buffer_limit_reached(self):
        return self.event_queue.qsize() >= config.ANALYTICS_BUFFER_MAX_SIZE

    def report_analytics(self, current_bt):
        """This method checks if BT data needs to be sent for analytics, records the transaction and reports data in case
        buffer limit is reached.
        It will be called when a BT ends and acts as an interface between transaction service and analytics service.
        """
        try:
            if not self.enabled:
                self.logger.debug('Analytics service is disabled. Transaction Analytics will not be reported...')
                self.service_activated.clear()
                return

            if self.analytics_enabled_for_bt(current_bt.registered_id):
                self.logger.debug('Analytics service is enabled. Recording analytics for BT...')
                self.record_transaction(current_bt)

                # starts analytics service to report data every ANALYTICS_REPORT_DATA_TIMEOUT (i.e.30) seconds
                self.service_activated.set()

                # report directly if buffer limit is reached
                if self._buffer_limit_reached():
                    self.logger.debug('Analytics Buffer limit reached, reporting data...')
                    self.report_data()
        except:
            self.logger.exception('Analytics Svc report_analytics failed')

    # methods to insert exit calls data for analytics
    def _is_backend_registered(self, backend_metric):
        return backend_metric['backendIdentifier']['type'] == pb.BackendIdentifier.REGISTERED

    def _get_entity_from_backend_metric(self, backend_metric):
        """ Returns type of entity based on backend properties
        """
        entity_type = 'BACKEND'
        registered_backend = backend_metric.get('backendIdentifier').get('registeredBackend')
        component_id = registered_backend.get('componentID')
        backend_id = registered_backend.get('backendID')
        if component_id and component_id != 0:
            entity_type = 'APPLICATION_COMPONENT'
            if registered_backend.get('componentIsForeignAppID'):
                entity_type = 'APPLICATION'

        entity_id = None
        if component_id and component_id != 0:
            entity_id = component_id
        elif backend_id and backend_id != 0:
            entity_id = backend_id

        return {
            'entityId': str(entity_id),
            'entityType': entity_type
        }

    def _get_avg_response_time_from_backend_metric(self, backend_metric):
        """ Internal method to calculate average response time from a backend metric
        """
        if backend_metric.get('numOfCalls') and backend_metric.get('numOfCalls') > 0:
            return backend_metric.get('timeTaken') / backend_metric.get('numOfCalls')

    def _get_exit_call_details_dict(self, bt):
        """Returns exit call dictionary to be included in the event being sent to analytics agent

        """
        exit_calls = []
        backend_metrics = make_backend_metrics_dicts(values(bt._exit_calls))

        for backend_metric in backend_metrics:
            if self._is_backend_registered(backend_metric):
                exit_call = {
                    'exitCallType': self.EXIT_POINT_TYPES[
                        backend_metric.get('backendIdentifier').get('registeredBackend').get('exitPointType')
                    ],
                    # Currently only synchronous exit calls points are supported in python agent
                    'isSynchronous': True,
                    # Currently there is no support for custom exit points for python agent
                    'customExitCallDefinitionId': '0',
                    'isCustomExitCall': False,
                    'avgResponseTimeMillis': self._get_avg_response_time_from_backend_metric(backend_metric),
                    'numberOfCalls': backend_metric.get('numOfCalls'),
                    'numberOfErrors': backend_metric.get('numOfErrors'),
                    'toEntity': self._get_entity_from_backend_metric(backend_metric)
                }

                exit_calls.append(exit_call)
        return exit_calls

    # methods to insert error details for analytics
    def _get_http_error_code(self, display_name):
        """returns http error code here if present
        """
        if 'HTTP' in display_name:
            splitted_display_name = display_name.split(' ')
            if len(splitted_display_name) == 2:
                return splitted_display_name[1]
        return None

    def _create_error_detail_from_stack_trace(self, stack_trace_elements):
        error_detail = ''
        for element in stack_trace_elements:
            error_detail += '{}({}:{})\n'.format(
                element.get('method').decode('utf-8'),
                element.get('fileName').decode('utf-8'),
                element.get('lineNumber'))

        return error_detail

    def _get_error_entry_from_exception_info(self, exception, stack_trace):
        """Creates error entry to be added into error list for given exceptions and stacktrace
        Parameter:
            exception: pb.RootException (PHPAgentProtobufs.proto)
            stack_trace: [pb.StackTrace] (PHPAgentProtobufs.proto)
        """
        error_detail = '{}.{}\n'.format(
            exception.get('root', {}).get('klass').decode('utf-8'),
            exception.get('root', {}).get('message').decode('utf-8'))

        error_detail += self._create_error_detail_from_stack_trace(stack_trace.get('elements', []))
        return {
            'errorDetail': error_detail,
            'errorType': 'EXCEPTION',
            'errorCode': None
        }

    def _get_error_list_dict(self, bt):
        """Returns dictionary of errors associated with a BT to be added to analytics event.
        """
        errors_dict = make_bt_errors_dict(bt.errors, bt.exceptions)
        error_list = []
        try:
            for error_info in errors_dict.get('errorInfo', {}).get('errors', {}):
                error_list.append({
                    'errorDetail': error_info.get('errorMessage').decode("utf-8") + '\n',
                    'errorType': error_info.get('displayName').decode("utf-8"),
                    'errorCode': self._get_http_error_code(error_info.get('displayName').decode("utf-8"))
                })

            for exception in errors_dict.get('exceptionInfo', {}).get('exceptions', {}):
                stack_trace_id = exception.get('root', {}).get('stackTraceID')
                stack_traces = errors_dict.get('exceptionInfo').get('stackTraces', [])
                current_stack_trace = {}
                if stack_trace_id is not None and len(stack_traces) > stack_trace_id:
                    current_stack_trace = stack_traces[stack_trace_id]

                error_list.append(self._get_error_entry_from_exception_info(exception, current_stack_trace))
        except:
            self.logger.exception('Failed to add errors to analytics event.')

        return error_list

    def _get_http_data_dict(self, bt):
        http_data = {}
        try:
            bt.http_data_gatherer = self.agent.data_gatherer_registry.get_http_data_gatherer(bt.registered_id)
            http_data['url'] = bt.request.path
            if bt.http_data_gatherer:
                cookies = {}
                for key, _, enabled_for_analytics in bt.http_data_gatherer.cookies:
                    if key in bt.request.cookies and enabled_for_analytics:
                        cookies[key] = bt.request.cookies[key]
                http_data['cookies'] = cookies

                headers = {}
                for key, _, enabled_for_analytics in bt.http_data_gatherer.headers:
                    if key in bt.request.headers and enabled_for_analytics:
                        headers[key] = bt.request.headers[key]
                http_data['headers'] = headers

                http_params = {}
                for (key, name), _, enabled_for_analytics in bt.http_data_gatherer.request_params:
                    if key in bt.request.args and enabled_for_analytics:
                        http_params[name] = bt.request.args[key]
                http_data['parameters'] = http_params

        except:
            self.logger.exception('Failed to add http data to analytics event')
        return http_data
