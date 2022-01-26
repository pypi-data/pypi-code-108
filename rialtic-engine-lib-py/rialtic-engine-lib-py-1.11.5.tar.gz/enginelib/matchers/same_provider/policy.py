from typing import Optional

from fhir.resources.claim import Claim, ClaimItem
from schema.insight_engine_request import InsightEngineRequest

from enginelib.claim_focus import ClaimFocus
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.errors import ClaimError, MissingFieldError

from .predicates import valid_taxonomy_code, match_taxonomy_codes
from .result import SameProviderResult


# TODO: Remove `apikey` once versions will be implemented.
def same_provider(
    cue: Claim,
    clue: ClaimItem,
    oc: Claim,
    ocl: ClaimItem,
    apikey: Optional[str] = None) -> SameProviderResult:
    """
    Args:
        cue: the claim under evaluation
        clue: the claim line under evaluation
        oc: other claim
        ocl: other claim line
        apikey: just a placeholder for backward-compatibility

    Raises:
        ClaimError if the following conditions are satisfied:
            1. rendProvNPI exist for both the CLUE and the CUE and are different; and...
                1.1 subject to 1, billProvNPI is missing in the CUE or in the OC; or
                1.2 subject to 1, rendProvTaxonomy is missing in the CLUE or the OCL; or
                1.3 subject to 1, billProvNPI exists for both the CUE or in the OC; and...
                    1.3.1 subject to 1 and 1.3, provTaxID is missing for either CUE or OC
    """

    # Wrap clue and ocl inside ClaimLineFocus
    cue_request = InsightEngineRequest.construct(claim=cue)
    clue = ClaimLineFocus(claim_line=clue, request=cue_request)
    oc_request = InsightEngineRequest.construct(claim=oc)
    ocl = ClaimLineFocus(claim_line=ocl, request=oc_request)

    # Wrap cue and oc inside ClaimFocus
    cue = ClaimFocus(claim=cue)
    oc = ClaimFocus(claim=oc)

    # START -> Node 100: Are CLUE and OCL rendProvNPI populated?
    try:
        clue_npi = clue.rend_prov_npi
        ocl_npi = ocl.rend_prov_npi
    except MissingFieldError:
        return SameProviderResult.Facility  # 100N

    try:
        # 100Y -> Node 200: Do CLUE and OCL have the same rendProvNPI?
        if clue_npi == ocl_npi:
            return SameProviderResult.SameRendering  # 200Y

        # 200N -> Node 300: Do OCL and CLUE have the same billProvNPI?
        if cue.bill_prov_npi == oc.bill_prov_npi:
            # 300Y -> Node 400: Are OCL and CLUE rendProvTaxonomy values
            #     both valid codes (as listed in Taxonomy crosswalk)?
            if valid_taxonomy_code(clue.rend_prov_taxonomy) and \
                    valid_taxonomy_code(ocl.rend_prov_taxonomy):
                # 400Y -> Node 600: Do CLUE and OCL have the same "MEDICARE
                #     SPECIALTY CODE" based on rendProvTaxonomy match to
                #     "PROVIDER TAXONOMY CODE" in Taxonomy Crosswalk?
                if match_taxonomy_codes(clue.rend_prov_taxonomy, ocl.rend_prov_taxonomy):
                    return SameProviderResult.Partial600Y

                # 600N
                return SameProviderResult.Partial600N

            # 400N
            return SameProviderResult.Partial400N

        # 300N -> Node 500: CLUE and OCL have the same provTaxID?
        # [new FHIR mapping]: assuming each billing provider has a unique provTaxID
        if cue.prov_tax_id == oc.prov_tax_id:
            # 500Y -> Node 700: Are OCL and CLUE rendProvTaxonomy values
            #     both valid codes (as listed in Taxonomy crosswalk)?
            if valid_taxonomy_code(clue.rend_prov_taxonomy) and \
                    valid_taxonomy_code(ocl.rend_prov_taxonomy):
                # 700Y -> Node 800: Do CLUE and OCL have the same "MEDICARE
                #     SPECIALTY CODE" based on rendProvTaxonomy match to
                #     "PROVIDER TAXONOMY CODE" in Taxonomy Crosswalk?
                if match_taxonomy_codes(clue.rend_prov_taxonomy,
                                        ocl.rend_prov_taxonomy):
                    return SameProviderResult.Partial800Y

                # 800N
                return SameProviderResult.Partial800N

            # 700N
            return SameProviderResult.Partial700N

        # 500N
        return SameProviderResult.Different
    except (ClaimError, MissingFieldError):
        return SameProviderResult.Error
