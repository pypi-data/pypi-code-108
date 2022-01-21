"""Validates site-related setup parameters"""
from django.core.validators import EmailValidator
from django.conf.global_settings import LANGUAGES
from askbot.deployment.utils import (DomainNameValidator, TimezoneValidator,
                                     LanguageCodeValidator)
from askbot.deployment.validators.option_validator import OptionValidator
from askbot.utils.console import bold

class SiteParamsValidator:
    """Validates website parameters"""
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns setup-related parameters"""
        lang_code = self.get_language_code()
        return {
            'admin_email': self.get_admin_email(),
            'admin_name': self.get_admin_name(),
            'admin_settings': self.options.admin_settings,
            'domain_name': self.get_domain_name(),
            'extra_settings': self.options.extra_settings,
            'language_code': lang_code,
            'language_name': self.get_language_name(lang_code),
            'language_settings': self.options.language_settings,
            'timezone': self.get_timezone()
        }

    def get_language_code(self):
        """Returns valid language code"""
        default_lang_code = self.parser.get_default('language_code')
        is_default = self.options.language_code == default_lang_code
        if self.options.interactive and is_default:
            return self.options.language_code

        language_code_prompt = 'Enter the ' + bold('language code') + '\n' + \
                'Allowed language code values are here:\n' + \
                'https://github.com/django/django/blob/master/django/conf/global_settings.py'

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='language_code',
                                    default_value=default_lang_code,
                                    prompt=language_code_prompt,
                                    required=True,
                                    validator=LanguageCodeValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --language-code is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Language code is invalid'})
        return validator.get_value()

    @classmethod
    def get_language_name(cls, language_code):
        """Returns valid language name"""
        return dict(LANGUAGES)[language_code]

    def get_timezone(self):
        """Returns valid timezone for the TIME_ZONE setting"""
        default_tz = self.parser.get_default('timezone')
        if self.options.interactive and self.options.timezone == default_tz:
            return self.options.timezone

        tz_prompt = 'Enter the ' + bold('time zone') + '\n' + \
                'Allowed timezone values are here:\n' + \
                'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones'

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='timezone',
                                    default_value=default_tz,
                                    prompt=tz_prompt,
                                    required=True,
                                    validator=TimezoneValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --timezone is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Timezone is invalid'})
        return validator.get_value()

    def get_domain_name(self):
        """Returns valdated domain name"""
        if not self.options.domain_name:
            return None

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='domain_name',
                                    default_value='',
                                    prompt='Enter the domain name',
                                    validator=DomainNameValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --domain-name is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Domain name is invalid'})
        return validator.get_value()


    def get_admin_name(self): #pylint: disable=missing-function-docstring
        if self.options.admin_settings:
            # we won't use this if admin_settings is provided
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='admin_name',
                                    required=True,
                                    prompt='Enter name of the site admin',
                                    cli_error_messages={'missing': '--admin-name is required'},
                                    interactive_error_messages=\
                                            {'missing': 'Admin name is required'})
        return validator.get_value()

    def get_admin_email(self):
        """Returns valid email"""
        if self.options.admin_settings:
            # we won't use this if admin_settings is provided
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    required=True,
                                    option_name='admin_email',
                                    prompt='Enter email of the site admin',
                                    validator=EmailValidator,
                                    cli_error_messages=\
                                            {'missing': '--admin-email is required',
                                             'invalid': 'value of --admin-email is invalid'},
                                    interactive_error_messages=\
                                            {'missing': 'Admin email is required',
                                             'invalid': 'Invalid email address'})
        return validator.get_value()
