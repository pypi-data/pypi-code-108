import datetime
import json
import os
import socket
from logging import Logger
from typing import List
from urllib.parse import urlparse

import time
from requests import Response
from gateways.common.cs18_api_errors import DevboxHttpException, GeneralHttpException, MaxRetriesException
from gateways.common.cs18_api_responses import (
    ApplicationResponse,
    CatalogApplicationResponse,
    ProductionResponse,
    SandboxResponse,
    ServiceResponse
)
from gateways.common.cs18_api_statuses import SandboxStatus, ServiceStatus


class SandboxUtils:
    """
    Methods for sandbox information retrieval
    """

    @staticmethod
    def get_app_artifacts_in_common_s3(
            apps: List[CatalogApplicationResponse],
            version: str = "production"
    ) -> dict:
        """
        Generates full path to artifact filename in S3 for given List[CatalogApplicationResponse]
        :param apps: List[CatalogApplicationResponse]
        :param version: str. Default: "production"
        :return: dict
        """
        artifacts = {}
        for app in apps:
            if "windows" in app.name:
                artifacts.update(
                    {
                        app.name: "{app_name}/{version}/{app_name}.zip".format(
                            app_name=app.name, version=version
                        )
                    }
                )
            else:
                artifacts.update(
                    {
                        app.name: "{app_name}/{version}/{app_name}.tar.gz".format(
                            app_name=app.name, version=version
                        )
                    }
                )

        return artifacts

    @staticmethod
    def get_app_by_name(
            applications: List[ApplicationResponse], app_name: str
    ) -> ApplicationResponse:
        """
        Returns a specific ApplicationResponse from a list by given name
        :param applications: List[ApplicationResponse]
        :param app_name: specific service name to look for
        :return: ApplicationResponse
        """
        return next(
            iter(
                [
                    application
                    for application in applications
                    if application.name == app_name
                ]
            ),
            None,
        )

    @staticmethod
    def is_deployment_ended(status: str) -> bool:
        """
        True if sandbox deployment has ended ActiveWithError or Active
        :param status: str
        :return: bool
        """
        return SandboxUtils.is_deployment_succeeded(status=status) or SandboxUtils.is_deployment_failed(status=status)

    @staticmethod
    def is_deployment_succeeded(status: str) -> bool:
        """
        True if sandbox status is Active
        :param status: str
        :return: bool
        """
        return status == SandboxStatus.ACTIVE

    @staticmethod
    def is_deployment_failed(status: str) -> bool:
        """
        True if sandbox status is ActiveWithError
        :param status: str
        :return: bool
        """
        return status == SandboxStatus.ACTIVE_WITH_ERROR

    @staticmethod
    def describe_sandbox_status(sandbox: SandboxResponse) -> str:
        """
        Generates string response of sandbox status
        :param sandbox: SandboxResponse
        :return: str
        """
        return "sandbox status: {STATUS} ({STATUS_DETAILS}), " \
               "app statuses: {APP_STATUSES}, " \
               "service statuses: {SERVICE_STATUSES}, " \
               "sandbox errors: [{ERRORS}]".format(STATUS=sandbox.sandbox_status,
                                                   STATUS_DETAILS=sandbox.status_details,
                                                   APP_STATUSES=", ".join(
                                                       "{APP_NAME}: {APP_STATUS}".format(
                                                           APP_NAME=app.name, APP_STATUS=app.status
                                                       )
                                                       for app in sandbox.applications
                                                   ),
                                                   SERVICE_STATUSES=", ".join(
                                                       f"{service.name}: {service.status}"
                                                       for service in sandbox.services
                                                   ),
                                                   ERRORS=", ".join(
                                                       "{CODE} ({MESSAGE})".format(CODE=error.code,
                                                                                   MESSAGE=error.message)
                                                       for error in sandbox.errors
                                                   ),
                                                   )

    @staticmethod
    def describe_production_status(production: ProductionResponse) -> str:
        return (
            "Production status: {STATUS} ({STATUS_DETAILS}), update_status: {UPDATE_STATUS}"
            "app statuses: {APP_STATUSES}, sandbox errors: [{ERRORS}]".format(
                STATUS=production.production_status,
                STATUS_DETAILS=production.status_details,
                UPDATE_STATUS=production.update_status,
                APP_STATUSES=", ".join(
                    "{APP_NAME}: {APP_STATUS}".format(
                        APP_NAME=app.name, APP_STATUS=app.status
                    )
                    for app in production.applications
                ),
                ERRORS=", ".join(
                    "{CODE} ({MESSAGE})".format(CODE=error.code, MESSAGE=error.message)
                    for error in production.errors
                ),
            )
        )

    @staticmethod
    def is_service_deployment_ended(service: ServiceResponse):
        return service.status not in [ServiceStatus.PENDING, ServiceStatus.SETUP]


