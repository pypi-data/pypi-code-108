import os

from pipedash.helper import log


class Registrar(object):
    _instance = None
    worker = None
    worker_id = None

    def __new__(cls):
        if cls._instance is None:
            log.info('Creating the object')
            cls._instance = super(Registrar, cls).__new__(cls)
            # Put any initialization here.

        return cls._instance

    def hasEnvironment(self):
        return self.environment is not None

    def setEnvironment(self, env):
        if self.environment is None:
            self.environment = env
        else:
            log.error("You are trying to change the environment - thats probably an error?")

    def isLiveEnvironment(self):
        return self.environment == "live"

    def get_port(self):
        return self.workerEndpointPort
