"""Validator for the directory parameters and
the setup procedure parameters"""
import os.path
from askbot.deployment import const
from askbot.deployment.validators.proj_dir_validator import ProjDirValidator
from askbot.deployment.validators.root_dir_validator import RootDirValidator
from askbot.deployment.validators.option_validator import OptionValidator
from askbot.deployment.utils import LogFilePathValidator
from askbot.utils.console import bold

class SetupParamsValidator:
    #pylint: disable=missing-class-docstring

    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params


    def get_params(self):
        """Returns setup parameters"""
        root_dir = RootDirValidator(self.console, self.parser).get_value()
        return {
            'force': self.options.force,
            'interactive': self.options.interactive,
            'root_dir': root_dir,
            'proj_dir': ProjDirValidator(self.console, self.parser, root_dir).get_value(),
            'media_root_dir': self.get_valid_dir(root_dir, const.DEFAULT_MEDIA_ROOT_SUBDIR),
            'static_root_dir': self.get_valid_dir(root_dir, const.DEFAULT_STATIC_ROOT_SUBDIR),
            'log_file_path': self.get_log_file_path(root_dir),
            'logging_settings': self.options.logging_settings,
        }


    def get_valid_dir(self, root_dir, default_subdir):
        """Returns valid value for the `MEDIA_ROOT` setting."""
        raw_value = self.options.media_root
        # if missing - return default
        if not raw_value:
            return os.path.join(root_dir, default_subdir)

        return os.path.abspath(raw_value)


    def get_log_file_path(self, root_dir):
        """Returns valid log file path
        Relative path is interpreted as relative to the ${root_dir}
        Absolute path will be accepted as is.
        """
        if self.options.logging_settings:
            return None

        raw_path = self.options.log_file_path
        if os.path.isabs(raw_path):
            return raw_path

        prompt = 'Enter the ' + bold('path to the log file')
        default_value = self.parser.get_default('log_file_path')

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='log_file_path',
                                    default_value=default_value,
                                    prompt=prompt,
                                    validator=LogFilePathValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --log-file-path is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Path is invalid'})
        value = validator.get_value()
        if os.path.isabs(value):
            return value
        return os.path.join(root_dir, value)
