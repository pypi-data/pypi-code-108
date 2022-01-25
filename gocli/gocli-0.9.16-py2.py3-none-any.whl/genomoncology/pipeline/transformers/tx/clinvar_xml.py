from cytoolz.curried import assoc, compose

from genomoncology.parse.doctypes import DocType, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping
from genomoncology.pipeline.transformers.functions import filter_keys

NAME_MAPPING = {
    # info
    "clinvar__CLNSIG__mstring": "clinvar__CLNSIG__mstring",
    "clinvar__variant_ID__string": "clinvar__variant_ID__string",
    "clinvar__CLNREVSTAT__mstring": "clinvar__CLNREVSTAT__mstring",
    "clinvar__CLNVI__mstring": "clinvar__CLNVI__mstring",
    "clinvar__CLNDN__mstring": "clinvar__CLNDN__mstring",
    "clinvar__all_submission_interpretations__mstring": "clinvar__all_submission_interpretations__mstring",  # noqa: E501
    "clinvar__all_submission_review_statuses__mstring": "clinvar__all_submission_review_statuses__mstring",  # noqa: E501
    "clinvar__all_submission_conditions__mstring": "clinvar__all_submission_conditions__mstring",  # noqa: E501
    "clinvar__all_submission_submitter__mstring": "clinvar__all_submission_submitter__mstring",  # noqa: E501
    "clinvar__all_submission_origin__mstring": "clinvar__all_submission_origin__mstring",  # noqa: E501
    "clinvar_alteration__string": "clinvar_alteration__string",
    "hgvs_g": "hgvs_g",
}

register(
    input_type=DocType.CLINVAR_XML,
    output_type=DocType.CLINVAR_XML,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.CLINVAR_XML.value),
        filter_keys(
            {
                "clinvar__CLNSIG__mstring",
                "clinvar__variant_ID__string",
                "clinvar__CLNREVSTAT__mstring",
                "clinvar__CLNVI__mstring",
                "clinvar__CLNDN__mstring",
                "clinvar__all_submission_interpretations__mstring",
                "clinvar__all_submission_review_statuses__mstring",
                "clinvar__all_submission_conditions__mstring",
                "clinvar__all_submission_submitter__mstring",
                "clinvar__all_submission_origin__mstring",
                "clinvar_alteration__string",
                "hgvs_g",
            }
        ),
        name_mapping(NAME_MAPPING),
    ),
)
