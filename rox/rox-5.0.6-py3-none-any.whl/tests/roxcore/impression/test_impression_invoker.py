import unittest

from rox.core.logging.logging import Logging
from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.consts import property_type
from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.impression.impression_invoker import ImpressionInvoker, ImpressionArgs
from rox.core.impression.models.reporting_value import ReportingValue
from rox.core.utils.time_utils import now_in_unix_milliseconds

try:
    from unittest.mock import Mock, MagicMock
except ImportError:
    from mock import Mock, MagicMock


class ImpressionInvokerTests(unittest.TestCase):
    def test_will_set_impression_invoker_empty_invoke_not_throwing_exception(self):
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, Mock())
        impression_invoker.invoke(None, None, None)

    def test_will_make_sure_impression_invoker_exception_not_raising_exception(self):
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, Mock())
        impression_invoker.invoke(None, None, None)
        
        logger = Mock()
        Logging.set_logger(logger)
        
        exception = Exception('user code error')
        
        def on_impression(e):
            raise exception

        impression_invoker.register_impression_handler(on_impression)
        try:
            impression_invoker.invoke(None, None, None)
        except:
            self.fail("Unexpected exception")

        self.assertEqual(2, len(logger.error.call_args_list))
        args, _ = logger.error.call_args_list[1]
        self.assertEqual(2, len(args))
        self.assertEqual(args[0], 'Impresssion handler exception')
        self.assertEqual(args[1], exception)

    def test_will_test_impression_invoker_invoke_and_parameters(self):
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, Mock())

        context = {'obj1', 1}

        reporting_value = ReportingValue('name', 'value', False)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            self.assertEqual(reporting_value, e.reporting_value)
            self.assertEqual(context, e.context)

            is_impression_raised['raised'] = True

        impression_invoker.register_impression_handler(on_impression)
        impression_invoker.invoke(reporting_value, None, context)

        self.assertTrue(is_impression_raised['raised'])

    def test_reporting_value_constructor(self):
        reporting_value = ReportingValue('pi', 'ka', True)

        self.assertEqual('pi', reporting_value.name)
        self.assertEqual('ka', reporting_value.value)

    def test_impression_args_constructor(self):
        context = {'obj1': 1}
        reporting_value = ReportingValue('name', 'value', False)

        impression_args = ImpressionArgs(reporting_value, context)

        self.assertEqual(reporting_value, impression_args.reporting_value)
        self.assertEqual(context, impression_args.context)

    def test_will_not_invoke_analytics_when_flag_is_off(self):
        internal_flags = Mock()
        analytics = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, analytics, False, Mock())

        context = {'obj1': 1}
        reporting_value = ReportingValue('name', 'value', False)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            self.assertEqual(reporting_value, e.reporting_value)
            self.assertEqual(context, e.context)

            is_impression_raised['raised'] = True

        impression_invoker.register_impression_handler(on_impression)
        impression_invoker.invoke(reporting_value, None, context)

        self.assertTrue(is_impression_raised['raised'])

    def test_will_not_invoke_analytics_when_is_roxy(self):
        def is_enabled(flag_name):
            if flag_name == 'rox.internal.analytics':
                return True

        internal_flags = Mock()
        internal_flags.is_enabled = Mock(side_effect=is_enabled)

        def get_custom_property(property_name):
            if property_name == 'rox.' + property_type.DISTINCT_ID.name:
                return CustomProperty('rox.' + property_type.DISTINCT_ID.name, CustomPropertyType.STRING, 'stam')

        custom_props = Mock()
        custom_props.get_custom_property = Mock(side_effect=get_custom_property)

        device_props = Mock()
        device_props.distinct_id = 'stamId'

        analytics = Mock()

        impression_invoker = ImpressionInvoker(internal_flags, custom_props, device_props, analytics, True, None)

        context = {'obj1': 1}
        reporting_value = ReportingValue('name', 'value', False)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            self.assertEqual(reporting_value, e.reporting_value)
            self.assertEqual(context, e.context)

            is_impression_raised['raised'] = True

        impression_invoker.register_impression_handler(on_impression)
        impression_invoker.invoke(reporting_value, None, context)

        self.assertTrue(is_impression_raised['raised'])
        self.assertEqual(0, analytics.track.call_count)

    def test_will_invoke_analytics(self):
        def is_enabled(flag_name):
            if flag_name == 'rox.internal.analytics':
                return True

        internal_flags = Mock()
        internal_flags.is_enabled = Mock(side_effect=is_enabled)

        def get_custom_property(property_name):
            if property_name == 'rox.' + property_type.DISTINCT_ID.name:
                return CustomProperty('rox.' + property_type.DISTINCT_ID.name, CustomPropertyType.STRING, 'stam')

        custom_props = Mock()
        custom_props.get_custom_property = Mock(side_effect=get_custom_property)

        device_props = Mock()
        device_props.distinct_id = 'stamId'

        out_event = {'event': None}

        def track(e):
            out_event['event'] = e

        analytics = Mock()
        analytics.track = Mock(side_effect=track)

        impression_invoker = ImpressionInvoker(internal_flags, custom_props, device_props, analytics, False, None)

        context = {'obj1': 1}
        reporting_value = ReportingValue('name', 'value', False)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            self.assertEqual(reporting_value, e.reporting_value)
            self.assertEqual(context, e.context)

            is_impression_raised['raised'] = True

        impression_invoker.register_impression_handler(on_impression)
        impression_invoker.invoke(reporting_value, None, context)

        self.assertTrue(is_impression_raised['raised'])
        self.assertEqual(1, analytics.track.call_count)
        self.assertEqual('stam', out_event['event']['distinctId'])
        self.assertEqual('0', out_event['event']['experimentVersion'])
        self.assertEqual('name', out_event['event']['flag'])
        self.assertEqual('value', out_event['event']['value'])
        self.assertEqual('IMPRESSION', out_event['event']['type'])
        self.assertTrue(out_event['event']['time'] <= now_in_unix_milliseconds())

    def test_will_invoke_analytics_with_stickiness_prop(self):
        def is_enabled(flag_name):
            if flag_name == 'rox.internal.analytics':
                return True

        internal_flags = Mock()
        internal_flags.is_enabled = Mock(side_effect=is_enabled)

        def get_custom_property(property_name):
            if property_name == 'stickProp':
                return CustomProperty('stickProp', CustomPropertyType.STRING, 'stamStick')
            if property_name == 'rox.' + property_type.DISTINCT_ID.name:
                return CustomProperty('rox.' + property_type.DISTINCT_ID.name, CustomPropertyType.STRING, 'stamDist')

        custom_props = Mock()
        custom_props.get_custom_property = Mock(side_effect=get_custom_property)

        device_props = Mock()
        device_props.distinct_id = 'stamId'

        out_event = {'event': None}

        def track(e):
            out_event['event'] = e

        analytics = Mock()
        analytics.track = Mock(side_effect=track)

        impression_invoker = ImpressionInvoker(internal_flags, custom_props, device_props, analytics, False, None)

        context = {'obj1': 1}
        reporting_value = ReportingValue('name', 'value', False)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            self.assertEqual(reporting_value, e.reporting_value)
            self.assertEqual(context, e.context)

            is_impression_raised['raised'] = True

        impression_invoker.register_impression_handler(on_impression)
        impression_invoker.invoke(reporting_value, 'stickProp', context)

        self.assertTrue(is_impression_raised['raised'])
        self.assertEqual(1, analytics.track.call_count)
        self.assertEqual('stamStick', out_event['event']['distinctId'])
        self.assertEqual('0', out_event['event']['experimentVersion'])
        self.assertEqual('name', out_event['event']['flag'])
        self.assertEqual('value', out_event['event']['value'])
        self.assertEqual('IMPRESSION', out_event['event']['type'])
        self.assertTrue(out_event['event']['time'] <= now_in_unix_milliseconds())

    def test_will_invoke_analytics_with_bad_distinct_id(self):
        def is_enabled(flag_name):
            if flag_name == 'rox.internal.analytics':
                return True

        internal_flags = Mock()
        internal_flags.is_enabled = Mock(side_effect=is_enabled)

        custom_props = Mock()
        custom_props.get_custom_property.return_value = None

        device_props = Mock()
        device_props.distinct_id = 'stamId'

        out_event = {'event': None}

        def track(e):
            out_event['event'] = e

        analytics = Mock()
        analytics.track = Mock(side_effect=track)

        impression_invoker = ImpressionInvoker(internal_flags, custom_props, device_props, analytics, False, None)

        context = {'obj1': 1}
        reporting_value = ReportingValue('name', 'value', False)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            self.assertEqual(reporting_value, e.reporting_value)
            self.assertEqual(context, e.context)

            is_impression_raised['raised'] = True

        impression_invoker.register_impression_handler(on_impression)
        impression_invoker.invoke(reporting_value, None, context)

        self.assertTrue(is_impression_raised['raised'])
        self.assertEqual(1, analytics.track.call_count)
        self.assertEqual('(null_distinct_id', out_event['event']['distinctId'])
        self.assertEqual('0', out_event['event']['experimentVersion'])
        self.assertEqual('name', out_event['event']['flag'])
        self.assertEqual('value', out_event['event']['value'])
        self.assertEqual('IMPRESSION', out_event['event']['type'])
        self.assertTrue(out_event['event']['time'] <= now_in_unix_milliseconds())
