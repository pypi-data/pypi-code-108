import flask
import os

from infosystem import database
from infosystem import request
from infosystem import subsystem as subsystem_module
from infosystem import scheduler
from infosystem import celery
from infosystem.bootstrap import Bootstrap
from infosystem.common.subsystem.apihandler import ApiHandler
from infosystem.common.input import InputResourceUtils
from infosystem.system import System
from infosystem._version import version as infosystem_version

from infosystem.resources import SYSADMIN_EXCLUSIVE_POLICIES, \
    SYSADMIN_RESOURCES, USER_RESOURCES


system = System('infosystem',
                subsystem_module.all,
                USER_RESOURCES,
                SYSADMIN_RESOURCES,
                SYSADMIN_EXCLUSIVE_POLICIES)


class SystemFlask(flask.Flask):

    request_class = request.Request

    def __init__(self, *args, **kwargs):
        super().__init__(__name__, static_folder=None)

        self.configure()
        self.configure_commands()
        self.init_database()
        self.after_init_database()

        system_list = [system] + list(kwargs.values()) + list(args)

        subsystem_list, self.user_resources, self.sysadmin_resources, \
            self.sysadmin_exclusive_resources = self._parse_systems(
                system_list)

        self.subsystems = {s.name: s for s in subsystem_list}

        self.api_handler = self.inject_dependencies()
        self.__validate_routes(self.subsystems)

        for subsystem in self.subsystems.values():
            self.register_blueprint(subsystem)

        # Add version in the root URL
        self.add_url_rule('/', view_func=self.version, methods=['GET'])

        self.before_request(
            request.RequestManager(self.subsystems).before_request)

    def configure(self):
        self.config['BASEDIR'] = os.path.abspath(os.path.dirname(__file__))
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.config['USE_WORKER'] = False

    def configure_commands(self):
        bootstrap_decorator = self.cli.command(name='bootstrap',
                                               help='Perform bootstrap')
        bootstrap_command = bootstrap_decorator(self.bootstrap)
        self.cli.add_command(bootstrap_command)

    def init_database(self):
        database.db.init_app(self)
        with self.app_context():
            database.db.create_all()

    def after_init_database(self):
        pass

    def version(self):
        return infosystem_version

    def schedule_jobs(self):
        pass

    def inject_dependencies(self) -> ApiHandler:
        bootstrap_resources = {
            'USER': self.user_resources,
            'SYSADMIN': self.sysadmin_resources,
            'SYSADMIN_EXCLUSIVE': self.sysadmin_exclusive_resources
        }
        api_handler = ApiHandler(self.subsystems, bootstrap_resources)

        for subsystem in self.subsystems.values():
            subsystem.api = api_handler.api

        return api_handler

    def __validate_routes(self, subsystems):
        errors = []
        for subsystem in subsystems.values():
            errors = errors + subsystem.validate_routes()
        if errors:
            for i in errors:
                print(i)  # TODO change to logger
            raise Exception(*errors)

    def bootstrap(self):
        """Bootstrap the system.

        - routes;
        - TODO(samueldmq): sysadmin;
        - default domain with admin and capabilities.

        """

        with self.app_context():
            api = self.api_handler.api()
            Bootstrap(api,
                      self.subsystems,
                      self.user_resources,
                      self.sysadmin_resources,
                      self.sysadmin_exclusive_resources).\
                execute()

    def _parse_systems(self, systems):
        user_resources = []
        sysadmin_resources = []
        sysadmin_exclusive_resources = []
        subsystems = []
        for system in systems:
            subsystems += system.subsystems
            user_resources += system.user_resources
            sysadmin_resources += system.sysadmin_resources
            sysadmin_exclusive_resources += system.sysadmin_exclusive_resources

        utils = InputResourceUtils
        user_resources = utils.remove_duplicates(user_resources)
        sysadmin_resources = utils.remove_duplicates(sysadmin_resources)
        sysadmin_exclusive_resources = utils.remove_duplicates(
            sysadmin_exclusive_resources)

        return (subsystems, user_resources,
                sysadmin_resources, sysadmin_exclusive_resources)

    def configure_celery(self):
        use_worker = self.config.get('USE_WORKER', False)
        if use_worker:
            celery.init_celery(self)

    def init_scheduler(self):
        self.scheduler = scheduler.Scheduler()
        self.schedule_jobs()
