from typing import List, Union, Tuple
from pathlib import Path
import glob
import os
import json
import asyncio

from slugify import slugify

from ehelply_bootstrapper.bootstrap import Bootstrap, LOADABLE_MYSQL
from ehelply_bootstrapper.drivers.mysql import MySQLCredentials
from ehelply_bootstrapper.drivers.aws_utils.aws_asm import ASM
from ehelply_bootstrapper.utils.state import State
from ehelply_bootstrapper.utils.environment import Environment
from ehelply_bootstrapper.utils.service import ServiceMeta, ServiceStatus, KPI
from ehelply_bootstrapper.utils.cryptography import Hashing

from ehelply_logger.Logger import VERBOSITY_NORMAL

from ehelply_microservice_library.integrations.m2m import M2M
from ehelply_microservice_library.integrations.sdk import SDK
from ehelply_microservice_library.integrations.fact import Fact, FactBase, get_fact_endpoint, get_fact_stage
from ehelply_microservice_library.integrations.logging import Log
from ehelply_microservice_library.integrations.meta import Meta
from ehelply_microservice_library.integrations.note import Note
from ehelply_microservice_library.integrations.monitor import Monitor
from ehelply_microservice_library.integrations.user import User
from ehelply_microservice_library.integrations.access import Access
from ehelply_microservice_library.integrations.security import Security
from ehelply_microservice_library.integrations.appointments import Appointments
from ehelply_microservice_library.integrations.places import Places
from ehelply_microservice_library.integrations.reviews import Reviews
from ehelply_microservice_library.integrations.products import Products
from ehelply_microservice_library.integrations.notifications import Notifications, NotificationType

from ehelply_microservice_library.utils.constants.constants_gatekeeper import *
from ehelply_microservice_library.utils.service_updater import ServiceUpdater
from ehelply_microservice_library.utils.secret_names import secret_name_database, secret_name_facts_vault, \
    secret_name_security_vault, secret_name_updater_vault

CONST_INTEGRATION_ACCESS: str = "access"
CONST_INTEGRATION_APPOINTMENTS: str = "appointments"
CONST_INTEGRATION_META: str = "meta"
CONST_INTEGRATION_NOTES: str = "notes"
CONST_INTEGRATION_NOTIFICATIONS: str = "notifications"
CONST_INTEGRATION_PLACES: str = "places"
CONST_INTEGRATION_REVIEWS: str = "reviews"
CONST_INTEGRATION_SECURITY: str = "security"
CONST_INTEGRATION_USERS: str = "users"
CONST_INTEGRATION_PRODUCTS: str = "products"


