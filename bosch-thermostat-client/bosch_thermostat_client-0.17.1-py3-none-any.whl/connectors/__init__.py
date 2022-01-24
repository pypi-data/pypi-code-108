from .http import HttpConnector
from .ivt import IVTXMPPConnector
from .nefit import NefitConnector
from .easycontrol import EasycontrolConnector

from bosch_thermostat_client.const import HTTP


def connector_ivt_chooser(session_type):
    return HttpConnector if session_type.upper() == HTTP else IVTXMPPConnector


__all__ = [
    "NefitConnector",
    "IVTXMPPConnector",
    "HttpConnector",
    "EasycontrolConnector",
]
