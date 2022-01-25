from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    # hgvs
    "chr": "chr",
    "start": "start",
    "ref": "ref",
    "alt": "alt",
    # info
    "AC__int": "info.AC",
    "AF__float": "info.AF",
    "AN__int": "info.AN",
    "EAS_AF__float": "info.EAS_AF",
    "AMR_AF__float": "info.AMR_AF",
    "AFR_AF__float": "info.AFR_AF",
    "EUR_AF__float": "info.EUR_AF",
    "SAS_AF__float": "info.SAS_AF",
}

register(
    input_type=DocType.CALL,
    output_type=DocType.THOUSANDGENOMES,
    transformer=compose(
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, __TYPE__, DocType.THOUSANDGENOMES.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.THOUSANDGENOMES,
    transformer=compose(
        lambda x: assoc(x, __CHILD__, DocType.THOUSANDGENOMES.value)
    ),
    is_header=True,
)
