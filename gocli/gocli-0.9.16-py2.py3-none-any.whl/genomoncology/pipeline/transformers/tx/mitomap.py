from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    "hgvs_g": "hgvs_g",
    "disease__string": "disease",
    "aa_change__string": "aa_change",
    "conservation__string": "conservation",
    "haplogroups__mstring": "haplogroups",
    "loci__string": "loci",
    "fl_count__int": "fl_count",
    "cr_count__int": "cr_count",
    "fl_frequency__float": "fl_frequency",
    "cr_frequency__float": "cr_frequency",
    "variant_haplogroup_counts__mint": "variant_haplogroup_counts",
    "haplogroup_counts__mint": "haplogroup_counts",
    "mitoTIP__float": "mitoTIP",
    "helix_count__int": "helix_count",
    "helix_total_count__int": "helix_total_count",
    "helix_frequency__float": "helix_frequency",
    "gene__string": "gene",
    "apogee__mstring": "apogee",
    "csra": "csra",
}

register(
    input_type=DocType.MITOMAP_RECORD,
    output_type=DocType.MITOMAP,
    transformer=compose(
        lambda x: assoc(x, __TYPE__, DocType.MITOMAP.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.MITOMAP_RECORD,
    output_type=DocType.MITOMAP,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.MITOMAP.value)),
    is_header=True,
)
