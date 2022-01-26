"""Tags that are used in the fluffy pipeline"""

FLUFFY_COMMON_TAGS = {
    frozenset(["multiqc"]): {
        "tags": ["multiqc-html"],
        "is_mandatory": True,
        "used_by": ["nipt"],
    },
    frozenset(["nipt_csv"]): {
        "tags": ["metrics"],
        "bundle_id": True,
        "is_mandatory": True,
        "used_by": ["nipt"],
    },
    frozenset(["nipt_first_pass_csv"]): {
        "tags": ["first-pass"],
        "bundle_id": True,
        "is_mandatory": False,
        "used_by": ["nipt"],
    },
    frozenset(["nipt_second_pass_csv"]): {
        "tags": ["second-pass"],
        "bundle_id": True,
        "is_mandatory": False,
        "used_by": ["nipt"],
    },
    frozenset(["wisecondor_aberrations"]): {
        "tags": ["wisecondor", "cnv"],
        "is_mandatory": True,
        "used_by": ["nipt"],
    },
}
