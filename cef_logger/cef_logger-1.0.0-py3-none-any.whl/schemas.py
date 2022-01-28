import enum
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Callable, Iterator, Union

from pydantic import BaseModel, Field


__all__ = (
    'MandatoryFields',
    'ExtensionFields',
)

MAC_REGEX = r'^([A-F0-9]{2}:){5}[A-F0-9]{2}$'
HOSTNAME_REGEX = r'^[A-Za-z0-9][A-Za-z0-9\.\-]*(?!\n)$'


class DateTime(datetime):

    DATETIME_FORMATS = (
        '%b %d %H:%M:%S.%f %Z%z',
        '%b %d %H:%M:%S %Z%z',
        '%b %d %H:%M:%S.%f',
        '%b %d %H:%M:%S',
        '%b %d %Y %H:%M:%S.%f %Z%z',
        '%b %d %Y %H:%M:%S %Z%z',
        '%b %d %Y %H:%M:%S.%f',
        '%b %d %Y %H:%M:%S',
    )

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        yield cls.validate_dt_formats

    @classmethod
    def validate_dt_formats(
        cls,
        value: Union[datetime, int, float, str]
    ) -> Union[int, float, str]:
        if isinstance(value, datetime):
            return value.strftime(cls.DATETIME_FORMATS[4])
        elif isinstance(value, (int, float)):
            datetime.fromtimestamp(value)
            return value
        elif isinstance(value, str):
            if value.isdigit():
                try:
                    datetime.fromtimestamp(float(value))
                except Exception as ex:
                    raise ValueError(str(ex))
                return value
            else:
                errors = []

                for dt_format in cls.DATETIME_FORMATS:
                    try:
                        datetime.strptime(value, dt_format)
                    except ValueError as ex:
                        errors.append(str(ex))
                    else:
                        return value

                raise ValueError('\n  '.join(errors))

        raise TypeError(f'Datetime came of type: {type(value)} '
                        f'expected: str, int, float')


class SeverityInts(enum.IntEnum):
    LOW_0 = 0
    LOW_1 = 1
    LOW_2 = 2
    LOW_3 = 3
    MEDIUM_1 = 4
    MEDIUM_2 = 5
    MEDIUM_3 = 6
    HIGH_1 = 7
    HIGH_2 = 8
    VERY_HIGH_1 = 9
    VERY_HIGH_2 = 10


class SeverityStrings(enum.Enum):
    Unknown = 'Unknown'
    Low = 'Low'
    Medium = 'Medium'
    High = 'High'
    Very_High = 'Very-High'


class MandatoryFields(BaseModel):
    Version: int
    DeviceVendor: str
    DeviceProduct: str
    DeviceVersion: str
    DeviceEventClassID: Union[int, str]
    Name: str
    Severity: Union[SeverityInts, SeverityStrings]


