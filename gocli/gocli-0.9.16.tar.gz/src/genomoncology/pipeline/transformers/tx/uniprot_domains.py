from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    "gene": "gene",
    "accessions__mstring": "accessions",
    "domains__mstring": "domains",
    "domain_starts__mstring": "domain_starts",
    "domain_ends__mstring": "domain_ends",
}

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT_DOMAIN,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.UNIPROT_DOMAIN.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT_DOMAIN,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.UNIPROT_DOMAIN.value),
    ),
    is_header=True,
)
