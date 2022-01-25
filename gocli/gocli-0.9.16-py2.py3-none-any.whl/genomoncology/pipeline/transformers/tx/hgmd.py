from cytoolz.curried import assoc, compose

from genomoncology import kms
from genomoncology.parse.doctypes import DocType, __TYPE__, __CHILD__
from genomoncology.pipeline.transformers.functions import filter_keys
from genomoncology.pipeline.transformers.registry import register
from genomoncology.pipeline.transformers.mapper_classes import VariantMapper


def clean_PROT__string(value):
    if isinstance(value, str):
        value = value.replace("%3D", "=").replace("%3A", ":")
    return value


def clean_DNA__string(value):
    if isinstance(value, str):
        value = value.replace("%3D", "=").replace("%3A", ":")
    return value


def clean_PHEN_string(value):
    if isinstance(value, tuple):
        value = ",".join(value)
    return value[1:-1].replace("%2C", ",").replace("_", " ")


register(
    input_type=DocType.CALL,
    output_type=DocType.HGMD,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.HGMD.value),
        filter_keys(
            {
                "CLASS__string",
                "DB__string",
                "DNA__string",
                "GENE__string",
                "PHEN__string",
                "PROT__string",
                "ID__string",
                "hgvs_g",
                "csra",
            }
        ),
        lambda x: assoc(
            x, "PROT__string", clean_PROT__string(x.get("PROT__string"))
        ),
        lambda x: assoc(
            x, "DNA__string", clean_PROT__string(x.get("DNA__string"))
        ),
        # clean PHEN: remove lead/trail quotes, replace underscores w/ spaces
        lambda x: assoc(
            x, "PHEN__string", clean_PHEN_string(x.get("PHEN__string", ""))
        ),
        lambda x: assoc(x, "ID__string", x.get("id", None)),
        lambda x: assoc(x, "csra", kms.annotations.to_csra(x)),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        # convert Call to Variant
        VariantMapper(),
    ),
    is_header=False,
)

register(
    input_type=DocType.CALL,
    output_type=DocType.HGMD,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.HGMD.value)),
    is_header=True,
)
