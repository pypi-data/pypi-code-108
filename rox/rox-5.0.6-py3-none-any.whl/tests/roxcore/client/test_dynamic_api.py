import unittest

from rox.core.client.dynamic_api import DynamicApi
from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.entities.flag import Flag
from rox.core.entities.flag_setter import FlagSetter
from rox.core.entities.rox_string import RoxString
from rox.core.entities.rox_int import RoxInt
from rox.core.entities.rox_double import RoxDouble
from rox.core.repositories.experiment_repository import ExperimentRepository
from rox.core.repositories.flag_repository import FlagRepository
from rox.core.roxx.parser import Parser
from rox.core.roxx.evaluation_result import EvaluationResult

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

class DynamicApiTests(unittest.TestCase):
    def test_is_enabled(self):
        parser = Parser(None)
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertTrue(dynamic_api.is_enabled('default.newFlag', True))
        self.assertEqual(True, flag_repo.get_flag('default.newFlag').is_enabled(None))
        self.assertFalse(dynamic_api.is_enabled('default.newFlag', False))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newFlag', 'and(true, true)', False, ['default.newFlag'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertTrue(dynamic_api.is_enabled('default.newFlag', False))

    def test_get_flag_value(self):
        flag = Flag(True)

        parser = Parser(None)
        flag_repo = FlagRepository()
        flag_repo.add_flag(flag, 'default.new_flag')
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertTrue(dynamic_api.value('default.new_flag', 'false'))

    def test_is_enabled_after_setup(self):
        parser = Parser(None)
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        exp_repo.set_experiments([ExperimentModel('1', 'default.newFlag', 'and(true, true)', False, ['default.newFlag'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertTrue(dynamic_api.is_enabled('default.newFlag', False))

    def test_get_value_for_string(self):
        parser = Parser(None)
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertEqual('A', dynamic_api.value('default.newVariant', 'A', ['A', 'B', 'C']))
        self.assertEqual('A', flag_repo.get_flag('default.newVariant').get_value())
        self.assertEqual('B', dynamic_api.value('default.newVariant', 'B', ['A', 'B', 'C']))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newVariant', 'ifThen(true, "B", "A")', False, ['default.newVariant'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual('B', dynamic_api.value('default.newVariant', 'A', ['A', 'B', 'C']))

    def test_get_value_for_int(self):
        parser = Parser(None)
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertEqual(1, dynamic_api.get_int('default.newVariant', 1, [1, 2, 3]))
        self.assertEqual(1, flag_repo.get_flag('default.newVariant').get_value())
        self.assertEqual(2, dynamic_api.get_int('default.newVariant', 2, [1, 2, 3]))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newVariant', 'ifThen(true, "2", "1")', False, ['default.newVariant'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual(2, dynamic_api.get_int('default.newVariant', 1, [1, 2, 3]))


    def test_get_value_for_double(self):
        parser = Parser(None)
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertEqual(1.0, dynamic_api.get_double('default.newVariant', 1.0, [1.0, 2.0, 3.0]))
        self.assertEqual(1.0, flag_repo.get_flag('default.newVariant').get_value())
        self.assertEqual(2.0, dynamic_api.get_double('default.newVariant', 2.0, [1.0, 2.0, 3.0]))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newVariant', 'ifThen(true, "2.0", "1.0")', False, ['default.newVariant'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual(2.0, dynamic_api.get_double('default.newVariant', 1.0, [1.0, 2.0, 3.0]))

    def test_get_default_code_value_for_double(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('abc')
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertEqual(1.0, dynamic_api.get_double('default.newVariant', 1.0, [1.0, 2.0, 3.0]))
        self.assertEqual(1.0, flag_repo.get_flag('default.newVariant').get_value())
        self.assertEqual(2.0, dynamic_api.get_double('default.newVariant', 2.0, [1.0, 2.0, 3.0]))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newVariant', 'ifThen(true, "2.0", "1.0")', False, ['default.newVariant'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual(0.0, dynamic_api.get_double('default.newVariant', 1.0, [1.0, 2.0, 3.0]))

    def test_get_default_code_value_for_int(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('abc')
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertEqual(1, dynamic_api.get_int('default.newVariant', 1, [1, 2, 3]))
        self.assertEqual(1, flag_repo.get_flag('default.newVariant').get_value())
        self.assertEqual(2, dynamic_api.get_int('default.newVariant', 2, [1, 2, 3]))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newVariant', 'ifThen(true, "2", "1")', False, ['default.newVariant'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual(0, dynamic_api.get_int('default.newVariant', 1, [1, 2, 3]))

    def test_throw_error_when_none_default_value(self):
        flag_repo = FlagRepository()
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        with self.assertRaises(TypeError):
            dynamic_api.get_int('default.newVariant', None, [1, 2, 3])

class EntitiesMockProvider:
    def create_flag(self, default_value):
        return Flag(default_value)

    def create_string(self, default_value, options):
        return RoxString(default_value, options)

    def create_double(self, default_value, options):
        return RoxDouble(default_value, options)

    def create_int(self, default_value, options):
        return RoxInt(default_value, options)
