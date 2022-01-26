import os
import textwrap
from enum import Enum

import configparser

from seeq.base import system
from seeq.sdk.configuration import ClientConfiguration
from seeq.spy import _errors

file_config = None


class Options:
    _DEFAULT_SEARCH_PAGE_SIZE = 1000
    _DEFAULT_PULL_PAGE_SIZE = 1000000
    _DEFAULT_PUSH_PAGE_SIZE = 100000
    _DEFAULT_MAX_CONCURRENT_REQUESTS = 8
    _DEFAULT_CLEAR_CONTENT_CACHE_BEFORE_RENDER = False
    _DEFAULT_ALLOW_VERSION_MISMATCH = False
    _DEFAULT_FRIENDLY_EXCEPTIONS = _errors.is_datalab()

    def __init__(self, client_configuration: ClientConfiguration):
        self.client_configuration = client_configuration
        self.search_page_size = self._DEFAULT_SEARCH_PAGE_SIZE
        self.pull_page_size = self._DEFAULT_PULL_PAGE_SIZE
        self.push_page_size = self._DEFAULT_PUSH_PAGE_SIZE
        self.max_concurrent_requests = self._DEFAULT_MAX_CONCURRENT_REQUESTS
        self.clear_content_cache_before_render = self._DEFAULT_CLEAR_CONTENT_CACHE_BEFORE_RENDER
        self.allow_version_mismatch = self._DEFAULT_ALLOW_VERSION_MISMATCH
        try:
            self.friendly_exceptions = self._DEFAULT_FRIENDLY_EXCEPTIONS
        except RuntimeError:
            pass

    def __str__(self):
        return '\n'.join([f"{k}: {v}" for k, v in self.__dict__.items()])

    def __getstate__(self):
        # We can only pickle certain members. This has to mirror __setstate__().
        return (self.search_page_size,
                self.pull_page_size,
                self.push_page_size,
                self.max_concurrent_requests,
                self.clear_content_cache_before_render,
                self.allow_version_mismatch)

    def __setstate__(self, state):
        (self.search_page_size,
         self.pull_page_size,
         self.push_page_size,
         self.max_concurrent_requests,
         self.clear_content_cache_before_render,
         self.allow_version_mismatch) = state

    @property
    def friendly_exceptions(self):
        return self._friendly_exceptions

    @friendly_exceptions.setter
    def friendly_exceptions(self, value):
        if value:
            try:
                _errors.add_spy_exception_handler()
                self._friendly_exceptions = True
            except RuntimeError:
                self._friendly_exceptions = False
                raise

        else:
            _errors.remove_spy_exception_handler()
            self._friendly_exceptions = False

    @property
    def retry_timeout_in_seconds(self):
        return self.client_configuration.retry_timeout_in_seconds

    @retry_timeout_in_seconds.setter
    def retry_timeout_in_seconds(self, value):
        self.client_configuration.retry_timeout_in_seconds = value

    def print(self):
        print(str(self))

    def help(self):
        help_string = f"""\
            Assign a new value to the following variables if you would like to adjust them.

            E.g.:
               spy.options.concurrent_requests = 3

            Available Options
            -----------------

            spy.options.search_page_size (default: {self._DEFAULT_SEARCH_PAGE_SIZE})

                The number of items retrieved on each round-trip to the Seeq Server during
                a spy.search() call. If you have a fast system and fast connection, you can
                make this higher.

            spy.options.pull_page_size (default: {self._DEFAULT_PULL_PAGE_SIZE})

                The number of samples/capsules retrieved on each round-trip to the Seeq
                Server during a spy.pull() call. If you have a slow system or slow
                connection, you may wish to make this lower. It is not recommended to
                exceed 1000000.

            spy.options.push_page_size (default: {self._DEFAULT_PUSH_PAGE_SIZE})

                The number of samples/capsules uploaded during each round-trip to the Seeq
                Server during a spy.push() call. If you have a slow system or slow
                connection, you may wish to make this lower. It is not recommended to
                exceed 1000000.

            spy.options.max_concurrent_requests (default: {self._DEFAULT_MAX_CONCURRENT_REQUESTS})

                The maximum number of simultaneous requests made to the Seeq Server during
                spy.pull() and spy.push() calls. The higher the number, the more you can
                monopolize the Seeq Server. If you keep it low, then other users are less
                likely to be impacted by your activity.

            spy.options.retry_timeout_in_seconds (default: {ClientConfiguration.DEFAULT_RETRY_TIMEOUT_IN_SECONDS})

                The amount of time to spend retrying a failed Seeq Server API call in an
                attempt to overcome network flakiness.

            spy.options.clear_content_cache_before_render (default: {str(self._DEFAULT_CLEAR_CONTENT_CACHE_BEFORE_RENDER)})

                When using spy.workbooks.pull(include_rendered_content=True), always
                re-render the content even if it had been previously rendered and cached.

            spy.options.allow_version_mismatch (default: {self._DEFAULT_ALLOW_VERSION_MISMATCH})

                Allow a major version mismatch between SPy and Seeq Server. (Normally,
                a mismatch raises a RuntimeError.)

            spy.options.friendly_exceptions (default: True if running in Data Lab, otherwise False)

                If True, exceptions raised in a Jupyter notebook will be displayed in a
                friendlier format. Stack traces will not be shown by default for most
                errors; error messages will precede the stack trace; and internal SPy
                code will be omitted from the stack trace.
        """

        print(textwrap.dedent(help_string))


