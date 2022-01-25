from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping
from genomoncology.pipeline.transformers.functions import turn_gene_to_list

NAME_MAPPING = {
    "gene": "gene",
    "disease_name__string": "disease_name",
    "disease_mim__string": "disease_mim",
}


register(
    input_type=DocType.TSV,
    output_type=DocType.SECONDARY_FINDINGS_GENES,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.SECONDARY_FINDINGS_GENES.value),
        lambda x: assoc(x, "gene", turn_gene_to_list(x)),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.TSV,
    output_type=DocType.SECONDARY_FINDINGS_GENES,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.SECONDARY_FINDINGS_GENES.value),
    ),
    is_header=True,
)
