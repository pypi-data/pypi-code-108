from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    "gene": "gene",
    "protein_full_name__string": "protein_full_name",
}

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT_PROTEIN_NAME,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.UNIPROT_PROTEIN_NAME.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT_PROTEIN_NAME,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.UNIPROT_PROTEIN_NAME.value),
    ),
    is_header=True,
)
