import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.roxx.evaluation_result import EvaluationResult
from rox.core.entities.rox_int import RoxInt

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class RoxIntTests(unittest.TestCase):
    def test_will_not_add_default_to_options_if_exists(self):
        rox_int = RoxInt(1, [1, 2, 3])
        self.assertEqual(3, len(rox_int.options))

    def test_will_add_default_to_options_if_not_exists(self):
        rox_int = RoxInt(1, [2, 3])

        self.assertEqual(3, len(rox_int.options))
        self.assertTrue(1 in rox_int.options)

    def test_will_throw_exception_for_none_default_value(self):
        with self.assertRaises(TypeError):
            RoxInt(None, [2, 3])

    def test_will_fail_on_non_int_value(self):
        with self.assertRaises(ValueError) as context:
            RoxInt('abc', [2, 3])
        self.assertTrue('abc is not of type int')

        with self.assertRaises(ValueError) as context:
            RoxInt(1, [2, 'def'])
        self.assertTrue('def is not of type int')

    def test_will_set_name(self):
        rox_int = RoxInt(1, [2, 3])

        self.assertIsNone(rox_int.name)

        rox_int.set_name('bop')

        self.assertEqual('bop', rox_int.name)

    def test_will_return_default_value_when_no_parser_or_condition(self):
        rox_int = RoxInt(1, [2, 3])

        self.assertEqual(1, rox_int.get_value())

        parser = Mock()
        rox_int.set_for_evaluation(parser, None, None)

        self.assertEqual(1, rox_int.get_value())

        rox_int.set_for_evaluation(None, None, ExperimentModel('id', 'name', '123', False, [1], set(), 'stam'))

        self.assertEqual(1, rox_int.get_value())

    def test_will_return_default_value_when_result_not_in_options(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(7)

        rox_int = RoxInt(1, [2, 3])
        rox_int.set_for_evaluation(parser, None, ExperimentModel('id', 'name', '123', False, [1], set(), 'stam'))

        self.assertEqual(7, rox_int.get_value())

    def test_will_return_value_when_on_evaluation(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(2)

        rox_int = RoxInt(1, [2, 3])
        rox_int.set_for_evaluation(parser, None, ExperimentModel('id', 'name', '123', False, [1], set(), 'stam'))

        self.assertEqual(2, rox_int.get_value())

    def test_will_raise_impression(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(2)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = True

        internal_flags = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, None, None, None, None, Mock())
        imp_invoker.register_impression_handler(on_impression)

        rox_int = RoxInt(1, [2, 3])
        rox_int.set_for_evaluation(parser, imp_invoker, ExperimentModel('id', 'name', '123', False, [1], set(), 'stam'))

        self.assertEqual(2, rox_int.get_value())
        self.assertTrue(is_impression_raised['raised'])

    def test_should_return_code_default_when_flag_dependency_does_not_exist(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('10')

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = e

        internal_flags = Mock()
        custom_property_repository = Mock()
        analytics_client = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, custom_property_repository, None, analytics_client, None, None)
        imp_invoker.register_impression_handler(on_impression)

        flag = RoxInt(10)
        flag.condition = 'flagValue("fff")'
        flag.impression_invoker = imp_invoker
        flag.parser = parser
        self.assertEqual(0, flag.get_value())
        self.assertEqual(0, is_impression_raised['raised'].reporting_value.value)

    def test_should_return_flag_default_value_when_expression_is_faulty(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(20)

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = e

        internal_flags = Mock()
        custom_property_repository = Mock()
        analytics_client = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, custom_property_repository, None, analytics_client, None, None)
        imp_invoker.register_impression_handler(on_impression)

        flag = RoxInt(20)
        flag.condition = 'thisisfake("5")'
        flag.impression_invoker = imp_invoker
        flag.parser = parser
        self.assertEqual(20, flag.get_value())
        self.assertEqual(20, is_impression_raised['raised'].reporting_value.value)
