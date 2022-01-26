"""Handles application configuration"""

# system imports
from pathlib import Path

# 3rd party imports
import yaml


class Config():
    """Wrapper around config file to get/set values and update the config file"""

    CONFIG_FILEPATH = '~/.config/ntbk/ntbk.yml'

    DEFAULTS = {
        'ntbk_dir': '',
        'editor': '',
        'default_filename': 'index',
        'template_dir': '_templates',
        'default_templates': {
            'log': {
                'index': 'log_default'
            }
        },
        'template_vars': {
            'foo': 'bar'
        }
    }

    REQUIRED_KEYS = ['ntbk_dir', 'editor', 'template_dir']

    _config = {}

    def __init__(self, config=None, file_path=None):
        """Initialize the config

        Keyword arguments:
        config -- Optional dict to initialize config
        file_path -- Optional path to override the default file location
        """

        self._config_path = (file_path or Path(self.CONFIG_FILEPATH)).expanduser()

        if config is not None:
            conf = dict(self.DEFAULTS)
            conf.update(config)
            self._config = conf
        else:
            self.load()

    def get(self, key, default=None):
        """Get the value from the config for the given key"""
        return self._config.get(key, default)

    def set(self, key, value):
        """Set the value in the config for the given key. The file will be immediately saved"""
        self._config[key] = value
        self.save()

    def save(self):
        """Write the config to disk"""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(yaml.dump(self._config), encoding='utf-8')

    def is_valid(self):
        """Whether or not the config file is valid"""
        for key in self.REQUIRED_KEYS:
            if key not in self._config or not self._config[key]:
                return False
        return True

    def load(self):
        """Load the config yaml from disk into the config class level dict variable"""
        if self.config_file_exists():
            with self._config_path.open(encoding='utf-8') as file:
                self._config = yaml.load(file, Loader=yaml.FullLoader)

    def config_file_exists(self):
        """Whether or not the config file exists on disk"""
        return self._config_path.exists()

    def reset_to_defaults(self):
        """Restore the config file to the original defaults defined in DEFAULTS"""
        self._config = self.DEFAULTS
        self.save()
