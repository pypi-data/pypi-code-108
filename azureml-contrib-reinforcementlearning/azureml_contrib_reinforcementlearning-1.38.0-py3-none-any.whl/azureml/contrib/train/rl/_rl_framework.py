# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Reinforcement Learning framework base, and supported framework classes"""

from os import path, listdir
from abc import ABC
from azureml.exceptions import UserErrorException


class RLFramework(ABC):
    _version = None
    _name = None
    _args = None

    def __init__(self, version=None, framework_arguments=None, *args, **kwargs):
        super().__init__()
        self.version = version if version else self.__class__.default_framework_version()
        self.framework_arguments = framework_arguments

    @classmethod
    def default_framework_version(cls):
        pass

    @classmethod
    def supported_versions(cls):
        pass

    @classmethod
    def is_supported_version(cls, version):
        if version in cls.supported_versions():
            return True
        else:
            return False

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        if self.__class__.is_supported_version(version):
            self._version = version
        else:
            raise UserErrorException(
                "Version {0} of Framework {1} is not currently supported, supported versions are: {2}"
                .format(version, self.name, self.__class__.supported_versions()))

    @property
    def framework_arguments(self):
        return self._args

    @framework_arguments.setter
    def framework_arguments(self, arguments):
        self._args = arguments

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __repr__(self):
        return '{}-{}'.format(self.name, self.version).lower()


class Ray(RLFramework):
    """Defines the version and arguments for the Ray framework.

    For more information about Ray, see https://github.com/ray-project/ray.

    :param version: The version of the Ray framework to use. If not specified, Ray.default_framework_version is used.
    :type version: str
    :param framework_arguments: Additional arguments passed to the ray start command when starting the Ray cluster.
        For example, you can set the redis memory size by specifying ['--redis-max-memory=100000000'].
        Note: these arguments are only applied when starting the head node and are not specified for worker nodes.
    :type framework_arguments: list
    """

    def __init__(self, version=None, framework_arguments=None, *args, **kwargs):
        """Initializes the version and arguments for the Ray framework.

        :param version: The version of the Ray framework to use. If not specified, Ray.default_framework_version
            is used.
        :type version: str
        :param framework_arguments: Additional arguments passed to the ray start command when starting the Ray cluster.
            For example, you can set the redis memory size by specifying ['--redis-max-memory=100000000'].
            Note: these arguments are only applied when starting the head node and are not specified for worker nodes.
        :type framework_arguments: list
        """
        self.name = "Ray"
        super().__init__(version, framework_arguments, *args, **kwargs)

    @classmethod
    def default_framework_version(cls):
        """The version of the Ray framework to use if one is explicitly specified.

        :return: The version.
        :rtype: str
        """
        return "0.8.0"

    @classmethod
    def supported_versions(cls):
        """The list of supported Ray versions.

        :return: The list of versions.
        :rtype: list
        """
        framework_dir = path.join(path.dirname(__file__), "scenarios")
        dir_list = listdir(framework_dir)
        supported_versions = set([])

        for scenario_file in dir_list:
            if scenario_file.startswith(cls.__name__.lower()):
                version = scenario_file.split('-')[1]
                supported_versions.add(version)

        return sorted(list(supported_versions))
