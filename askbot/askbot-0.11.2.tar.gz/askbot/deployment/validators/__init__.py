"""Validators for the CLI arguments"""
from askbot.deployment.validators.setup_params_validator import SetupParamsValidator
from askbot.deployment.validators.site_params_validator import SiteParamsValidator
from askbot.deployment.validators.db_params_validator import DbParamsValidator
from askbot.deployment.validators.email_params_validator import EmailParamsValidator

class ParamsValidator: #pylint: disable=too-few-public-methods
    """Root parameters validator"""
    def __init__(self, console, parser):
        self.console = console
        self.parser = parser

    def get_params(self):
        """Returns dictionary of valid parametrs.
        If necessary - will propmpt the user to enter
        any missing parameters.
        """
        params = dict()

        validators = (
            SetupParamsValidator,
            DbParamsValidator,
            SiteParamsValidator,
            EmailParamsValidator,
        )

        for validator_class in validators:
            validator = validator_class(self.console, self.parser, params)
            params.update(validator.get_params())

        options = self.parser.parse_args()
        # these parameters are passed without validatons
        params.update({
            'logging_settings': options.logging_settings,
            'caching_settings': options.caching_settings,
            'email_settings': options.email_settings,
            'extra_settings': options.extra_settings
        })

        return params
