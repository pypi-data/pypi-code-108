import sys
import traceback

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task
from burlap import common


class ServiceManagementSatchel(Satchel):

    name = 'service'

    @task
    def pre_deploy(self):
        """
        Runs methods services have requested be run before each deployment.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_pre_deployers.get(service)
            if funcs:
                print('Running pre-deployments for service %s...' % (service,))
                for func in funcs:
                    func()

    @task
    def deploy(self):
        """
        Applies routine, typically application-level changes to the service.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_deployers.get(service)
            if funcs:
                print('Deploying service %s...' % (service,))
                for func in funcs:
                    if not self.dryrun:
                        func()

    @task
    def post_deploy(self):
        """
        Runs methods services have requested be run before after deployment.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            self.vprint('post_deploy:', service)
            funcs = common.service_post_deployers.get(service)
            if funcs:
                self.vprint('Running post-deployments for service %s...' % (service,))
                for func in funcs:
                    try:
                        func()
                    except Exception as e:
                        print('Post deployment error: %s' % e, file=sys.stderr)
                        print(traceback.format_exc(), file=sys.stderr)

    @task
    def pre_db_dump(self):
        """
        Runs methods services that have requested to be run before each
        database dump.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_pre_db_dumpers.get(service)
            if funcs:
                print('Running pre-database dump for service %s...' % (service,))
                for func in funcs:
                    func()

    @task
    def post_db_dump(self):
        """
        Runs methods services that have requested to be run before each
        database dump.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_post_db_dumpers.get(service)
            if funcs:
                print('Running post-database dump for service %s...' % (service,))
                for func in funcs:
                    func()


    @task
    def refresh(self):
        self.configure()
        self.deploy()
        self.post_deploy()

    @task
    def configure(self):
        """
        Applies one-time settings changes to the host, usually to initialize the service.
        """
        print('env.services:', self.genv.services)
        for service in list(self.genv.services):
            service = service.strip().upper()
            funcs = common.service_configurators.get(service, [])
            if funcs:
                print('!'*80)
                print('Configuring service %s...' % (service,))
                for func in funcs:
                    print('Function:', func)
                    if not self.dryrun:
                        func()

service = ServiceManagementSatchel()
