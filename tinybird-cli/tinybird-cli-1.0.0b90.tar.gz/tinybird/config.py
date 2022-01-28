from pathlib import Path
import os.path
import json
import click

from tinybird import __cli__
from .feedback_manager import FeedbackManager

try:
    from tinybird.__cli__ import __revision__
except Exception:
    __revision__ = None

DEFAULT_API_HOST = 'https://api.tinybird.co'
DEFAULT_LOCALHOST = 'http://localhost:8001'
CURRENT_VERSION = f"{__cli__.__version__}"
VERSION = f"{__cli__.__version__} (rev {__revision__})"
DEFAULT_UI_HOST = 'https://ui.tinybird.co'
SUPPORTED_CONNECTORS = ['bigquery', 'snowflake']
PROJECT_PATHS = [
    'datasources',
    'datasources/fixtures',
    'endpoints',
    'pipes'
]
MIN_WORKSPACE_ID_LENGTH = 36


async def get_config(hostFlag, tokenFlag):
    if hostFlag:
        hostFlag = hostFlag.rstrip('/')

    config_file = Path(os.getcwd()) / ".tinyb"
    config = {}
    try:
        with open(config_file) as file:
            config = json.loads(file.read())
    except IOError:
        pass
    except json.decoder.JSONDecodeError:
        click.echo(FeedbackManager.error_load_file_config(config_file=config_file))
        return
    config['token'] = tokenFlag or config.get('token', None)
    config['host'] = hostFlag or config.get('host', DEFAULT_API_HOST)
    config['workspaces'] = config.get('workspaces', [])
    return config


async def write_config(config, dest_file='.tinyb'):
    config_file = Path(os.getcwd()) / dest_file
    with open(config_file, 'w') as file:
        file.write(json.dumps(config, indent=4, sort_keys=True))


class FeatureFlags:
    @classmethod
    def ignore_sql_errors(cls) -> bool:  # Context: #1155
        return "TB_IGNORE_SQL_ERRORS" in os.environ

    @classmethod
    def is_localhost(cls) -> bool:
        return "SET_LOCALHOST" in os.environ
