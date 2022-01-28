from __future__ import print_function

import unittest
import os
import signal
import subprocess

from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook
from typing import Any, Dict


class BadookTestsHook(BaseHook):
    """
    a hook to run badook tests using the badook tests SDK.

    :param target_directory: The directory containing the test project, passed as the `-d` argument to the `bdk` command
    :type target_directory: str
    :param data_cluster_url: The base URL fro the badook runtime cluster
    :type data_cluster_url: str
    :param management_cluster_url: The base URL fro the badook management instance
    :type management_cluster_url: str
    :param client_id: The environments client_id
    :type client_id: str
    :param client_secret: The environments client_secret
    :type client_secret: str
    """

    def __init__(self,
                 target_directory: str = None,
                 conn_id: str = None,
                 data_cluster_url: str = None,
                 management_cluster_url: str = None,
                 client_id: str = None,
                 client_secret: str = None):
        if conn_id:
            conn = self.get_connection(conn_id)
            self.data_cluster_url = conn.data_cluster_url
            self.management_cluster_url = conn.management_cluster_url
            self.client_id = conn.client_id
            self.client_secret = conn.client_secret
        else:
            self.data_cluster_url = data_cluster_url
            self.management_cluster_url = management_cluster_url
            self.client_id = client_id
            self.client_secret = client_secret
        self.target_directory = target_directory

    @staticmethod
    def get_connection_form_widgets() -> Dict[str, Any]:
        """Returns connection widgets to add to connection form"""
        from flask_appbuilder.fieldwidgets import BS3PasswordFieldWidget, BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import PasswordField, StringField

        return {
            "client_id": PasswordField(
                lazy_gettext('badook cluster client_id'), widget=BS3PasswordFieldWidget()
            ),
            "client_secret": PasswordField(
                lazy_gettext('badook cluster client_secret'), widget=BS3PasswordFieldWidget()
            ),
            "data_cluster_url": StringField(
                lazy_gettext('data cluster base URL'), widget=BS3TextFieldWidget()
            ),
            "management_cluster_url": PasswordField(
                lazy_gettext('badook cloud environment URL'), widget=BS3PasswordFieldWidget()
            ),
        }

    def run(self):
        """
        Run tests using the bdk cli
        """

        from badook_tests.config import set_config_from_settings, Settings
        from badook_tests import BadookBaseTestResult, BadookTestRunnerError

        config = Settings(
            data_cluster_url=self.data_cluster_url,
            management_cluster_url=self.management_cluster_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            config_file_path=None)
        set_config_from_settings(config)

        try:
            suit = unittest.defaultTestLoader.discover(self.target_directory)
            unittest.TextTestRunner(resultclass=BadookBaseTestResult).run(suit)
        except BadookTestRunnerError as e:
            raise AirflowException(e.msg)
