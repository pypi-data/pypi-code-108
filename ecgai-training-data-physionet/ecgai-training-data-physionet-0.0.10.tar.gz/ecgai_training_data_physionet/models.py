import json
from typing import List, Optional

from ecgai_logging.log_decorator import log
from pydantic import BaseModel, ValidationError
from pydantic.utils import to_camel


# def to_camel(string: str) -> str:
#     return ''.join(word.capitalize() for word in string.split('_'))
def module_name():
    return __name__


class MyBaseModel(BaseModel):
    def __hash__(self):  # make hashable BaseModel subclass
        return hash((type(self),) + tuple(self.__dict__.values()))

    class Config:
        alias_generator = to_camel
        # by_alias = True

    @classmethod
    @log
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    @log
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))


class DiagnosticCode(MyBaseModel):
    scp_code: str
    description: str
    confidence: Optional[str]

    @classmethod
    @log
    def create(cls, scp_code: str, description: str, confidence: str = ''):
        d = dict(ScpCode=scp_code, Description=description, Confidence=confidence)
        return cls.from_dict(d)


class EcgLeadRecord(MyBaseModel):
    lead_name: str  # = Field(..., alias='leadName')
    signal: List[float]  # = Field(..., alias='signal')

    @classmethod
    @log
    def create(cls, lead_name: str, signal: List[float]):
        try:
            d = dict(LeadName=lead_name, Signal=signal)
            return cls.from_dict(d)
        except ValidationError as e:
            # logging.error(e)
            raise e


class EcgRecord(MyBaseModel):
    record_id: int
    record_name: str  # = Field(..., alias='recordId')
    age: Optional[int] = None
    sex: Optional[str] = None
    report: Optional[str] = None
    diagnostic_codes: list[DiagnosticCode] = []
    # record_name: str
    # units:str
    database_name: str  # = Field(..., alias='databaseName')
    sample_rate: int  # = Field(..., alias='sampleRate')
    leads: List[EcgLeadRecord]  # = Field(..., alias='leads')

    @classmethod
    @log
    def create(cls, record_id: int, record_name: str, database_name: str, sample_rate: int, leads: List[EcgLeadRecord],
               age: int = None, sex: str = None, report: str = None, diagnostic_codes=None
               ):
        if diagnostic_codes is None:
            diagnostic_codes = []
        d = dict(
            RecordId=record_id,
            RecordName=record_name,
            Age=age,
            Sex=sex,
            Report=report,
            DiagnosticCodes=diagnostic_codes,
            DatabaseName=database_name,
            SampleRate=sample_rate,
            Leads=leads,
        )
        return cls.from_dict(d)