class ErrorUtils:
    @staticmethod
    def get_exception_error_codes(exception: DevboxHttpException) -> List[str]:
        return [err.code for err in exception.errors]

    @staticmethod
    def format_errors(exception: DevboxHttpException) -> str:
        return ",".join(f"{err.code} [{err.message}]" for err in exception.errors)


class Utils:
    """
    Various helper methods
    """

    @staticmethod
    def wait_for(
            func,
            interval_sec: int = 10,
            max_retries: int = 10,
            subject: str = "",
            silent: bool = False
    ) -> int:
        """
        Runs a given function in a loop until max_retries have been exhausted
        :param func: function to perform in a loop
        :param interval_sec: interval in seconds
        :param max_retries: max retries before exiting the loop
        :param subject: action to be performed, for human readability
        :param silent: print to stdout, True/False
        :return: number of attempts or Exception
        """
        current_attempt = 1
        while True:
            result = func()
            predicate_success, more_info = (
                result if isinstance(result, tuple) else (result, None)
            )
            if not silent:
                print(
                    "[{TIMESTAMP} utc] Attempt {ATTEMPT}/{MAX_ATTEMPTS} {CHECK_RESULT}{SUBJECT}{MORE_INFO}".format(
                        TIMESTAMP=Utils.get_current_time_utc().strftime("%X"),
                        ATTEMPT=current_attempt,
                        MAX_ATTEMPTS=max_retries,
                        CHECK_RESULT="succeeded" if predicate_success else "failed",
                        SUBJECT=" for '{}'".format(subject) if subject else "",
                        MORE_INFO=", {}".format(more_info) if more_info else "",
                    )
                )
            if predicate_success:
                return current_attempt

            current_attempt += 1
            if current_attempt > max_retries:
                raise MaxRetriesException(max_retries, subject)

            time.sleep(interval_sec)

    @staticmethod
    def wait_until_time(
            func,
            interval_sec: int = 10,
            max_seconds: int = 300,  # 5 min
            subject: str = "",
            silent: bool = False
    ):
        """
        Runs a given function in a loop until max_retries have been exhausted
        :param func: function to perform in a loop
        :param interval_sec: interval in seconds
        :param max_seconds: max seconds before exiting the loop
        :param subject: action to be performed, for human readability
        :param silent: print to stdout, True/False
        :return: None or Exception
        """
        current_time = time.time()
        timeout = current_time + max_seconds

        while current_time < timeout:
            result = func()
            predicate_success, more_info = (
                result if isinstance(result, tuple) else (result, None)
            )
            if not silent:
                print(
                    "[{TIMESTAMP} utc] Attempt {ATTEMPT}/{MAX_ATTEMPTS_SECONDS} "
                    "{CHECK_RESULT}{SUBJECT}{MORE_INFO}".format(
                        TIMESTAMP=Utils.get_current_time_utc().strftime("%X"),
                        ATTEMPT=(max_seconds - round(timeout - current_time)),
                        MAX_ATTEMPTS_SECONDS=max_seconds,
                        CHECK_RESULT="succeeded" if predicate_success else "failed",
                        SUBJECT=" for '{}'".format(subject) if subject else "",
                        MORE_INFO=", {}".format(more_info) if more_info else "",
                    )
                )
            if predicate_success:
                return

            current_time = time.time()
            time.sleep(interval_sec)

        if current_time > timeout:
            raise MaxRetriesException(max_seconds, subject)

    @staticmethod
    def wait_for_dns_ready(url_or_hostname: str,
                           logger: Logger,
                           interval_sec: int = 1,
                           max_attempts: int = 60,
                           silent: bool = False) -> int:
        def check_dns(name: str):
            try:
                socket.gethostbyname(name)
                return True, ''
            except Exception as ex:
                return False, f"due to error '{str(ex)}'"

        hostname = urlparse(url_or_hostname).hostname if '//' in url_or_hostname else url_or_hostname

        attempts = Utils.wait_for(func=lambda: check_dns(name=hostname),
                                  interval_sec=interval_sec,
                                  max_retries=max_attempts,
                                  subject=f"check dns resolution of {hostname}",
                                  silent=silent)
        if attempts > 1 and logger:
            logger.info(f"It took {attempts} attempts to resolve dns of '{url_or_hostname}'")
        return attempts

    @staticmethod
    def get_current_time_utc() -> datetime:
        """
        Returns current datetime in UTC
        :return: datetime
        """
        return datetime.datetime.now(datetime.timezone.utc)

    @staticmethod
    def find_dir(file: str) -> str:
        """
        Helper method to find specific file under current working directory
        :param file: str
        :return: str
        """
        for dirpath, _, filenames in os.walk(os.getcwd()):
            if file in filenames:
                return dirpath
        return "{} was not found".format(file)

    @staticmethod
    def get_as_json(my_object) -> dict:
        object_as_json_str = json.dumps(my_object, default=lambda o: o.__dict__)
        return json.loads(object_as_json_str)

    @staticmethod
    def str_to_bool(value: str) -> bool:
        value_l = value.lower()
        if value_l in ['true', '1']:
            return True

        if value_l in ['false', '0']:
            return False

        raise ValueError(f'Invalid boolean value "{value}"')


