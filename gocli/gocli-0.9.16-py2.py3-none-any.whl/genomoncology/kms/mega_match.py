from cytoolz.curried import curry

from genomoncology.kms.match import vie_results_to_alts
from gosdk.models import MegaMatchResult

PARAM_NAME_CHANGES = {
    "exclude_non1a_negative_matches": "exclude_non1A_negative_matches"
}


@curry
def mega_match(vies, sdk=None, **kwargs):
    # get the alterations
    alterations, benign_alterations = vie_results_to_alts(vies)

    # convert any parameter names that were changed by click
    for param_name, updated_name in PARAM_NAME_CHANGES.items():
        if param_name in kwargs:
            kwargs[updated_name] = kwargs.pop(param_name, None)

    mega_match_response = sdk.call_with_retry(
        sdk.therapies.mega_match_post,
        alterations=alterations,
        benign_alterations=benign_alterations,
        **kwargs,
    )

    return convert_mega_match_response(mega_match_response)


def convert_mega_match_response(mm_response: MegaMatchResult):
    if mm_response:
        mm_response = mm_response.convert_to_dict()
    return mm_response
