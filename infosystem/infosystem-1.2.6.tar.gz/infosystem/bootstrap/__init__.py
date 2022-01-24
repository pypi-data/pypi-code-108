from infosystem.common.subsystem.apihandler import Api
from typing import Dict, List

from infosystem.common.subsystem import Subsystem
from infosystem.common.input import RouteResource
from infosystem.bootstrap.default import BootstrapDefault
from infosystem.bootstrap.routes import BootstrapRoutes


class Bootstrap(object):

    def __init__(self, api: Api,
                 subsystems: Dict[str, Subsystem],
                 user_resources: List[RouteResource],
                 sysadmin_resources: List[RouteResource],
                 sysadmin_exclusive_resources: List[RouteResource]):
        self.user_resources = user_resources
        self.sysadmin_resources = sysadmin_resources
        self.sysadmin_exclusive_resources = sysadmin_exclusive_resources

        self.routes = BootstrapRoutes(subsystems, api)
        self.default = BootstrapDefault(api)
        self.application_manager = api.applications()

    def execute(self):
        self.routes.execute()

        if not self.application_manager.list():
            self.default.execute(self.user_resources,
                                 self.sysadmin_resources,
                                 self.sysadmin_exclusive_resources)
