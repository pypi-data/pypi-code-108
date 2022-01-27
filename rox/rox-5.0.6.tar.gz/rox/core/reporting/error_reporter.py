from concurrent.futures import ThreadPoolExecutor

from rox.core.logging.logging import Logging
from rox.core.network.request import RequestData

class ErrorReporter:
    BUGSNAG_NOTIFY_URL = 'https://notify.bugsnag.com'

    def __init__(self, request, device_properties, buid):
        self.request = request
        self.device_properties = device_properties
        self.buid = buid
        self.executor = ThreadPoolExecutor(1)

    def report(self, message, ex, stack):
        if self.device_properties.rollout_environment == 'LOCAL':
            return

        Logging.get_logger().error('Error report: %s' % message, ex)

        if self.device_properties.rox_options.is_self_managed():
            return

        try:
            payload = self.create_payload(message, ex, stack)
        except Exception as ex:
            Logging.get_logger().error('failed to create bugsnag json payload of the error', ex)
        else:
            self.executor.submit(self.send_error, payload)

    def send_error(self, payload):
        Logging.get_logger().debug('Sending bugsnag error report...')

        try:
            self.request.send_post(RequestData(ErrorReporter.BUGSNAG_NOTIFY_URL, payload))
            Logging.get_logger().debug('Bugsnag error report was sent')
        except Exception as ex:
            Logging.get_logger().error('Failed to send bugsnag error ', ex)

    def create_payload(self, message, ex, stack):
        payload = {}
        self.add_api_key(payload)
        self.add_notifier(payload)
        self.add_events(message, ex, stack, payload)

        return payload

    def add_metadata(self, message, ev):
        latest_buid = self.buid.get_latest_buid()

        inner_data = {
            'message': message,
            'deviceId': self.device_properties.distinct_id,
            'buid': '' if latest_buid is None else str(latest_buid)
        }

        metadata = {
            'data': inner_data
        }

        ev['metaData'] = metadata

    def add_api_key(self, payload):
        payload['apiKey'] = '5e7127139b31b7d270b510e3b4b99021'

    def add_events(self, message, ex, stack, payload):
        evs = []
        self.add_event(message, ex, stack, evs)
        payload['events'] = evs

    def add_event(self, message, ex, stack, events):
        ev = {}
        self.add_payload_version(ev)
        self.add_exceptions(message, ex, stack, ev)
        self.add_user('id', self.device_properties.rollout_key, ev)
        self.add_metadata(message, ev)
        self.add_app(ev)
        events.append(ev)

    def add_payload_version(self, ev):
        ev['payloadVersion'] = 2

    def add_notifier(self, payload):
        notifier = {
            'name': 'Rollout Python SDK',
            'version': self.device_properties.lib_version
        }
        payload['notifier'] = notifier

    def add_user(self, id, rollout_key, ev):
        user = {
            id: rollout_key
        }
        ev['user'] = user

    def add_exceptions(self, message, ex, stack, ev):
        exceptions = []
        exception = {}

        if ex is None:
            exception['errorClass'] = message
            exception['message'] = message
            exception['stacktrace'] = []
        else:
            exception['errorClass'] = ex.args[0] if len(ex.args) > 0 else message
            exception['message'] = ex.args[0] if len(ex.args) > 0 else message

            stack_trace_array = []
            for frame in stack:
                if isinstance(frame, tuple):
                    file_name, line_number, method_name = frame[0], frame[1], frame[2]
                else:
                    file_name, line_number, method_name = frame.filename, frame.lineno, frame.name

                stack_trace_object = {
                    'file': file_name,
                    'method': method_name,
                    'lineNumber': line_number,
                    'columnNumber': 0,
                }
                stack_trace_array.append(stack_trace_object)

            exception['stacktrace'] = stack_trace_array

        exceptions.append(exception)
        ev['exceptions'] = exceptions

    def add_app(self, ev):
        app = {
            'releaseStage': self.device_properties.rollout_environment,
            'version': self.device_properties.lib_version
        }
        ev['app'] = app
