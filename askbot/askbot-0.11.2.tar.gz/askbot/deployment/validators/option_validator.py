"""Validates any option, given the `validator` class, and other parameters
"""
from django.core.exceptions import ValidationError

class PermissiveValidator:
    """This validator allows any value"""
    #pylint: disable=too-few-public-methods
    def __call__(self, value):
        return

class OptionValidator:
    """The validator class.
    .get_value() method
    is the only one you need to use
    after the proper setup"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, console, parser, #pylint: disable=too-many-arguments
                 option_name=None,
                 default_value=None, required=False,
                 prompt=None, validator=None, cli_error_messages=None,
                 interactive_error_messages=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.option_name = option_name
        self.default_value = default_value
        self.required = required
        self.prompt = prompt
        self.validator = validator or PermissiveValidator
        self.cli_error_messages = cli_error_messages
        self.interactive_error_messages = interactive_error_messages

    def get_value(self):
        """Returns a valid value or raises an exception"""
        if self.options.interactive:
            # give a chance to to the cli value
            cli_value = getattr(self.options, self.option_name)
            if cli_value and self.validate_interactive(cli_value):
                return cli_value
            # otherwise read from the keyboard input
            return self.get_interactive_value()

        # in the non-interactive session - we only use the cli value
        return self.get_cli_value()

    def get_value_from_console(self):
        """Returns a value entered at the console"""
        default = self.default_value
        if default is not None:
            return self.console.simple_dialog(self.prompt, default=default)
        return self.console.simple_dialog(self.prompt, required=True)

    def get_interactive_value(self):
        """Returns validated value as entered by the user"""
        has_default = self.default_value is not None
        while True:
            value = self.get_value_from_console()
            if not value and not self.required and has_default:
                return self.default_value
            if self.validate_interactive(value):
                return value

    def validate_interactive(self, value):
        """Validates the value for the interactive session"""
        if not value:
            if self.required:
                raise ValidationError(self.cli_error_messages['missing'])
            if self.default_value is not None:
                return self.default_value
        try:
            self.validator()(value)
        except ValidationError:
            self.console.print_error(self.interactive_error_messages['invalid'])
            return False
        return True

    def get_cli_value(self):
        """Validates and returns value as entered via the CLI"""
        value = getattr(self.options, self.option_name)
        if not value:
            if self.required:
                raise ValidationError(self.cli_error_messages['missing'])
            if self.default_value is not None:
                return self.default_value

        try:
            self.validator()(value)
        except ValidationError:
            raise ValidationError(self.cli_error_messages['invalid'])
        return value
