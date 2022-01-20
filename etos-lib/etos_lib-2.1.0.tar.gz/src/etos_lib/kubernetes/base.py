# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library base kubernetes library."""
import os
from uuid import uuid4
import yaml
from kubernetes import client, config  # pylint:disable=no-name-in-module


class Kubernetes:
    """Base kubernetes library."""

    __batch = None
    __core = None
    __apps = None
    __extensions = None

    def __init__(
        self, namespace=os.getenv("ETOS_NAMESPACE"), context=None, in_cluster=True
    ):
        """Initialize kubernetes library and load kubernetes configuration.

        :param namespace: Which namespace to operate in.
        :type namespace: str
        :param context: From which Kubernetes context should we load config from.
                        This is only relevant when running locally (in_cluster=False).
        :type context: str
        :param in_cluster: Whether or not the kubernetes service is executing in a cluster.
                           Set to False when running locally, set to True when running in
                           kubernetes.
        :type in_cluster: bool
        """
        self.namespace = namespace
        self.context = context
        self.in_cluster = in_cluster
        self._load_config()

    def _load_config(self):
        """Load kubernetes configuration."""
        if self.in_cluster:
            config.load_incluster_config()
        else:
            config.load_kube_config(context=self.context)

    @staticmethod
    def load_yaml(data):
        """Load a YAML file.

        :param data: YAML data to load.
        :type data: str
        :return: Loaded yaml data.
        :rtype: :obj:`yaml`
        """
        return yaml.load(data, Loader=yaml.Loader)

    @staticmethod
    def uniqueify(name):
        """Make a name unique.

        :param name: Name to make unique.
        :type name: str
        :return: New, unique, name.
        :rtype: str
        """
        return f"{name}-{uuid4().hex[:10].upper()}"

    @property
    def apps_v1(self):
        """AppsV1Api for Kubernetes."""
        if self.__apps is None:
            self.__apps = client.AppsV1Api()
        return self.__apps

    @property
    def batch_v1(self):
        """BatchV1Api for Kubernetes."""
        if self.__batch is None:
            self.__batch = client.BatchV1Api()
        return self.__batch

    @property
    def extensions(self):
        """Create a ExtensionsV1beta1Api endpoint."""
        if self.__extensions is None:
            self.__extensions = client.ExtensionsV1beta1Api()
        return self.__extensions

    @property
    def core(self):
        """Create a CoreV1Api endpoint."""
        if self.__core is None:
            self.__core = client.CoreV1Api()
        return self.__core
