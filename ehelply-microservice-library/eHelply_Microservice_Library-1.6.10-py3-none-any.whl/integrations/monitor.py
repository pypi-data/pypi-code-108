from __future__ import annotations
from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_microservice_library.integrations.fact import get_fact_endpoint

from ehelply_bootstrapper.utils.state import State

from ehelply_microservice_library.integrations.sdk import SDK
from ehelply_python_sdk.services.access.auth_rules import AuthException

from ehelply_python_sdk.services.monitor.sdk import *

from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import json


class UsageMQ(BaseModel):
    project_uuid: str
    usage_key: str
    quantity: int  # Quantity formats represented by a x10000000 integer. Precision to the millonth


class Monitor(Integration):
    """
    Monitor integration is used to talk to the ehelply-meta microservice
    """

    def __init__(self) -> None:
        super().__init__("monitor")

        class IntegratedSDK(MonitorSDK):
            def get_base_url(self) -> str:
                return get_fact_endpoint('ehelply-monitors')

        self.sdk: IntegratedSDK = IntegratedSDK(
            sdk_configuration=SDK.instance.sdk_configuration,
            requests_session=SDK.instance.requests_session
        )

        self.sqs = State.aws.make_client("sqs")

    def load(self):
        pass

    async def get_project(self, project_uuid: str) -> Optional[GetProjectResponse]:
        """
        Automation helper method for returning whether a project spend is maxed as a bool

        Args:
            project_uuid:

        Returns:

        """
        if project_uuid == 'ehelply-resources' or project_uuid == 'ehelply-cloud':
            return None

        get_project_response: GetProjectResponse = await self.sdk.get_project(project_uuid=project_uuid)

        # if is_response_error(get_project_response):
        #     raise AuthException("Retrieving project details failed.")

        return get_project_response

    def add_usage(self, usage: UsageMQ) -> bool:
        """
        Add usage to a project

        NOTE: Quantity formats represented by a x10000000 integer. Precision to the millonth

        :return:
        """
        if usage.project_uuid == 'ehelply-resources' or usage.project_uuid == 'ehelply-cloud':
            return False

        self.sqs.send_message(
            QueueUrl=get_fact_endpoint("mq-usage"),
            MessageBody=json.dumps(jsonable_encoder(usage.dict()))
        )

        return True
