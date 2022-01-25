from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


def parse_float(f):
    try:
        return float(f)
    except ValueError:
        return None


def parse_int(i):
    try:
        return int(i)
    except ValueError:
        return None


def parse_values(x):
    # have to do these conversions due to scientific
    # notation and possible "NA" values
    for name, value in x.items():
        if name.endswith("__float"):
            x[name] = parse_float(value)
        elif name.endswith("__int"):
            x[name] = parse_int(value)
    return x


NAME_MAPPING = {
    "gene": "gene",
    "pLI_score__float": "pLI",
    "mis_z__float": "mis_z",
    "syn_z__float": "syn_z",
    "lof_z__float": "lof_z",
    "oe_lof_upper_rank__int": "oe_lof_upper_rank",
    "oe_lof_upper_bin__int": "oe_lof_upper_bin",
    "oe_lof_upper_bin_6__int": "oe_lof_upper_bin_6",
    "oe_mis__float": "oe_mis",
    "oe_lof__float": "oe_lof",
    "oe_mis_pphen__float": "oe_mis_pphen",
    "oe_syn__float": "oe_syn",
    "oe_syn_lower__float": "oe_syn_lower",
    "oe_syn_upper__float": "oe_syn_upper",
    "oe_mis_lower__float": "oe_mis_lower",
    "oe_mis_upper__float": "oe_mis_upper",
    "oe_lof_lower__float": "oe_lof_lower",
    "oe_lof_upper__float": "oe_lof_upper",
}

register(
    input_type=DocType.TSV,
    output_type=DocType.GNOMAD_GENE,
    transformer=compose(
        lambda x: parse_values(x),
        lambda x: assoc(x, __TYPE__, DocType.GNOMAD_GENE.value),
        lambda x: assoc(x, "is_gene_annotation", True),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.TSV,
    output_type=DocType.GNOMAD_GENE,
    transformer=compose(
        lambda x: assoc(x, __CHILD__, DocType.GNOMAD_GENE.value)
    ),
    is_header=True,
)
