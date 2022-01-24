"""
Model external (aka "remote") MLOps events that are sent to DataRobot via API.
"""
#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

from datetime import datetime
from enum import Enum


class EventType(Enum):
    """
    Helper symbols to avoid having to memorize event type strings.
    """
    PRED_REQUEST_FAILED = "prediction_request.failed"
    DEP_ACCURACY_GREEN = "model_deployments.accuracy_green"
    DEP_ACCURACY_RED = "model_deployments.accuracy_red"
    DEP_ACCURACY_YELLOW = "model_deployments.accuracy_yellow_from_green"
    DEP_DRIFT_GREEN = "model_deployments.data_drift_green"
    DEP_DRIFT_RED = "model_deployments.data_drift_red"
    DEP_DRIFT_YELLOW = "model_deployments.data_drift_yellow_from_green"
    DEP_MODEL_REPLACED = "model_deployments.model_replacement"
    DEP_SERVICE_GREEN = "model_deployments.service_health_green"
    DEP_SERVICE_RED = "model_deployments.service_health_red"
    DEP_SERVICE_YELLOW = "model_deployments.service_health_yellow_from_green"


class Event:
    """
    Represents an external event.
    The MLOps client creates this object.
    """
    def __init__(
            self, event_type, message, entity_id=None, org_id=None,
            data=None, prediction_request_data=None
    ):
        # type: (EventType, str, str, str, dict, dict) -> None
        """
        :param event_type: event type; use EventType enum
        :param message: string message to accompany event
        :param entity_id: ID of deployment or other entity involved in event. Can be auto-filled.
        :param org_id: ID of organization (if orgs are in use)
        :param data: optional data struct, depends on event type
        :param prediction_request_data: optional data struct,
               contains information about prediction request
        """
        self._event_type = event_type.value
        self._message = message
        self._entity_id = entity_id  # deployment, etc.
        self._org_id = org_id
        self._data = data
        self._prediction_request_data = prediction_request_data
        self._timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f%z")

    def get_event_type(self):
        return self._event_type

    def get_message(self):
        return self._message

    def get_entity_id(self):
        return self._entity_id

    def get_org_id(self):
        return self._org_id

    def get_data(self):
        return self._data

    def get_prediction_request_data(self):
        return self._prediction_request_data

    def get_timestamp(self):
        return self._timestamp

    @staticmethod
    def is_entity_a_deployment():
        """
        True if the event's entityId should automatically be set to the
        the deployment ID by MLOps.
        This is currently true for all supported event types.
        :return: True if entity is a deployment
        """
        return True

    def set_entity_id(self, entity_id):
        """
        The MLOps instance knows its deployment ID;
        when entity_id should be deployment ID, it can set this automatically.
        :param entity_id: ObjectID for deployment or other entity
        """
        self._entity_id = entity_id
