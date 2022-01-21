"""
Creates a development/evaluation deployment.
Initializes all files necessary for the Django project,
and does not set up anything to interface with the
web-facing server. The latter is the responsibility
of the deployment scripts (e.g. Dockerfile).
"""

import os.path
import sys
from argparse import ArgumentParser
from django.core.exceptions import ValidationError

from askbot.deployment import const
from askbot.deployment import deployers
from askbot.deployment.validators import ParamsValidator
from askbot.deployment.console import Console
from askbot.deployment.exceptions import DeploymentError
from askbot.utils.functions import generate_random_key

DESCRIPTION = """Creates files for the django project of Askbot.

The goal of this script is to create a working project and
sample settings. This setup is sufficient for the development.

Use the produced settings.py as a template for your production deployment.

If you wish to contribute to a more functional deployment script
have a look at the Dockerfile.
"""

class AskbotSetup:
    """Class that does the job of this module."""

    ASKBOT_ROOT = os.path.dirname(os.path.dirname(__file__))
    SOURCE_DIR = 'setup_templates'

    def __init__(self):
        self.parser = ArgumentParser(description=DESCRIPTION)
        self.add_arguments()

    def add_arguments(self):
        """Configures the CLI parameters"""
        self.add_setup_args()
        self.add_db_args()
        self.add_site_args()
        self.add_email_args()
        # these override some of the detailed settings
        self.add_settings_snippet_args()

    def add_email_args(self):
        """Settings specific to the email setup"""
        self.parser.add_argument(
            '--email-settings',
            dest='email_settings',
            action='store',
            help='Settings snippet for the email - Python code.'
        )

        self.parser.add_argument(
            '--server-email',
            action='store',
            dest='server_email',
            default='',
            help='Value for the SERVER_EMAIL setting'
        )

        self.parser.add_argument(
            '--default-from-email',
            action='store',
            dest='default_from_email',
            default='',
            help='Value for the DEFAULT_FROM_EMAIL setting'
        )

        self.parser.add_argument(
            '--email-host-user',
            action='store',
            dest='email_host_user',
            default='',
            help='Value for the EMAIL_HOST_USER setting'
        )

        self.parser.add_argument(
            '--email-host-password',
            action='store',
            dest='email_host_password',
            default='',
            help='Value for the EMAIL_HOST_PASSWORD setting'
        )

        self.parser.add_argument(
            '--email-subject-prefix',
            action='store',
            dest='email_subject_prefix',
            default='',
            help='Value for the EMAIL_SUBJECT_PREFIX setting'
        )

        self.parser.add_argument(
            '--email-host',
            action='store',
            dest='email_host',
            default='',
            help='Value for the EMAIL_HOST setting'
        )

        self.parser.add_argument(
            '--email-port',
            action='store',
            dest='email_port',
            default='',
            help='Value for the EMAIL_PORT setting'
        )

        self.parser.add_argument(
            '--email-use-tls',
            action='store_true',
            default=False,
            dest='email_use_tls',
            help='Value for the EMAIL_USE_TLS setting'
        )

        self.parser.add_argument(
            '--email-backend',
            action='store',
            dest='email_backend',
            default='django.core.mail.backends.smtp.EmailBackend',
            help='Value for the EMAIL_BACKEND setting'
        )

    def add_site_args(self):
        """Settings specific to the workings of the site"""
        self.parser.add_argument(
            '--admin-name',
            action='store',
            dest='admin_name',
            help='Name of the site admin'
        )

        self.parser.add_argument(
            '--admin-email',
            action='store',
            dest='admin_email',
            help='Admin of the site admin'
        )

        self.parser.add_argument(
            '--domain-name',
            dest='domain_name',
            action='store',
            help=const.DOMAIN_NAME_HELP
        )

        self.parser.add_argument(
            '--language-code', '-l',
            dest='language_code',
            action='store',
            default='en',
            help=const.LANGUAGE_CODE_HELP
        )

        self.parser.add_argument(
            '--timezone', '-t',
            dest='timezone',
            action='store',
            default='UTC',
            help='Name of the timezone, for example Europe/Berlin'
        )

        self.parser.add_argument(
            '--log-file-path',
            dest='log_file_path',
            action='store',
            default='log/askbot_app.log',
            help=const.LOG_FILE_PATH_HELP
        )

    def add_settings_snippet_args(self):
        """Arguments for the settings snippets.
        Values of these must be a Python code in the format of the
        django settings.py file, containing the specific groups of settings.
        Use of these is intended with the scripted deployments, e.g. - with Docker.

        The values are not validated. It is the responsibility of the user
        to test the produced settings.py file.

        When provided, these settings completely override corresponding detailed parameters.
        For example - `--db-settings` if provided, will override --db-name, --db-password, etc.
        """
        self.parser.add_argument(
            '--admin-settings',
            dest='admin_settings',
            action='store',
            help='Settings snippet for the ADMINS and MANAGERS variables - Python code.'
        )
        self.parser.add_argument(
            '--language-settings',
            dest='language_settings',
            help='Settings snippet for the language - Python code.'
        )

        self.parser.add_argument(
            '--logging-settings',
            dest='logging_settings',
            help='Settings snippet for the logging - Python code.'
        )

        self.parser.add_argument(
            '--caching-settings',
            dest='caching_settings',
            help='Settings snippet for caching - Python code.'
        )

        self.parser.add_argument(
            '--append-settings',
            dest='extra_settings',
            help='Extra settings snippet - python code - ' + \
                'appended to the settings.py file - Python code.'
        )

    def add_db_args(self):
        """DB parameters for the settings.py"""

        self.parser.add_argument(
            '--db-settings',
            dest='database_settings',
            action='store',
            help='Database settings snippet - Python code.\n' + \
                    'If given, all remaining db parameters will be ignored.'
        )

        self.parser.add_argument(
            '--db-engine', '-e',
            dest='database_engine',
            action='store',
            choices=[eng[0] for eng in const.DATABASE_ENGINE_CHOICES],
            type=int,
            help=const.DATABASE_ENGINE_HELP
        )

        self.parser.add_argument(
            '--db-name', '-d',
            dest='database_name',
            help='Database name'
        )

        self.parser.add_argument(
            '--db-user', '-u',
            dest='database_user',
            help='Database user name'
        )

        self.parser.add_argument(
            '--db-password', '-p',
            dest='database_password',
            help='Database password'
        )

        self.parser.add_argument(
            '--db-host',
            dest='database_host',
            help='Database host'
        )

        self.parser.add_argument(
            '--db-port',
            dest='database_port',
            help='Database port'
        )

    def add_setup_args(self):
        """Control the behaviour of this setup procedure"""
        self.parser.add_argument(
            '--root-directory', '-r',
            dest='root_dir',
            help=const.ROOT_DIR_HELP
        )

        self.parser.add_argument(
            '--proj-name',
            dest='proj_name',
            help=const.PROJ_NAME_HELP
        )

        self.parser.add_argument(
            '--media-root',
            dest='media_root',
            action='store',
            help=const.MEDIA_ROOT_HELP
        )

        self.parser.add_argument(
            '--static-root',
            dest='static_root',
            action='store',
        )

        self.parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            help='Overwrite the existing files'
        )

        self.parser.add_argument(
            '--noinput',
            dest='interactive',
            action='store_false',
            help='The installer will fail instead of asking for missing values.'
        )

    def __call__(self): # this is the main part of the original askbot_setup()
        try:
            # If necessary and if we are in the interactive mode,
            # will ask for the missing parameters.
            # Otherwise will use the default values.
            console = Console()
            validator = ParamsValidator(console, self.parser)
            params = validator.get_params()
            params['secret_key'] = generate_random_key(length=32)

            for key, val in params.items():
                print(f'{key}={val}')

            # make the directories
            force = params['force']
            deployers.makedir(params['root_dir'], force)
            deployers.makedir(params['proj_dir'], force)
            deployers.makedir(params['media_root_dir'], force)
            deployers.makedir(params['static_root_dir'], force)
            deployers.makedir(os.path.dirname(params['log_file_path']), force)

            deployers.ManagePy(params).deploy()
            deployers.UrlsPy(params).deploy()
            deployers.SettingsPy(params).deploy()
            # print next steps help
            #console.print_postamble(params)

        except ValidationError as error:
            if error.messages and len(error.messages) == 1:
                print(f'Error: {error.messages[0]}')
                sys.exit(1)
            print(f'\n\n{error}\nAborted')
            sys.exit(1)
        except DeploymentError as error:
            print(f'\n\n{error}')
            sys.exit(1)

        except KeyboardInterrupt:
            print("\n\nAborted.")
            sys.exit(1)

askbot_setup = AskbotSetup()
