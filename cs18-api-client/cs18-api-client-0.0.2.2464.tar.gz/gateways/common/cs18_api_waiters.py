import datetime
import time
from typing import Tuple, Optional, Callable

from gateways.colony_client import Colony
from gateways.common.cs18_api_errors import SandboxNotFound, SandboxEndingFailed
from gateways.common.cs18_api_responses import SandboxResponse, ProductionBlueResponse, ProductionGreenResponse, \
    BlueprintResponse
from gateways.common.cs18_api_statuses import SandboxStatus, SandboxDeploymentStatus, ProductionUpdateStatus
from gateways.utils import SandboxUtils, Utils


class CommonWaiters:
    """
    Various status waiters
    """

    def __init__(self, colony_api: Colony):
        self._api = colony_api

    def wait_until_qualiy_is(self, sandbox_id: str, status: str, max_minutes: int = 4):
        Utils.wait_until_time(
            func=lambda: self._is_qualiy_status(sandbox_id=sandbox_id, status=status),
            interval_sec=10,
            max_seconds=60 * max_minutes,
            subject=f'Is qualiy "{status}"?',
        )

    def _is_qualiy_status(self, sandbox_id: str, status: str):
        # sandbox = self._api.get_sandbox_details(sandbox_id=sandbox_id)
        success, sandbox, error = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        if not success:
            return False, error

        if SandboxUtils.is_deployment_failed(status=sandbox.sandbox_status):
            sandbox_status_description = SandboxUtils.describe_sandbox_status(sandbox=sandbox)
            raise Exception(f"Sandbox {sandbox_id} deployment failed, {sandbox_status_description}")

        if sandbox.debugging_service == status:
            return True, f'Yes, it\'s "{sandbox.debugging_service}"'

        return False, f'No, it\'s "{sandbox.debugging_service}"'

    def wait_until_sandbox_deployed_successfully(self, sandbox_id: str, **kwargs):
        """
        :param sandbox_id: str
        :param kwargs: interval_sec [5], max_retries [60]
        """
        Utils.wait_until_time(
            func=lambda: self._sandbox_deployed_successfully(sandbox_id=sandbox_id),
            interval_sec=kwargs.get("interval_sec", 10),
            max_seconds=kwargs.get("max_seconds", 1500),
            subject="sandbox {} deployed".format(sandbox_id),
        )

    def wait_until_sandbox_deployed_with_errors(self, sandbox_id: str, **kwargs):
        """
        :param sandbox_id: str
        :param kwargs: interval_sec [5], max_retries [60]
        """
        Utils.wait_until_time(
            func=lambda: self._sandbox_deployed_with_errors(sandbox_id=sandbox_id),
            interval_sec=kwargs.get("interval_sec", 10),
            max_seconds=kwargs.get("max_seconds", 1500),
            subject="sandbox {} deployed".format(sandbox_id),
        )

    def wait_until_production_blue_deployed_successfully(self,
                                                         production_id: str,
                                                         interval_sec: int = 5,
                                                         max_retries: int = 60,
                                                         wait_for_qualiy: bool = False):
        Utils.wait_for(func=lambda: self._production_blue_deployed(production_id=production_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject='Production Blue {} deployed'.format(production_id))

        Utils.wait_for(func=lambda: self._production_blue_started(production_id=production_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject=f'Production Blue {production_id} started')

        if wait_for_qualiy:
            Utils.wait_for(func=lambda: self._production_blue_have_working_qualiy(production_id=production_id),
                           interval_sec=interval_sec,
                           max_retries=max_retries,
                           subject=f'Production Blue {production_id} have working qualiy')

    def wait_until_production_green_deployed_successfully(self,
                                                          production_id: str,
                                                          interval_sec: int = 5,
                                                          max_retries: int = 60,
                                                          wait_for_qualiy: bool = False):
        Utils.wait_for(func=lambda: self._production_green_deployed(production_id=production_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject=f'Production Green {production_id} deployed')

        Utils.wait_for(func=lambda: self._production_green_started(production_id=production_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject=f'Production Green {production_id} started')

        if wait_for_qualiy:
            Utils.wait_for(func=lambda: self._production_green_have_working_qualiy(production_id=production_id),
                           interval_sec=interval_sec,
                           max_retries=max_retries,
                           subject=f'Production Green {production_id} have working qualiy')

    def wait_until_production_green_is_promoted(self,
                                                production_id: str,
                                                green_sandbox_id: str,
                                                interval_sec: int = 5,
                                                max_retries: int = 60):
        Utils.wait_for(func=lambda: self._production_green_is_promoted(production_id=production_id,
                                                                       green_sandbox_id=green_sandbox_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject=f'Was production green (p: {production_id}, s: {green_sandbox_id}) promoted?')

    def wait_until_production_green_is_exposed(self,
                                               production_id: str,
                                               exposure_value: int,
                                               interval_sec: int = 10,
                                               max_seconds: int = 60*5):
        Utils.wait_until_time(func=lambda: self._production_green_is_exposed(production_id=production_id,
                                                                             exposure=exposure_value),
                              interval_sec=interval_sec,
                              max_seconds=max_seconds,
                              subject=f'Was production green exposure updated to {exposure_value}%?')

    def wait_until_production_green_deleted(self,
                                      production_id: str,
                                      interval_sec: int = 5,
                                      max_retries: int = 60):
        Utils.wait_for(func=lambda: self._production_green_deleted(production_id=production_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject='Production green {} deleted'.format(production_id))

    def wait_until_production_deleted(self,
                                      production_id: str,
                                      interval_sec: int = 5,
                                      max_retries: int = 60):
        Utils.wait_for(func=lambda: self._production_blue_deleted(production_id=production_id),
                       interval_sec=interval_sec,
                       max_retries=max_retries,
                       subject='Production {} deleted'.format(production_id))

    def wait_until_sandbox_started(self, sandbox_id: str, **kwargs):
        """
        :param sandbox_id: str
        :param kwargs: interval_sec [5], max_retries [60]
        """
        Utils.wait_for(
            func=lambda: self._sandbox_started(sandbox_id=sandbox_id),
            interval_sec=kwargs.get("interval_sec", 5),
            max_retries=kwargs.get("max_retries", 60),
            subject="sandbox {} started".format(sandbox_id),
        )

    def wait_until_services_deployment_ended(self, sandbox_id: str, max_minutes: float = 15, interval_sec: int = 10):
        # waiting for all services to finish deployment either with success or failure
        Utils.wait_until_time(
            func=lambda: self._services_deployment_ended(sandbox_id=sandbox_id, throw_on_sandbox_failure=False),
            interval_sec=interval_sec,
            max_seconds=int(60 * max_minutes),
            subject=f"services in sandbox {sandbox_id} finished deployment",
        )

    def wait_until_sandbox_ended(self, sandbox_id: str, **kwargs):
        """
        :param sandbox_id: str
        :param kwargs: interval_sec [5], max_retries [60]
        """
        Utils.wait_for(func=lambda: self._sandbox_ended(sandbox_id=sandbox_id),
                       interval_sec=kwargs.get("interval_sec", 5),
                       max_retries=kwargs.get("max_retries", 60),
                       subject='sandbox {} deleted'.format(sandbox_id))

    def _sandbox_ended(self, sandbox_id: str) -> Tuple[bool, str]:
        success, sandbox, _ = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        return success and (sandbox.sandbox_status == SandboxStatus.ENDED or
                            sandbox.sandbox_status == SandboxStatus.ENDING_FAILED), \
               f"sandbox status is {sandbox.sandbox_status}"

    def wait_until_sandbox_successfully_ended(self, sandbox_id: str, **kwargs):
        """
        :param sandbox_id: str
        :param kwargs: interval_sec [5], max_retries [60]
        """
        Utils.wait_for(func=lambda: self._sandbox_successfully_ended(sandbox_id=sandbox_id),
                       interval_sec=kwargs.get("interval_sec", 5),
                       max_retries=kwargs.get("max_retries", 30),
                       subject='sandbox {} deleted'.format(sandbox_id))

    def _sandbox_successfully_ended(self, sandbox_id: str) -> Tuple[bool, str]:
        success, sandbox, _ = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        predicted_success = success and (sandbox.sandbox_status == SandboxStatus.ENDED)

        if sandbox.sandbox_status == SandboxStatus.ENDING_FAILED:
            raise SandboxEndingFailed(sandbox_id, sandbox.errors)

        return predicted_success, f"sandbox status is {sandbox.sandbox_status}"

    def wait_until_sandbox_not_waiting(self, sandbox_id: str, **kwargs):
        """
        :param sandbox_id: str
        :param kwargs: interval_sec [5], max_retries [60]
        """
        Utils.wait_for(func=lambda: self._sandbox_not_waiting(sandbox_id=sandbox_id),
                       interval_sec=kwargs.get("interval_sec", 5),
                       max_retries=kwargs.get("max_retries", 60),
                       subject='sandbox {} deleted'.format(sandbox_id))

    def _sandbox_not_waiting(self, sandbox_id: str) -> bool:
        success, sandbox, _ = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        return success and (sandbox.status_details != SandboxDeploymentStatus.WAITING)

    @staticmethod
    def wait_until_utc_datetime(target: datetime):
        print(
            "[{TIMESTAMP} utc] Waiting to {TARGET} ...".format(
                TIMESTAMP=Utils.get_current_time_utc().strftime("%X"),
                TARGET=target.strftime("%X"),
            )
        )

        if not target.tzinfo:
            target.tzinfo = datetime.timezone.utc
        while datetime.datetime.now(datetime.timezone.utc) < target:
            time.sleep(1)

        print(
            "[{TIMESTAMP} utc] Done".format(
                TIMESTAMP=Utils.get_current_time_utc().strftime("%X")
            )
        )

    def _services_deployment_ended(self, sandbox_id: str, throw_on_sandbox_failure: bool = False) -> Tuple[bool, str]:
        success, sandbox, error = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        if not success:
            return False, error

        sandbox_status_description = SandboxUtils.describe_sandbox_status(sandbox=sandbox)

        if sandbox.sandbox_status == SandboxStatus.NOT_FOUND:
            raise SandboxNotFound(sandbox_status_description)

        if throw_on_sandbox_failure and SandboxUtils.is_deployment_failed(status=sandbox.sandbox_status):
            raise Exception(f"Sandbox {sandbox_id} deployment failed, {sandbox_status_description}")

        services_deployed = all(SandboxUtils.is_service_deployment_ended(service) for service in sandbox.services)
        return services_deployed, sandbox_status_description

    def _sandbox_deployed_successfully(self, sandbox_id: str) -> Tuple[bool, str]:
        return self._sandbox_deployment_ended(sandbox_id=sandbox_id, throw_on_failure=True)

    def _sandbox_deployed_with_errors(self, sandbox_id: str) -> Tuple[bool, str]:
        return self._sandbox_deployment_ended(sandbox_id=sandbox_id, throw_on_failure=False)

    def _sandbox_deployment_ended(
            self,
            sandbox_id: str,
            throw_on_failure: bool = False
    ) -> Tuple[bool, str]:
        success, sandbox, failure_reason = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        if not success:
            return False, failure_reason
        if sandbox is None:
            return False, "no sandbox"
        sandbox_status_description = SandboxUtils.describe_sandbox_status(
            sandbox=sandbox
        )
        if sandbox.sandbox_status == SandboxStatus.NOT_FOUND:
            raise SandboxNotFound(sandbox_status_description)

        if throw_on_failure and SandboxUtils.is_deployment_failed(status=sandbox.sandbox_status):
            raise Exception(
                "Sandbox {SANDBOX_ID} deployment failed, {REASON}".format(
                    SANDBOX_ID=sandbox_id, REASON=sandbox_status_description
                )
            )
        return (
            SandboxUtils.is_deployment_ended(status=sandbox.sandbox_status),
            sandbox_status_description,
        )

    def _safely_get_sandbox_details(self, sandbox_id: str, handle_timeout: bool = True) \
            -> Tuple[bool, Optional[SandboxResponse], str]:
        try:
            sandbox = self._api.get_sandbox_details(sandbox_id=sandbox_id)
            return True, sandbox, ""
        except TimeoutError:
            if not handle_timeout:
                raise
            return False, None, "Timeout Error"

    def _sandbox_started(self, sandbox_id: str) -> bool:
        success, sandbox, _ = self._safely_get_sandbox_details(sandbox_id=sandbox_id)
        return success and sandbox.start_time is not None

    def _production_blue_started(self, production_id: str) -> bool:
        success, blue_env, _ = self._safely_get_production_details(production_id=production_id)
        return success and blue_env.deployment_start_time is not None

    def _production_blue_have_working_qualiy(self, production_id: str) -> bool:
        success, blue_env, _ = self._safely_get_production_details(production_id=production_id)
        return success and blue_env.debugging_service == 'on'

    def _production_green_started(self, production_id: str) -> bool:
        success, green_env, _ = self._safely_get_production_green_details(production_id=production_id)
        return success and green_env.deployment_start_time is not None

    def _production_green_have_working_qualiy(self, production_id: str) -> bool:
        success, blue_env, _ = self._safely_get_production_green_details(production_id=production_id)
        return success and blue_env.debugging_service == 'on'

    def _production_blue_deployed(self, production_id: str) -> Tuple[bool, str]:
        success, production, failure_reason = self._safely_get_production_details(production_id=production_id)
        if not success:
            return False, failure_reason
        if not production:
            return False, "No blue environment"
        status_description = SandboxUtils.describe_production_status(
            production=production
        )
        if SandboxUtils.is_deployment_failed(status=production.production_status):
            raise Exception(
                "Production(blue) {ID} deployment failed, {REASON}".format(
                    ID=production_id, REASON=status_description
                )
            )
        return (
            SandboxUtils.is_deployment_ended(status=production.production_status),
            status_description,
        )

    def _production_blue_deleted(self, production_id: str) -> bool:
        success, blue_env, _ = self._safely_get_production_details(production_id=production_id)
        return success and not blue_env

    def _production_green_deleted(self, production_id: str) -> bool:
        success, blue_env, _ = self._safely_get_production_details(production_id=production_id)
        # After green deletion is completed update status should be 'None'
        return success and blue_env.update_status == 'None'

    def _safely_get_production_details(self, production_id: str, handle_timeout: bool = True) \
            -> Tuple[bool, Optional[ProductionBlueResponse], str]:
        try:
            production = self._api.get_production_details(production_id=production_id)
            return True, production, ""
        except TimeoutError:
            if not handle_timeout:
                raise
            return False, None, "Timeout Error"

    def _safely_get_production_green_details(self, production_id: str, handle_timeout: bool = True) \
            -> Tuple[bool, Optional[ProductionGreenResponse], str]:
        try:
            production = self._api.get_production_green_details(production_id=production_id)
            return True, production, ""
        except TimeoutError:
            if not handle_timeout:
                raise
            return False, None, "Timeout Error"

    def _production_green_deployed(self, production_id: str) -> Tuple[bool, str]:
        success, production, failure_reason = self._safely_get_production_green_details(production_id=production_id)
        if not success:
            return False, failure_reason
        if not production:
            return False, "No green environment"
        status_description = SandboxUtils.describe_production_status(production=production)
        if SandboxUtils.is_deployment_failed(status=production.production_status):
            raise Exception(
                'Production(green) {ID} deployment failed, {REASON}'.format(ID=production_id, REASON=status_description)
            )
        return SandboxUtils.is_deployment_ended(status=production.production_status), status_description

    def _production_green_is_promoted(self, production_id: str, green_sandbox_id: str) -> Tuple[bool, str]:
        success, production, failure_reason = self._safely_get_production_details(production_id=production_id)
        if not success:
            return False, f'No, {failure_reason}'

        if not production:
            return False, 'No, blue environment was not even found'

        if production.sandbox_id != green_sandbox_id:
            return False, f'No, blue is still {production.sandbox_id}'

        return True, f"Yes, blue is now {production.sandbox_id}"

    def _production_green_is_exposed(self, production_id: str, exposure: int) -> Tuple[bool, str]:
        success, production, failure_reason = self._safely_get_production_green_details(production_id=production_id)
        if not success:
            return False, f'No, {failure_reason}'

        if not production:
            return False, 'No, green environment was not even found'

        if production.update_status == ProductionUpdateStatus.EXPOSING_GREEN:
            return False, f'No, green exposure is still being updated'

        if production.exposure != exposure:
            return False, f'No, green exposure is {production.exposure}%'

        return True, f"Yes, green exposure is {exposure}%"

    def wait_until_sandbox_output_resolved(self, sandbox_id: str, output_name: str,
                                           interval_sec: int = 10, max_seconds = 60):
        Utils.wait_until_time(
            func=lambda: self._sandbox_output_resolved(sandbox_id=sandbox_id, output_name=output_name),
            interval_sec=interval_sec,
            max_seconds=max_seconds,
            subject="waiting for output {} of sandbox {}".format(output_name, sandbox_id),
        )

    def _sandbox_output_resolved(self, sandbox_id: str, output_name: str):
        sandbox_details = self._api.get_sandbox_details(sandbox_id=sandbox_id)
        return any([o for o in sandbox_details.outputs if o.name == output_name and o.value is not None])

    def wait_until_blueprint_exist(self, blueprint_name: str, check_extra: Callable[[BlueprintResponse], bool] = None,
                                   interval_sec: int = 1, max_seconds: int = 15):
        Utils.wait_until_time(
            func=lambda: self._blueprint_exist(blueprint_name, check_extra),
            interval_sec=interval_sec,
            max_seconds=max_seconds,
            subject="waiting for blueprint '{}' to be in blueprint list".format(blueprint_name),
        )

    def _blueprint_exist(self, blueprint_name: str, func: Callable[[BlueprintResponse], bool] = None):
        return any([b for b in self._api.list_blueprints()
                    if b.name == blueprint_name and
                    (True if not func else func(b))])
