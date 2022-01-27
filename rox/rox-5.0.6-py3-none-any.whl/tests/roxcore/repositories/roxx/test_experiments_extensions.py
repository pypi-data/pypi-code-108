import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.entities.flag import Flag
from rox.core.entities.flag_setter import FlagSetter
from rox.core.entities.rox_string import RoxString
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.repositories.custom_property_repository import CustomPropertyRepository
from rox.core.repositories.experiment_repository import ExperimentRepository
from rox.core.repositories.flag_repository import FlagRepository
from rox.core.repositories.roxx.experiments_extensions import ExperimentsExtensions, get_bucket
from rox.core.repositories.roxx.properties_extensions import PropertiesExtensions
from rox.core.repositories.target_group_repository import TargetGroupRepository
from rox.core.roxx.parser import Parser

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class ExperimentsExtensionsTests(unittest.TestCase):
    def test_custom_property_with_simple_value(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, None, None)
        experiments_extensions.extend()

        self.assertEqual(False, parser.evaluate_expression('isInTargetGroup("targetGroup1")').value)

    def test_is_in_percentage_range(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, None, None)
        experiments_extensions.extend()

        self.assertEqual(True, parser.evaluate_expression('isInPercentageRange(0, 0.5, "device2.seed2")').value)

    def test_not_is_in_percentage_range(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, None, None)
        experiments_extensions.extend()

        self.assertEqual(False, parser.evaluate_expression('isInPercentageRange(0.5, 1, "device2.seed2")').value)

    def test_get_bucket(self):
        result = get_bucket('device2.seed2')

        self.assertEqual(0.18721251450181298, result)

    def test_flag_value_no_flag_no_experiment(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        self.assertEqual('false', parser.evaluate_expression('flagValue("f1")').value)

    def test_flag_value_no_flag_evaluate_experiment(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        experiments = [ExperimentModel('id', 'name', '"op2"', False, ['f1'], set(), 'stam')]
        experiment_repository.set_experiments(experiments)

        self.assertEqual('op2', parser.evaluate_expression('flagValue("f1")').value)

    def test_flag_value_flag_evaluation_default(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        rox_string = RoxString('op1', ['op2'])
        flag_repository.add_flag(rox_string, 'f1')

        self.assertEqual('op1', parser.evaluate_expression('flagValue("f1")').value)

    def test_flag_dependency_value(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        f = Flag()
        flag_repository.add_flag(f, 'f1')

        rox_string = RoxString('blue', ['red', 'green'])
        flag_repository.add_flag(rox_string, 'v1')
        rox_string.condition = 'ifThen(eq("true", flagValue("f1")), "red", "green")'
        rox_string.parser = parser

        self.assertEqual('green', rox_string.get_value())

    def test_flag_dependency_impression_handler(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()
        internal_flags = Mock()
        ii = ImpressionInvoker(internal_flags, None, None, None, False, Mock())
        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        f = Flag()
        flag_repository.add_flag(f, 'f1')
        f.impression_invoker = ii

        rox_string = RoxString('blue', ['red', 'green'])
        flag_repository.add_flag(rox_string, 'v1')
        rox_string.condition = 'ifThen(eq("true", flagValue("f1")), "red", "green")'
        rox_string.parser = parser
        rox_string.impression_invoker = ii

        impression_list = []

        def on_impression(args):
            impression_list.append(args)

        ii.register_impression_handler(on_impression)

        self.assertEqual('green', rox_string.get_value())

        self.assertEqual(2, len(impression_list))

        self.assertEqual('f1', impression_list[0].reporting_value.name)
        self.assertEqual('false', impression_list[0].reporting_value.value)

        self.assertEqual('v1', impression_list[1].reporting_value.name)
        self.assertEqual('green', impression_list[1].reporting_value.value)

    def test_flag_dependency_2_levels_bottom_not_exists(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        f = Flag()
        flag_repository.add_flag(f, 'f1')
        f.parser = parser
        f.condition = 'flagValue("someFlag")'

        rox_string = RoxString('blue', ['red', 'green'])
        flag_repository.add_flag(rox_string, 'v1')
        rox_string.condition = 'ifThen(eq("true", flagValue("f1")), "red", "green")'
        rox_string.parser = parser

        self.assertEqual('green', rox_string.get_value())

    def test_flag_dependency_unexisting_flag_but_existing_experiment(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiment_models = [
            ExperimentModel('exp1id', 'exp1name', 'ifThen(true, "true", "false")', False, ['someFlag'], set(), 'stam'),
            ExperimentModel('exp2id', 'exp2name', 'ifThen(eq("true", flagValue("someFlag")), "blue", "green")', False,
                            ['colorVar'], set(), 'stam')
        ]
        flag_setter = FlagSetter(flag_repository, parser, experiment_repository, None)
        experiment_repository.set_experiments(experiment_models)
        flag_setter.set_experiments()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        color_var = RoxString('red', ['red', 'green', 'blue'])
        color_var.parser = parser
        flag_repository.add_flag(color_var, 'colorVar')

        self.assertEqual('blue', color_var.get_value())

    def test_flag_dependency_unexisting_flag_and_experiment_undefined(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        experiment_models = [
            ExperimentModel('exp1id', 'exp1name', 'undefined', False, ['someFlag'], set(), 'stam'),
            ExperimentModel('exp2id', 'exp2name', 'ifThen(eq("true", flagValue("someFlag")), "blue", "green")', False,
                            ['colorVar'], set(), 'stam')
        ]
        flag_setter = FlagSetter(flag_repository, parser, experiment_repository, None)
        experiment_repository.set_experiments(experiment_models)
        flag_setter.set_experiments()

        experiments_extensions = ExperimentsExtensions(parser, target_groups_repository, flag_repository,
                                                       experiment_repository)
        experiments_extensions.extend()

        color_var = RoxString('red', ['red', 'green', 'blue'])
        color_var.parser = parser
        flag_repository.add_flag(color_var, 'colorVar')

        self.assertEqual('green', color_var.get_value())

    def test_flag_dependency_with_context(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        property_repository = CustomPropertyRepository()
        PropertiesExtensions(parser, property_repository).extend()
        ExperimentsExtensions(parser, target_groups_repository, flag_repository, experiment_repository).extend()

        property_repository.add_custom_property(CustomProperty('prop', CustomPropertyType.BOOL,
                                                               lambda context: context['isPropOn']))

        flag1 = Flag()
        flag1.condition = 'property("prop")'
        flag1.parser = parser
        flag_repository.add_flag(flag1, 'flag1')

        flag2 = Flag()
        flag2.condition = 'flagValue("flag1")'
        flag2.parser = parser
        flag_repository.add_flag(flag2, 'flag2')

        context = {'isPropOn': True}

        self.assertEqual('true', flag2.get_value(context))

    def test_flag_dependency_with_context_used_on_experiment_with_no_flag(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        property_repository = CustomPropertyRepository()
        PropertiesExtensions(parser, property_repository).extend()
        ExperimentsExtensions(parser, target_groups_repository, flag_repository, experiment_repository).extend()

        property_repository.add_custom_property(CustomProperty('prop', CustomPropertyType.BOOL,
                                                               lambda context: context['isPropOn']))

        flag3 = Flag()
        flag3.condition = 'flagValue("flag2")'
        flag3.parser = parser
        flag_repository.add_flag(flag3, 'flag3')

        experiment_models = [ExperimentModel('exp1id', 'exp1name', 'property("prop")', False, ['flag2'], set(), 'stam')]
        experiment_repository.set_experiments(experiment_models)

        context = {'isPropOn': True}

        self.assertEqual('true', flag3.get_value(context))

    def test_flag_dependency_with_context_2_level_mid_level_no_flag_eval_experiment(self):
        parser = Parser(None)
        target_groups_repository = TargetGroupRepository()
        experiment_repository = ExperimentRepository()
        flag_repository = FlagRepository()

        property_repository = CustomPropertyRepository()
        PropertiesExtensions(parser, property_repository).extend()
        ExperimentsExtensions(parser, target_groups_repository, flag_repository, experiment_repository).extend()

        property_repository.add_custom_property(CustomProperty('prop', CustomPropertyType.BOOL,
                                                               lambda context: context['isPropOn']))

        flag1 = Flag()
        flag1.condition = 'property("prop")'
        flag1.parser = parser
        flag_repository.add_flag(flag1, 'flag1')

        flag3 = Flag()
        flag3.condition = 'flagValue("flag2")'
        flag3.parser = parser
        flag_repository.add_flag(flag3, 'flag3')

        experiment_models = [ExperimentModel('exp1id', 'exp1name', 'flagValue("flag1")', False, ['flag2'], set(), 'stam')]
        experiment_repository.set_experiments(experiment_models)

        context = {'isPropOn': True}

        self.assertEqual('true', flag3.get_value(context))
