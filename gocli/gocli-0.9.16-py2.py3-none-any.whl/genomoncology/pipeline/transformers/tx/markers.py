from cytoolz.curried import assoc, compose

from genomoncology.parse.doctypes import DocType, __TYPE__, __CHILD__
from genomoncology.pipeline.transformers.functions import filter_keys, rename
from genomoncology.pipeline.transformers.registry import register


register(
    input_type=DocType.ANNOTATED_CALL,
    output_type=DocType.MARKER,
    transformer=compose(
        assoc(key=__TYPE__, value=DocType.MARKER.value),
        filter_keys(
            {
                "alt_depth",
                "is_het",
                "is_phased",
                "is_somatic",
                "mutation_hash",
                "quality",
                "ref_depth",
                "total_depth",
                "vaf",
                "vaf_alt",
            }
        ),
        rename("annotations.hgvs_g", "mutation_hash"),
    ),
)

register(
    input_type=DocType.ANNOTATED_CALL,
    output_type=DocType.MARKER,
    transformer=assoc(key=__CHILD__, value=DocType.MARKER.value),
    is_header=True,
)