class GatewayUtils:
    """
    Various helper methods.
    Possibly move handle_response to more appropriate place,
        since it's an method for handling exception generation
    """

    @staticmethod
    def get_cs18_api_address(provider: str, host: str = None) -> str:
        """
        Returns CS18 API endpoint, either from config_file,
        or host if provided. Default: http://localhost:5050
        :param provider: str
        :param host: optional str
        :return: str
        """
        if host:
            return host

        data = "test_execution_data_{}".format(provider)
        config_file = "{dir}/{file}".format(dir=Utils.find_dir(data), file=data)
        if os.path.isfile(config_file):
            with open(config_file, "r") as file:
                config_json = json.load(file)
                for service in config_json["applications"]:
                    if service["name"] == "cs18-api":
                        return service.get("shortcuts")[0]
        return "http://localhost:5050"

    @staticmethod
    def get_cs18_web_address(provider: str, host: str = None) -> str:
        """
        Returns CS18 web address, either from config_file,
        or host if provided. Default: http://localhost
        :param provider: str
        :param host: optional str
        :return: str
        """
        if host:
            return host

        data = "test_execution_data_{}".format(provider)
        config_file = "{dir}/{file}".format(dir=Utils.find_dir(data), file=data)
        if os.path.isfile(config_file):
            with open(config_file, "r") as file:
                config_json = json.load(file)
                for service in config_json["applications"]:
                    if service["name"] == "cs18-ui":
                        return service.get("shortcuts")[0]
        return "http://localhost"

    @staticmethod
    def handle_response(response: Response, return_codes: List[int]):
        """
        Raises appropriate exception when response's
        return code is not found in return_codes list
        :param response: Response
        :param return_codes: List[int]
        :return: Exception if needed
        """
        if response.status_code not in return_codes:
            try:
                raise DevboxHttpException(response)
            except (json.JSONDecodeError, AttributeError):
                raise GeneralHttpException(response)