class ServiceBootstrap(Bootstrap):
    """
    This class helps to set up the entire service

    In the default configuration, some assumptions are made about surrounding infrastructure. However, if these
    assumptions are wrong and require changing, this class is built to be as flexible as possible.

    Assumptions:
        * A facts microservice is already deployed. This is a service that shares constants with all services and do not require security
        * A monitoring microservice is already deployed. This will take in heartbeats and help manage exceptions
        * A security microservice is already deployed. This handles tokens, access keys, and encryption keys
        * An updater microservice is already deployed. This handles automatic updating of microservice template code
        * AWS ASM is being utilized to hold secrets and constants which require security

    """

    def __init__(self):
        """
        Prepares the bootstrapper class.

        Ignore this method unless you need to init any values for the microservice itself.
        """
        service_environment_path: str = str(self.get_service_environment_path())
        Environment(path=service_environment_path)

        service_gatekeeper_key: str = self.get_service_gatekeeper_key()

        service_loadables: List[str] = self.get_service_loadables()
        service_configs: Union[List[str], None] = self.get_service_configs()
        service_verbosity: int = self.get_service_verbosity()
        service_config_path: str = str(self.get_service_config_path())

        service_name: str = self.get_service_name()
        service_key: str = slugify(service_name)
        service_version: str = self.get_service_version()
        service_summary: str = self.get_service_summary()
        service_authors: List[str] = self.get_service_authors()
        service_author_emails: List[str] = self.get_service_author_emails()

        service_meta: ServiceMeta = ServiceMeta(
            name=service_name,
            key=service_key,
            version=service_version,
            summary=service_summary,
            authors=service_authors,
            author_emails=service_author_emails
        )

        self.service_status: ServiceStatus = ServiceStatus()

        super().__init__(
            service_meta=service_meta,
            service_gatekeeper_key=service_gatekeeper_key,
            service_environment_path=service_environment_path,
            service_loadables=service_loadables,
            service_config_path=service_config_path,
            service_configs=service_configs,
            service_verbosity=service_verbosity
        )

    def get_service_name(self) -> str:
        """
        Returns the service name

        Returns:
            str: Service name

        """
        raise Exception(
            "get_service_name must be overridden in your service file. Please see `service.py`")

    def get_service_version(self) -> str:
        """
        Returns the service version

        Returns:
            str: Service version in semver format. eg 1.3.13

        """
        raise Exception(
            "get_service_version must be overridden in your service file. Please see `service.py`")

    def get_service_loadables(self) -> List[str]:
        """
        This defines which drivers should be loaded when the service runs
        Each driver has an associated constant
        Add the applicable constant to the list for the drivers you wish to use

        Returns:
            List[str]: A list of loadables. These are the drivers that will be loaded when the service boots

        """
        raise Exception(
            "get_service_loadables must be overridden in your service file. Please see `service.py`")

    def get_service_required_integrations(self) -> List[str]:
        """
        This defines which integrations are required.

        Returns:
            List[str]: A list of integrations

        """
        raise Exception(
            "get_service_required_integrations must be overridden in your service file. Please see `service.py`")

    def get_service_optional_integrations(self) -> List[str]:
        """
        This defines which integrations are optional.

        Returns:
            List[str]: A list of integrations

        """
        return []

    def get_service_summary(self) -> str:
        """
        A summary of the service

        Returns:
            str: Service summary

        """
        raise Exception(
            "get_service_summary must be overridden in your service file. Please see `service.py`")

    def get_service_authors(self) -> List[str]:
        """
        Service authors

        Returns:
            List[str]: A list of author names

        """
        raise Exception(
            "get_service_authors must be overridden in your service file. Please see `service.py`")

    def get_service_author_emails(self) -> List[str]:
        """
        Email addresses of the service authors

        Returns:
            List[str]: A list of author emails in the same order as get_service_authors

        """
        raise Exception(
            "get_service_author_emails must be overridden in your service file. Please see `service.py`")

    def get_service_gatekeeper_key(self) -> str:
        """
        Gets the gatekeeper key from the environment variables. The gatekeeper key is an encryption key that decrypts
        any initial credentials which are required to start or use a microservice.

        Returns:
            str: Gatekeeper key

        """
        return json.loads(os.environ[GATEKEEPER_KEY_ENVIRONMENT_NAME])['secret_key']

    def get_root_path(self) -> Path:
        """
        Gets the root path

        Returns:
            Path: The root path

        """
        raise Exception("get_root_path must be overridden in service.py to be used.")

    def get_https_certificate_paths(self) -> Tuple[Union[None, str], Union[None, str]]:
        """
        Gets the certificates to run the dev server as https

        If, we return None, None the server will be launched as http

        Returns:
            Tuple[Union[None, str], Union[None, str]]: HTTPS certificate paths. First path is private key, second is cert

        """
        # certificates_path: Path = Path(Path(__file__).resolve().parents[2]).joinpath('certificates')
        #
        # return str(certificates_path.joinpath('private.key')), str(certificates_path.joinpath('certificate.crt'))
        return None, None

    def get_service_configs(self) -> Union[List[str], None]:
        """
        This is used to define the names (including .yaml) of other configuration files you would like to have the application
        load for you. If you are satisfied with the app.yaml and bootstrap.yaml configuration files, leave this value at None

        Returns:
            Union[List[str], None]: Additional

        """
        configs: List[str] = []

        service_configs_path: Path = self.get_service_config_path()

        for config in glob.glob(str(service_configs_path.joinpath('service')) + "/*.yaml"):
            config: Path = Path(config)
            configs.append(str(config.relative_to(service_configs_path)))

        return configs

    def get_service_verbosity(self) -> int:
        """

        This is used to define the level of debug we want to preform. Typically this is just used within the logger to
        output different amounts of information. The typical range is between 0 (No debug) to 3 (Full Debug)

        Returns:
            None

        """
        return VERBOSITY_NORMAL

    def get_service_environment_path(self) -> str:
        """
        This is an override for the environment path

        Returns:
            str: Path of the env.json file

        """
        return None

    def get_service_config_path(self) -> Path:
        """
        This is an override for the configuration path

        Returns:
            str: Path of configs folder

        """
        return None

    def get_service_package_path(self) -> Path:
        """
        This is an override for the microservice path

        Returns:
            str: Path of the microservice root

        """
        return None

    def get_fact_subscriptions(self) -> List[str]:
        """
        List of facts to subscribe to

        Returns:
            List[str]: List of facts to subscribe to and pull down from a facts microservice.

        """
        return []

    def get_fact_providers(self) -> List[FactBase]:
        """
        List of facts to push at a regular basis

        Returns:
            List[FactBase]: A list of facts to push to a facts microservice

        """
        return []

    def get_notification_types(self) -> List[NotificationType]:
        """
        List of notification types to push when the microservice loads

        Returns:
            List[NotificationType]: Notification types to be used throughout this service

        """
        return []

    def get_kpi(self) -> List[KPI]:
        """
        List of up to date KPIs

        Returns:
            List[KPI]: KPIs to report

        """
        return []

    def is_load_service_routers(self) -> bool:
        """
        Whether or not to register the service routers or not
        Returns:
            Bool
        """
        return True

    def fastapi_routers(self):
        """
        Register fastapi routers

        Returns:
            None

        """

        # !!!!! Imports for routers must go here to remove an order of operation bug that occurs when endpoints need to
        #          talk to a DB

        if self.is_load_service_routers():
            from ehelply_microservice_library.routers import router_service_monitor
            self.fastapi_driver.instance.include_router(
                router_service_monitor.router,
                prefix="/ehelply_monitor",
                tags=["ehelply", "service"],
                responses={404: {"description": "Not found"}},
            )

            from ehelply_microservice_library.routers import router_service_meta as service_meta_router
            self.fastapi_driver.instance.include_router(
                service_meta_router.router,
                prefix="/ehelply_meta",
                tags=["ehelply", "service"],
                responses={404: {"description": "Not found"}},
            )

            from ehelply_microservice_library.routers import router_service as service_router
            self.fastapi_driver.instance.include_router(
                service_router.router,
                prefix="/ehelply_service",
                tags=["ehelply", "service"],
                responses={404: {"description": "Not found"}},
            )

            from ehelply_microservice_library.routers import router_service_security as service_security_router
            self.fastapi_driver.instance.include_router(
                service_security_router.router,
                prefix="/ehelply_security",
                tags=["ehelply", "service"],
                responses={404: {"description": "Not found"}},
            )

    def get_secret_subscriptions(self) -> List[str]:
        """
        Hook into adding additional secret names to fetch during microservice boot

        Returns:
            List[str]: A list of secrets to subscribe to

        """
        return []

    def fetch_secrets(self):
        """
        Fetches secrets from AWS ASM

        Returns:
            None

        """
        subscribe_to_secrets: list = [
            secret_name_facts_vault(),
            secret_name_security_vault(),
            secret_name_updater_vault()
        ]

        if LOADABLE_MYSQL in self.get_service_loadables():
            subscribe_to_secrets.append(secret_name_database())

        subscribe_to_secrets += self.get_secret_subscriptions()

        for secret_name in subscribe_to_secrets:
            State.secrets.add(ASM.get_secret(secret_name=secret_name), category=secret_name)

    def register_integrations(self):
        """
        Register service integrations
        A service integration is a wrapper around ehelply microservices to make them easier to talk to

        Returns:
            None

        """
        # The fact service integration works on a subscription model. You provide the integration with a list of facts
        #   you care about and it will grab the facts from the fact service for you and ensure it stays updated for
        #   if/when the value of the fact changes.
        subscribe_to_facts: list = [
                                       "cognito-ehelply",

                                       "db-rds-ehelply",

                                       "mq-logging",
                                       "mq-monitoring",
                                       "mq-usage",

                                       "ehelply-templates",
                                       "ehelply-sam"
                                   ] + self.get_fact_subscriptions()

        active_integrations: List[
            str] = self.get_service_required_integrations() + self.get_service_optional_integrations()

        if CONST_INTEGRATION_ACCESS in active_integrations:
            subscribe_to_facts.append("ehelply-access")

        if CONST_INTEGRATION_SECURITY in active_integrations:
            subscribe_to_facts.append("ehelply-security")

        if CONST_INTEGRATION_NOTES in active_integrations:
            subscribe_to_facts.append("ehelply-notes")

        if CONST_INTEGRATION_META in active_integrations:
            subscribe_to_facts.append("ehelply-meta")

        if CONST_INTEGRATION_USERS in active_integrations:
            subscribe_to_facts.append("ehelply-users")

        if CONST_INTEGRATION_PRODUCTS in active_integrations:
            subscribe_to_facts.append("ehelply-products")

        if CONST_INTEGRATION_NOTIFICATIONS in active_integrations:
            subscribe_to_facts.append("mq-notifications")
            subscribe_to_facts.append("ehelply-notifications")

        if CONST_INTEGRATION_PLACES in active_integrations:
            pass
            # TODO: Once added to facts: subscribe_to_facts.append("ehelply-places")

        if CONST_INTEGRATION_REVIEWS in active_integrations:
            pass
            # TODO: Once added to facts: subscribe_to_facts.append("ehelply-reviews")

        if CONST_INTEGRATION_APPOINTMENTS in active_integrations:
            pass
            # TODO: Once added to facts: subscribe_to_facts.append("ehelply-appointments")

        # Register the fact service integration
        self.register_integration(Fact(State.logger, subscribe_to_facts))

        # Register the M2M service integration
        self.register_integration(M2M(self.service_gatekeeper_key))

        # Register the SDK service integration
        self.register_integration(SDK(self.service_gatekeeper_key))

        # Register the core service integration
        self.register_integration(Log(self.service_meta.key))
        self.register_integration(Monitor())

        # Register the service integrations
        if CONST_INTEGRATION_ACCESS in active_integrations:
            self.register_integration(Access())

        if CONST_INTEGRATION_SECURITY in active_integrations:
            self.register_integration(Security())

        if CONST_INTEGRATION_NOTES in active_integrations:
            self.register_integration(Note())

        if CONST_INTEGRATION_META in active_integrations:
            self.register_integration(Meta())

        if CONST_INTEGRATION_USERS in active_integrations:
            self.register_integration(User())

        if CONST_INTEGRATION_NOTIFICATIONS in active_integrations:
            self.register_integration(Notifications(self.get_notification_types()))

        if CONST_INTEGRATION_PLACES in active_integrations:
            self.register_integration(Places())

        if CONST_INTEGRATION_REVIEWS in active_integrations:
            self.register_integration(Reviews())

        if CONST_INTEGRATION_APPOINTMENTS in active_integrations:
            self.register_integration(Appointments())

        if CONST_INTEGRATION_PRODUCTS in active_integrations:
            self.register_integration(Products())

    def get_mysql_credentials(self) -> MySQLCredentials:
        """
        Returns MySQL credentials

        Returns:
            MySQLCredentials: SQL Credentials

        """
        # rds_fact: dict = get_fact_stage("db-rds-ehelply")
        db_secret = State.secrets.get(category=secret_name_database())[0]
        return MySQLCredentials(
            host=db_secret.host,
            database=db_secret.dbname,
            port=db_secret.port,
            username=db_secret.username,
            password=db_secret.password,
        )

    def facts(self):
        """
        Push all the fact providers to the fact service

        Returns:
            None

        """
        if len(self.get_fact_providers()) > 0:
            State.logger.info("Pushing facts...")
        for fact in self.get_fact_providers():
            fact_integration: Fact = State.integrations.get("fact")
            fact_integration.push_fact(fact)

    def migrate(self):
        """
        Preforms MySQL Migrations

        Returns:
            None

        """
        if LOADABLE_MYSQL in self.service_loadables and State.config.sql.migrate:
            State.logger.info("Running Migrations..")
            import alembic.config
            alembicArgs = [
                '--raiseerr',
                'upgrade', 'head',
            ]
            alembic.config.main(argv=alembicArgs)

    async def monitor(self):
        """
        Creates link to a monitor service via a new thread

        Returns:
            None

        """
        monitor_integration: Monitor = State.integrations.get("monitor")
        # monitor_integration.register_service()

        State.logger.info("Booting async monitor... Expect to see out of order Batcher info in the logs.")
        from ehelply_microservice_library.routers.router_service_monitor import MonitorHeartbeatThread
        monitor_thread = MonitorHeartbeatThread(
            logger=State.logger,
            heartbeat_interval_minutes=get_fact_stage("mq-monitoring")["interval"],
            queue_url=get_fact_endpoint("mq-monitoring"),
            environment=Environment.stage(),
            service_meta=self.service_meta,
            service_status=self.service_status,
        )
        monitor_thread.start()

    def check_for_updates(self):
        """
        Checks for service template updates

        Returns:
            None

        """
        access_key: str = State.secrets.get(category=secret_name_updater_vault())[0].access
        secret_key: str = State.secrets.get(category=secret_name_updater_vault())[0].secret

        service_updater: ServiceUpdater = ServiceUpdater(access_key=access_key, secret_key=secret_key,
                                                         root_path=self.get_service_package_path())
        # update_available: bool = service_updater.is_update_available()

        try:
            update_available: bool = service_updater.is_update_available()
            if update_available:
                State.logger.info("New updates are available for the service template")
                State.logger.info("Service template update preview: " + str(service_updater.preview().dict()))
            else:
                State.logger.info("No service template updates are available")
        except:
            State.logger.warning("Unable to check for service template updates")

    async def fetch_keys(self):
        """
        Fetches keys from the security microservice

        Returns:
            None

        """
        from ehelply_microservice_library.routers.router_service_security import refresh_encryption_keys
        await refresh_encryption_keys(category=self.service_meta.key)

        State.logger.info("Booting security key fetcher... Expect to see out of order Batcher/Timer info in the logs.")
        from ehelply_microservice_library.routers.router_service_security import SecurityKeysThread
        security_keys_thread = SecurityKeysThread(
            logger=State.logger,
            delay=20 * 60,  # 20 min
            category=self.service_meta.key
        )
        security_keys_thread.start()

    async def fetch_kpis(self):
        """
        Fetches KPIs from this microservice. Look into bootstrapper.get_kpi()

        Returns:
            None

        """
        State.logger.info("Booting service KPI fetcher... Expect to see out of order Batcher/Timer info in the logs.")
        from ehelply_microservice_library.routers.router_service_monitor import KPIFetcherThread
        kpi_fetcher_thread = KPIFetcherThread(
            logger=State.logger,
            queue_url=get_fact_endpoint("mq-monitoring"),
            service_meta=self.service_meta
        )
        kpi_fetcher_thread.start()

    def configure_security(self):
        """
        Hashing cost factor is a function of 2^COST_FACTOR

        Returns:
            None

        """
        Hashing.COST_FACTOR = 12

    def before_boot(self):
        """
        EVENT HOOK - Runs before microservice begins booting

        Returns:
            None

        """
        State.logger.info("Setting up security")

        self.configure_security()

    async def before_integrations(self):
        """
        EVENT HOOK - Runs before microservice loads integrations

        Returns:
            None

        """
        State.logger.info("Fetching secrets...")

        self.fetch_secrets()

    async def before_drivers(self):
        """
        EVENT HOOK - Runs before microservice loads drivers

        Returns:
            None

        """
        State.logger.info("Pushing service specific facts...")

        self.facts()

        State.logger.info("Fetching encryption keys...")

        await self.fetch_keys()

    async def post_load(self):
        """
        Entry point of the application that is executed after the bootstrapping process completes

        If the microservice operates completely based on FastAPI endpoints, you can leave this method as is.
        If you require any custom logic or additional threads to be spun up, do it in this method.

        Returns:
            None

        """

        State.logger.info("Integrating into cluster...")

        await self.monitor()

        State.logger.info("Setting up KPI fetching...")

        await self.fetch_kpis()

        State.logger.info("Checking for service template updates...")

        self.check_for_updates()

        State.logger.info("Running application code...")
