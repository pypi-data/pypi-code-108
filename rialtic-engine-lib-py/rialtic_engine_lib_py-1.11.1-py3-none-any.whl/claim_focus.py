import datetime as dt
import re
from enum import Enum
from typing import Dict, List, Optional, Union, cast, Tuple, Set, Type

from fhir.resources.address import Address
from fhir.resources.claim import Claim, ClaimInsurance, ClaimItem, ClaimRelated, ClaimSupportingInfo, ClaimDiagnosis
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.coverage import Coverage
from fhir.resources.fhirtypes import Date, Decimal
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.location import Location
from fhir.resources.money import Money
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.relatedperson import RelatedPerson
from fhir.resources.resource import Resource
from fhir.resources.servicerequest import ServiceRequest
from schema.insight_engine_request import InsightEngineRequest

from enginelib.claim_insurance_focus import (ClaimInsuranceFocus,
                                             find_primary_insurance)
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.comparator import ClaimComparator, CompareResult
from enginelib.errors import ClaimError, Error, MissingFieldError
from enginelib.types import Period


class ClaimTypeFocus(str, Enum):
    PROFESSIONAL = "professional"
    INSTITUTIONAL = "institutional"
    DENTAL = "dental"
    PHARMACY = "pharmacy"

    @staticmethod
    def get_claim_type_set():
        return (
            (
                {"cms1500", "837p", "005010x222", "professional", "vision"},
                ClaimTypeFocus.PROFESSIONAL
            ),
            (
                {"ub04", "837i", "005010x223", "institutional"},
                ClaimTypeFocus.INSTITUTIONAL
            ),
            (
                {"ada2006", "837d", "005010x224", "dental", "oral"},
                ClaimTypeFocus.DENTAL
            ),
            (
                {"837", "ncpdpd0", "ncpdpbatch12",
                 "ncpdpwcpcucf", "pharmacy", "drug"},
                ClaimTypeFocus.PHARMACY
            )
        )

    @classmethod
    def from_string(cls, value: str) -> "ClaimTypeFocus":
        normalized_value = re.sub("[^0-9a-z]", "", value.lower())

        for values, claim_type in cls.get_claim_type_set():
            if normalized_value in values:
                return cls.__new__(cls, claim_type)

        raise ClaimError("Unsupported claim type %s" % value)


