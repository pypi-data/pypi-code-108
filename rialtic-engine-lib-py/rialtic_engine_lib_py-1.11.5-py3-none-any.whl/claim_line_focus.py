import datetime as dt
from typing import Dict, List, Optional, Union, cast, Set, Type

from fhir.resources.claim import (ClaimCareTeam, ClaimDiagnosis, ClaimInsurance, ClaimItem)
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.encounter import Encounter
from fhir.resources.fhirtypes import Date, Decimal, PositiveInt
from fhir.resources.identifier import Identifier
from fhir.resources.money import Money
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.period import Period as FHIRPeriod
from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from schema.insight_engine_request import InsightEngineRequest

import enginelib.utils as elut
from enginelib.claim_insurance_focus import (ClaimInsuranceFocus,
                                             find_primary_insurance)
from enginelib.comparator import (ClaimComparator, ClaimItemComparator,
                                  CompareResult)
from enginelib.errors import ClaimError, MissingFieldError, Error
from enginelib.resources import contained_resources
from enginelib.types import Period
import warnings


class ClaimLineFocus:
    """
    A class that provides easy access to attributes on claim lines
    """

    def __init__(self, claim_line: ClaimItem, request: InsightEngineRequest):
        self.claim_line = claim_line
        self.request = request
        self._contained: Optional[Dict[str, Resource]] = None

    @property
    def contained(self) -> Dict[str, Resource]:
        if self._contained is not None:
            return self._contained

        # set up references for contained elements
        self._contained = dict()
        if getattr(self.request.claim, "contained", None):
            resources = [cast(Resource, elem) for elem in self.request.claim.contained]
            self._contained = {
                resource.id: resource for resource in resources
                if resource.id is not None
            }

        return self._contained

    def _error(self, error_class: Type[Error], message: str):
        try:
            identifier = cast(Identifier, self.request.claim.identifier[0])
            claim_num = identifier.value
            try:
                line_num = self.claim_line.sequence
                msg = f'{message} [claim {claim_num}, line {line_num}].'
            except AttributeError:
                msg = f'{message} [claim {claim_num}].'
        except (AttributeError, TypeError, IndexError):
            msg = f'{message} [unidentified claim: claimNum missing from the claim].'

        return error_class(msg)

    def _missing_field_error(self, field_name: str = 'unspecified'):
        message = f'Field `{field_name}` was not found on this claim line.'
        return self._error(MissingFieldError, message)

    @property
    def _procedure_code_fallback(self) -> str:
        """
        [new FHIR mapping]

        Since procedureCode is used in *every* engine, its implementation was adapted
        in a way that makes it most likely to be compatible with the previous mapping.

        Basically, this fallback implementation is aware of any field that is mapped to:

            claim.item[n].productOrService.coding

        Currently, in the new mapping, those fields are:
            ndcCode                 (coding.system ends with "/ndc_code")
            procedureCode           (coding.system ends with "/HC")
            jurisdictionCode        (coding.system ends with "/ER")
            hiecProductCode         (coding.system ends with "/IV")
            abcCode                 (coding.system ends with "/WK")

        If more fields are mapped to the same location, this function needs to be
        updated accordingly if we want procedure_code to work with old test cases.
        """
        try:
            product_or_service = cast(CodeableConcept, self.claim_line.productOrService)
            forbidden_endings = ['wk', 'iv', 'er', 'ndc_code']
            candidates: Set[str] = set()
            for coding in cast(List[Coding], product_or_service.coding):
                if hasattr(coding, 'system') and isinstance(coding.system, str):
                    normalized_system = coding.system.rstrip().lower()
                    not_procedure_code = any(map(normalized_system.endswith, forbidden_endings))
                    if not_procedure_code:
                        continue

                # The reason we use upper() instead of lower() is because usually
                #     procedureCodes with non-numeric characters have them upper case,
                #     many are hardcoded in node predicates inside engines.
                normalized_code = coding.code.upper().strip()
                candidates.add(normalized_code)

            n = len(candidates)
            if n == 1:
                return next(iter(candidates))
            if n < 1:
                raise self._missing_field_error(field_name='procedureCode')
            if n > 1:
                raise self._error(
                    error_class=ClaimError,
                    message='Too many possible values for field procedureCode were found for this claim line.'
                )
        except (AttributeError, TypeError):
            raise self._missing_field_error(field_name='procedureCode')

    @property
    def procedure_code(self) -> str:
        """
        [new FHIR mapping]

        Since this field is used in *every* engine, its implementation will be adapted
        in a way that makes it most likely to be compatible with the previous mapping.
        """
        try:
            product_or_service = cast(CodeableConcept, self.claim_line.productOrService)
            for coding in cast(List[Coding], product_or_service.coding):
                if hasattr(coding, 'system') and isinstance(coding.system, str):
                    if coding.system.lower().rstrip().endswith('hc'):
                        return coding.code.strip().upper()
            return self._procedure_code_fallback
        except (IndexError, AttributeError):
            raise self._missing_field_error(field_name='procedureCode')

    @property
    def ndc_code(self) -> str:
        try:
            product_or_service = cast(CodeableConcept, self.claim_line.detail[0].productOrService)
            for coding in cast(List[Coding], product_or_service.coding):
                if hasattr(coding, 'system') and isinstance(coding.system, str):
                    if coding.system.lower().endswith("ndc_code"):
                        return coding.code
            else:
                raise ClaimError("ndcCode could not be found")
        except (IndexError, AttributeError, TypeError, ClaimError):
            raise self._missing_field_error(field_name="ndcCode")

    @property
    def service_period(self) -> Period:
        """
        Service Period for claim line

        Returns
        -------
            If the claim line has a single service date, both dates in this tuple will be same
            Otherwise they will be start and end date of service period
        """
        try:
            serv_date = self.claim_line.servicedDate
            if serv_date:
                return Period(serv_date, serv_date)
            else:
                period = cast(FHIRPeriod, self.claim_line.servicedPeriod)
                if not (period.start and period.end):
                    raise self._missing_field_error(field_name='servicedPeriod')
                return Period(period.start, period.end)
        except (AttributeError, ClaimError):
            raise self._missing_field_error(field_name='servicedPeriod')

    @property
    def patient(self) -> Patient:
        try:
            ref = cast(Reference, self.request.claim.patient).reference
            ref = self._cleanup(ref)
        except AttributeError:
            raise self._error(ClaimError, 'Patient not found on claim')
        try:
            p = cast(Patient, self.contained[ref])
            if p.resource_type != 'Patient':
                self._error(ClaimError, 'Patient not found on claim.')
            return p
        except KeyError:
            raise self._error(ClaimError, f'Patient with id #{ref} not found in contained objects of the claim.')

    @property
    def provider(self) -> Union[Practitioner, PractitionerRole, Organization]:
        try:
            ref = cast(Reference, self.request.claim.provider).reference
        except AttributeError:
            raise ClaimError(f"Provider not found on claim")
        try:
            return self.contained[ref]
        except KeyError:
            raise ClaimError(f"Provider with id: {ref} not found in contained objects")

    # TODO(*): Remove old `provider`, rename this to `provider`.
    @property
    def provider_future(self) -> Practitioner:
        """Provider property from specifications."""
        provider = None
        claim_line = self.claim_line
        claim = self.request.claim
        claim_resources = contained_resources(claim)

        # Create {sequence: careTeam} dict to easy find items.
        care_teams = {
            cast(ClaimCareTeam, care_team).sequence: care_team
            for care_team in claim.careTeam
        }
        for index in claim_line.careTeamSequence:
            try:
                provider_id = cast(
                    Reference,
                    cast(
                        ClaimCareTeam,
                        care_teams[index]  # might raise KeyError
                    ).provider
                ).reference
            except KeyError:
                # Provider indexed in field claim_line.careTeamSequence
                #     was not present in claim.careTeam:
                continue

            if provider_id not in claim_resources:
                continue

            resource = claim_resources[provider_id]
            if resource.resource_type != 'Practitioner':
                continue

            if provider is not None:
                # NOTE: checked with analysts: it is ok to assume only
                #     one practitioner per claim line.
                raise ClaimError("Too many practitioners")

            provider = cast(Practitioner, resource)

        if provider is None:
            raise ClaimError("No practitioner")

        return provider

    def _get_care_team_provider(self, provider_type: str) -> Practitioner:
        supervisor_codes = {"ordering": "dk",
                            "supervising": "dq"}
        provider_code = supervisor_codes.get(provider_type)
        claim_line = self.claim_line
        claim = self.request.claim

        # Create {sequence: careTeam} dict to easy find items.
        care_teams = {
            cast(ClaimCareTeam, care_team).sequence: care_team
            for care_team in claim.careTeam
        }

        for index in claim_line.careTeamSequence:
            try:
                care_team = cast(
                    ClaimCareTeam,
                    care_teams[index]  # might raise KeyError
                )
                code = cast(Coding, cast(CodeableConcept, care_team.role).coding[0]).code
            except (IndexError, KeyError, AttributeError, TypeError):
                # Provider indexed in field claim_line.careTeamSequence was not present in claim.careTeam:
                # or the Provider did not contain the `role` attribute
                continue

            if code.lower() == provider_code:
                try:
                    provider_reference = cast(
                        Reference,
                        care_team.provider
                    ).reference
                except (AttributeError, TypeError):
                    raise ClaimError("The Care Team does not contain a reference to the provider")
                else:
                    provider_reference = provider_reference[1:] if provider_reference[0] == "#" else provider_reference
                    return cast(Practitioner, self.contained[provider_reference])
            else:
                continue

        raise ClaimError(f"The {provider_type} provider is not present in the claim")

    @property
    def supervising_provider(self) -> Practitioner:
        # I want any exceptions raised by this function to be propagated upwards
        provider = self._get_care_team_provider("supervising")
        return provider

    @property
    def supervising_provider_last(self) -> str:
        try:
            supervising_provider = self.supervising_provider
            last_name = supervising_provider.name[0].family
        except (AttributeError, IndexError, ClaimError):
            raise ClaimError("The family name of the supervising provider could not be obtained")
        return last_name

    @property
    def ordering_provider(self) -> Practitioner:
        # I want any exceptions raised by this function to be propagated upwards
        provider = self._get_care_team_provider("ordering")
        return provider

    @property
    def ordering_provider_last(self) -> str:
        try:
            ordering_provider = self.ordering_provider
            last_name = ordering_provider.name[0].family
        except (AttributeError, IndexError, ClaimError):
            raise ClaimError("The family name of the ordering provider could not be obtained")
        return last_name

    @property
    def practitioner(self) -> Practitioner:
        """
        note: this property exists for backwards compatibility
        """
        return self.provider

    @property
    def patient_age(self) -> int:
        """
        Age of patient on service date or start of service period

        Notes
        -----
        Patient age may differ from one line to the next if the
        beginning of service differs
        """
        try:
            birth = self.patient.birthDate
            start, _ = self.service_period
            return elut.date_diff(start, birth, unit="year")
        except AttributeError:
            raise ClaimError(f"Birthdate not found on patient with id {self.patient.id}")

    @property
    def modifier_codes(self) -> List[str]:
        try:
            codes = [
                coding.code
                for codings in [
                    cast(List[Coding], c.coding)
                    for c in cast(List[CodeableConcept], self.claim_line.modifier)
                ]
                for coding in codings
            ]
            return codes
        except (AttributeError, TypeError):
            pass

        return list()

    @property
    def location_codes(self) -> List[str]:
        """Legacy code. This should be removed in future versions.
        Content Team confirmed: only one place of service per claim line!"""
        try:
            return [
                cast(Coding, c).code
                for c in cast(
                    CodeableConcept,
                    self.claim_line.locationCodeableConcept
                ).coding
            ]
        except (AttributeError, TypeError):
            pass

        return list()

    @property
    def claim_type(self) -> str:
        try:
            code = cast(Coding,
                        cast(CodeableConcept,
                             self.request.claim.type
                             ).coding[0]  # why is this a list? what are the other items? can claim have multiple types?
                        ).code
            if not code:
                raise ClaimError()
            return code
        except (AttributeError, IndexError, ClaimError):
            raise self._missing_field_error(field_name='claimType')

    @property
    def line_charge_amt(self) -> Decimal:
        try:
            value = cast(
                Money,
                self.claim_line.unitPrice
            ).value
            if value:
                return value
        except (AttributeError, IndexError, ClaimError):
            pass

        raise self._missing_field_error(field_name='lineChargeAmt')

    @property
    def pos_code(self) -> str:
        """
        `DEPRECATED`
        Same as `place_of_service` property

        Returns:
            placeOfService property if exists

        Raises:
            ClaimError: if placeOfService extraction failed
        """
        return self.place_of_service

    # TODO(plyq): Part of ClaimFocus. Remove after versioning.
    @property
    def insurance(self) -> List[ClaimInsurance]:
        try:
            return [
                cast(ClaimInsurance, insurance)
                for insurance in self.request.claim.insurance
            ]
        except AttributeError:
            raise ClaimError(f"Insurance not found on claim")

    # TODO(plyq): Part of ClaimFocus. Remove after versioning.
    @property
    def primary_insurance(self) -> ClaimInsurance:
        return find_primary_insurance(self.insurance, self.request)

    # TODO(plyq): Part of ClaimFocus. Remove after versioning.
    @property
    def subscriber_id(self) -> str:
        """Subscriber id for the primary coverage.

        1. If subscriberId is present, return it
        2. If there is only one identifier, return it
        3. Go thru all identifiers and find the one from each all others start
        4. If such identifier doesn't exist, raise ClaimError
        """
        primary_insurance = ClaimInsuranceFocus(self.primary_insurance, request=self.request)
        return primary_insurance.subscriber_id

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
    def primary_diagnosis_pointer_code(self) -> str:
        try:
            try:
                diagPointer = self.claim_line.diagnosisSequence[0]
            except (IndexError):
                raise ClaimError("No Diagnosis pointer found for this claim line.")
            return cast(List[Coding],
                        cast(ClaimDiagnosis, self.request.claim.diagnosis[diagPointer - 1])
                        .diagnosisCodeableConcept).coding[0].code
        except (AttributeError, TypeError, ClaimError):
            raise ClaimError("No Diagnosis codes found for this diagnosis sequence.")

    @property
    def diag_pointers(self) -> List[str]:
        if not hasattr(self.claim_line, 'diagnosisSequence') or \
                not isinstance(self.claim_line.diagnosisSequence, list):
            return list()

        diagnoses = list()
        for i, index in enumerate(self.claim_line.diagnosisSequence):
            try:
                claim_diagnosis = cast(ClaimDiagnosis, self.request.claim.diagnosis[index - 1])
                diagnosis_codeable_concept = cast(CodeableConcept, claim_diagnosis.diagnosisCodeableConcept)
                diagnosis = cast(Coding, diagnosis_codeable_concept.coding[0]).code
                diagnoses.append(diagnosis)
            except (AttributeError, TypeError, IndexError):
                raise self._missing_field_error(field_name=f'diagPointer{i}')

        return diagnoses

    @property
    def program_indicators(self) -> List[str]:
        """Used in only on engine: mcd-fl-childhealthcheckreferralcodes-py
        After that engine is fixed, it can be removed.
        """
        indicators: Set[str] = set()
        try:
            for codeable_concept in cast(List[CodeableConcept], self.claim_line.programCode):
                for coding in cast(List[Coding], codeable_concept.coding):
                    if not coding.system.lower().strip().endswith('emergency_indicator'):
                        indicators.add(coding.code.lower().strip())
        except (AttributeError, TypeError):
            pass

        return list(indicators)

    @property
    def program_indicator(self) -> str:
        """
        [new FHIR mapping]

        Does not raise error because the return type is List[...]. Eventually all
        fields that return list will not raise errors and simply return an empty
        list in case no value was found for that field on the claim or claim line.
        """
        indicators: Set[str] = set()
        try:
            for codeable_concept in cast(List[CodeableConcept], self.claim_line.programCode):
                for coding in cast(List[Coding], codeable_concept.coding):
                    if not coding.system.lower().strip().endswith('emergency_indicator'):
                        indicators.add(coding.code.lower().strip())
            n = len(indicators)
            if n > 1:
                raise self._error(ClaimError, 'Too many candidates for field programIndicator.')
            if n == 1:
                return next(iter(indicators))
        except (AttributeError, TypeError):
            pass

        raise self._missing_field_error('programIndicator')

    @property
    def emergency_indicator(self) -> str:
        """
        [new FHIR mapping]
        """
        try:
            for codeable_concept in cast(List[CodeableConcept], self.claim_line.programCode):
                for coding in cast(List[Coding], codeable_concept.coding):
                    if coding.system.lower().strip().endswith('emergency_indicator'):
                        return coding.code.lower().strip()
        except (AttributeError, TypeError):
            pass

        raise self._missing_field_error('emergencyIndicator')

    @property
    def quantity(self) -> Decimal:
        try:
            return cast(Quantity, self.claim_line.quantity).value
        except (AttributeError, ClaimError):
            raise self._missing_field_error('units')

    @property
    def sequence(self) -> PositiveInt:
        try:
            return self.claim_line.sequence
        except (AttributeError, ClaimError):
            raise self._missing_field_error('sequence')

    @property
    def other_claim_line(self) -> List[ClaimItem]:
        """
        Get OCL on the same claim
        """
        warnings.warn("other_claim_line is deprecated. "
                      "Please use other_claim_lines instead that returns ClaimLineFocus",
                      DeprecationWarning)
        return [cast(ClaimItem, claim_item) for claim_item in self.request.claim.item if
                claim_item is not self.claim_line]

    @property
    def other_claim_lines(self) -> List["ClaimLineFocus"]:
        """
        Get OCL on the same claim that are wrapped by ClaimLineFocus
        """
        return [
            self.__class__(cast(ClaimItem, claim_item), self.request)
            for claim_item in self.request.claim.item
            if claim_item is not self.claim_line
        ]

    @property
    def encounters(self) -> List[Encounter]:
        try:
            refs = [
                cast(Reference, encounter).reference
                for encounter in self.claim_line.encounter
            ]
        except (AttributeError, TypeError):
            raise ClaimError(f"Encounter not found on claim")
        return [
            cast(Encounter, self.contained[ref])
            for ref in refs
            if ref in self.contained
        ]

    @property
    def admit_date(self) -> Date:
        date_candidates = []
        for encounter in self.encounters:
            try:
                date_ = encounter.period.start
                if encounter.hospitalization.admitSource:
                    date_candidates.append(date_)
            except AttributeError:
                continue
        date_candidates = list(set(date_candidates))
        if len(date_candidates) == 0:
            raise ClaimError("AdmitDate is not found")
        elif len(date_candidates) > 1:
            raise ClaimError("There are at least 2 candidates for admitDate")
        else:
            return date_candidates[0]

    @property
    def discharge_date(self) -> Date:
        date_candidates = []
        for encounter in self.encounters:
            try:
                date_ = encounter.period.end
                if encounter.hospitalization.dischargeDisposition:
                    date_candidates.append(date_)
            except AttributeError:
                continue
        date_candidates = list(set(date_candidates))
        if len(date_candidates) == 0:
            raise ClaimError("DischargeDate is not found")
        elif len(date_candidates) > 1:
            raise ClaimError("There are at least 2 candidates for dischargeDate")
        else:
            return date_candidates[0]

    @property
    def revenue_code(self) -> str:
        # Claim.item[n].revenue.coding.code
        try:
            code = cast(Coding,
                        cast(CodeableConcept,
                             self.claim_line.revenue
                             ).coding[0]
                        ).code
            if not code:
                raise ClaimError()
            return code
        except (AttributeError, IndexError, ClaimError):
            raise ClaimError("No revenue found on this claim line")

    @property
    def place_of_service(self) -> str:
        """
        Extracts placeOfService for ClaimLime.
        Used `locationCodeableConcept` original field.

        Returns:
            placeOfService property if exists

        Raises:
            ClaimError: if placeOfService extraction failed
        """
        try:
            code = cast(List[Coding],
                        cast(CodeableConcept,
                             self.claim_line.locationCodeableConcept
                             ).coding
                        )[0].code
            if not code:
                raise ClaimError()
        except (IndexError, AttributeError, ClaimError):
            raise ClaimError(
                'Place of service code not found for this claim line'
            )
        return code

    @property
    def _rendering_practitioner_role(self) -> PractitionerRole:
        """
        [new FHIR mapping]
        """
        seq = self.claim_line.sequence - 1
        practitioner_role: Optional[PractitionerRole] = None
        if not hasattr(self.claim_line, 'careTeamSequence') or not \
                isinstance(self.claim_line.careTeamSequence, list):
            raise self._error(ClaimError, 'No rendering provider was found in this claim line.')
        for i, index in enumerate(self.claim_line.careTeamSequence):
            # Change from 1-based index to 0-based index:
            index -= 1

            # Locate the corresponding ClaimCareTeam object:
            try:
                care_team = cast(ClaimCareTeam, self.request.claim.careTeam[index])
            except IndexError:
                message = f'Malformed claim: claim.item[{seq}].careTeamSequence[{i}] is {index + 1}, ' \
                      f'but claim.careTeam[{index}] was not found in this claim.'
                raise self._error(ClaimError, message)

            # Check condition for being a rendering provider:
            try:
                role = cast(CodeableConcept, care_team.role)
                role_codes = [coding.code for coding in cast(List[Coding], role.coding)]
                if '82' not in role_codes:
                    continue
            except AttributeError:
                continue

            # Find the actual PractitionerRole object:
            try:
                ref = cast(Reference, care_team.provider).reference
                ref = self._cleanup(ref)
                try:
                    new_practitioner_role = cast(Resource, self.contained[ref])
                except KeyError:
                    message = f'Malformed claim: claim.item[{seq}].careTeamSequence[{i}] is {index + 1}, ' \
                              f'and claim.careTeam[{index}].provider.reference is "{ref}", ' \
                              f'but no such resource was found in claim.contained.'
                    raise self._error(ClaimError, message)
            except AttributeError:
                continue

            if new_practitioner_role.resource_type != 'PractitionerRole':
                continue

            if practitioner_role is not None:
                message = 'Too many candidates for rendering provider were found in this claim line.'
                raise self._error(ClaimError, message)

            practitioner_role = cast(PractitionerRole, new_practitioner_role)

        if practitioner_role is None:
            raise self._error(ClaimError, 'No rendering provider was found in this claim line.')

        return practitioner_role

    @property
    def rend_prov_npi(self) -> str:
        """
        [new FHIR mapping]
        """
        practitioner_role = self._rendering_practitioner_role
        try:
            ref = cast(Reference, practitioner_role.practitioner).reference
            ref = self._cleanup(ref)
            try:
                provider = cast(Resource, self.contained[ref])
            except KeyError:
                raise self._error(ClaimError, f'Resource with id {ref} not found in claim.contained.')

            if provider.resource_type != 'Practitioner':
                raise self._error(ClaimError, f'Resource with id {ref} was expected to be a Practitioner.')

            provider = cast(Practitioner, provider)

            npi_number: Optional[str] = None
            for identifier in cast(List[Identifier], provider.identifier):
                try:
                    system = identifier.system
                    if not system.endswith('XX'):
                        continue

                    new_npi_number = identifier.value
                    if npi_number is not None:
                        raise self._error(ClaimError, 'Too many candidate values for rendProvNPI in this claim line.')

                    npi_number = new_npi_number
                except AttributeError:
                    continue

            if npi_number is None:
                raise self._missing_field_error('rendProvNPI')

            return npi_number
        except (AttributeError, IndexError, TypeError):
            raise self._missing_field_error('rendProvNPI')

    @staticmethod
    def _cleanup(ref: str) -> str:
        return ref[1:] if ref and ref[0] == '#' else ref

    @property
    def rend_prov_taxonomy(self) -> str:
        """
        [new FHIR mapping]
        """
        practitioner_role = self._rendering_practitioner_role
        try:
            # WARNING! Assuming only one specialty code per PractitionerRole object:
            specialty = cast(CodeableConcept, practitioner_role.specialty[0])
            return cast(Coding, specialty.coding[0]).code
        except (AttributeError, IndexError, TypeError):
            raise self._missing_field_error('rendProvTaxonomy')

    def other_clf_period_diff(self, other: "ClaimLineFocus", unit: str) -> int:
        """
        :param unit: one of day, month, year
        :return: service period difference in unit-s.
        """
        return elut.date_diff(self.service_period[0], other.service_period[0], unit=unit)

    @staticmethod
    def stub(
            procedure_code: str = "TEST",
            service_start: dt.date = dt.date.min,
            service_end: dt.date = dt.date.max,
            units: int = 0
    ):
        claim_item = ClaimItem.parse_obj({
            "sequence": 1,
            "productOrService": {
                "coding": [
                    {
                        "code": f"{procedure_code}",
                        "system": "http://hl7.org/fhir/ex-serviceproduct"
                    }
                ]
            },
            "quantity": {
                "value": f"{units}"
            },
            #   python datetime library default string format for dates is YYYY-MM-DD
            #   this is the same as HL7 FHIR
            "servicedPeriod": {
                "end": f"{service_end}",
                "start": f"{service_start}"
            }
        })
        return ClaimLineFocus(claim_item, InsightEngineRequest())

    def __eq__(self, other: object) -> bool:
        """Check that claim id-s and claim line sequences are same.

        Args:
            other: claim line focus to compare

        Returns:
            True if id-s and sequences are the same

        Raises:
            NotImplementedError: if comparing with non-ClaimLineFocus
            ClaimError: if there are not any id.
        """
        if not isinstance(other, ClaimLineFocus):
            raise NotImplementedError(
                "ClaimFocus object is comparable only "
                "with another ClaimFocus object"
            )
        compare_results = (
            ClaimComparator.compare(self.request.claim, other.request.claim),
            ClaimItemComparator.compare(self.claim_line, other.claim_line),
        )
        return all(result == CompareResult.EQ for result in compare_results)

    def _find_identifiers(self, id_type: str, id_name: str) -> str:
        id_value: Optional[str] = None
        not_found_error_msg = f"No {id_name} found on this claim line."
        too_many_error_msg = f"Too many {id_name}s in the claim line."

        try:
            identifiers = cast(List[Identifier], self.provider_future.identifier)
            for identifier in identifiers:
                identifier_type = cast(
                    Coding,
                    cast(CodeableConcept, identifier.type).coding[0]
                )
                if identifier_type.code == id_type:
                    if id_value is None:
                        id_value = identifier.value
                    else:
                        # found more than one value of rendProvNPI
                        raise ClaimError(too_many_error_msg)

            if id_value:
                return id_value

            # in case there were identifiers but not of id_type
            raise ClaimError(not_found_error_msg)
        except (ClaimError, AttributeError, TypeError, IndexError):
            # in case there were no identifiers at all
            if id_value is None:
                raise ClaimError(not_found_error_msg)
            else:
                raise ClaimError(too_many_error_msg)

        return id_value

