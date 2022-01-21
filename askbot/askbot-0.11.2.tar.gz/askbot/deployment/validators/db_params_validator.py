"""`DbParamsValidator` - class that provides valid database parameters"""
import os
from django.core.exceptions import ValidationError
from askbot.utils.console import bold
from askbot.deployment import const
from askbot.deployment.console import get_sqlite_db_path_prompt
from askbot.deployment.validators.option_validator import OptionValidator
from askbot.deployment.utils import DomainNameValidator, PortNumberValidator

class DbParamsValidator: #pylint: disable=missing-class-docstring
    def __init__(self, console, parser, params=None):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()
        self.prev_params = params

    def get_params(self):
        """Returns database-related parameters"""
        db_engine = None
        if not self.options.database_settings:
            db_engine = self.get_db_engine()

        return {
            'database_engine': db_engine,
            'database_host': self.get_db_host(db_engine),
            'database_name': self.get_db_name(db_engine),
            'database_password': self.get_db_password(db_engine),
            'database_settings': self.options.database_settings,
            'database_user': self.get_db_user(db_engine),
            'database_port': self.get_db_port(db_engine)
        }

    def get_db_host(self, db_engine):
        """Returns host name for the db settings, default value is empty string"""
        if self.options.database_settings:
            return ''

        if 'sqlite' in db_engine:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='database_host',
                                    default_value='',
                                    prompt='Enter the ' + bold('database host name'),
                                    validator=DomainNameValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --db-host is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Database host is invalid'})
        return validator.get_value()

    def get_db_port(self, db_engine):
        """Returns port number, default value is empty string"""
        if self.options.database_settings:
            return ''
        if 'sqlite' in db_engine:
            return ''

        validator = OptionValidator(self.console,
                                    self.parser,
                                    option_name='database_port',
                                    default_value='',
                                    prompt='Enter the ' + bold('database port'),
                                    validator=PortNumberValidator,
                                    cli_error_messages=\
                                            {'invalid': 'value of --db-port is invalid'},
                                    interactive_error_messages=\
                                            {'invalid': 'Port is invalid'})
        return validator.get_value()

    def get_db_engine(self):
        """Dialog asking for a value 1-4"""
        if self.options.database_settings:
            return ''

        choices = [ch[0] for ch in const.DATABASE_ENGINE_CHOICES]
        if not self.options.interactive:
            cli_value = self.options.database_engine
            if not cli_value:
                return const.DATABASE_ENGINE_CODES[const.SQLITE]
            if cli_value not in choices:
                raise ValidationError('Invalid choice for the --db-engine parameter')

        num_choices = [(str(idx + 1), item) for (idx, item) in enumerate(choices)]

        prompt = 'Select the ' + bold('database engine') + ': ' + \
                ', '.join(['%s - %s' % ch for ch in num_choices]) + '.'
        num_choice = self.console.choice_dialog(prompt, choices=dict(num_choices), default='sqlite')
        if num_choice == 'sqlite': # a hack
            num_choice = '2'
        choice = dict(num_choices)[num_choice]
        return const.DATABASE_ENGINE_CODES[choice]

    def get_db_user(self, db_engine):
        """Asks for the database user name"""
        if self.options.database_settings:
            return ''

        if 'sqlite' in db_engine:
            return ''

        if not self.options.interactive:
            cli_value = self.options.database_user
            if not cli_value:
                raise ValidationError('--db-user parameter is required')
            return cli_value

        prompt = 'Enter ' + bold('database user name') + '.'
        return self.console.simple_dialog(prompt, required=True)

    def get_db_name(self, db_engine):
        """Asks user to enter the database name"""
        if self.options.database_settings:
            return ''

        if not self.options.interactive:
            cli_value = self.options.database_name
            if not cli_value:
                if 'sqlite' in db_engine:
                    return const.DEFAULT_SQLITE_DB_NAME
                raise ValidationError('--db-name parameter is required')
            return cli_value

        if 'sqlite' in db_engine:
            prompt = get_sqlite_db_path_prompt(self.prev_params['proj_dir'])
            db_path = self.console.simple_dialog(prompt,
                                                 default=const.DEFAULT_SQLITE_DB_NAME)
            if os.path.isabs(db_path):
                return db_path
            return os.path.join(self.prev_params['proj_dir'], db_path)

        return self.console.simple_dialog('Enter ' + bold('database name') + '.', required=True)

    def get_db_password(self, db_engine):
        """Asks user to enter the database password"""
        if self.options.database_settings:
            return ''

        if 'sqlite' in db_engine:
            return ''

        if not self.options.interactive:
            if not self.options.database_password:
                raise ValidationError('--db-password parameter is required')
            return self.options.database_password

        prompt = 'Enter ' + bold('database password') + '.'
        return self.console.simple_dialog(prompt, required=True)
