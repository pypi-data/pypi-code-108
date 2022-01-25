import json
import logging
import os
from pathlib import Path


def write_default_settings(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    global_variables = {
        'debug': False,
        'ignore_warnings': False,
        'skip_vesion_check': False,
        'context': 'prod-2',  # TODO - we shouldn't default to an ID but to the name - `grid-cloud`
        'grid_url': 'https://platform.grid.ai'
    }
    with P.open('w') as file:
        json.dump(global_variables, file, ensure_ascii=False, indent=4)


def reset_global_variables() -> None:
    """ Reset the settings from env variables"""
    global DEBUG, SKIP_VERSION_CHECK, CONTEXT, IGNORE_WARNINGS, GRID_URL

    if 'debug' in os.environ:
        DEBUG = bool(os.environ['DEBUG'])

    if 'ignore_warnings' in os.environ:
        IGNORE_WARNINGS = bool(os.environ['IGNORE_WARNINGS'])

    if 'skip_version_check' in os.environ:
        SKIP_VERSION_CHECK = bool(os.environ['SKIP_VERSION_CHECK'])

    if 'context' in os.environ:
        CONTEXT = os.environ['GRID_CLUSTER_ID']

    if 'grid_url' in os.environ:
        GRID_URL = os.environ['GRID_URL']


P = Path.home().joinpath(".grid/settings.json")
# Make sure path exists.
Path(P.parents[0]).mkdir(parents=True, exist_ok=True)
# If file doesn't exist, create with default global settings
if not P.exists():
    write_default_settings(P)
user_settings = json.load(P.open())
# TODO ENV variables could lead into confusion
DEBUG = bool(os.getenv("DEBUG", user_settings.get('debug', False)))
IGNORE_WARNINGS = bool(os.getenv('IGNORE_WARNINGS', user_settings.get('ignore_warnings', False)))
SKIP_VERSION_CHECK = bool(os.getenv('SKIP_VERSION_CHECK', user_settings.get('skip_vesion_check', False)))
CONTEXT = os.getenv('GRID_CLUSTER_ID', user_settings.get('context', 'prod-2'))
GRID_URL = os.getenv("GRID_URL", user_settings.get('grid_url', 'https://platform.grid.ai'))

TESTING = bool(os.getenv("TESTING") or os.getenv("CI"))
GRID_CREDENTIAL_PATH = os.getenv('GRID_CREDENTIAL_PATH', str(Path.home() / '.grid' / 'credentials.json'))
GRID_SETTINGS_PATH = os.getenv('GRID_SETTINGS_PATH', str(Path.home() / '.grid' / 'settings.json'))
TERMINAL_STATES = {"CANCELLED", "FAILED", "SUCCEEDED"}
STARTED_STATES = {"RUNNING", *TERMINAL_STATES}
WAITING_STATES = {"PENDING"}
logger = logging.getLogger(__name__)  # pragma: no cover
SHOW_PROCESS_STATUS_DETAILS = os.getenv('SHOW_PROCESS_STATUS_DETAILS')
GRID_SKIP_GITHUB_TOKEN_CHECK = bool(os.getenv("GRID_SKIP_GITHUB_TOKEN_CHECK", default=None))
TESTING = os.getenv("TESTING", default=os.getenv("CI", default=None))
SSL_CA_CERT = os.getenv("REQUESTS_CA_BUNDLE", default=os.getenv("SSL_CERT_FILE", default=None))
GRID_SSH_CONFIG = os.getenv("GRID_SSH_CONFIG", default=str(Path.home() / ".ssh/config"))
