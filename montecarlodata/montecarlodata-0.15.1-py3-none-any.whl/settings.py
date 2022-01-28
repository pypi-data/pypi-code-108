import os
from pathlib import Path

"""Environmental configuration"""

# Verbose error logging
MCD_VERBOSE_ERRORS = os.getenv('MCD_VERBOSE_ERRORS', False) in (True, 'true', 'True')

# MCD API endpoint
MCD_API_ENDPOINT = os.getenv('MCD_API_ENDPOINT', 'https://api.getmontecarlo.com/graphql')

# MCD ID header (for use in local development and testing)
MCD_USER_ID_HEADER = os.getenv('MCD_USER_ID_HEADER')

# MCD API ID. Overwrites config-file
MCD_DEFAULT_API_ID = os.getenv('MCD_DEFAULT_API_ID')

# MCD API Token. Overwrites config-file
MCD_DEFAULT_API_TOKEN = os.getenv('MCD_DEFAULT_API_TOKEN')

# dbt cloud API token
DBT_CLOUD_API_TOKEN = os.getenv('DBT_CLOUD_API_TOKEN')

# dbt cloud account ID
DBT_CLOUD_ACCOUNT_ID = os.getenv('DBT_CLOUD_ACCOUNT_ID')


"""Tool Defaults"""

# Default profile to be used
DEFAULT_PROFILE_NAME = 'default'

# Default path where any configuration files are written
DEFAULT_CONFIG_PATH = os.path.join(str(Path.home()), '.mcd')

# Default region where data collector is deployed
DEFAULT_AWS_REGION = 'us-east-1'

"""Internal Use"""

# File name for profile configuration
PROFILE_FILE_NAME = 'profiles.ini'

# Configuration sub-command
CONFIG_SUB_COMMAND = 'configure'

# Help flag of arguments and options
HELP_FLAG = '--help'

# Option file flag
OPTION_FILE_FLAG = '--option-file'

# Value (if entered) to show prompt with hidden input
SHOW_PROMPT_VALUE = '-1'

"""Monitors as code configs"""

DEFAULT_MONTECARLO_MONITOR_CONFIG_VERSION = 1

PROJECT_CONFIG_FILENAME = 'montecarlo.yml'

TARGET_DIRECTORY_NAME = 'target'

DEFAULT_INCLUDE_PATTERNS = [
    '**/*.yaml',
    '**/*.yml',
]

DEFAULT_EXCLUDE_PATTERNS = [
    'target/*',
    'dbt_project.yml',
    'montecarlo.yml'
]
