from fhir.resources.claim import Claim
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address
from enginelib.matchers.same_patient.result import SamePatientResult
from enginelib.claim_focus import ClaimFocus, ClaimError

from .predicates import same_address, different_gender, normalize


from typing import cast

from enginelib.errors import MissingFieldError


def same_patient(cue: Claim, oc: Claim) -> SamePatientResult:
    mapping = {
        '100N': SamePatientResult.Different,
        '200Y': SamePatientResult.Same,
        '300N': SamePatientResult.Different,
        '400N': SamePatientResult.Different,
        '600Y': SamePatientResult.Suspected600Y,
        '700N': SamePatientResult.Different,
        '800Y': SamePatientResult.Suspected800Y,
        '800N': SamePatientResult.Different,
        '900Y': SamePatientResult.Suspected900Y,
        '900N': SamePatientResult.Different
    }

    # noinspection PyBroadException
    try:
        label = same_patient_label(cue, oc)
    except ClaimError as err:
        raise err
    except Exception:
        return SamePatientResult.Error

    return mapping.get(label, SamePatientResult.Error)


def same_patient_label(cue: Claim, oc: Claim) -> str:
    cue_focus = ClaimFocus(cue)
    oc_focus = ClaimFocus(oc)
    if not cue.insurance:
        raise ClaimError("No insurance found for CUE")
    if not oc.insurance:
        raise ClaimError("No insurance found for OC")

    try:
        ids_equal = cue_focus.subscriber_id == oc_focus.subscriber_id
    except MissingFieldError:
        ids_equal = False

    # node 100
    #   true -> node 200
    #   false -> SamePatientResult.Different
    if not ids_equal:
        return '100N'

    try:
        relations_equal = (
                cue_focus.relation_to_insured in ['18', 'self'] and
                oc_focus.relation_to_insured in ['18', 'self']
        )
    except MissingFieldError:
        relations_equal = False
    # node 100: insurance.subscriberID == oc.insurance.subscriberID

    # node 200: cue.insurance.relationToInsured == oc.insurance.relationToInsured
    #   true -> SamePatient.Same
    #   false -> node 300
    if relations_equal:
        return '200Y'

    # node 300: cue.patient.BirthDate == oc.patient.BirthDate
        # true -> node 400
        # false -> SamePatientResult.Different
    if cue_focus.patient.birthDate != oc_focus.patient.birthDate:
        return '300N'

    # node 400: cue.patient.gender =? oc.patient.gender
        # true -> node 500
        # false -> SamePatientResult.Different
    if different_gender(normalize(cue_focus.patient.gender),
                        normalize(oc_focus.patient.gender)):
        return '400N'

    # Names: could probably also think a bit more about the
    # valid relations between names the same person can have.
    # Kind of sceptical of the heuristic
    # "nicknames start with the same first 3 letters as the
    # given name they riff on".

    # But until that's resolved:

    # patients are guaranteed to only have 1 full name
    cueName = cast(HumanName, cue_focus.patient.name[0])
    ocName = cast(HumanName, oc_focus.patient.name[0])

    # node 500: cue.patient.name.given === oc.patient.name.given
    # true -> node 600
    # false -> node 700
    if normalize(' '.join(sorted(cueName.given))) == \
            normalize(' '.join(sorted(ocName.given))):
        # node 600: cue.patient.name.family == oc.patient.name.family
        # true -> Suspected600Y
        # false -> node 800
        if normalize(cueName.family) == \
                normalize(ocName.family):
            return '600Y'

        # node 800: cue and oc have the same address
        # Note; while FHIR allows patients to have multiple addresses,
        # Rialtic claims will only have 1 address per patient
        # true -> Suspected800Y
        # false -> Different
        elif same_address(cast(Address, cue_focus.patient.address[0]),
                          cast(Address, oc_focus.patient.address[0]),
                          ):
            return '800Y'
        else:
            return '800N'

    else:
        # node 700: cue.patient.name.given[:3] == oc.patient.name.given[:3]
        # true -> node 900
        # false -> Different
        if normalize(cueName.given[0][:3]) == \
                normalize(ocName.given[0][:3]):

            # node 900: cue.patient.name.family == oc.patient.name.family
            # true -> Suspected900Y
            # false -> Different
            if normalize(cueName.family) == \
               normalize(ocName.family):
                return '900Y'
            else:
                return '900N'
        else:
            return '700N'
