from enum import Enum
from datetime import datetime
from typing import Optional, List


class ProcessData:
    ID_object: int
    ID_polygon: int
    position: int
    title: str
    type: None
    icon: str
    mode: int
    created_at: datetime
    updated_at: datetime
    ID_object_process_read: int
    ID_process_write: int
    ID_process_read: int

    def __init__(self, ID_object: int, ID_polygon: int, position: int, title: str, type: None, icon: str, mode: int,
                 created_at: datetime, updated_at: datetime, ID_object_process_read: int, ID_process_write: int,
                 ID_process_read: int) -> None:
        self.ID_object = ID_object
        self.ID_polygon = ID_polygon
        self.position = position
        self.title = title
        self.type = type
        self.icon = icon
        self.mode = mode
        self.created_at = created_at
        self.updated_at = updated_at
        self.ID_object_process_read = ID_object_process_read
        self.ID_process_write = ID_process_write
        self.ID_process_read = ID_process_read


class AnalogType(Enum):
    INPUT = "input"


class AnalogData:
    ID_analog_math: int
    ID_analog: int
    type: AnalogType
    math: str
    created_at: datetime
    updated_at: datetime
    ID_aux: int
    max_voltage: Optional[int]
    max_value: Optional[int]

    def __init__(self, ID_analog_math: int, ID_analog: int, type: AnalogType, math: str, created_at: datetime,
                 updated_at: datetime, ID_aux: int, max_voltage: Optional[int], max_value: Optional[int]) -> None:
        self.ID_analog_math = ID_analog_math
        self.ID_analog = ID_analog
        self.type = type
        self.math = math
        self.created_at = created_at
        self.updated_at = updated_at
        self.ID_aux = ID_aux
        self.max_voltage = max_voltage
        self.max_value = max_value


class ExpansionData:
    ID_AUX_station: int
    ID_station: int
    title: str
    output: int
    type: int
    expansion: int
    local: int
    settings: None
    created_at: datetime
    updated_at: datetime
    ID_aux_expansion: int
    ID_expansion_version: int
    ID_expansion: int
    pan: int
    address: int

    def __init__(self, ID_AUX_station: int, ID_station: int, title: str, output: int, type: int, expansion: int,
                 local: int, settings: None, created_at: datetime, updated_at: datetime, ID_aux_expansion: int,
                 ID_expansion_version: int, ID_expansion: int, pan: int, address: int) -> None:
        self.ID_AUX_station = ID_AUX_station
        self.ID_station = ID_station
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


class ReaderData:
    ID_object_reader: int
    ID_object: int
    created_at: datetime
    updated_at: datetime
    ID_polygon: int
    title: str
    type: int
    icon: str
    mode: int
    ID_aux_station: int
    ID_AUX_station: int
    ID_station: int
    output: int
    expansion: int
    local: int
    settings: Optional[str]
    ID_org: int
    ID_station_type: int
    serial: int
    code: str
    active: int
    token: int
    location: str
    number: str
    position: int
    Expansion: Optional[List[ExpansionData]] = []
    Analog: Optional[List[AnalogData]] = []

    def __init__(self, ID_object_reader: int, ID_object: int, position: int, created_at: datetime,
                 updated_at: datetime, ID_polygon: int, title: str, type: int, icon: str, mode: int,
                 ID_aux_station: int, ID_AUX_station: int, ID_station: int, output: int, local: int,
                 settings: Optional[str], ID_org: int, ID_station_type: int, expansion: int, serial: int, code: str, active: int,
                 token: int, location: str, number: str, Expansion: Optional[List[ExpansionData]] = None,
                 Analog: Optional[List[AnalogData]] = None) -> None:
        self.ID_object_reader = ID_object_reader
        self.ID_object = ID_object
        self.position = position
        self.created_at = created_at
        self.updated_at = updated_at
        self.ID_polygon = ID_polygon
        self.title = title
        self.type = type
        self.icon = icon
        self.mode = mode
        self.ID_aux_station = ID_aux_station
        self.ID_AUX_station = ID_AUX_station
        self.ID_station = ID_station
        self.output = output
        self.local = local
        self.settings = settings
        self.ID_org = ID_org
        self.ID_station_type = ID_station_type
        self.serial = serial
        self.code = code
        self.active = active
        self.token = token
        self.location = location
        self.number = number
        self.expansion = expansion
        self.Expansion = []
        self.Analog = []
        if Expansion:
            for param in Expansion:
                self.Expansion.append(ExpansionData(**dict(param)))
        if Analog:
            for param in Analog:
                self.Analog.append(AnalogData(**dict(param)))


class Object:
    ID_object: int
    ID_polygon: int
    position: int
    title: str
    type: str
    icon: str
    mode: int
    created_at: datetime
    updated_at: datetime
    reader: Optional[List[ReaderData]] = []
    process: Optional[List[ProcessData]] = []

    def __init__(self, ID_object: int, ID_polygon: int, title: str, type: str, icon: str, mode: int,
                 created_at: datetime, updated_at: datetime, position: int, Reader: Optional[List[ReaderData]] = None,
                 Process: Optional[List[ProcessData]] = None) -> None:
        self.ID_object = ID_object
        self.ID_polygon = ID_polygon
        self.position = position
        self.title = title
        self.type = type
        self.icon = icon
        self.mode = mode
        self.created_at = created_at
        self.updated_at = updated_at
        self.reader = []
        self.process = []
        if Reader:
            for param in Reader:
                self.reader.append(ReaderData(**dict(param)))

        if Process:
            for param in Process:
                self.process.append(ProcessData(**dict(param)))


class ObjectData:
    object: List[Object]

    def __init__(self, data) -> None:
        self.data = []
        for param in data:
            self.data.append(Object(**dict(param)))
