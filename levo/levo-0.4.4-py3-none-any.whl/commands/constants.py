"""Constants related to CLI commands & sub commands"""

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

DEBUG_SETTINGS_HELP = (
    "Accept all of the Python's log level values: CRITICAL, ERROR, WARNING, INFO,"
    " DEBUG, and NOTSET (all case insensitive)."
)

NO_REPORTS_TO_SAAS_OPTION = "--disable-reporting-to-saas"
NO_REPORTS_TO_SAAS_HELP = "Do not send test reports to Levo's SaaS portal."

HEADER_OPTION = "--header"
HEADER_OPTION_SHORT = "-H"
HEADER_OPTION_HELP = (
    "Custom header that will be used in all requests to the target server."
    ' Example: -H "Authorization: Bearer 123" .'
)

AUTH_OPTION = "--auth"
AUTH_OPTION_SHORT = "-a"
AUTH_OPTION_HELP = (
    "Use in conjunction with '--auth'."
    " For basic authentication this specifies the target server's user and password. Example: USER:PASSWORD ."
    " For token and apikey authentication this is the appropriate key:value."
)
AUTH_TYPE_OPTION = "--auth-type"
AUTH_TYPE_OPTION_SHORT = "-A"
AUTH_TYPE_OPTION_HELP = "The authentication mechanism to be used. Defaults to 'basic'."
AUTH_TYPE_OPTION_CHOICES = ["basic", "token", "apikey"]
AUTH_TYPE_OPTION_CHOICES_DEFAULT = "basic"

ERROR_TRACE_OPTION = "--show-errors-tracebacks"
ERROR_TRACE_OPTION_HELP = "Show full tracebacks for internal errors."

VERBOSITY_OPTION = "--verbosity"
VERBOSITY_OPTION_SHORT = "-v"
