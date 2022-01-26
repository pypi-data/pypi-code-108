from re import split
from deprecation import deprecated
from typing import Generator, List, Optional, cast

from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coverage import Coverage
from fhir.resources.reference import Reference

from enginelib.claim_focus import ClaimFocus, ClaimInsurance


__US_STATE_ABBRV = {
    "AL": "alabama",
    "AK": "alaska",
    "AR": "arkansas",
    "AZ": "arizona",
    "CA": "california",
    "CO": "colorado",
    "CT": "connecticut",
    "DE": "delaware",
    "DC": "district of columbia",
    "FL": "florida",
    "GA": "georgia",
    "HI": "hawaii",
    "ID": "idaho",
    "IL": "illinois",
    "IN": "indiana",
    "IA": "iowa",
    "KS": "kansas",
    "KY": "kentucky",
    "LA": "louisiana",
    "ME": "maine",
    "MD": "maryland",
    "MA": "massachusetts",
    "MI": "michigan",
    "MN": "minnesota",
    "MS": "mississippi",
    "MO": "missouri",
    "MT": "montana",
    "NE": "nebraska",
    "NV": "nevada",
    "NH": "new hampshire",
    "NJ": "new jersey",
    "NY": "new york",
    "NC": "north carolina",
    "ND": "north dakota",
    "OH": "ohio",
    "OK": "oklahoma",
    "OR": "oregon",
    "PA": "pennsylvania",
    "PR": "puerto rico",
    "RI": "rhode island",
    "SC": "south carolina",
    "SD": "south dakota",
    "TN": "tennessee",
    "TX": "texas",
    "UT": "utah",
    "VT": "vermont",
    "VA": "virginia",
    "WV": "west virginia",
    "WI": "wisconsin",
    "WY": "wyoming",
}


@deprecated(
    deprecated_in="0.0.9",
    removed_in="1.0.0",
    details="Use `ClaimFocus.subscriber_id` instead."
    )
def subscriber_ids(cue: ClaimFocus) -> Generator[str, None, None]:
    """DEPRECATED.

    Use `ClaimFocus.subscriber_id` instead.
    TODO(plyq): Remove after versioning implementation.
    Not used in `same_patient` matcher.
    """
    for ins in cue.claim.insurance:
        coverage: Coverage = cue.contained[ins.coverage.reference]
        yield coverage.subscriberId


def normalize(txt: Optional[str]) -> Optional[str]:
    return txt.lower().strip().strip(",").strip(".") \
        if txt is not None else None


def same_address(address1: Address, address2: Address) -> bool:
    # both have a text description
    if (
        address1.text is not None
        and address2.text is not None
        and normalize(address2.text) ==
            normalize(address1.text)
    ):
        return True

    are_same = [
        _same_address_by_field(address1, address2),
        _same_address_field2txt(address1, address2),
        _same_address_field2txt(address2, address1),
    ]
    return any(are_same)


def _same_address_field2txt(
    field_address: Address, text_address: Address
) -> bool:
    """
    Compare whether the address given in the attributes of one address
    match the address in the text of another address
    """
    if text_address.text is None or field_address.text is not None:
        return False
    return all(
        elt is None or elt in normalize(text_address.text)
        for elt in [normalize(field_address.line[0])]
        + [
            normalize(field_address.city),
            normalize(field_address.state),
            normalize(field_address.district),
            normalize(field_address.postalCode),
            normalize(field_address.country),
        ]
    )


def _get_state(state_name: Optional[str]) -> Optional[str]:
    if state_name is None:
        return None
    elif state_name in __US_STATE_ABBRV:
        return __US_STATE_ABBRV[state_name]
    else:
        return state_name.lower()


def _same_address_by_field(address1: Address, address2: Address) -> bool:
    """
    Compare whether the fields of two Addresses describe the same address
    """
    if address1.line is None or address2.line is None:
        return False

    def equal_or_null(a: Optional[str], b: Optional[str]):
        return a is None or b is None or a == b

    # fields: line, country, city, state, district, postal code
    return (
            len({normalize(address1.line[0])} &
                {normalize(address2.line[0])}) > 0
            and equal_or_null(normalize(address1.country),
                          normalize(address2.country))
            and equal_or_null(normalize(address1.city),
                          normalize(address2.city))
            and equal_or_null(
            _get_state(address1.state), _get_state(address2.state)
        )
            and equal_or_null(normalize(address1.district),
                          normalize(address2.district))
            and equal_or_null(normalize(address1.postalCode),
                          normalize(address2.postalCode))
    )


def different_gender(gender1: Optional[str], gender2: Optional[str]) -> bool:
    """Are two gender codes determinative of different genders"""
    if gender1 is None or gender2 is None:
        return True
    if gender1 == "unknown" or gender2 == "unknown":
        return True

    else:
        return gender1 != gender2


@deprecated(
    deprecated_in="0.0.9",
    removed_in="1.0.0",
    details="Use `ClaimFocus.relation_to_insured` instead."
    )
def same_relation_to_insured(
    claim1: ClaimFocus, claim2: ClaimFocus
) -> Generator[bool, None, None]:
    """DEPRECATED.

    Use `ClaimFocus.relation_to_insured` instead.
    TODO(plyq): Remove after versioning implementation.
    Not used in `same_patient` matcher.
    """
    for ins1 in claim1.claim.insurance:
        for ins2 in claim2.claim.insurance:
            r1 = _get_relations_to_insured(claim1, ins1)
            r2 = _get_relations_to_insured(claim2, ins2)
            yield any(
                relation in r1 and relation != "other" for relation in r2
            )


def _get_relations_to_insured(
    claim_focus: ClaimFocus, ins: ClaimInsurance
) -> List[str]:

    claim_ins = cast(ClaimInsurance, ins).coverage
    try:
        ref = cast(Reference, claim_ins).reference
        cov = cast(Coverage, claim_focus.contained[ref])
    except KeyError:
        return []

    relation = cast(CodeableConcept, cov.relationship)
    if relation is not None:
        return [coding.code for coding in relation.coding]
    else:
        return []
