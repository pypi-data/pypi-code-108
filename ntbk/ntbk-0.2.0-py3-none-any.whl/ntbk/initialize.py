"""Functions for initializing the app"""

# system imports
import os

# app imports
from ntbk.entities.notebook import Notebook
from ntbk.exceptions import InvalidConfigException


def init_config_file(config):
    """Create the config file if it doesn't exist, then make sure the file is valid.

    Arguments:
        config -- Config instance
    """
    if not config.config_file_exists():
        config.reset_to_defaults()

    if not config.get('ntbk_dir'):
        ntbk_dir = input('Enter notebook save directory (default = ~/ntbk): ') or '~/ntbk'
        config.set('ntbk_dir', ntbk_dir)

    if not config.get('editor'):
        editor = input('Editor (will fallback to $EDITOR, '\
            'then finally vim if not specified): ')\
            or (os.environ['EDITOR'] if 'EDITOR' in os.environ else 'vim')

        config.set('editor', editor)

    if not config.is_valid():
        raise InvalidConfigException()


def init_notebook(config):
    """
    Prompts user for notebook path and editor if not set, then updates config.
    Creates notebook if necessary.

    Arguments:
        config - Config instance
    """
    if not config.is_valid():
        raise InvalidConfigException()

    notebook = Notebook(config)

    if not notebook.exists():
        notebook.create()


def init_app(config):
    """Initializes everything needed to run the app.

    Arguments:
        config - Config instance
    """
    init_config_file(config)
    init_notebook(config)
