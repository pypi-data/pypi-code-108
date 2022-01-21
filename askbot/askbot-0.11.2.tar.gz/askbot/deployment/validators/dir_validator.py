"""Base class for the more specialized directory validators:
RootDirValidator, ProjDirValidator."""
import os
from django.core.exceptions import ValidationError

class DirValidator:
    """The base class for the directory validation.
    In the sub-class specify values of the option_name, user_prompt, default
    and implement the .clean() method
    """
    def __init__(self, console, parser):
        self.console = console
        self.options = parser.parse_args()
        self.parser = parser
        self.entered_by_hand = False
        self.option_name = None
        self.user_prompt = None
        self.default = ''


    def clean(self, raw_value):
        """Subclass must implement this method"""
        raise NotImplementedError


    def get_default_value(self):
        """Returns value accepted by default"""
        return self.default


    def get_raw_value(self):
        """Returns raw project name value.
        If value is default, will prompt for the keyboard input."""
        default = self.get_default_value()
        cli_value = getattr(self.options, self.option_name)
        if not cli_value:
            if not self.options.force and os.path.exists(default):
                user_input = self.console.simple_dialog(self.user_prompt, required=True)
            else:
                user_input = self.console.simple_dialog(self.user_prompt, default=default)

            self.entered_by_hand = True
            return user_input
        return cli_value


    def get_value(self):
        """Returns validater absolute directory path"""
        if not self.options.interactive:
            raw_cli_value = getattr(self.options, self.option_name)
            default = self.get_default_value()
            dir_path, error_message = self.clean(raw_cli_value or default)
            if error_message:
                if self.options.force:
                    return dir_path
                raise ValidationError(error_message)
            return dir_path

        while True:
            raw_dir_path = self.get_raw_value()
            dir_path, error_message = self.clean(raw_dir_path)

            # return a value or, print error and continue
            if error_message:
                if self.options.force:
                    return dir_path
                self.console.print_error(error_message)
            else:
                return dir_path