class ClaimFocus:
    _fields_looked_at: Set[str] = set()

    def __init__(self, claim: Claim, request: InsightEngineRequest = None):
        self.claim = claim
        self.request = request if request is not None else InsightEngineRequest(
            claim=claim)
        self._contained: Optional[Dict[str, Resource]] = None
        self._lines: Optional[List[ClaimLineFocus]] = None

        self._supporting_info_category_codes_cache: Dict[int, List[str]] = dict()

    @property
    def contained(self) -> Dict[str, Resource]:
        if self._contained is not None:
            return self._contained

        self._contained = dict()
        if getattr(self.claim, "contained", None):
            resources = [cast(Resource, elem) for elem in self.claim.contained]
            self._contained = {
                resource.id: resource for resource in resources
                if resource.id is not None
            }

        return self._contained

    def _error(self, error_class: Type[Error], message: str):
        try:
            identifier = cast(Identifier, self.request.claim.identifier[0])
            claim_num = identifier.value
            msg = f'{message} [claim {claim_num}].'
        except (AttributeError, TypeError, IndexError):
            msg = f'{message} [unidentified claim: claimNum missing from the claim].'

        return error_class(msg)

    def _missing_field_error(self, field_name: str = 'unspecified'):
        message = f'Field `{field_name}` was not found on this claim.'
        return self._error(MissingFieldError, message)

    @property
    def diagnosis_codes(self) -> List[str]:
        try:
            return [
                coding.code
                for codings in [
                    cast(List[Coding], c.coding)
                    for c in cast(List[CodeableConcept],
                                  [cast(ClaimDiagnosis, concept).diagnosisCodeableConcept for concept in
                                   self.request.claim.diagnosis])]
                for coding in codings
            ]
        except (AttributeError, TypeError):
            pass

        return list()

    @property
    def reference_claim_num(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            related = cast(ClaimRelated, self.claim.related[0])
            identifier = cast(Identifier, related.reference)
            return identifier.value.strip().lower()
        except (AttributeError, TypeError):
            pass

        raise self._missing_field_error('referenceClaimNum')

    @property
    def lines(self) -> Optional[List[ClaimLineFocus]]:
        if self._lines is not None:
            return self._lines

        if self.request is None:
            self.request = InsightEngineRequest.construct(claim=self.claim)

        self._lines = [ClaimLineFocus(cast(ClaimItem, c), self.request)
                       for c in self.claim.item]
        return self._lines

    @property
    def billable_period(self) -> Period:
        try:
            period = cast(Period, self.claim.billablePeriod)
            if period.start is not None and period.end is not None:
                return Period(start=period.start, end=period.end)
        except AttributeError:
            pass

        raise self._missing_field_error('billablePeriod')

    @property
    def _svc_facility(self) -> Location:
        """
        [new FHIR mapping]
        """
        ref = cast(Reference, self.claim.facility).reference
        ref = self._cleanup(ref)
        resource = self.contained[ref]
        if resource.resource_type != 'Location':
            raise TypeError()

        return cast(Location, resource)

    @property
    def facility_place_of_service(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            location = self._svc_facility
            physical_type = cast(CodeableConcept, location.physicalType)
            coding = cast(Coding, physical_type.coding[0])
            return coding.code.strip().lower()
        except (AttributeError, KeyError, TypeError, IndexError):
            raise self._missing_field_error('facilityPlaceOfService')

    @property
    def svc_facility_name(self) -> str:
        try:
            facility = self._svc_facility
            return facility.name.strip().lower()
        except (AttributeError, KeyError, TypeError):
            raise self._missing_field_error('svcFacilityName')

    def _svc_facility_add(self, index: int) -> str:
        """
        [new FHIR mapping]
        """
        facility = self._svc_facility
        address = cast(Address, facility.address)
        return address.line[index].strip().lower()

    @property
    def svc_facility_add1(self) -> str:
        try:
            return self._svc_facility_add(0)
        except (AttributeError, KeyError, TypeError, IndexError):
            raise self._missing_field_error('svcFacilityAdd1')

    @property
    def svc_facility_add2(self) -> str:
        try:
            return self._svc_facility_add(1)
        except (AttributeError, KeyError, TypeError, IndexError):
            raise self._missing_field_error('svcFacilityAdd2')

    @property
    def svc_facility_city(self) -> str:
        try:
            facility = self._svc_facility
            city = cast(Address, facility.address).city
            return city.strip().lower()
        except (AttributeError, KeyError, TypeError):
            raise self._missing_field_error('svcFacilityCity')

    @property
    def svc_facility_state(self) -> str:
        try:
            facility = self._svc_facility
            state = cast(Address, facility.address).state
            return state.strip().lower()
        except (AttributeError, KeyError, TypeError):
            raise self._missing_field_error('svcFacilityState')

    @property
    def svc_facility_zip(self) -> str:
        try:
            facility = self._svc_facility
            postal_code = cast(Address, facility.address).postalCode
            return postal_code.strip().lower()
        except (AttributeError, KeyError, TypeError):
            raise self._missing_field_error('svcFacilityZip')

    @property
    def _billing_provider(self) -> Practitioner:
        ref = cast(Reference, self.claim.provider).reference
        ref = self._cleanup(ref)
        resource = self.contained[ref]
        if resource.resource_type != 'PractitionerRole':
            raise TypeError()

        practitioner_role = cast(PractitionerRole, resource)
        ref = cast(Reference, practitioner_role.practitioner).reference
        ref = self._cleanup(ref)
        resource = self.contained[ref]
        if resource.resource_type != 'Practitioner':
            raise TypeError()

        # Stephanie: no need to check this explicitly as only
        #     billing providers are mapped to claim.provider.
        # practitioner = cast(Practitioner, resource)
        # if '85' not in practitioner.id:
        #     raise TypeError()

        return cast(Practitioner, resource)

    @staticmethod
    def _slash_suffix(text: str) -> str:
        match = re.search('/([^/]*)$', text)
        if match is not None:
            return match.group(1)
        return text

    @property
    def _prov_tax_id_and_qual(self) -> Tuple[str, str]:
        practitioner = self._billing_provider
        for identifier in cast(List[Identifier], practitioner.identifier):
            try:
                if self._slash_suffix(identifier.system) != 'XX':
                    tax_id = identifier.value.strip().lower()
                    tax_id_qual = self._slash_suffix(identifier.system.strip()).lower()
                    return tax_id, tax_id_qual
            except AttributeError:
                pass

        raise AttributeError()

    @property
    def prov_tax_id_qual(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            _, tax_id_qual = self._prov_tax_id_and_qual
            return tax_id_qual
        except (AttributeError, TypeError, KeyError):
            pass

        raise self._missing_field_error('provTaxIDQual')

    @property
    def prov_tax_id(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            tax_id, _ = self._prov_tax_id_and_qual
            return tax_id
        except (AttributeError, TypeError, KeyError):
            pass

        raise self._missing_field_error('provTaxID')

    @property
    def bill_prov_npi(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            practitioner = self._billing_provider
            for identifier in cast(List[Identifier], practitioner.identifier):
                try:
                    if identifier.system.endswith('XX'):
                        return identifier.value.strip().lower()
                except AttributeError:
                    pass
        except (AttributeError, TypeError, KeyError):
            pass

        raise self._missing_field_error('billProvNPI')

    @property
    def bill_prov_last_name(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            practitioner = self._billing_provider
            name = cast(HumanName, practitioner.name[0])
            if name.family:
                return name.family.strip().lower()

        except (AttributeError, TypeError, KeyError):
            pass

        raise self._missing_field_error('billProvLastName')

    @property
    def bill_prov_taxonomy(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            ref = cast(Reference, self.claim.provider).reference
            ref = self._cleanup(ref)
            resource = self.contained[ref]
            if resource.resource_type != 'PractitionerRole':
                raise TypeError()

            practitioner_role = cast(PractitionerRole, resource)
            specialty = cast(CodeableConcept, practitioner_role.specialty[0])
            coding = cast(Coding, specialty.coding[0])
            if coding.code:
                return coding.code.strip().lower()
        except (AttributeError, TypeError, KeyError):
            pass

        raise self._missing_field_error('billProvTaxonomy')

    @property
    def patient(self) -> Patient:
        try:
            ref = cast(Reference, self.claim.patient).reference
            ref = self._cleanup(ref)
        except AttributeError:
            raise self._error(ClaimError, f'reference to patient not found on claim')

        try:
            return cast(Patient, self.contained[ref])
        except KeyError:
            raise self._error(ClaimError, f'Patient with id: {ref} not found in contained objects')

    @property
    def patient_zip(self) -> str:
        try:
            address = cast(Address, self.patient.address[0])
            z = address.postalCode
            if z:
                return z
        except (AttributeError, IndexError, TypeError):
            pass

        raise self._missing_field_error('patientZip')

    @property
    def patient_birthDate(self) -> dt.date:
        """
        Birth Date of patient
        """
        try:
            patient = self.patient
        except ClaimError:
            raise self._error(ClaimError, 'Patient not found on claim')

        try:
            birthDate = patient.birthDate
            return birthDate
        except AttributeError:
            raise self._error(ClaimError, f'Birthdate not found on patient with id {self.patient.id}.')

    @property
    def provider(self) -> Union[Practitioner, Organization, PractitionerRole]:
        try:
            ref = cast(Reference, self.claim.provider).reference
            ref = self._cleanup(ref)
        except AttributeError:
            raise ClaimError("reference to provider not found on the claim")
        try:
            return self.contained[ref]
        except KeyError:
            raise ClaimError(
                f"provider with id: {ref} not found in contained objects")

    def _supporting_info_category_codes(self, info: ClaimSupportingInfo) -> List[str]:
        """
        Returns:
            All codes in info.category.coding[·].code

        Raises:
            AttributeError
            TypeError
        """
        seq = info.sequence
        if seq not in self._supporting_info_category_codes_cache:
            codeable_concept = cast(CodeableConcept, info.category)
            coding = cast(List[Coding], codeable_concept.coding)
            codes = [c.code.strip().lower() for c in coding]
            self._supporting_info_category_codes_cache[seq] = codes

        return self._supporting_info_category_codes_cache[seq]

    def _supporting_info_with_given_code(self, *args: str) -> List[ClaimSupportingInfo]:
        """
        Returns:
            List containing all ClaimSupportingInfo objects in
            self.claim.supportingInfo for which key appears in
            category.coding[·].code
        """
        info_list: List[ClaimSupportingInfo] = list()
        keys = [key.strip().lower() for key in args]

        try:
            supporting_info = cast(List[ClaimSupportingInfo], self.claim.supportingInfo)
            for info in supporting_info:
                try:
                    codes = self._supporting_info_category_codes(info)
                    if any(key in codes for key in keys):
                        info_list.append(info)
                except (AttributeError, TypeError):
                    continue

        except (AttributeError, TypeError):
            pass

        return info_list

    @property
    def info_indicator(self) -> bool:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('info')
        return len(info_list) > 0

    @property
    def supporting_info(self) -> List[str]:
        """
        [new FHIR mapping]

        Returns:
            List of all possible values for supportingInfo field.

        Raises:
            ClaimError
        """
        info_list = self._supporting_info_with_given_code('info')
        all_info: Set[str] = set()

        try:
            for info in info_list:
                try:
                    codes = set(self._supporting_info_category_codes(info))
                    codes.remove('info')
                    all_info.update(codes)
                except (AttributeError, TypeError, KeyError):
                    continue

        except (AttributeError, TypeError, IndexError):
            pass

        return list(all_info)

    @property
    def cob_paid_amt(self) -> Decimal:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('D')
        if len(info_list) > 1:
            raise ClaimError('Too many candidate values for field cobPaidAmt.')

        try:
            info = info_list[0]
            quantity = cast(Quantity, info.valueQuantity)
            return quantity.value
        except (AttributeError, TypeError, IndexError):
            pass

        raise self._missing_field_error('cobPaidAmt')

    @property
    def date_current_illness(self) -> dt.date:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('431')
        if len(info_list) > 1:
            raise self._error(ClaimError, 'Too many candidate values for field dateCurrentIllness.')

        try:
            info = info_list[0]
            period = cast(Period, info.timingPeriod)
            if period.start:
                return period.start

        except (AttributeError, TypeError, IndexError):
            pass

        raise self._missing_field_error('dateCurrentIllness')

    def other_date(self, qualifier: str) -> dt.date:
        """
        [new FHIR mapping]
        """
        other_date_qualifiers = ('453', '454', '304', '484', '455', '471', '090', '091', '444', '050', '439')
        if qualifier not in other_date_qualifiers:
            raise ClaimError('The given qualifier is not a valid otherDateQualifier.')

        info_list = self._supporting_info_with_given_code(qualifier)
        if len(info_list) > 1:
            raise ClaimError(f'Too many candidate values for field otherDate with qualifier {qualifier}.')

        try:
            info = info_list[0]
            period = cast(Period, info.timingPeriod)
            if period.start:
                return period.start

        except (AttributeError, TypeError, IndexError):
            pass

        raise self._error(ClaimError, f'Field otherDate for qualifier {qualifier} was not found on claim.')

    @property
    def other_date_qualifier(self) -> str:
        """
        [new FHIR mapping]

        | Field name                    | Description                                        | Qualifier |
        |-------------------------------|----------------------------------------------------|:---------:|
        | accidentDate                  | Accident                                           |    439    |
        | admitDate                     | Admission                                          |    435    |
        | dateCurrentIllness            | Onset of Current Illness or Symptom                |    431    |
        | disabilityEnd                 | Disability Period End                              |    361    |
        | disabilityStart               | Disability Period Start                            |    360    |
        | disabilityStart/disabilityEnd | Disability Dates                                   |    314    |
        | dischargeDate                 | Discharge                                          |    096    |
        | otherDate                     | Initial Treatment Date                             |    454    |
        | otherDate                     | Last Seen Date                                     |    304    |
        | otherDate                     | Acute Manifestation                                |    453    |
        | otherDate                     | Last Menstrual Period                              |    484    |
        | otherDate                     | Last X-ray Date                                    |    455    |
        | otherDate                     | Hearing and Vision Prescription Date               |    471    |
        | otherDate                     | Assumed and Relinquished Care Dates - report start |    090    |
        | otherDate                     | Assumed and Relinquished Care Dates - report end   |    091    |
        | otherDate                     | Property and Casualty Date of First Contact        |    444    |
        | otherDate                     | Repricer Received Date                             |    050    |
        | workReturnDate                | Authorized Return to Work                          |    296    |
        | workStopDate                  | DateLastWorked                                     |    297    |
        """
        message = 'This field is not supposed to be accessed directly; rather, it should be passed to the ' \
                  'other_date() method, so that the desired otherDate field can be returned.'
        raise NotImplementedError(message)

    @property
    def work_stop_date(self) -> dt.date:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('297')
        if len(info_list) > 1:
            raise self._error(ClaimError, 'Too many candidate values for field workStopDate.')

        try:
            info = info_list[0]
            period = cast(Period, info.timingPeriod)
            if period.start:
                return period.start

        except (AttributeError, TypeError, IndexError):
            pass

        raise self._missing_field_error('workStopDate')

    @property
    def work_return_date(self) -> dt.date:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('296')
        if len(info_list) > 1:
            raise self._error(ClaimError, 'Too many candidate values for field workReturnDate.')

        try:
            info = info_list[0]
            period = cast(Period, info.timingPeriod)
            if period.end:
                return period.end

        except (AttributeError, TypeError, IndexError):
            pass

        raise self._missing_field_error('workReturnDate')

    @property
    def admit_date(self) -> Date:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('435')
        if len(info_list) > 1:
            raise self._error(ClaimError, 'Too many candidate values for field admitDate.')

        try:
            info = info_list[0]
            period = cast(Period, info.timingPeriod)
            if period.start:
                return period.start

        except (AttributeError, TypeError, IndexError):
            pass

        raise self._missing_field_error('admitDate')

    @property
    def discharge_date(self) -> Date:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('096')
        if len(info_list) > 1:
            raise self._error(ClaimError, 'Too many candidate values for field dischargeDate.')

        try:
            info = info_list[0]
            period = cast(Period, info.timingPeriod)
            if period.end:
                return period.end

        except (AttributeError, TypeError, IndexError):
            pass

        raise self._missing_field_error('dischargeDate')

    @property
    def attachment(self) -> bool:
        """
        [new FHIR mapping]
        """
        info_list = self._supporting_info_with_given_code('attachment')
        return len(info_list) > 0

    @property
    def attachments(self) -> List[str]:
        """
        [OLD MAPPING]
        """
        try:
            target = list()
            info_list = cast(List[ClaimSupportingInfo], self.claim.supportingInfo)
            for info in info_list:
                category = cast(CodeableConcept, info.category)
                code = cast(Coding, category.coding[0]).code
                if code == 'attachment':
                    target.append(info.valueString)
            if target:
                return target
            raise AttributeError()
        except (AttributeError, IndexError, TypeError):
            return list()

    @property
    def claim_type(self) -> str:
        try:
            code = cast(Coding,
                        cast(CodeableConcept,
                             self.claim.type
                             ).coding[0]
                        ).code
            if not code:
                raise ClaimError()
            return code
        except (AttributeError, IndexError, ClaimError):
            raise self._missing_field_error('claimType')

    @property
    # TODO(plyq): replace existing `claim_type` with this once versioning will be done.
    def claim_type_normalized(self) -> ClaimTypeFocus:
        return ClaimTypeFocus.from_string(self.claim_type)

    @property
    def related_claim(self) -> str:
        """
        [new FHIR mapping]

        Confirmed by the Content Team: there can be only one value for this field.
        """
        try:
            related = cast(ClaimRelated, self.claim.related[0])
            relationship = cast(CodeableConcept, related.relationship)
            coding = cast(Coding, relationship.coding[0])
            if coding.code:
                return coding.code.strip().lower()
        except (AttributeError, TypeError, IndexError):
            pass

        return '1'

    @property
    def relatedClaimRelations(self) -> List[str]:
        """
        Legacy. Should be removed in future version.
        """
        if self.claim.related is None:
            return []

        try:
            codes = []
            for rel in self.claim.related:
                code = cast(
                    Coding,
                    cast(
                        CodeableConcept,
                        cast(
                            ClaimRelated,
                            rel
                        ).relationship
                    ).coding[0]
                ).code
                codes.append(code)
            return codes
        except (AttributeError, TypeError):
            raise ClaimError("")

    @property
    def pre_auth_ref(self) -> List[str]:
        try:
            insurance = cast(List[ClaimInsurance], self.claim.insurance)
            for ins in insurance:
                if ins.sequence == 1:
                    if ins.preAuthRef:
                        return ins.preAuthRef
            raise AttributeError()
        except (AttributeError, TypeError):
            raise self._missing_field_error('preAuthRef')

    @staticmethod
    def _cleanup(ref: str) -> str:
        return ref[1:] if ref and ref[0] == '#' else ref

    @property
    def referring_provider(self) -> Optional[Union[Practitioner, Organization]]:
        try:
            ref = cast(Reference, self.claim.referral).reference
            ref = self._cleanup(ref)
            service_request = cast(ServiceRequest, self.contained[ref])
            ref = cast(Reference, service_request.requester).reference
            ref = self._cleanup(ref)
            provider = self.contained[ref]
            if provider:
                if provider.resource_type.lower() == 'practitioner':
                    return cast(Practitioner, provider)
                if provider.resource_type.lower() == 'organization':
                    return cast(Organization, provider)
                raise AttributeError()
        except (AttributeError, KeyError, TypeError):
            raise self._error(ClaimError, f'Referring provider not found on this claim.')

    @property
    def referring_provider_last(self) -> str:
        try:
            provider = self.referring_provider
            return cast(HumanName, provider.name[0]).family
        except (AttributeError, IndexError, ClaimError):
            raise self._missing_field_error('providerReferringLast')

    @property
    def supervising_provider(self) -> Optional[Union[Practitioner, Organization]]:
        """In the OLD FHIR mapping, there are three sets of fields that are mapped to the same
        place providerReferring*, providerOrdering* and providerSupervising*
        This is why we just make an alias to referring_provider here."""
        return self.referring_provider

    # noinspection DuplicatedCode
    @staticmethod
    def practitioner_identifiers(provider: Union[Practitioner, Organization]) -> Dict[str, str]:
        ids = dict()
        for prov_id in provider.identifier:
            if hasattr(prov_id, 'type') and prov_id.type:
                prov_id_type = cast(
                    Coding,
                    cast(
                        CodeableConcept,
                        prov_id.type
                    ).coding[0]
                ).code.upper()
            else:
                # The default type is assumed to be NPI
                prov_id_type = 'NPI'

            # ATTENTION: assuming each Practitioner referenced in a claim line
            #     has only one identifier of each type.
            ids[prov_id_type] = cast(
                Identifier,
                prov_id
            ).value.strip()

        return ids

    @property
    def referring_npi_number(self) -> str:
        referring_provider = self.referring_provider
        try:
            identifiers = self.practitioner_identifiers(referring_provider)
            return identifiers['NPI']
        except (KeyError, ClaimError):
            raise self._missing_field_error('orderingNPINumber')

    @property
    def ordering_npi_number(self) -> str:
        return self.referring_npi_number

    @property
    def supervising_npi_number(self) -> str:
        return self.referring_npi_number

    @property
    def subscriberIDs(self) -> List[str]:
        """Only used by mcr-nl-telconsultfuinp-py,
        Once that engine is fixed, it can be removed. """
        # |claim.insurance| = 1..*.
        if not self.claim.insurance:
            raise ClaimError("No insurance found on this claim")

        ids = []
        for ins in self.claim.insurance:
            claim_ins = cast(ClaimInsurance, ins).coverage
            try:
                ref = cast(Reference, claim_ins).reference
                cov = self.contained[ref]
            except KeyError:
                continue

            sub_id = cast(Coverage, cov).subscriberId
            if sub_id is not None:
                ids.append(sub_id)
        return ids

    @property
    def clm_total_charge_amt(self) -> Optional[Decimal]:
        """
        [new FHIR mapping]

        path: claim.total.value
        """
        try:
            return cast(Money, self.claim.total).value
        except AttributeError:
            pass

        raise self._missing_field_error('clmTotalChargeAmt')

    @property
    def totalChargedAmount(self) -> Optional[Decimal]:
        """ Do not use this getter. It shall be removed in future versions. """
        if self.claim.total:
            if cast(Money, self.claim.total).value is not None:
                return cast(Money, self.claim.total).value
        return None

    @property
    def bill_type(self) -> str:
        # Claim.subType.coding.code
        try:
            code = cast(Coding,
                        cast(CodeableConcept,
                             self.claim.subType
                             ).coding[0]
                        ).code
            if not code:
                raise ClaimError()
            return code
        except (AttributeError, IndexError, ClaimError):
            raise self._missing_field_error('billType')

    @property
    def claim_num(self) -> str:
        try:
            return cast(Identifier, self.claim.identifier[0]).value
        except (IndexError, AttributeError, TypeError):
            raise self._missing_field_error('claimNum')

    @property
    def hospitalized_period(self) -> Period:
        """
        Hospitalization Period for claim.

        NOTE: It is different with claim line hospitalization properties.

        Returns
        -------
            If the claim has a single hospitalizatoin timing date, both
            dates in this tuple will be same. Otherwise they will be start
            and end date of hospitalization timing period
        """
        raise NotImplementedError('PLEASE, update engine code to use admit_date and/or discharge_date'
                                  ' getters and not hospitalized_period property directly!')

    def __eq__(self, other: object) -> bool:
        """Check that claim id-s are same.

        Args:
            other: claim focus to compare

        Returns:
            True if id-s are the same

        Raises:
            NotImplementedError: if comparing with non-ClaimFocus
            ClaimError: if there are not any id.
        """
        if not isinstance(other, ClaimFocus):
            raise NotImplementedError(
                "ClaimFocus object is comparable only "
                "with another ClaimFocus object"
            )
        compare_result = ClaimComparator.compare(self.claim, other.claim)
        return compare_result == CompareResult.EQ

    @property
    def insurance(self) -> List[ClaimInsurance]:
        try:
            return [
                cast(ClaimInsurance, insurance)
                for insurance in self.claim.insurance
            ]
        except AttributeError:
            raise ClaimError(f"Insurance not found on claim")

    @property
    def primary_insurance(self) -> ClaimInsurance:
        return find_primary_insurance(self.insurance, self.request)

    @property
    def subscriber_id(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            for insurance in cast(List[ClaimInsurance], self.claim.insurance):
                if not insurance.focal:
                    continue
                ref = cast(Reference, insurance.coverage).reference
                ref = self._cleanup(ref)
                coverage = cast(Coverage, self.contained[ref])
                return coverage.subscriberId.strip().lower()
        except (AttributeError, TypeError, KeyError):
            pass

        raise self._missing_field_error('subscriberId')

    @property
    def _subscriber_name(self) -> Optional[HumanName]:
        for insurance in cast(List[ClaimInsurance], self.claim.insurance):
            if not insurance.focal:
                continue

            ref = cast(Reference, insurance.coverage).reference
            ref = self._cleanup(ref)
            resource = self.contained[ref]
            if resource.resource_type != 'Coverage':
                break

            coverage = cast(Coverage, resource)
            ref = cast(Reference, coverage.subscriber).reference
            ref = self._cleanup(ref)
            resource = self.contained[ref]
            if resource.resource_type != 'RelatedPerson':
                break

            related_person = cast(RelatedPerson, resource)
            return cast(HumanName, related_person.name[0])

    @property
    def subscriber_first_name(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            name = self._subscriber_name
            if name is not None:
                return name.given[0].strip().lower()
        except (AttributeError, TypeError, KeyError, IndexError):
            pass

        raise self._missing_field_error('subscriberFirstName')

    @property
    def subscriber_last_name(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            name = self._subscriber_name
            if name is not None:
                return name.family.strip().lower()
        except (AttributeError, TypeError, KeyError, IndexError):
            pass

        raise self._missing_field_error('subscriberLastName')

    @property
    def relation_to_insured(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            for insurance in cast(List[ClaimInsurance], self.claim.insurance):
                if not insurance.focal:
                    continue
                ref = cast(Reference, insurance.coverage).reference
                ref = self._cleanup(ref)
                coverage = cast(Coverage, self.contained[ref])
                relationship = cast(CodeableConcept, coverage.relationship)
                return cast(Coding, relationship.coding[0]).code.strip().lower()
        except (AttributeError, TypeError, IndexError, KeyError):
            pass

        raise self._missing_field_error('relationToInsured')

    @property
    def group_num(self) -> str:
        """
        Returns the Value of coverage class type "group"
        primary insurance
        :return: str
        """
        primary_insurance = ClaimInsuranceFocus(
            self.primary_insurance, request=self.request)
        return primary_insurance.group_number

    @property
    def group_name(self) -> str:
        """
        Returns the Name of coverage class type "group"
        primary insurance
        :return: str
        """
        primary_insurance = ClaimInsuranceFocus(
            self.primary_insurance, request=self.request)
        return primary_insurance.group_name

    @property
    def created(self) -> dt.date:
        """
        Returns the date that the 837 claim was submitted to payer
        :return: dt.date
        """
        try:
            created_date = self.claim.created
        except (AttributeError, TypeError):
            raise self._missing_field_error("createdDate")
        return created_date
