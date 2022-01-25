from typing import Dict, cast

from fhir.resources.claim import Claim
from fhir.resources.resource import Resource


def contained_resources(claim: Claim) -> Dict[str, Resource]:
    if not hasattr(claim, "contained"):
        return dict()
    return {
        cast(Resource, element).id:
            cast(Resource, element)
        for element in claim.contained
    }
