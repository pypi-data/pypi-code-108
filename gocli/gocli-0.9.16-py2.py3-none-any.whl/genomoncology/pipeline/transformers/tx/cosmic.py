from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    # hgvs
    "hgvs_g": "hgvs_g",
    "csra": "csra",
    "chr": "#CHROM",
    "start": "POS",
    "position": "POS",
    "ref": "REF",
    "alt": "ALT",
    "gene": "Gene name",
    "CNT__int": "CNT",
    "tissues__mstring": "TISSUES",
    "tissue_frequency__mstring": "TISSUES_FREQ",
    "resistance_mutation__mstring": "RESISTANCE_MUTATION",
    "genomicID__string": "ID",
    "ID__mstring": "MUTATION_ID",
    "CDS__mstring": "CDS",
    "AA__mstring": "AA",
    "gene_name__mstring": "Gene name",
    "legacy_id__string": "LEGACY_ID",
}


def create_alterations_field(x):
    alterations = set()
    try:
        gene_names = x.get("gene_name__mstring", [])
        aa = x.get("AA__mstring", [])
        cds = x.get("CDS__mstring", [])
        if len(gene_names) != len(aa) != len(cds):
            return None
        # clean gene names
        gene_names = clean_gene(gene_names, make_set=False)
        for i in range(len(gene_names)):
            gene_val = gene_names[i]
            aa_val = aa[i]
            cds_val = cds[i]
            aa_val = aa_val.split("p.")[-1]
            if "=" in aa_val:
                continue
            if aa_val != "?":
                alterations.add(gene_val + " " + aa_val)
            else:
                alterations.add(gene_val + " " + cds_val)

    except IndexError:
        alterations = set()

    return list(alterations)


def get_keys(x, field):
    return list(x.get(field, {}).keys())


def process_tissue_frequency(x):
    freq_results = []
    freq_info = x.get("tissue_frequency__mstring")
    for tissue, freq in freq_info.items():
        freq_results.append(f"{tissue}={freq}")
    return freq_results


def clean_gene(gene_list, make_set=True):
    if not isinstance(gene_list, list):
        gene_list = [gene_list]
    # remove everything after "_ENST"
    gene_list = [
        gene.split("_ENST")[0] for gene in gene_list if gene is not None
    ]
    if make_set:
        return list(set(gene_list))
    return gene_list


def remove_start_field(x):
    x.pop("start", "")
    return x


def handle_hgvs_g(x):
    if (
        x.get("chr") is None
        and x.get("start") is None
        and x.get("ref") is None
        and x.get("alt") is None
    ):
        return None
    return kms.annotations.to_csra(x)


register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.COSMIC,
    transformer=compose(
        lambda x: assoc(x, "alterations", create_alterations_field(x)),
        lambda x: assoc(
            x,
            "resistance_mutation__mstring",
            get_keys(x, "resistance_mutation__mstring"),
        ),
        lambda x: assoc(
            x, "tissues__mstring", get_keys(x, "tissues__mstring")
        ),
        lambda x: assoc(
            x, "tissue_frequency__mstring", process_tissue_frequency(x)
        ),
        lambda x: remove_start_field(x),
        lambda x: assoc(x, "csra", handle_hgvs_g(x)),
        lambda x: assoc(x, "hgvs_g", handle_hgvs_g(x)),
        lambda x: assoc(x, "gene", clean_gene(x.get("gene", []))),
        lambda x: assoc(x, __TYPE__, DocType.COSMIC.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.COSMIC,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.COSMIC.value)),
    is_header=True,
)
