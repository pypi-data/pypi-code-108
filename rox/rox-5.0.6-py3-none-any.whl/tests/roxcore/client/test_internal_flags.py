import unittest

from rox.core.client.internal_flags import InternalFlags
from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.entities.flag import Flag
from rox.core.roxx.evaluation_result import EvaluationResult
from rox.server.rox_options import RoxOptions

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class InternalFlagsTests(unittest.TestCase):
    def test_will_return_false_when_no_experiment(self):
        parser = Mock()
        exp_repo = Mock()
        exp_repo.get_experiment_by_flag.return_value = None
        internal_flags = InternalFlags(exp_repo, parser, RoxOptions())

        self.assertFalse(internal_flags.is_enabled('stam'))

    def test_will_return_false_when_expession_is_null(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(None)
        exp_repo = Mock()
        exp_repo.get_experiment_by_flag.return_value = ExperimentModel('id', 'name', 'stam', False, None, None, 'stam')
        internal_flags = InternalFlags(exp_repo, parser, RoxOptions())

        self.assertFalse(internal_flags.is_enabled('stam'))

    def test_will_return_false_when_expession_is_false(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(Flag.FLAG_FALSE_VALUE)
        exp_repo = Mock()
        exp_repo.get_experiment_by_flag.return_value = ExperimentModel('id', 'name', 'stam', False, None, None, 'stam')
        internal_flags = InternalFlags(exp_repo, parser, RoxOptions())

        self.assertFalse(internal_flags.is_enabled('stam'))

    def test_will_return_true_when_expession_is_true(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult(Flag.FLAG_TRUE_VALUE)
        exp_repo = Mock()
        exp_repo.get_experiment_by_flag.return_value = ExperimentModel('id', 'name', 'stam', False, None, None, 'stam')
        internal_flags = InternalFlags(exp_repo, parser, RoxOptions())

        self.assertTrue(internal_flags.is_enabled('stam'))
