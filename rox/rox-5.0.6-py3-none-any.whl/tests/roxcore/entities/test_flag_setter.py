import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.entities.flag import Flag
from rox.core.entities.flag_setter import FlagSetter
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.repositories.experiment_repository import ExperimentRepository
from rox.core.repositories.flag_repository import FlagRepository

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class FlagSetterTests(unittest.TestCase):
    def test_will_set_flag_data(self):
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        parser = Mock()
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, None)

        flag_repo.add_flag(Flag(), 'f1')
        exp_repo.set_experiments([ExperimentModel('33', '1', '1', False, ['f1'], set(), 'stam')])

        flag_setter = FlagSetter(flag_repo, parser, exp_repo, impression_invoker)
        flag_setter.set_experiments()

        self.assertEqual('1', flag_repo.get_flag('f1').condition)
        self.assertEqual(parser, flag_repo.get_flag('f1').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f1').impression_invoker)
        self.assertEqual('33', flag_repo.get_flag('f1').experiment.id)

    def test_will_not_set_for_other_flag(self):
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        parser = Mock()
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, None)

        flag_repo.add_flag(Flag(), 'f1')
        flag_repo.add_flag(Flag(), 'f2')
        exp_repo.set_experiments([ExperimentModel('1', '1', '1', False, ['f1'], set(), 'stam')])

        flag_setter = FlagSetter(flag_repo, parser, exp_repo, impression_invoker)
        flag_setter.set_experiments()

        self.assertEqual('', flag_repo.get_flag('f2').condition)
        self.assertEqual(parser, flag_repo.get_flag('f2').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f2').impression_invoker)
        self.assertIsNone(flag_repo.get_flag('f2').experiment)

    def test_will_set_flag_without_experiment_and_then_add_experiment(self):
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        parser = Mock()
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, None)

        flag_setter = FlagSetter(flag_repo, parser, exp_repo, impression_invoker)
        flag_repo.add_flag(Flag(), 'f2')

        flag_setter.set_experiments()

        self.assertEqual('', flag_repo.get_flag('f2').condition)
        self.assertEqual(parser, flag_repo.get_flag('f2').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f2').impression_invoker)
        self.assertIsNone(flag_repo.get_flag('f2').experiment)

        exp_repo.set_experiments([ExperimentModel('id1', '1', 'con', False, ['f2'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual('con', flag_repo.get_flag('f2').condition)
        self.assertEqual(parser, flag_repo.get_flag('f2').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f2').impression_invoker)
        self.assertEqual('id1', flag_repo.get_flag('f2').experiment.id)

    def test_will_set_experiment_for_flag_and_will_remove_it(self):
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        parser = Mock()
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, None)

        flag_setter = FlagSetter(flag_repo, parser, exp_repo, impression_invoker)
        flag_repo.add_flag(Flag(), 'f2')

        exp_repo.set_experiments([ExperimentModel('id1', '1', 'con1', False, ['f2'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual('con1', flag_repo.get_flag('f2').condition)
        self.assertEqual(parser, flag_repo.get_flag('f2').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f2').impression_invoker)
        self.assertEqual('id1', flag_repo.get_flag('f2').experiment.id)

        exp_repo.set_experiments([])
        flag_setter.set_experiments()

        self.assertEqual('', flag_repo.get_flag('f2').condition)
        self.assertEqual(parser, flag_repo.get_flag('f2').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f2').impression_invoker)
        self.assertIsNone(flag_repo.get_flag('f2').experiment)

    def test_will_set_data_for_added_flag(self):
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        parser = Mock()
        internal_flags = Mock()
        impression_invoker = ImpressionInvoker(internal_flags, None, None, None, False, None)

        exp_repo.set_experiments([ExperimentModel('1', '1', '1', False, ['f1'], set(), 'stam')])

        flag_setter = FlagSetter(flag_repo, parser, exp_repo, impression_invoker)
        flag_setter.set_experiments()

        flag_repo.add_flag(Flag(), 'f1')
        flag_repo.add_flag(Flag(), 'f2')

        self.assertEqual('1', flag_repo.get_flag('f1').condition)
        self.assertEqual('', flag_repo.get_flag('f2').condition)
        self.assertEqual(parser, flag_repo.get_flag('f1').parser)
        self.assertEqual(parser, flag_repo.get_flag('f2').parser)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f1').impression_invoker)
        self.assertEqual(impression_invoker, flag_repo.get_flag('f2').impression_invoker)
        self.assertEqual('1', flag_repo.get_flag('f1').experiment.id)
        self.assertIsNone(flag_repo.get_flag('f2').experiment)
