"""
********************************************************************************
* Name: test_dask_scheduler
* Author: nswain, tran, teva
* Created On: October 15, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import unittest
from unittest import mock
from tethys_dask_scheduler.plugin import TethysSchedulerPlugin, dask_setup


class SchedulerPluginTest(unittest.TestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_init(self):
        mock_scheduler = mock.MagicMock()
        tds_plugin = TethysSchedulerPlugin(tethys_endpoint='http://localhost:8080', scheduler=mock_scheduler)

        # Check result
        self.assertEqual('http://localhost:8080', tds_plugin.tethys_endpoint)
        self.assertEqual(mock_scheduler, tds_plugin.scheduler)

    @mock.patch('tethys_dask_scheduler.plugin.AsyncHTTPClient')
    def test_transition(self, mock_async):
        endpoint = 'http://localhost:8080'
        mock_scheduler = mock.MagicMock()
        tds_plugin = TethysSchedulerPlugin(tethys_endpoint=endpoint, scheduler=mock_scheduler)
        mock_scheduler.get_metadata.return_value = True
        mock_http_client = mock.MagicMock()
        mock_async.return_value = mock_http_client

        job_key = 'sum-4a062-d246-11e8-9aec-e33e562837e2'
        start = 'start'
        finish = 'complete'

        # Call the method
        tds_plugin.transition(key=job_key, start=start, finish=finish)

        rts_call_args = mock_http_client.fetch.call_args_list
        check_str = '{}/update-dask-job-status/{}/?status={}-{}'.format(endpoint, job_key, start, finish)
        self.assertEqual(check_str, rts_call_args[0][0][0])

    @mock.patch('tethys_dask_scheduler.plugin.logger')
    def test_dask_setup_tethys_host_http(self, mock_logger):
        mock_scheduler = mock.MagicMock()
        tethys_host = 'http://127.0.0.1:8000'

        dask_setup.callback(mock_scheduler, tethys_host=tethys_host)

        # Test
        mock_logger.info.assert_called_with('Tethys Host at:     http://127.0.0.1:8000')
        mock_scheduler.add_plugin.assert_called()
        add_plugin_call = mock_scheduler.add_plugin.call_args_list[0]
        # instance of TethysSchedulerPlugin should have been arg passed to add_plugin
        tethys_plugin = add_plugin_call[0][0]
        self.assertIsInstance(tethys_plugin, TethysSchedulerPlugin)
        self.assertEqual(mock_scheduler, tethys_plugin.scheduler)
        self.assertEqual('http://127.0.0.1:8000', tethys_plugin.tethys_endpoint)

    @mock.patch('tethys_dask_scheduler.plugin.logger')
    def test_dask_setup_tethys_host_https(self, mock_logger):
        mock_scheduler = mock.MagicMock()
        tethys_host = 'https://127.0.0.1:8000'

        dask_setup.callback(mock_scheduler, tethys_host=tethys_host)

        # Test
        mock_logger.info.assert_called_with('Tethys Host at:    https://127.0.0.1:8000')
        mock_scheduler.add_plugin.assert_called()
        add_plugin_call = mock_scheduler.add_plugin.call_args_list[0]
        # instance of TethysSchedulerPlugin should have been arg passed to add_plugin
        tethys_plugin = add_plugin_call[0][0]
        self.assertIsInstance(tethys_plugin, TethysSchedulerPlugin)
        self.assertEqual(mock_scheduler, tethys_plugin.scheduler)
        self.assertEqual('https://127.0.0.1:8000', tethys_plugin.tethys_endpoint)

    @mock.patch('tethys_dask_scheduler.plugin.logger')
    def test_dask_setup_tethys_host_no_protocol(self, mock_logger):
        mock_scheduler = mock.MagicMock()
        tethys_host = '127.0.0.1:8000'

        dask_setup.callback(mock_scheduler, tethys_host=tethys_host)

        # Test
        mock_logger.info.assert_called_with('Tethys Host at:     http://127.0.0.1:8000')
        mock_scheduler.add_plugin.assert_called()
        add_plugin_call = mock_scheduler.add_plugin.call_args_list[0]
        # instance of TethysSchedulerPlugin should have been arg passed to add_plugin
        tethys_plugin = add_plugin_call[0][0]
        self.assertIsInstance(tethys_plugin, TethysSchedulerPlugin)
        self.assertEqual(mock_scheduler, tethys_plugin.scheduler)
        self.assertEqual('http://127.0.0.1:8000', tethys_plugin.tethys_endpoint)
