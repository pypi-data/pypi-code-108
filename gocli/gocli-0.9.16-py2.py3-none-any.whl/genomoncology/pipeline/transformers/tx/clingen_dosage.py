from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import (
    register,
    name_mapping,
    split_value,
)

SPLIT_CHARS = ",;"

NAME_MAPPING = {
    "gene": "Gene Symbol",
    "haploinsufficiency_score__int": "Haploinsufficiency Score",
    "haploinsufficiency_evidence__string": "Haploinsufficiency Description",
    "haploinsufficiency_pubmed_id__mstring": "haplo_pmid",
    "haploinsufficient_phenotype_ID__mstring": "haplo_omim",
    "triplosensitivity_score__int": "Triplosensitivity Score",
    "triplosensitivity_evidence__string": "Triplosensitivity Description",
    "triplosensitivity_pubmed_id__mstring": "triplo_pmid",
    "triplosensitive_phenotype_ID__mstring": "triplo_omim",
}


def parse_haplo_pmid_fields(x):
    t = [
        v
        for k, v in x.items()
        if k.startswith("Haploinsufficiency PMID") and v
    ]
    return t


def parse_triplo_pmid_fields(x):
    return [
        v for k, v in x.items() if k.startswith("Triplosensitivity PMID") and v
    ]


def split_values(x, key):
    value = x.get(key, [])
    return split_value(value, split_chars=SPLIT_CHARS) if value else []


register(
    input_type=DocType.TSV,
    output_type=DocType.CLINGEN_DOSAGE,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.CLINGEN_DOSAGE.value),
        name_mapping(NAME_MAPPING, empty_values=(None, "", ".", [])),
        lambda x: assoc(x, "haplo_pmid", parse_haplo_pmid_fields(x)),
        lambda x: assoc(
            x, "haplo_omim", split_values(x, "Haploinsufficiency Disease ID")
        ),
        lambda x: assoc(x, "triplo_pmid", parse_triplo_pmid_fields(x)),
        lambda x: assoc(
            x,
            "triplo_omim",
            split_values(x, "Triplosensitivity Disease ID"),
        ),
    ),
)


register(
    input_type=DocType.TSV,
    output_type=DocType.CLINGEN_DOSAGE,
    transformer=compose(
        lambda x: assoc(x, __CHILD__, DocType.CLINGEN_DOSAGE.value)
    ),
    is_header=True,
)
