from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping
from genomoncology.pipeline.transformers.functions import filter_keys

# Note: this transformer is not used with any of the new
# clinvar loading commands

ORIGIN_MAPPING = {
    "0": "unknown",
    "1": "germline",
    "2": "somatic",
    "4": "inherited",
    "8": "paternal",
    "16": "maternal",
    "32": "de-novo",
    "64": "biparental",
    "128": "uniparental",
    "256": "not-tested",
    "512": "tested-inconclusive",
    "1073741824": "other",
}

NAME_MAPPING = {
    # hgvs
    "chr": "chr",
    "start": "start",
    "ref": "ref",
    "alt": "alt",
    # info
    "CLNSIG__mstring": "info.CLNSIG",
    "variant_ID__string": "id",
    "CLNREVSTAT__mstring": "info.CLNREVSTAT",
    "CLNVI__mstring": "info.CLNVI",
    "ORIGIN__mstring": "info.ORIGIN",
    "CLNDN__mstring": "info.CLNDN",
}


def clean_origin(value):
    value = [ORIGIN_MAPPING.get(value[int(i)]) for i in range(0, len(value))]
    return value


def clean_clndn(value):
    clndn_values = []
    for item in value:
        for clndn in item.split("|"):
            clndn_values.append(clndn)
    return clndn_values


register(
    input_type=DocType.CALL,
    output_type=DocType.CLINVAR,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.CLINVAR.value),
        filter_keys(
            {
                "CLNSIG__mstring",
                "variant_ID__string",
                "CLNREVSTAT__mstring",
                "CLNVI__mstring",
                "ORIGIN__mstring",
                "CLNDN__mstring",
                "hgvs_g",
            }
        ),
        lambda x: assoc(
            x, "ORIGIN__mstring", clean_origin(x.get("ORIGIN__mstring", ""))
        ),
        lambda x: assoc(
            x, "CLNDN__mstring", clean_clndn(x.get("CLNDN__mstring", ""))
        ),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.CLINVAR,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.CLINVAR.value)),
    is_header=True,
)
