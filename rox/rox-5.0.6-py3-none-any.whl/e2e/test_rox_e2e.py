import os
import unittest
from concurrent.futures import TimeoutError

from e2e.container import Container
from e2e.custom_props import create_custom_props
from e2e.test_variables import TestVars
from rox.core.configuration.configuration_fetched_invoker import FetcherStatus
from rox.server.rox_server import Rox
from rox.server.rox_options import RoxOptions


class Logger:
    def debug(self, message, ex=None):
        print('debug', message)

    def error(self, message, ex=None):
        print('error', message)

    def warn(self, message, ex=None):
        print('warn', message)


class E2ETests(unittest.TestCase):
    cancel_periodic_event = None

    @classmethod
    def setUpClass(cls):
        os.environ['ROLLOUT_MODE'] = 'QA'

        def configuration_fetched_handler(e):
            if e is not None and e.fetcher_status == FetcherStatus.APPLIED_FROM_NETWORK:
                TestVars.configuration_fetched_count += 1

        def impression_handler(e):
            if e is not None and e.reporting_value is not None:
                if e.reporting_value.name == 'flag_for_impression':
                    TestVars.is_impression_raised = True
            TestVars.impression_returned_args = e

        option = RoxOptions(
            configuration_fetched_handler=configuration_fetched_handler,
            impression_handler=impression_handler,
            dev_mode_key='9645e58956e6d44b453789c8',
            logger=Logger()
        )

        Rox.register(Container.instance)
        create_custom_props()

        task = Rox.setup('5b74327d44338c07e9c0f4c7', option)
        cls.cancel_periodic_event = task.result()

    @classmethod
    def tearDownClass(cls):
        if cls.cancel_periodic_event is not None:
            cls.cancel_periodic_event.set()

    def test_simple_flag(self):
        self.assertTrue(Container.instance.simple_flag.is_enabled())

    def test_simple_flag_overwritten(self):
        self.assertFalse(Container.instance.simple_flag_overwritten.is_enabled())

    def test_variant(self):
        self.assertEqual('red', Container.instance.variant.get_value())

    def test_size_variant(self):
        self.assertEqual(14, Container.instance.size_variant.get_value())

    def test_specific_size_variant(self):
        self.assertEqual(14.4, Container.instance.specific_size_variant.get_value())

    def test_variant_overwritten(self):
        self.assertEqual('green', Container.instance.variant_overwritten.get_value())

    def test_size_variant_overwritten(self):
        self.assertEqual(40, Container.instance.size_variant_overwritten.get_value())

    def test_specific_size_variant_overwritten(self):
        self.assertEqual(40.7, Container.instance.specific_size_variant_overwritten.get_value())

    def test_all_custom_properties(self):
        self.assertTrue(Container.instance.flag_custom_properties.is_enabled())

        self.assertTrue(TestVars.is_computed_boolean_prop_called)
        self.assertTrue(TestVars.is_computed_float_prop_called)
        self.assertTrue(TestVars.is_computed_int_prop_called)
        self.assertTrue(TestVars.is_computed_semver_prop_called)
        self.assertTrue(TestVars.is_computed_string_prop_called)

    def test_fetch_within_timeout(self):
        number_of_config_fetches = TestVars.configuration_fetched_count
        timeout = 5
        task = Rox.fetch()
        try:
            task.result(timeout)
        except TimeoutError:
            self.fail()

        self.assertTrue(number_of_config_fetches < TestVars.configuration_fetched_count)

    def test_variant_with_context(self):
        some_positive_context = {'isDuckAndCover': True}
        some_negative_context = {'isDuckAndCover': False}

        self.assertEqual('red', Container.instance.variant_with_context.get_value())

        self.assertEqual('blue', Container.instance.variant_with_context.get_value(some_positive_context))
        self.assertEqual('red', Container.instance.variant_with_context.get_value(some_negative_context))

    def test_target_groups_all_any_none(self):
        TestVars.target_group1 = True
        TestVars.target_group2 = True

        self.assertTrue(Container.instance.flag_target_groups_all.is_enabled())
        self.assertTrue(Container.instance.flag_target_groups_any.is_enabled())
        self.assertFalse(Container.instance.flag_target_groups_none.is_enabled())

        TestVars.target_group1 = False
        self.assertFalse(Container.instance.flag_target_groups_all.is_enabled())
        self.assertTrue(Container.instance.flag_target_groups_any.is_enabled())
        self.assertFalse(Container.instance.flag_target_groups_none.is_enabled())

        TestVars.target_group2 = False
        self.assertFalse(Container.instance.flag_target_groups_all.is_enabled())
        self.assertFalse(Container.instance.flag_target_groups_any.is_enabled())
        self.assertTrue(Container.instance.flag_target_groups_none.is_enabled())

    def test_impression_handler(self):
        Container.instance.flag_for_impression.is_enabled()
        self.assertTrue(TestVars.is_impression_raised)
        TestVars.is_impression_raised = False

        context = {'var': 'val'}
        flag_impression_value = Container.instance.flag_for_impression_with_experiment_and_context.is_enabled(context)
        self.assertIsNotNone(TestVars.impression_returned_args)
        self.assertIsNotNone(TestVars.impression_returned_args.reporting_value)
        self.assertEqual('true', TestVars.impression_returned_args.reporting_value.value)
        self.assertTrue(flag_impression_value)
        self.assertEqual('flag_for_impression_with_experiment_and_context', TestVars.impression_returned_args.reporting_value.name)

        self.assertIsNotNone(TestVars.impression_returned_args)
        self.assertIsNotNone(TestVars.impression_returned_args.experiment)
        self.assertEqual('5b79155c90e2a5058399b7b4', TestVars.impression_returned_args.experiment.identifier)
        self.assertEqual('flag for impression with experiment and context', TestVars.impression_returned_args.experiment.name)

        self.assertEqual('val', TestVars.impression_returned_args.context['var'])

    def test_flag_dependency(self):
        TestVars.is_prop_for_target_group_for_dependency = True
        self.assertTrue(Container.instance.flag_for_dependency.is_enabled())
        self.assertFalse(Container.instance.flag_dependent.is_enabled())

        TestVars.is_prop_for_target_group_for_dependency = False
        self.assertTrue(Container.instance.flag_dependent.is_enabled())
        self.assertFalse(Container.instance.flag_for_dependency.is_enabled())

    def test_variant_dependency_with_context(self):
        some_positive_context = {'isDuckAndCover': True}
        some_negative_context = {'isDuckAndCover': False}

        self.assertEqual('White', Container.instance.flag_color_dependent_with_context.get_value())
        self.assertEqual('White', Container.instance.flag_color_dependent_with_context.get_value(some_negative_context))
        self.assertEqual('Yellow', Container.instance.flag_color_dependent_with_context.get_value(some_positive_context))