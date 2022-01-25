from cytoolz.curried import assoc, compose

from genomoncology import kms
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    "hgvs_g": "hgvs_g",
    "functional_region__string": "functional_region",
    "aa_change__string": "aa_change",
    "count__int": "count",
    "total__int": "total",
    "frequency__float": "frequency",
    "csra": "csra",
}

register(
    input_type=DocType.MTDB_RECORD,
    output_type=DocType.MTDB,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.MTDB.value),
        name_mapping(NAME_MAPPING),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
    ),
)

register(
    input_type=DocType.MTDB_RECORD,
    output_type=DocType.MTDB,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.MTDB.value)),
    is_header=True,
)
