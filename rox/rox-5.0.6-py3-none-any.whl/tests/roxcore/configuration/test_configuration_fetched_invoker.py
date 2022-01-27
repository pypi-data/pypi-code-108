import unittest
from datetime import datetime

from rox.core.configuration.configuration_fetched_invoker import ConfigurationFetchedInvoker, FetcherError, FetcherStatus, ConfigurationFetchedArgs


class ConfigurationFetchedInvokerTests(unittest.TestCase):
    def test_configuration_invoker_with_no_subscriber_no_exception(self):
        configuration_fetched_invoker = ConfigurationFetchedInvoker(None)
        configuration_fetched_invoker.invoke_error(FetcherError.UNKNOWN)

        configuration_fetched_invoker = ConfigurationFetchedInvoker(None)
        configuration_fetched_invoker.invoke(FetcherStatus.APPLIED_FROM_EMBEDDED, datetime.now(), True)

    def test_configuration_fetched_args_constructor(self):
        status = FetcherStatus.APPLIED_FROM_EMBEDDED
        time = datetime.now()
        has_changes = True

        conf_fetched_args = ConfigurationFetchedArgs(fetcher_status=status, creation_date=time, has_changes=has_changes)

        self.assertEqual(status, conf_fetched_args.fetcher_status)
        self.assertEqual(time, conf_fetched_args.creation_date)
        self.assertEqual(has_changes, conf_fetched_args.has_changes)
        self.assertEqual(FetcherError.NO_ERROR, conf_fetched_args.error_details)

        error = FetcherError.SIGNATURE_VERIFICATION_ERROR
        conf_fetched_args = ConfigurationFetchedArgs(error_details=error)

        self.assertEqual(FetcherStatus.ERROR_FETCHED_FAILED, conf_fetched_args.fetcher_status)
        self.assertEqual(None, conf_fetched_args.creation_date)
        self.assertEqual(False, conf_fetched_args.has_changes)
        self.assertEqual(error, conf_fetched_args.error_details)

    def test_configuration_invoker_invoke_with_error(self):
        is_configuration_handler_invoker_raised = {'raised': False}  # Workaround for Python 2 (Python 3 could use nonlocal keyword below)

        def on_configuration_fetched(e):
            self.assertEqual(FetcherStatus.ERROR_FETCHED_FAILED, e.fetcher_status)
            self.assertEqual(None, e.creation_date)
            self.assertEqual(False, e.has_changes)
            self.assertEqual(FetcherError.UNKNOWN, e.error_details)

            is_configuration_handler_invoker_raised['raised'] = True

        configuration_fetched_invoker = ConfigurationFetchedInvoker(None)
        configuration_fetched_invoker.register_configuration_fetched_handler(on_configuration_fetched)
        configuration_fetched_invoker.invoke_error(FetcherError.UNKNOWN)

        self.assertTrue(is_configuration_handler_invoker_raised['raised'])

    def test_configuration_invoker_invoke_ok(self):
        is_configuration_handler_invoker_raised = {'raised': False}  # Workaround for Python 2 (Python 3 could use nonlocal keyword below)

        now = datetime.now()
        status = FetcherStatus.APPLIED_FROM_NETWORK
        has_changes = True

        def on_configuration_fetched(e):
            self.assertEqual(status, e.fetcher_status)
            self.assertEqual(now, e.creation_date)
            self.assertEqual(has_changes, e.has_changes)
            self.assertEqual(FetcherError.NO_ERROR, e.error_details)

            is_configuration_handler_invoker_raised['raised'] = True

        configuration_fetched_invoker = ConfigurationFetchedInvoker(None)
        configuration_fetched_invoker.register_configuration_fetched_handler(on_configuration_fetched)
        configuration_fetched_invoker.invoke(status, now, has_changes)

        self.assertTrue(is_configuration_handler_invoker_raised['raised'])
