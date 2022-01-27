import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.roxx.evaluation_result import EvaluationResult
from rox.core.entities.rox_string import RoxString

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class RoxStringTests(unittest.TestCase):
    def test_will_not_add_default_to_options_if_exists(self):
        rox_string = RoxString('1', ['1', '2', '3'])
        self.assertEqual(3, len(rox_string.options))

    def test_will_add_default_to_options_if_not_exists(self):
        rox_string = RoxString('1', ['2', '3'])

        self.assertEqual(3, len(rox_string.options))
        self.assertTrue('1' in rox_string.options)

    def test_will_set_name(self):
        rox_string = RoxString('1', ['2', '3'])

        self.assertIsNone(rox_string.name)

        rox_string.set_name('bop')

        self.assertEqual('bop', rox_string.name)

    def test_will_return_default_value_when_no_parser_or_condition(self):
        rox_string = RoxString('1', ['2', '3'])

        self.assertEqual('1', rox_string.get_value())

        parser = Mock()
        rox_string.set_for_evaluation(parser, None, None)

        self.assertEqual('1', rox_string.get_value())

        rox_string.set_for_evaluation(None, None, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'))

        self.assertEqual('1', rox_string.get_value())

    def test_will_return_default_value_when_result_not_in_options(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('xxx')

        rox_string = RoxString('1', ['2', '3'])
        rox_string.set_for_evaluation(parser, None, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'))

        self.assertEqual('xxx', rox_string.get_value())

    def test_will_return_value_when_on_evaluation(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('2')

        rox_string = RoxString('1', ['2', '3'])
        rox_string.set_for_evaluation(parser, None, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'))

        self.assertEqual('2', rox_string.get_value())

    def test_will_raise_impression(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('2')

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = True

        internal_flags = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, None, None, None, None, Mock())
        imp_invoker.register_impression_handler(on_impression)

        rox_string = RoxString('1', ['2', '3'])
        rox_string.set_for_evaluation(parser, imp_invoker, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'))

        self.assertEqual('2', rox_string.get_value())
        self.assertTrue(is_impression_raised['raised'])

    def test_should_return_flag_default_when_flag_dependency_does_not_exist(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('')

        is_impression_raised = {'raised': None}

        def on_impression(e):
            is_impression_raised['raised'] = e

        internal_flags = Mock()
        custom_property_repository = Mock()
        analytics_client = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, custom_property_repository, None, analytics_client, None, None)
        imp_invoker.register_impression_handler(on_impression)

        flag = RoxString('10')
        flag.condition = 'flagValue("fff")'
        flag.impression_invoker = imp_invoker
        flag.parser = parser
        self.assertEqual('', flag.get_value())
        self.assertEqual('', is_impression_raised['raised'].reporting_value.value)

    def test_should_return_flag_default_value_when_expression_is_faulty(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(2)

        is_impression_raised = {'raised': None}

        def on_impression(e):
            is_impression_raised['raised'] = e

        internal_flags = Mock()
        custom_property_repository = Mock()
        analytics_client = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, custom_property_repository, None, analytics_client, None, None)
        imp_invoker.register_impression_handler(on_impression)

        flag = RoxString('20')
        flag.condition = 'thisisfake("5")'
        flag.impression_invoker = imp_invoker
        flag.parser = parser
        self.assertEqual('20', flag.get_value())
        self.assertEqual('20', is_impression_raised['raised'].reporting_value.value)
