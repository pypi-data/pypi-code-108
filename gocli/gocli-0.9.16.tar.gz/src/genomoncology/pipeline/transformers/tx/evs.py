from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


def convert_ac_to_vaf(x, field):
    return (
        float(x[field][x["orig_alts__mstring"].index(x["alt"]) + 1])
        / sum([float(i) for i in x[field]])
    ) * 100


NAME_MAPPING = {
    # hgvs
    "chr": "chr",
    "start": "start",
    "ref": "ref",
    "alt": "alt",
    "build": "build",
    "orig_alts__mstring": "__record__",
    # info
    "EA__float": "info.EA_AC",
    "AA__float": "info.AA_AC",
    "All__float": "info.TAC",
}

register(
    input_type=DocType.CALL,
    output_type=DocType.EVS,
    transformer=compose(
        lambda x: assoc(x, "EA__float", convert_ac_to_vaf(x, "EA__float")),
        lambda x: assoc(x, "AA__float", convert_ac_to_vaf(x, "AA__float")),
        lambda x: assoc(x, "All__float", convert_ac_to_vaf(x, "All__float")),
        lambda x: assoc(x, "orig_alts__mstring", x["orig_alts__mstring"].alts),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, __TYPE__, DocType.EVS.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.EVS,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.EVS.value)),
    is_header=True,
)
