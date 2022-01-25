from cytoolz.curried import assoc, compose

from genomoncology import kms
from genomoncology.parse.doctypes import DocType, __TYPE__, __CHILD__
from genomoncology.pipeline.transformers.functions import filter_keys
from genomoncology.pipeline.transformers.registry import register
from genomoncology.pipeline.transformers.mapper_classes import VariantMapper


SSR_MAPPING = {
    0: "unspecified",
    1: "Paralog",
    2: "byEST",
    4: "oldAlign",
    8: "Para_EST",
    16: "1kg_failed",
    1024: "other",
    3: "Paralog,byEST",
    5: "oldAlign,Paralog",
    6: "oldAlign,byEST",
    9: "Para_EST,Paralog",
    10: "Para_EST,byEST",
    12: "Para_EST,oldAlign",
    11: "Para_EST,Paralog,byEST",
    13: "Para_EST,Paralog,oldAlign",
    14: "Para_EST,byEST,oldAlign",
    17: "Paralogkg_failed,Paralog",
    18: "Paralogkg_failed,byEST",
    20: "Paralogkg_failed,oldAlign",
    24: "Paralogkg_failed,Para_EST",
    19: "Paralogkg_failed,Paralog,byEST",
    21: "Paralogkg_failed,Paralog,oldAlign",
    25: "Paralogkg_failed,Paralog,Para_EST",
    22: "Paralogkg_failed,byEST,oldAlign",
    26: "Paralogkg_failed,byEST,Para_EST",
    28: "Paralogkg_failed,oldAlign,Para_EST",
    23: "Paralogkg_failed,Paralog,byEST,oldAlign",
    27: "Paralogkg_failed,Paralog,byEST,Para_EST",
    30: "Paralogkg_failed,byEST,oldAlign,Para_EST",
    31: "Paralogkg_failed,Paralog,byEST,oldAlign,Para_EST",
    1025: "other,Paralog",
    1026: "other,byEST",
    1028: "other,oldAlign",
    1032: "other,Para_EST",
    1040: "other,Paralogkg_failed",
    1027: "other,Paralog,byEST",
    1029: "other,Paralog,oldAlign",
    1033: "other,Paralog,Para_EST",
    1041: "other,Paralog,Paralogkg_failed",
    1030: "other,byEST,oldAlign",
    1034: "other,byEST,Para_EST",
    1042: "other,byEST,Paralogkg_failed",
    1036: "other,oldAlign,Para_EST",
    1044: "other,oldAlign,Paralogkg_failed",
    1048: "other,Para_EST,Paralogkg_failed",
    1031: "other,Paralog,byEST,oldAlign",
    1035: "other,Paralog,byEST,Para_EST",
    1043: "other,Paralog,byEST,Paralogkg_failed",
    1037: "other,Paralog,oldAlign,Para_EST",
    1045: "other,Paralog,oldAlign,Paralogkg_failed",
    1049: "other,Paralog,Para_EST,Paralogkg_failed",
    1038: "other,byEST,oldAlign,Para_EST",
    1046: "other,byEST,oldAlign,Paralogkg_failed",
    1050: "other,byEST,Para_EST,Paralogkg_failed",
    1052: "other,oldAlign,Para_EST,Paralogkg_failed",
    1039: "other,Paralog,byEST,oldAlign,Para_EST",
    1047: "other,Paralog,byEST,oldAlign,Paralogkg_failed",
    1053: "other,Paralog,oldAlign,Para_EST,Paralogkg_failed",
    1054: "other,byEST,oldAlign,Para_EST,Paralogkg_failed",
    1055: "other,Paralog,byEST,oldAlign,Para_EST,Paralogkg_failed",
}


def clean_ssr(value):
    if type(value) == int:
        value = SSR_MAPPING.get(value)
    return value


register(
    input_type=DocType.CALL,
    output_type=DocType.DBSNP,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.DBSNP.value),
        filter_keys(
            {"VLD__string", "SSR__string", "RS__string", "hgvs_g", "csra"}
        ),
        # clean SSR: replace origin int code with string
        lambda x: assoc(x, "SSR__string", clean_ssr(x.get("SSR__string", ""))),
        lambda x: assoc(x, "csra", kms.annotations.to_csra(x)),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        # convert Call to Variant
        VariantMapper(),
    ),
    is_header=False,
)

register(
    input_type=DocType.CALL,
    output_type=DocType.DBSNP,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.DBSNP.value)),
    is_header=True,
)