class ExtensionFields(BaseModel):
    act: str = Field(default=None, max_length=63)
    app: str = Field(default=None, max_length=31)

    c6a1: IPv6Address = Field(default=None)
    c6a1Label: str = Field(default=None, max_length=1023)
    c6a2: IPv6Address = Field(default=None)
    c6a2Label: str = Field(default=None, max_length=1023)
    c6a3: IPv6Address = Field(default=None)
    c6a3Label: str = Field(default=None, max_length=1023)
    c6a4: IPv6Address = Field(default=None)
    c6a4Label: str = Field(default=None, max_length=1023)

    cat: str = Field(default=None, max_length=1023)

    cfp1: float = Field(default=None)
    cfp1Label: str = Field(default=None, max_length=1023)
    cfp2: float = Field(default=None)
    cfp2Label: str = Field(default=None, max_length=1023)
    cfp3: float = Field(default=None)
    cfp3Label: str = Field(default=None, max_length=1023)
    cfp4: float = Field(default=None)
    cfp4Label: str = Field(default=None, max_length=1023)

    cn1: int = Field(default=None)
    cn1Label: str = Field(default=None, max_length=1023)
    cn2: int = Field(default=None)
    cn2Label: str = Field(default=None, max_length=1023)
    cn3: int = Field(default=None)
    cn3Label: str = Field(default=None, max_length=1023)

    cnt: int = Field(default=None)

    cs1: str = Field(default=None, max_length=4000)
    cs1Label: str = Field(default=None, max_length=1023)
    cs2: str = Field(default=None, max_length=4000)
    cs2Label: str = Field(default=None, max_length=1023)
    cs3: str = Field(default=None, max_length=4000)
    cs3Label: str = Field(default=None, max_length=1023)
    cs4: str = Field(default=None, max_length=4000)
    cs4Label: str = Field(default=None, max_length=1023)
    cs5: str = Field(default=None, max_length=4000)
    cs5Label: str = Field(default=None, max_length=1023)
    cs6: str = Field(default=None, max_length=4000)
    cs6Label: str = Field(default=None, max_length=1023)

    destinationDnsDomain: str = Field(
        default=None, max_length=255, regex=HOSTNAME_REGEX,
    )
    destinationServiceName: str = Field(default=None, max_length=1023)
    destinationTranslatedAddress: IPv4Address = Field(default=None)
    destinationTranslatedPort: int = Field(default=None, gt=0, le=65535)

    deviceCustomDate1: DateTime = Field(default=None)
    deviceCustomDate1Label: str = Field(default=None, max_length=1023)
    deviceCustomDate2: DateTime = Field(default=None)
    deviceCustomDate2Label: str = Field(default=None, max_length=1023)

    deviceDirection: int = Field(default=None, ge=0, le=1)
    deviceDnsDomain: str = Field(
        default=None, max_length=255, regex=HOSTNAME_REGEX,
    )
    deviceExternalId: str = Field(default=None, max_length=255)
    deviceFacility: str = Field(default=None, max_length=1023)
    deviceInboundInterface: str = Field(default=None, max_length=128)
    deviceNtDomain: str = Field(default=None, max_length=255)
    deviceOutboundInterface: str = Field(default=None, max_length=128)
    devicePayloadId: str = Field(default=None, max_length=128)
    deviceProcessName: str = Field(default=None, max_length=1023)
    deviceTranslatedAddress: IPv4Address = Field(default=None)

    dhost: str = Field(default=None, max_length=255, regex=HOSTNAME_REGEX)
    dmac: str = Field(default=None, regex=MAC_REGEX)
    dntdom: str = Field(default=None, max_length=255)
    dpid: int = Field(default=None)
    dpriv: int = Field(default=None)
    dproc: str = Field(default=None, max_length=1023)
    dpt: int = Field(default=None, gt=0, le=65535)
    dst: IPv4Address = Field(default=None)
    dtz: str = Field(default=None, max_length=255)
    duid: str = Field(default=None, max_length=1023)
    duser: str = Field(default=None, max_length=1023)
    dvc: IPv4Address = Field(default=None)
    dvchost: str = Field(default=None, max_length=100, regex=HOSTNAME_REGEX)
    dvcmac: str = Field(default=None, regex=MAC_REGEX)
    dvcpid: int = Field(default=None)
    end: DateTime = Field(default=None)
    externalId: str = Field(default=None, max_length=40)

    fileCreateTime: DateTime = Field(default=None)
    fileHash: str = Field(default=None, max_length=255)
    fileId: str = Field(default=None, max_length=1023)
    fileModificationTime: DateTime = Field(default=None)
    filePath: str = Field(default=None, max_length=1023)
    filePermission: str = Field(default=None, max_length=1023)
    fileType: str = Field(default=None, max_length=1023)

    flexDate1: DateTime = Field(default=None)
    flexDate1Label: str = Field(default=None, max_length=128)
    flexString1: str = Field(default=None, max_length=1023)
    flexString1Label: str = Field(default=None, max_length=128)
    flexString2: str = Field(default=None, max_length=1023)
    flexString2Label: str = Field(default=None, max_length=128)

    fname: str = Field(default=None, max_length=1023)
    fsize: int = Field(default=None)
    in_: int = Field(default=None)
    msg: str = Field(default=None, max_length=1023)

    oldFileCreateTime: DateTime = Field(default=None)
    oldFileHash: str = Field(default=None, max_length=255)
    oldFileId: str = Field(default=None, max_length=1023)
    oldFileModificationTime: DateTime = Field(default=None)
    oldFileName: str = Field(default=None, max_length=1023)
    oldFilePath: str = Field(default=None, max_length=1023)
    oldFilePermission: str = Field(default=None, max_length=1023)
    oldFileSize: int = Field(default=None)
    oldFileType: str = Field(default=None, max_length=1023)

    out: int = Field(default=None)
    outcome: str = Field(default=None, max_length=63)
    proto: str = Field(default=None, max_length=31)
    reason: str = Field(default=None, max_length=1023)
    request: str = Field(default=None, max_length=1023)
    requestClientApplication: str = Field(default=None, max_length=1023)
    requestContext: str = Field(default=None, max_length=2048)
    requestCookies: str = Field(default=None, max_length=1023)
    requestMethod: str = Field(default=None, max_length=1023)
    rt: DateTime = Field(default=None)

    shost: str = Field(default=None, max_length=1023, regex=HOSTNAME_REGEX)
    smac: str = Field(default=None, regex=MAC_REGEX)
    sntdom: str = Field(default=None, max_length=255)
    sourceDnsDomain: str = Field(
        default=None, max_length=255, regex=HOSTNAME_REGEX,
    )
    sourceServiceName: str = Field(default=None, max_length=1023)
    sourceTranslatedAddress: IPv4Address = Field(default=None)
    sourceTranslatedPort: int = Field(default=None, gt=0, le=65535)

    spid: int = Field(default=None)
    spriv: str = Field(default=None, max_length=1023)
    sproc: str = Field(default=None, max_length=1023)
    spt: int = Field(default=None, gt=0, le=65535)
    src: IPv4Address = Field(default=None)
    start: DateTime = Field(default=None)
    suid: str = Field(default=None, max_length=1023)
    suser: str = Field(default=None, max_length=1023)
    type: int = Field(default=None)
