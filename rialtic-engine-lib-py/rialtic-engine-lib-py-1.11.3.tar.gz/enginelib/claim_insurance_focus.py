from typing import List, cast

from fhir.resources.claim import ClaimInsurance
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.coverage import Coverage
from fhir.resources.identifier import Identifier
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource
from schema.insight_engine_request import InsightEngineRequest

from enginelib.errors import ClaimError


class ClaimInsuranceFocus:
    def __init__(self, insurance: ClaimInsurance, request: InsightEngineRequest):
        self.insurance = insurance
        self.request = request
        # set up references for contained elements
        self.contained = (
            {
                cast(Resource, element).id: cast(Resource, element)
                for element in request.claim.contained
            }
            if getattr(request.claim, "contained", None)
            else {}
        )

    @property
    def coverage(self) -> Coverage:
        try:
            # Find unique coverages.
            ref = cast(Reference, self.insurance.coverage.reference)
        except AttributeError:
            raise ClaimError(f"Coverage not found on insurance")
        try:
            return self.contained[ref]
        except KeyError:
            raise ClaimError(
                f"Coverage with id: {ref} not found in contained objects")

    @property
    def coverage_type(self) -> str:
        """Lowercase coverage type."""
        try:
            coverage_type = cast(
                List[Coding], cast(CodeableConcept, self.coverage.type).coding
            )[0].code
            if not coverage_type:
                raise ClaimError()
            return coverage_type.lower()
        except (IndexError, AttributeError, ClaimError):
            raise ClaimError("Type is not found for this coverage")

    @property
    def subscriber_id(self) -> str:
        """Primary subscriber id.

        1. If subscriberId is present, return it
        2. If there is only one identifier, return it
        3. Go thru all identifiers and find the one from each all others start
        4. If such identifier doesn't exist, raise ClaimError
        """
        coverage = self.coverage
        # subscriberId is present.
        try:
            subscriber_id = coverage.subscriberId
        except AttributeError:
            # If subscriberId is missing, go to identifier.
            subscriber_id = None
        if subscriber_id is not None:
            return subscriber_id
        try:
            # Find primary identifier.
            subscriber_id = self._identifiers_to_id()
        except (ClaimError, AttributeError, IndexError):
            raise ClaimError("Can't find primary coverage identifier")
        return subscriber_id

    @property
    def relation_to_insured(self) -> str:
        """Lowercase coverage's relationship."""
        try:
            relationship = cast(
                List[Coding], cast(
                    CodeableConcept, self.coverage.relationship).coding
            )[0].code
            if not relationship:
                raise ClaimError()
            return relationship.lower()
        except (IndexError, AttributeError, TypeError, ClaimError):
            raise ClaimError("Relationship is not found for this coverage")

    @property
    def group_number(self) -> str:
        """
        Extracts group number from coverage class
        claim.insurance.coverage>coverage.class.value
        :return: string
        """
        try:
            cov_class = self.coverage.class_fhir
            for ccl in cov_class:
                if cast(Coding,
                        cast(CodeableConcept,
                             ccl.type
                             ).coding[0]
                        ).code == "group":
                    return ccl.value
            raise ClaimError()
        except (IndexError, AttributeError, ClaimError):
            raise ClaimError("Can't find coverage class group value")

    @property
    def group_name(self) -> str:
        """
        Extracts group name from coverage class
        claim.insurance.coverage>coverage.class.name
        :return: string
        """
        try:
            cov_class = self.coverage.class_fhir
            for ccl in cov_class:
                if cast(Coding,
                        cast(CodeableConcept,
                             ccl.type
                             ).coding[0]
                        ).code == "group":
                    return ccl.name
            raise ClaimError()
        except (IndexError, AttributeError, ClaimError):
            raise ClaimError("Can't find coverage class group name")

    def _identifiers_to_id(self) -> str:
        try:
            identifiers = cast(Identifier, self.coverage.identifier)
            if not identifiers:
                raise ClaimError()
        except (IndexError, AttributeError, ClaimError):
            raise ClaimError("Identifier not found for this claim line")
        # Single identifier.
        if len(identifiers) == 1:
            return identifiers[0].value
        # Multiple identifiers.
        ids = [identifier.value for identifier in identifiers]
        min_id = min(ids)
        # Case: 1234, 1234-01, 1234-02 identifiers.
        if all([id_.startswith(min_id) for id_ in ids]):
            return min_id
        # Case: 12341, 12342, 12343 identifiers.
        min_id = min_id[:-1]
        if all([id_.startswith(min_id) for id_ in ids]):
            return min_id
        raise ClaimError("Can't find primary coverage identifier")


def find_primary_insurance(insurances: List[ClaimInsurance], request: InsightEngineRequest) -> ClaimInsurance:
    """
    To identify primary insurance, one can use the `coverage.order` field inside
    the insurance to determine which one should go first, however, we can't expect
    it to be there all the time. So if it's missing the engine will have to take
    into account the following hierarchy of insurances:
    - Medicare
    - Tricare
    - Miscellaneous commercial insurance
    - Medicaid
    with only one special case:
    - If a patient has Tricare and commercial insurance then commercial insurance will be used
    """
    all_insurances = [ClaimInsuranceFocus(
        insurance, request=request) for insurance in insurances]
    selected_insurance = all_insurances[0]
    selected_insurance_coverage = selected_insurance.coverage
    selected_insurance_coverage_order = selected_insurance_coverage.order or float(
        "inf")
    try:
        selected_insurance_coverage_type = selected_insurance.coverage_type
    except ClaimError:
        selected_insurance_coverage_type = "other"

    for insurance in insurances:
        insurance = ClaimInsuranceFocus(insurance, request=request)
        insurance_coverage = insurance.coverage
        insurance_coverage_order = insurance_coverage.order or float("inf")
        try:
            insurance_coverage_type = insurance.coverage_type
        except ClaimError:
            insurance_coverage_type = "other"

        def swap_insurance():
            nonlocal selected_insurance, selected_insurance_coverage_order
            nonlocal selected_insurance_coverage, selected_insurance_coverage_type
            selected_insurance = insurance
            selected_insurance_coverage = insurance_coverage
            selected_insurance_coverage_order = insurance_coverage_order
            selected_insurance_coverage_type = insurance_coverage_type

        # if insurance.focal should not be used, then please,
        #     comment out following block of lines:
        if selected_insurance.insurance.focal and not insurance.insurance.focal:
            continue
        if insurance.insurance.focal and not selected_insurance.insurance.focal:
            swap_insurance()
            continue
        # Now they are either both focal or both non-focal.
        if selected_insurance_coverage_order < insurance_coverage_order:
            continue
        if insurance_coverage_order < selected_insurance_coverage_order:
            swap_insurance()
            continue
        # Now they both have the same coverage order
        if __insurance_precedes(insurance_coverage_type, selected_insurance_coverage_type):
            swap_insurance()
            continue
    return selected_insurance.insurance


def __insurance_precedes(insurance_type, selected_insurance_type) -> bool:
    """In case the coverage.order field is missing, the
    following order should be used based on insuranceType:
    1. Medicare
    2. Tricare
    3. Miscellaneous commercial insurance
    4. Medicaid
    The exception being when a patient has both Tricare and commercial
    insurance, then the commercial insurance should be used."""
    if selected_insurance_type == 'medicare':
        return False
    if insurance_type == 'medicare':
        return True
    if insurance_type == 'tricare':
        return selected_insurance_type == 'medicaid'
    if selected_insurance_type == 'tricare':
        return insurance_type != 'medicaid'
