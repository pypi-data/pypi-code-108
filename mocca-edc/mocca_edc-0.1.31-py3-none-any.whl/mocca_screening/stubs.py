from datetime import datetime
from typing import Protocol, Type

from edc_model.stubs import BaseUuidModelStub
from edc_screening.stubs import (
    SubjectScreeningModelStub as BaseSubjectScreeningModelStub,
)


class MoccaSiteStub(BaseUuidModelStub, Protocol):
    name: str


class MoccaRegisterModelStub(BaseUuidModelStub, Protocol):
    age_in_years: int
    birth_year: int
    gender: str
    mocca_site: MoccaSiteStub
    mocca_study_identfier: str
    report_datetime: datetime
    screening_identifier: str


class MoccaRegisterFormStub(Protocol):
    cleaned_data: dict
    instance: MoccaRegisterModelStub
    model: Type[MoccaRegisterModelStub]

    def clean(self) -> dict:
        ...


class MoccaRegisterFormValidatorStub(MoccaRegisterFormStub, Protocol):
    def get_age(self) -> int:
        ...


class SubjectScreeningModelStub(BaseSubjectScreeningModelStub, Protocol):
    care: str
    mocca_register: MoccaRegisterModelStub
    pregnant: str
    requires_acute_care: str
    unsuitable_for_study: str
    willing_to_consent: str
