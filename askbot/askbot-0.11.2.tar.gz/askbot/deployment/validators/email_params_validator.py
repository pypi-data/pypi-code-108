"""Validates email setup parameters"""
from django.core.validators import EmailValidator
from askbot.deployment.validators.option_validator import OptionValidator
from askbot.deployment.utils import DomainNameValidator, PortNumberValidator
from askbot.utils.console import bold

class EmailParamsValidator: #pylint: disable=missing-class-docstring
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns valid email setting values"""
        default_from_email = self.get_default_from_email()
        return {'default_from_email': default_from_email,
                'server_email': self.get_server_email(default_from_email),
                'email_backend': self.options.email_backend,
                'email_subject_prefix': self.options.email_subject_prefix,
                'email_host_user': self.options.email_host_user,
                'email_host_password': self.options.email_host_password,
                'email_host': self.get_email_host(),
                'email_port': self.get_email_port(),
                'email_use_tls': self.options.email_use_tls}

    def get_default_from_email(self):
        """Returns DEFAULT_FROM_EMAIL email"""
        if self.options.email_settings:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    required=False,
                                    default_value=self.prev_params['admin_email'],
                                    option_name='default_from_email',
                                    prompt='Enter the ' + bold('default from email'),
                                    validator=EmailValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --default-from-email is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Invalid email address'})
        return validator.get_value()

    def get_server_email(self, default_value):
        """Returns server email"""
        if self.options.email_settings:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    required=False,
                                    default_value=default_value,
                                    option_name='server_email',
                                    prompt='Enter the ' + bold('server email'),
                                    validator=EmailValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --server-email is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Invalid email address'})
        return validator.get_value()

    def get_email_host(self):
        """Returns host name of the email server"""
        if self.options.email_settings:
            return ''

        if self.options.interactive and not self.options.email_host:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='email_host',
                                    default_value='',
                                    required=False,
                                    prompt='Enter the ' + bold('mail server host name'),
                                    validator=DomainNameValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --email-host is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Host name is invalid'})
        return validator.get_value()

    def get_email_port(self):
        """Returns the mail server port number"""
        if self.options.interactive and not self.options.email_port:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='email_port',
                                    default_value='',
                                    required=False,
                                    prompt='Enter the ' + bold('mail server port number'),
                                    validator=PortNumberValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --email-port is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Port is invalid'})
        return validator.get_value()
