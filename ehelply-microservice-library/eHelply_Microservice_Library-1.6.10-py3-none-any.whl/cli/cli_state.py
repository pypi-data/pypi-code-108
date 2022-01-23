from ehelply_microservice_library.service_bootstrap import ServiceBootstrap
from typing import Type


class CLIState:
    service: Type[ServiceBootstrap]
