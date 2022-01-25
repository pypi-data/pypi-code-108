from cytoolz.curried import curry

from genomoncology.cli.const import GRCh37
from genomoncology.kms.annotations import convert_to_csra, to_csra
from genomoncology.parse import (
    is_call_or_variant,
    DocType,
    __CHILD__,
    __TYPE__,
)
from genomoncology.pipeline.converters import obj_to_dict
from gosdk.models import VariantInterpretationResponse


@curry
def get_variant_interpretations(
    data, sdk=None, template_name=None, delete_if_exists=False, build=GRCh37
):
    csra_batch = convert_to_csra(
        [{**d, "build": build} for d in data], add_build=False
    )

    variant_interpretations_response = (
        sdk.call_with_retry(
            sdk.variant_interpretations.generate_variant_interpretations,
            batch=csra_batch,
            template_names=[template_name],
            delete_if_exists=delete_if_exists,
            build=build,
        )
        if csra_batch
        else None
    )

    variant_interpretations_calls = []
    for call in data:
        variant_interpretations_calls.append(
            add_interpretations_to_calls(
                variant_interpretations_response, call
            )
        )

    return variant_interpretations_calls


def add_interpretations_to_calls(
    interpretations_response: VariantInterpretationResponse, call: dict
):
    if interpretations_response and is_call_or_variant(call):
        csra = to_csra(call, add_build=False)
        variant_interpretation_data = obj_to_dict(
            None, interpretations_response.get_var_int_data(csra) or {}
        )
        call["variant_interpretations"] = variant_interpretation_data.get(
            "variant_interpretations", []
        )
        call["protein_effects"] = variant_interpretation_data.get(
            "protein_effects", []
        )
        call["annotations"] = variant_interpretation_data.get(
            "annotations", {}
        )
        call[__TYPE__] = f"ANNOTATED_{call.get(__TYPE__, 'CALL')}"

    elif DocType.HEADER.is_a(call):
        call[__CHILD__] = f"ANNOTATED_{call.get(__CHILD__, 'CALL')}"

    return call
