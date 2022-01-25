from cytoolz.curried import assoc, compose

from genomoncology import kms
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


SPLIT_CHARS = ";"


NAME_MAPPING = {
    "chr": "chromosome",
    "start": "position",
    "ref": "ref",
    "alt": "alt",
    "pathology__mstring": "pathology",
    "tRNA__string": "tRNA",
    "tRNA_structural_domain__string": "tRNA_structural_domain",
}


def clean_pathology(value):
    return [path.strip() for path in value]


register(
    input_type=DocType.TSV,
    output_type=DocType.MITO_TRNA,
    transformer=compose(
        lambda x: assoc(
            x,
            "pathology__mstring",
            clean_pathology(x.get("pathology__mstring", "")),
        ),
        lambda x: assoc(x, "csra", kms.annotations.to_csra(x, add_chr=False)),
        lambda x: assoc(
            x, "hgvs_g", kms.annotations.to_csra(x, add_chr=False)
        ),
        lambda x: assoc(x, __TYPE__, DocType.MITO_TRNA.value),
        name_mapping(
            NAME_MAPPING, empty_values=(None, "."), split_chars=SPLIT_CHARS
        ),
    ),
)

register(
    input_type=DocType.TSV,
    output_type=DocType.MITO_TRNA,
    transformer=compose(
        lambda x: assoc(x, __CHILD__, DocType.MITO_TRNA.value)
    ),
    is_header=True,
)
