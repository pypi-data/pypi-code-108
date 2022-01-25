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
    "build": "build",
    # info
    "DSS__int": "info.DSS",
    "WSSF__float": "info.WSSF",
    "VSSF__float": "info.VSSF",
    "WME__float": "info.WME",
    "VME__float": "info.VME",
    "LWME__float": "info.LWME",
    "LVME__float": "info.LVME",
    "LWNNS__float": "info.LWNNS",
    "LVNNS__float": "info.LVNNS",
    "LWHSF__float": "info.LWHSF",
    "LVHSF__float": "info.LVHSF",
}

register(
    input_type=DocType.CALL,
    output_type=DocType.SPLICING,
    transformer=compose(
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, __TYPE__, DocType.SPLICING.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.SPLICING,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.SPLICING.value)),
    is_header=True,
)
