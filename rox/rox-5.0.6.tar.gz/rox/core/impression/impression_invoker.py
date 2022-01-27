import os
from collections import namedtuple

from rox.core.consts import property_type
from rox.core.error_handling.exception_trigger import ExceptionTrigger
from rox.core.logging.logging import Logging
from rox.core.utils.time_utils import now_in_unix_milliseconds
from rox.core.utils.type_utils import is_string

ImpressionArgs = namedtuple('ImpressionArgs', ['reporting_value', 'context'])


class ImpressionInvoker:
    def __init__(self, internal_flags, custom_property_repository, device_properties, analytics_client, is_roxy, user_unhandled_error_invoker):
        self.internal_flags = internal_flags
        self.custom_property_repository = custom_property_repository
        self.device_properties = device_properties
        self.analytics_client = analytics_client
        self.is_roxy = is_roxy
        self.user_unhandled_error_invoker = user_unhandled_error_invoker

        self.impression_handlers = []

    def invoke(self, reporting_value, stickiness_property, context):
        try:
            internal_experiment = self.internal_flags.is_enabled('rox.internal.analytics')
            if internal_experiment and not self.is_roxy:
                prop = self.custom_property_repository.get_custom_property(stickiness_property) or self.custom_property_repository.get_custom_property('rox.' + property_type.DISTINCT_ID.name)
                distinct_id = '(null_distinct_id'
                if prop is not None:
                    prop_value = prop.value(context)
                    if is_string(prop_value):
                        distinct_id = prop_value

                event_time = now_in_unix_milliseconds()
                try:
                    event_time = int(os.getenv('rox.analytics.ms'))
                except ValueError:
                    pass
                except TypeError:
                    pass

                self.analytics_client.track({
                    'flag': reporting_value.name,
                    'value': reporting_value.value,
                    'distinctId': distinct_id,
                    'experimentVersion': '0',
                    'type': 'IMPRESSION',
                    'time': event_time,
                })
        except Exception as ex:
            Logging.get_logger().error('Failed to send analytics', ex)

        self.raise_impression_event(ImpressionArgs(reporting_value, context))

    def register_impression_handler(self, handler):
        self.impression_handlers.append(handler)

    def raise_impression_event(self, args):
        for handler in self.impression_handlers:
            try:
                handler(args)
            except Exception as ex:
                self.user_unhandled_error_invoker.invoke(handler, ExceptionTrigger.IMPRESSION_HANDLER, ex)
                Logging.get_logger().error('Impresssion handler exception', ex)
