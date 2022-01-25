from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "gene": "gene",
    # info
    "phenotype__mstring": "phenotype",
    "hpo__mstring": "hpo_id",
}


def parse_hpo_gene(x):
    return x["key"]


register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.HPO,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.HPO.value),
        name_mapping(NAME_MAPPING),
        lambda x: assoc(x, "gene", parse_hpo_gene(x)),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.HPO,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.HPO.value),
    ),
    is_header=True,
)
