from cytoolz.curried import curry, unique, concat
from glom import Coalesce

from genomoncology.kms.match import (
    calls_to_alterations,
    transform_match_response,
)
from genomoncology.parse import DocType, __TYPE__
from genomoncology.parse.ensures import ensure_collection


@curry
def match_trials(calls, diseases=None, sdk=None, dob=None, gender=None):
    alterations = calls_to_alterations(calls)
    diseases = ensure_collection(diseases or ["ANY"])

    response = sdk.call_with_retry(
        sdk.trials.match_trials_post,
        alterations=alterations,
        diseases=diseases,
        date_of_birth=dob,
        gender=gender,
    )

    return transform_match_response(response, DEFAULT_SPEC)


DEFAULT_SPEC = {
    __TYPE__: Coalesce(default=DocType.TRIAL.value),
    "nct_id": "nct_id",
    "title": "title",
    "phase": "phase",
    "recruiting_status": "recruiting_status",
    "trigger_alterations": (
        "detected_alterations",
        ["trigger_alterations"],
        lambda x: list(unique(concat(x))),
    ),
    "trigger_diseases": (
        "matched_diseases",
        ["matched_disease"],
        lambda x: list(unique(x)),
    ),
}
