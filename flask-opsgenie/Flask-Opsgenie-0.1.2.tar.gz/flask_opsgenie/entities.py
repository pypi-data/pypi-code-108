from enum import Enum
from typing import Any, Dict, List
from flask_opsgenie.exceptions import InvalidOpsgenieAlertParams

class AlertType(Enum):

    STATUS_ALERT = 1
    LATENCY_ALERT = 2
    EXCEPTION = 3
    MANUAL = 4


class AlertPriority(Enum):

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"


class OpsgenieAlertParams:

    def __init__(self, opsgenie_token:str=None, alert_tags:List[str]=None, alert_alias:str=None,
                 alert_status_alias:str=None, alert_latency_alias:str=None, alert_exception_alias:str=None,
                 no_traceback:str=None,alert_priority:str=None, alert_responder:Dict[str, str]=None,
                 opsgenie_api_base:str=None, alert_details:Dict[str, Any]=None):
        self.opsgenie_token = opsgenie_token
        if not self.opsgenie_token:
            raise InvalidOpsgenieAlertParams(f'Missing opsgenie api token')
        self.alert_tags = alert_tags

        # set a default tag
        if not self.alert_tags:
            self.alert_tags = ["flask-alert"]
        self.alert_details = alert_details

        # set default service id if not present
        if not self.alert_details.get("service_id"):
            self.alert_details["service_id"] = f'flask-service-{self.alert_details["host"]}'

        self.alert_alias = alert_alias
        self.alert_status_alias = alert_status_alias
        self.alert_latency_alias = alert_latency_alias
        self.alert_exception_alias = alert_exception_alias
        self.no_traceback = no_traceback
        self.alert_priority = AlertPriority(alert_priority)
        self.alert_responder = alert_responder
        self.opsgenie_api_base = opsgenie_api_base
