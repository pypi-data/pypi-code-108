from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "gene": "gene",
    # info
    "disease_name__mstring": "disease name",
    "gene_mim__mstring": "gene mim",
    "disease_mim__mstring": "disease mim",
    "DDD_category__mstring": "DDD category",
    "allelic_requirement__mstring": "allelic requirement",
    "mutation_consequence__mstring": "mutation consequence",
    "phenotypes__mstring": "phenotypes",
    "organ_specificity_list__mstring": "organ specificity list",
    "pmids__mstring": "pmids",
    "panel__mstring": "panel",
    "prev_symbols__mstring": "prev symbols",
    "hgnc_id__mstring": "hgnc id",
    "gene_disease_pair_entry_date__mstring": "gene disease pair entry date",
}

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.BAYLOR_DECIPHER,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.BAYLOR_DECIPHER.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.BAYLOR_DECIPHER,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.BAYLOR_DECIPHER.value),
    ),
    is_header=True,
)
