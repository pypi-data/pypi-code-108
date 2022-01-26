

import os
import logging
import subprocess
from .base import UpdaterDomainBase


class PipDomain(UpdaterDomainBase):
    def __init__(self, **kwargs):
        self._env = kwargs.pop('env')
        self._packages = [x.strip() for x in kwargs.pop('packages').strip().split('\n')]
        super(PipDomain, self).__init__(**kwargs)
        for package in self.packages:
            self._register_package_name(package)

    @property
    def env(self):
        return self._env

    @property
    def packages(self):
        return self._packages

    @property
    def pip_path(self):
        if self.env:
            return os.path.join(self.env, 'bin', 'pip')
        else:
            return 'pip'

    def _execute(self, args):
        cmd = [self.pip_path]
        cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True)
        logging.debug(result)
        return result.stdout

    def _get_package_information(self, package):
        result = self._execute(['show', package])
        lines = result.splitlines()
        rv = {}
        for line in lines:
            key, value = line.decode().split(':')
            rv[key.strip()] = value.strip()
        return rv

    def _get_current_version(self, package):
        return self._get_package_information(package)['Version']

    def _get_target_version(self, package):
        return getattr(self._config, package).get('version', 'latest')

    def _update_package(self, package):
        # # TODO Remove this when ready for deployment.
        # if package != "ebs-linuxnode-updater":
        #     logging.info("Skipping '{}' package '{}' for update check."
        #                  "".format(self._name, package))
        #     return
        logging.debug("Checking '{}' package '{}' for updates"
                      "".format(self._name, package))
        _starting_version = self._get_current_version(package)
        logging.debug("Current version for '{}' : {}"
                      "".format(package, _starting_version))
        logging.debug("Target version for '{}' : {}"
                      "".format(package, self._get_target_version(package)))
        if self._get_target_version(package) == 'latest':
            self._execute(['install', '--upgrade', package])

        _final_version = self._get_current_version(package)
        logging.info("'{}' : {}".format(package, _final_version))
        if _final_version != _starting_version:
            logging.info("Upgraded package '{}' from '{}' to '{}'"
                         "".format(package, _starting_version, _final_version))

    def _update(self):
        for package in self._packages:
            self._update_package(package)


def install(manager):
    manager.install_domain_handler('pip', PipDomain)
