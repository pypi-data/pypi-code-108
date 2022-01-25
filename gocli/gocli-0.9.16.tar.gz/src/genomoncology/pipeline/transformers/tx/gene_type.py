from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import (
    register,
    name_mapping,
    get_boolean_value,
)


NAME_MAPPING = {
    "gene": "gene",
    "oncogene__boolean": "oncogene",
    "tumor_suppressor__boolean": "tumor_suppressor",
    "source__string": "source",
}

register(
    input_type=DocType.TSV,
    output_type=DocType.GENE_TYPE,
    transformer=compose(
        lambda x: assoc(
            x,
            "tumor_suppressor__boolean",
            get_boolean_value(x.get("tumor_suppressor__boolean", "")),
        ),
        lambda x: assoc(
            x,
            "oncogene__boolean",
            get_boolean_value(x.get("oncogene__boolean", "")),
        ),
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.GENE_TYPE.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.TSV,
    output_type=DocType.GENE_TYPE,
    transformer=compose(
        lambda x: assoc(
            x,
            "tumor_suppressor__boolean",
            get_boolean_value(x.get("tumor_suppressor__boolean", "")),
        ),
        lambda x: assoc(
            x,
            "oncogene__boolean",
            get_boolean_value(x.get("oncogene__boolean", "")),
        ),
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.GENE_TYPE.value),
    ),
    is_header=True,
)
