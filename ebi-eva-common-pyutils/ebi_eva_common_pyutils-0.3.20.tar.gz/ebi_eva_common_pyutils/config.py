import os

import yaml


class Configuration:
    """
    Configuration class that allow to load a yaml file either at construction or later in the execution.
    It can be used like a dict but should be used as readonly.
    """
    config_file = None
    content = {}

    def __init__(self, *search_path):
        if search_path:
            self.load_config_file(*search_path)

    @staticmethod
    def _find_config_file(search_path):
        for p in search_path:
            if p and os.path.isfile(p):
                return p

    def load_config_file(self, *search_path):
        self.config_file = self._find_config_file(search_path)
        if self.config_file:
            with open(self.config_file, 'r') as f:
                self.content = yaml.safe_load(f)
        else:
            raise FileNotFoundError('Could not find any config file in specified search path')

    def get(self, item, ret_default=None):
        """
        Dict-style item retrieval with default
        :param item: The key to search for
        :param ret_default: What to return if the key is not present
        """
        try:
            return self[item]
        except KeyError:
            return ret_default

    def query(self, *parts, ret_default=None):
        """
        Drill down into a config, e.g. cfg.query('logging', 'handlers', 'a_handler', 'level')
        :param ret_default:
        :return: The relevant item if it exists in the config, else ret_default.
        """
        top_level = self.content
        item = None

        for p in parts:
            item = top_level.get(p)
            if item:
                top_level = item
            else:
                return ret_default
        return item

    def report(self):
        return yaml.safe_dump(self.content, default_flow_style=False)

    def __getitem__(self, item):
        """Allow dict-style access, e.g. config['this'] or config['this']['that']."""
        return self.content[item]

    def __contains__(self, item):
        """Allow search in the first layer of the config with 'in' operator."""
        return self.content.__contains__(item)


cfg = Configuration()
"""
Provides a singleton that can be used as a central place for configuration.
"""