class Setting(Enum):
    CONFIG_FOLDER = {'env': 'SEEQ_SPY_CONFIG_FOLDER', 'ini': None}
    CONFIG_FILENAME = {'env': 'SEEQ_SPY_CONFIG_FILENAME', 'ini': None}
    SEEQ_URL = {'env': 'SEEQ_SERVER_URL', 'ini': 'seeq_server_url'}
    PRIVATE_URL = {'env': 'SEEQ_PRIVATE_URL', 'ini': None}
    SEEQ_CERT_PATH = {'env': 'SEEQ_CERT_PATH', 'ini': 'seeq_cert_path'}
    SEEQ_KEY_PATH = {'env': 'SEEQ_KEY_PATH', 'ini': 'seeq_key_path'}
    AGENT_KEY_PATH = {'env': 'AGENT_KEY_PATH', 'ini': 'agent_key_path'}
    SEEQ_PROJECT_UUID = {'env': 'SEEQ_PROJECT_UUID', 'ini': None}

    def get_env_name(self):
        return self.value['env']

    def get_ini_name(self):
        return self.value['ini']

    def get(self):
        setting = os.environ.get(self.get_env_name())
        if not setting and self.get_ini_name():
            # noinspection PyBroadException
            try:
                config = Setting.get_file_config()
                setting = config.get('spy', self.get_ini_name(), fallback=None)
            except BaseException:
                # This can happen on a machine where the home folder is not accessible, like on Spark / AWS Glue
                return None

        return setting

    def set(self, value):
        os.environ[self.get_env_name()] = value

    def unset(self):
        del os.environ[self.get_env_name()]

    @staticmethod
    def get_config_folder():
        """
        This is the config folder for the SPy library, which is where any additional configuration files for SPy must be
        stored. The default location is the same as the Seeq global folder.
        :return: Location of the config folder
        """
        config_folder = Setting.CONFIG_FOLDER.get()
        if not config_folder:
            if system.is_windows():
                config_folder = os.path.join(os.environ["ProgramData"], 'Seeq')
            else:
                config_folder = os.path.join(system.get_home_dir(), '.seeq')

        system.create_folder_if_necessary_with_correct_permissions(config_folder)

        return config_folder

    @staticmethod
    def set_config_folder(path):
        Setting.CONFIG_FOLDER.set(path)

    @staticmethod
    def get_config_filename():
        filename = Setting.CONFIG_FILENAME.get()
        return filename if filename else "spy.ini"

    @staticmethod
    def get_config_path():
        return os.path.join(Setting.get_config_folder(), Setting.get_config_filename())

    @staticmethod
    def get_seeq_url():
        url = Setting.SEEQ_URL.get()
        return url if url else 'http://localhost:34216'

    @staticmethod
    def set_seeq_url(url):
        Setting.SEEQ_URL.set(url)

    @staticmethod
    def unset_seeq_url():
        if Setting.SEEQ_URL.get() is not None:
            Setting.SEEQ_URL.unset()

    @staticmethod
    def get_private_url():
        url = Setting.PRIVATE_URL.get()
        return url if url else Setting.get_seeq_url()

    @staticmethod
    def set_private_url(url):
        Setting.PRIVATE_URL.set(url)

    @staticmethod
    def unset_private_url():
        if Setting.PRIVATE_URL.get() is not None:
            Setting.PRIVATE_URL.unset()

    @staticmethod
    def get_seeq_cert_path():
        path = Setting.SEEQ_CERT_PATH.get()
        if path:
            return path
        else:
            # noinspection PyBroadException
            try:
                return os.path.join(Setting.get_config_folder(), 'keys', 'seeq-cert.pem')
            except BaseException:
                # This can happen on a machine where the home folder is not accessible, like on Spark / AWS Glue
                return None

    @staticmethod
    def get_seeq_key_path():
        path = Setting.SEEQ_KEY_PATH.get()
        if path:
            return path
        else:
            # noinspection PyBroadException
            try:
                return os.path.join(Setting.get_config_folder(), 'keys', 'seeq-key.pem')
            except BaseException:
                # This can happen on a machine where the home folder is not accessible, like on Spark / AWS Glue
                return None

    @staticmethod
    def get_file_config():
        global file_config
        if not file_config:
            file_config = configparser.ConfigParser()
            file_config.read(Setting.get_config_path())
        return file_config


# For compatibility with older versions of Data Lab
def set_seeq_url(url):
    Setting.SEEQ_URL.set(url)


def get_data_lab_orchestrator_url():
    return f'{Setting.get_seeq_url()}/data-lab'


def get_data_lab_project_id():
    """
    Get Seeq ID assigned to this Data Lab Project

    Returns
    -------
    {str, None}
        The Seeq ID as a string, or None if no ID assigned
    """
    return Setting.SEEQ_PROJECT_UUID.get()


def get_data_lab_project_url():
    """
    Get Data Lab Project URL in form of
        ``{Seeq_Server_URL}/data-lab/{Data Lab Project ID}``

    Returns
    -------
    {str}
        The Data Lab Project URL as a string
    """
    return f'{get_data_lab_orchestrator_url()}/{get_data_lab_project_id()}'
