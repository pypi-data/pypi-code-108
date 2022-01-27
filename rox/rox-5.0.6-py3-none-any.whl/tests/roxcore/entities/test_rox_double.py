import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.roxx.evaluation_result import EvaluationResult
from rox.core.entities.rox_double import RoxDouble

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class RoxDoubleTests(unittest.TestCase):
    def test_will_not_add_default_to_options_if_exists(self):
        rox_double = RoxDouble(1.0, [1.0, 2.0, 3.0])
        self.assertEqual(3, len(rox_double.options))

    def test_will_add_default_to_options_if_not_exists(self):
        rox_double = RoxDouble(1.0, [2.0, 3.0])

        self.assertEqual(3, len(rox_double.options))
        self.assertTrue(1.0 in rox_double.options)

    def test_will_throw_exception_for_none_default_value(self):
        with self.assertRaises(TypeError):
            RoxDouble(None, [2.0, 3.0]) 

    def test_will_fail_on_non_float_value(self):
        with self.assertRaises(ValueError) as context:
            RoxDouble('abc', [2.0, 3.0])
        self.assertTrue('abc is not of type float')

        with self.assertRaises(ValueError) as context:
            RoxDouble(1.0, [2.0, 'def'])
        self.assertTrue('def is not of type float')

    def test_will_set_name(self):
        rox_double = RoxDouble(1.0, [2.0, 3.0])

        self.assertIsNone(rox_double.name)

        rox_double.set_name('bop')

        self.assertEqual('bop', rox_double.name)

    def test_will_return_default_value_when_no_parser_or_condition(self):
        rox_double = RoxDouble(1.0, [2.0, 3.0])

        self.assertEqual(1.0, rox_double.get_value())

        parser = Mock()
        rox_double.set_for_evaluation(parser, None, None)

        self.assertEqual(1.0, rox_double.get_value())

        rox_double.set_for_evaluation(None, None, ExperimentModel('id', 'name', '123', False, [1.0], set(), 'stam'))

        self.assertEqual(1.0, rox_double.get_value())

    def test_will_return_default_value_when_result_not_in_options(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(7.0)

        rox_double = RoxDouble(1.0, [2.0, 3.0])
        rox_double.set_for_evaluation(parser, None, ExperimentModel('id', 'name', '123', False, [1.0], set(), 'stam'))

        self.assertEqual(7.0, rox_double.get_value())

    def test_will_return_value_when_on_evaluation(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(2.0)

        rox_double = RoxDouble(1.0, [2.0, 3.0])
        rox_double.set_for_evaluation(parser, None, ExperimentModel('id', 'name', '123', False, [1.0], set(), 'stam'))

        self.assertEqual(2.0, rox_double.get_value())

    def test_will_raise_impression(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(2.0)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = True

        internal_flags = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, None, None, None, None, Mock())
        imp_invoker.register_impression_handler(on_impression)

        rox_double = RoxDouble(1.0, [2.0, 3.0])
        rox_double.set_for_evaluation(parser, imp_invoker, ExperimentModel('id', 'name', '123', False, [1.0], set(), 'stam'))

        self.assertEqual(2.0, rox_double.get_value())
        self.assertTrue(is_impression_raised['raised'])

    def test_should_return_code_default_when_flag_dependency_does_not_exist(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('20.5')

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = e

        internal_flags = Mock()
        custom_property_repository = Mock()
        analytics_client = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, custom_property_repository, None, analytics_client, None, None)
        imp_invoker.register_impression_handler(on_impression)

        flag = RoxDouble(10.6)
        flag.condition = 'flagValue("fff")'
        flag.impression_invoker = imp_invoker
        flag.parser = parser
        self.assertEqual(0.0, flag.get_value())
        self.assertEqual(0.0, is_impression_raised['raised'].reporting_value.value)

    def test_should_return_flag_default_value_when_expression_is_faulty(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(20.5)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = e

        internal_flags = Mock()
        custom_property_repository = Mock()
        analytics_client = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, custom_property_repository, None, analytics_client, None, None)
        imp_invoker.register_impression_handler(on_impression)

        flag = RoxDouble(20.5)
        flag.condition = 'thisisfake("5")'
        flag.impression_invoker = imp_invoker
        flag.parser = parser
        self.assertEqual(20.5, flag.get_value())
        self.assertEqual(20.5, is_impression_raised['raised'].reporting_value.value)
