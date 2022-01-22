from typing import Union, Any, List, Optional
from pydantic import BaseModel, validator, StrictStr, StrictBool
from datetime import datetime

from oianalytics import api


# Credentials
class BasicAuthCredentialsDTO(BaseModel):
    baseUrl: StrictStr
    login: StrictStr
    pwd: StrictStr

    def to_object(self):
        return api.OIAnalyticsAPICredentials(
            base_url=self.baseUrl, login=self.login, pwd=self.pwd
        )


class TokenCredentialsDTO(BaseModel):
    baseUrl: StrictStr
    token: StrictStr

    def to_object(self):
        return api.OIAnalyticsAPICredentials(base_url=self.baseUrl, token=self.token)


CredentialsDTO = Union[BasicAuthCredentialsDTO, TokenCredentialsDTO]


# Triggers
class CronTriggerDTO(BaseModel):
    type: StrictStr
    cron: StrictStr

    @validator("type")
    def check_type(cls, value):
        if value != "cron-trigger":
            raise ValueError("Trigger type should be 'cron-trigger'")
        return value


TriggerDTO = Union[CronTriggerDTO]


# Model inputs
class BaseInputDTO(
    BaseModel
):  # This class is currently simplified, it might be more robust to make it abstract and
    # specify each type with children
    type: StrictStr
    sourceCodeName: StrictStr
    value: Any

    def get_main_value(self):
        if self.type == "BATCH_STRUCTURE":
            return self.value["id"]
        elif isinstance(self.value, dict):
            return self.value["reference"]
        else:
            return self.value


# Model instance
class ModelInstanceDTO(BaseModel):
    trigger: TriggerDTO
    active: StrictBool
    dataExchangeMode: StrictStr
    inputParameters: List[BaseInputDTO]
    outputParameters: List

    def get_input_dict(self, input_types: Optional[List[str]] = None):
        if input_types is None:
            return {
                param.sourceCodeName: param.get_main_value()
                for param in self.inputParameters
            }
        else:
            return {
                param.sourceCodeName: param.get_main_value()
                for param in self.inputParameters
                if param.type in input_types
            }


# Model execution
class ModelExecutionDTO(BaseModel):
    testMode: StrictBool
    credentials: CredentialsDTO
    lastSuccessfulExecutionInstant: datetime
    currentExecutionInstant: datetime
    pythonModelInstance: ModelInstanceDTO
