from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

# Note: uniprot is the only data_set that has the
# "is_codon_range_annotation" flag set to True.
# This makes it easy to section off the uniprot
# annotations during the annotations-match process.

NAME_MAPPING = {
    "gene": "gene",
    "protein_full_name__string": "protein_full_name",
    "uniprot_id__string": "uniprot_id",
    "protein_length__int": "protein_length",
    "protein_alternate_names__mstring": "protein_alternate_names",
    "uniprot_canonical_nm_id__mstring": "uniprot_canonical_nm_id",
    "uniprot_canonical_np_id__mstring": "uniprot_canonical_np_id",
    # this field is a list of json dictionaries
    "features__mstring": "features",
}


def convert_to_int(val):
    try:
        return int(val)
    except ValueError:
        return None


register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT,
    transformer=compose(
        lambda x: assoc(
            x,
            "protein_length__int",
            convert_to_int(x.get("protein_length__int")),
        ),
        lambda x: assoc(x, "is_codon_range_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.UNIPROT.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT,
    transformer=compose(
        lambda x: assoc(x, "is_codon_range_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.UNIPROT.value),
    ),
    is_header=True,
)
