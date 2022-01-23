from datetime import datetime
from typing import List, Optional


class AnalogClass:
    ID_analog_math: int
    ID_analog: int
    type: str
    math: str
    created_at: datetime
    updated_at: datetime
    ID_aux: int
    max_voltage: int
    max_value: int

    def __init__(self, ID_analog_math: int, ID_analog: int, type: str, math: str, created_at: datetime,
                 updated_at: datetime, ID_aux: int, max_voltage: int, max_value: int) -> None:
        self.ID_analog_math = ID_analog_math
        self.ID_analog = ID_analog
        self.type = type
        self.math = math
        self.created_at = created_at
        self.updated_at = updated_at
        self.ID_aux = ID_aux
        self.max_voltage = max_voltage
        self.max_value = max_value


class Aux:
    ID_AUX_station: int
    ID_station: int
    title: str
    stationTitle: str
    output: int
    type: int
    expansion: int
    local: int
    settings: None
    created_at: datetime
    updated_at: datetime
    ID_aux_expansion: Optional[int]
    ID_expansion_version: Optional[int]
    ID_expansion: Optional[int]
    pan: Optional[int]
    address: Optional[int]
    ID_org: Optional[int]
    ID_station_type: Optional[int]
    serial: Optional[int]
    code: Optional[str]
    active: Optional[int]
    token: Optional[int]
    location: Optional[str]
    number: Optional[str]
    Analog: Optional[AnalogClass]

    def __init__(self, ID_AUX_station: int, ID_station: int, title: str, output: int, type: int, expansion: int,
                 local: int, settings: None, created_at: datetime, updated_at: datetime, ID_org: Optional[int],
                 ID_station_type: Optional[int], serial: Optional[int], code: Optional[str], active: Optional[int],
                 token: Optional[int], location: Optional[str], number: Optional[str],
                 Analog: Optional[AnalogClass] = None,
                 ID_aux_expansion: Optional[int] = 0, ID_expansion_version: Optional[int] = 0,
                 ID_expansion: Optional[int] = 0, pan: Optional[int] = 0, address: Optional[int] = 0,
                 stationTitle: str = '') -> None:
        self.ID_AUX_station = ID_AUX_station
        self.ID_station = ID_station
        self.stationTitle = stationTitle
        self.title = title
        self.output = output
        self.type = type
        self.expansion = expansion
        self.local = local
        self.settings = settings
        self.created_at = created_at
        self.updated_at = updated_at
        self.ID_aux_expansion = ID_aux_expansion
        self.ID_expansion_version = ID_expansion_version
        self.ID_expansion = ID_expansion
        self.pan = pan
        self.address = address
        self.ID_org = ID_org
        self.ID_station_type = ID_station_type
        self.serial = serial
        self.code = code
        self.active = active
        self.token = token
        self.location = location
        self.number = number
        if Analog != None:
            self.Analog = AnalogClass(**dict(Analog))


class AuxStationData:
    aux: Aux

    def __init__(self, data) -> None:
        self.aux = Aux(**dict(data))


def AuxOnIDLocal(AuxData: List[Aux], ID_aux):
    for aux in AuxData:
        if int(aux.ID_AUX_station) == int(ID_aux):
            return aux

    return None
