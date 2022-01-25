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
    "AC__int": "info.AC",
    "AC_Adj__int": "info.AC_Adj",
    "AF__float": "info.AF",
    "AN__int": "info.AN",
    "AN_Adj__int": "info.AN_Adj",
    "AC_AFR__int": "info.AC_AFR",
    "AC_AMR__int": "info.AC_AMR",
    "AC_EAS__int": "info.AC_EAS",
    "AC_FIN__int": "info.AC_FIN",
    "AC_NFE__int": "info.AC_NFE",
    "AC_OTH__int": "info.AC_OTH",
    "AC_SAS__int": "info.AC_SAS",
    "AN_AFR__int": "info.AN_AFR",
    "AN_AMR__int": "info.AN_AMR",
    "AN_EAS__int": "info.AN_EAS",
    "AN_FIN__int": "info.AN_FIN",
    "AN_NFE__int": "info.AN_NFE",
    "AN_OTH__int": "info.AN_OTH",
    "AN_SAS__int": "info.AN_SAS",
    "Hemi_AFR__int": "info.Hemi_AFR",
    "Hemi_AMR__int": "info.Hemi_AMR",
    "Hemi_EAS__int": "info.Hemi_EAS",
    "Hemi_FIN__int": "info.Hemi_FIN",
    "Hemi_NFE__int": "info.Hemi_NFE",
    "Hemi_OTH__int": "info.Hemi_OTH",
    "Hemi_SAS__int": "info.Hemi_SAS",
    "Het_AFR__mint": "info.Het_AFR",
    "Het_AMR__mint": "info.Het_AMR",
    "Het_EAS__mint": "info.Het_EAS",
    "Het_FIN__mint": "info.Het_FIN",
    "Het_NFE__mint": "info.Het_NFE",
    "Het_OTH__mint": "info.Het_OTH",
    "Het_SAS__mint": "info.Het_SAS",
    "Hom_AFR__int": "info.Hom_AFR",
    "Hom_AMR__int": "info.Hom_AMR",
    "Hom_EAS__int": "info.Hom_EAS",
    "Hom_FIN__int": "info.Hom_FIN",
    "Hom_NFE__int": "info.Hom_NFE",
    "Hom_OTH__int": "info.Hom_OTH",
    "Hom_SAS__int": "info.Hom_SAS",
}

register(
    input_type=DocType.CALL,
    output_type=DocType.EXAC,
    transformer=compose(
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, __TYPE__, DocType.EXAC.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.CALL,
    output_type=DocType.EXAC,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.EXAC.value)),
    is_header=True,
)
