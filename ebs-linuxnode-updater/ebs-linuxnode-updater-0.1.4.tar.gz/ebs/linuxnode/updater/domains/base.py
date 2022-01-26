
import logging


class UpdaterDomainBase(object):
    def __init__(self, **kwargs):
        self._config = kwargs.pop('config')
        self._method = kwargs.pop('method')
        self._name = kwargs.pop('name')

    @property
    def method(self):
        return self._method

    def _register_package_name(self, package):
        self._config.register_package_name(package, self)

    def _update(self):
        raise NotImplementedError

    def update(self):
        logging.debug("Checking domain '{}' for updates".format(self._name))
        self._update()
