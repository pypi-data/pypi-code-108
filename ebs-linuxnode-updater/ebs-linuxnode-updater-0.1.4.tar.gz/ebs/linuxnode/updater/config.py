

import os
import sys
import shutil
import logging
import pkg_resources
from six.moves.configparser import ConfigParser
from appdirs import user_config_dir


class UpdaterConfig(object):
    _appname = os.path.join('ebs', 'updater')
    _root = os.path.abspath(os.path.dirname(__file__))
    _roots = [_root]
    _config_file = os.path.join(user_config_dir(_appname), 'config.ini')

    def __init__(self):
        if not os.path.exists(os.path.dirname(self._config_file)):
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        if not os.path.exists(self._config_file):
            _ROOT = os.path.abspath(os.path.dirname(__file__))
            shutil.copy(os.path.join(_ROOT, 'default/config.ini'), self._config_file)
        self._config = ConfigParser()
        logging.debug("Reading Config File {}".format(self._config_file))
        self._config.read(self._config_file)
        logging.debug("EBS Linux Node Updater, version {0}".format(self.updater_version))
        self._handlers = {}
        self._domains = {}
        self._package_map = {}

    @property
    def updater_version(self):
        return pkg_resources.get_distribution('ebs-linuxnode-updater').version

    def _write_config(self):
        with open(self._config_file, 'w') as configfile:
            self._config.write(configfile)

    def _check_section(self, section):
        if not self._config.has_section(section):
            self._config.add_section(section)
            self._write_config()

    def _extract_multiline(self, section, option):
        rvals = self._config.get(section, option)
        if '\n' in rvals:
            return [x.strip() for x in rvals.strip().split('\n')]
        else:
            return rvals

    @property
    def domains(self):
        return self._extract_multiline('control', 'domains')

    def install_domain_handler(self, method, handler):
        logging.debug("Installing '{}' as handler for method '{}'".format(handler, method))
        self._handlers[method] = handler

    def register_package_name(self, name, handler):
        logging.debug("Registering '{}' as a package name for handler '{}'".format(name, handler))
        self._package_map[name] = handler

    def __getattr__(self, item):
        if item in self.domains:
            if item not in self._domains.keys():
                method = self._config.get(item, 'method')
                if method not in self._handlers.keys():
                    raise KeyError("'{}' is not a recognized method handler!".format(method))
                self._domains[item] = self._handlers[method](
                    config=self, name=item, **dict(self._config.items(item))
                )
            return self._domains[item]
        elif item in self._package_map.keys():
            return dict(self._config.items(item))
        else:
            raise AttributeError(item)


_config = UpdaterConfig()
sys.modules[__name__] = _config
