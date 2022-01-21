"""Class that deploys the settings.py file where it belongs"""
import os
from askbot.deployment.deployers.file_deployer import FileDeployer
from askbot.deployment.deployers.settings_py_admins_snippet import SettingsPyAdminsSnippet
from askbot.deployment.deployers.settings_py_databases_snippet import SettingsPyDatabasesSnippet
from askbot.deployment.deployers.settings_py_email_snippet import SettingsPyEmailSnippet
from askbot.deployment.deployers.settings_py_caching_snippet import SettingsPyCachingSnippet
from askbot.deployment.deployers.settings_py_languages_snippet import SettingsPyLanguagesSnippet
from askbot.deployment.deployers.settings_py_logging_snippet import SettingsPyLoggingSnippet

class SettingsPy(FileDeployer): # pylint: disable=missing-class-docstring
    template_path = 'deployment/templates/settings_py.jinja2'

    def get_file_path(self):
        """Returns deployment path to the settings.py file"""
        return os.path.join(self.params['proj_dir'], 'settings.py')

    def get_template_parameters(self):
        """Returns parameters for the settings.py template"""
        return {
            'admins_settings': SettingsPyAdminsSnippet(self.params).render(),
            'allowed_host': self.params['domain_name'] or '*',
            'caching_settings': SettingsPyCachingSnippet(self.params).render(),
            'databases_settings': SettingsPyDatabasesSnippet(self.params).render(),
            'email_settings': SettingsPyEmailSnippet(self.params).render(),
            'extra_settings': self.params['extra_settings'],
            'language_settings': SettingsPyLanguagesSnippet(self.params).render(),
            'logging_settings': SettingsPyLoggingSnippet(self.params).render(),
            'media_root_dir': self.params['media_root_dir'],
            'secret_key': self.params['secret_key'],
            'static_root_dir': self.params['static_root_dir'],
            'timezone': self.params['timezone'],
        }
