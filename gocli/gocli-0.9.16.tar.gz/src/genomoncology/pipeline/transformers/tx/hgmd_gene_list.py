from cytoolz.curried import assoc, compose

from genomoncology.parse.doctypes import DocType, __TYPE__, __CHILD__
from genomoncology.pipeline.transformers import name_mapping
from genomoncology.pipeline.transformers.registry import register

NAME_MAPPING = {"gene": "gene"}

register(
    input_type=DocType.TSV,
    output_type=DocType.HGMD_GENE_LIST,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.HGMD_GENE_LIST.value),
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, "is_hgmd_gene__boolean", True),
        name_mapping(NAME_MAPPING),
    ),
    is_header=False,
)

register(
    input_type=DocType.TSV,
    output_type=DocType.HGMD_GENE_LIST,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.HGMD_GENE_LIST.value),
    ),
    is_header=True,
)
