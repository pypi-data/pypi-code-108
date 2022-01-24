from .ivt import IVTGateway
from .nefit import NefitGateway
from .easycontrol import EasycontrolGateway
from bosch_thermostat_client.const.ivt import IVT
from bosch_thermostat_client.const.nefit import NEFIT
from bosch_thermostat_client.const.easycontrol import EASYCONTROL


def gateway_chooser(device_type=IVT):
    return {IVT: IVTGateway, NEFIT: NefitGateway, EASYCONTROL: EasycontrolGateway}[
        device_type
    ]
