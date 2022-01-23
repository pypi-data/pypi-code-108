import traceback
from typing import Union, Optional

import sentry_sdk
from ehelply_bootstrapper.utils.state import State
from fastapi import HTTPException
from pydantic import BaseModel

from ehelply_microservice_library.integrations.fact import get_fact_endpoint
from ehelply_microservice_library.integrations.m2m import M2M


class CloudParticipantAuthRequest(BaseModel):
    x_access_token: Optional[str] = None
    x_secret_token: Optional[str] = None
    authorization: Optional[str] = None
    ehelply_active_participant: Optional[str] = None
    ehelply_project: Optional[str] = None
    ehelply_data: Optional[str] = None


class CloudParticipantRequest(BaseModel):
    auth: CloudParticipantAuthRequest
    node: str
    service_target: str
    ignore_project_enabled: bool = False
    ignore_spend_limits: bool = False
    exception_if_unauthorized: bool = True
    exception_if_spend_maxed: bool = True
    exception_if_project_not_enabled: bool = True
    skip_project_check: bool = False


class CloudParticipantAuthResponse(BaseModel):
    authorization: Optional[str] = None
    access_token: Optional[str] = None
    secret_token: Optional[str] = None
    claims: Optional[dict] = None
    data: Optional[dict] = None


class CloudParticipantResponse(BaseModel):
    auth: CloudParticipantAuthResponse
    active_participant: str
    project_uuid: str
    is_privileged: bool = False
    entity_identifier: Optional[str] = None


class CloudParticipant(BaseModel):
    active_participant: str
    project_uuid: str
    is_privileged: bool = False
    entity_identifier: Optional[str] = None


async def ehelply_cloud_access(
        auth: CloudParticipantAuthRequest,
        node: str,
        service_target: str,
        ignore_project_enabled=False,
        ignore_spend_limits=False,
        exception_if_unauthorized=True,
        exception_if_spend_maxed=True,
        exception_if_project_not_enabled=True,
        skip_project_check=False,
) -> Union[bool, CloudParticipantResponse]:
    """

    Args:
        auth:
        node:
        service_target:
        ignore_project_enabled:
        ignore_spend_limits:
        exception_if_unauthorized:
        exception_if_spend_maxed:
        exception_if_project_not_enabled:
        skip_project_check:

    Returns:

    """

    with sentry_sdk.start_span(op="cp_authorization", description="CloudParticipant Authorization") as span:
        cloud_participant_request: CloudParticipantRequest = CloudParticipantRequest(
            auth=auth,
            node=node,
            service_target=service_target,
            ignore_project_enabled=ignore_project_enabled,
            ignore_spend_limits=ignore_spend_limits,
            exception_if_unauthorized=exception_if_unauthorized,
            exception_if_spend_maxed=exception_if_spend_maxed,
            exception_if_project_not_enabled=exception_if_project_not_enabled,
            skip_project_check=skip_project_check
        )

        m2m: M2M = State.integrations.get("m2m")

        result = m2m.requests.post(
            f"{get_fact_endpoint('ehelply-sam')}/projects/cloud_participant",
            json={"cloud_participant_auth": cloud_participant_request.dict()}
        )

        if result.status_code == 200:
            result = result.json()
            try:
                return CloudParticipantResponse(**result)
            except:
                if isinstance(result, bool):
                    return result
                else:
                    State.logger.warning(message="ehelply_cloud_access received an invalid response from ehelply-sam.")
                    State.logger.warning(message=str(result))
                    raise HTTPException(
                        status_code=500,
                        detail="Ruh Roh, something has gone terribly wrong - Denied by eHelply - ehelply_cloud_access 01."
                    )

        try:
            error_detail = result.json()['detail']
        except:
            traceback.print_exc()
            State.logger.warning(message="ehelply_cloud_access caused an unexpected error.")
            State.logger.warning(message=str(result.json()))
            raise HTTPException(
                status_code=500,
                detail="Ruh Roh, something has gone terribly wrong - Denied by eHelply - ehelply_cloud_access 02."
            )

        raise HTTPException(
            status_code=result.status_code,
            detail=error_detail
        )
