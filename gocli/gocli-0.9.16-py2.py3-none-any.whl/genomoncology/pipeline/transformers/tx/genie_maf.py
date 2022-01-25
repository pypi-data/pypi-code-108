from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    # hgvs
    "chr": "Chromosome",
    "start": "Start_Position",
    "ref": "Reference_Allele",
    "alt": "alt",
    # other data
    "sample_name": "Tumor_Sample_Barcode",
    "ref_depth": "t_ref_count",
    "alt_depth": "t_alt_count",
    "build": "build",
}

register(
    input_type=DocType.MAF,
    output_type=DocType.VARIANT,
    transformer=compose(
        lambda x: assoc(x, "file_path", "GENIE"),
        lambda x: assoc(x, "run_id", "GENIE"),
        lambda x: assoc(x, "start", int(x["start"])),
        lambda x: assoc(x, __TYPE__, DocType.VARIANT.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.MAF,
    output_type=DocType.VARIANT,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.VARIANT.value)),
    is_header=True,
)
