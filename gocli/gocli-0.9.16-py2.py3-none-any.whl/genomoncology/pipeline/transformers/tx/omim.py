from cytoolz.curried import assoc, compose, remove, pipe, merge_with, merge
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping
import re


NAME_MAPPING = {
    "gene": "gene",
    "gene_mim__mstring": "MIM Number",
    "phenotype__mstring": "phenotype",
    "phenotype_mim__mstring": "phenotype_mim",
    "inheritance__mstring": "inheritance",
}


def split_filter(value, delimiter, pred_func):
    return filter(pred_func, value.split(delimiter))


def split_remove(value, delimiter, pred_func):
    return remove(pred_func, value.split(delimiter))


def parse_omim_inheritance(omim_pheno_d):
    omim_inheritance_l = [
        "Multifactorial",
        "autosomal dominant",
        "X-linked dominant",
        "X-linked",
        "X-linked recessive",
        "Y-linked",
        "autosomal recessive",
        "Autosomal dominant",
        "Autosomal recessive",
        "Mitochondrial",
        "?Autosomal dominant",
        "Isolated cases",
        "Somatic mutation",
        "Digenic recessive",
        "Somatic mosaicism",
        "?X - linked recessive",
        "Inherited chromosomal imbalance",
        "Pseudoautosomal dominant",
        "Pseudoautosomal recessive",
        "Digenic dominant",
    ]

    # structure of the phenotype field is:
    # {phenotype strings and mim string} {(digit)} {inheritances}
    # so split on (digit) and take the stuff that comes after
    phen = omim_pheno_d["phenotype"]
    omim_inheritance_strings = re.compile(r"\(\d\)").split(phen)[-1]
    phen_before_inheritance = phen[
        0 : len(phen) - len(omim_inheritance_strings)
    ]
    omim_inheritance_strings = omim_inheritance_strings.strip()
    omim_inheritance_values = split_filter(
        omim_inheritance_strings, ", ", lambda x: x in omim_inheritance_l
    )
    omim_pheno_d = assoc(
        omim_pheno_d, "inheritance", ";".join(omim_inheritance_values)
    )

    omim_leftovers = split_remove(
        omim_inheritance_strings, ", ", lambda x: x in omim_inheritance_l
    )

    phen = phen_before_inheritance + ", ".join(omim_leftovers)
    omim_pheno_d["phenotype"] = phen

    return omim_pheno_d


def parse_omim_position(omim_pheno_d):
    omim_position_l = ["(1)", "(2)", "(3)", "(4)"]
    omim_pheno_d = assoc(
        omim_pheno_d,
        "phenotype",
        " ".join(
            split_remove(
                omim_pheno_d["phenotype"], " ", lambda x: x in omim_position_l
            )
        ),
    )
    return omim_pheno_d


def parse_omim_pheno_id(omim_pheno_d):
    if omim_pheno_d["phenotype"][-6:].isdigit():
        omim_pheno_d = assoc(
            omim_pheno_d, "phenotype_mim", omim_pheno_d["phenotype"][-6:]
        )
        omim_pheno_d = assoc(
            omim_pheno_d, "phenotype", omim_pheno_d["phenotype"][:-8]
        )
    else:
        omim_pheno_d = assoc(omim_pheno_d, "phenotype_mim", "")
    return omim_pheno_d


def phenotype_pipeline(x):
    return pipe(
        {"phenotype": x},
        parse_omim_inheritance,
        parse_omim_position,
        parse_omim_pheno_id,
    )


def parse_omim_phenotypes(x):
    if "Phenotypes" in x:

        if all([phen == "None" for phen in x["Phenotypes"]]):
            # do not add any of the phenotypes fields if they are all None
            return x

        # filter out Nones
        x["Phenotypes"] = [phen for phen in x["Phenotypes"] if phen != "None"]

        x["Phenotypes"] = "; ".join(x["Phenotypes"])
        return merge_with(
            list, map(phenotype_pipeline, x["Phenotypes"].split("; "))
        )
    else:
        return x


def parse_omim_gene(x):
    return x["key"]


def replace_empty_or_null_strings_with_none(omim_ann):
    for key in filter(lambda x: x.endswith("mstring"), omim_ann.keys()):
        omim_ann[key] = ["None" if not v else v for v in omim_ann[key]]
    return omim_ann


register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.OMIM,
    transformer=compose(
        lambda x: replace_empty_or_null_strings_with_none(x),
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.OMIM.value),
        name_mapping(NAME_MAPPING),
        lambda x: merge(x, parse_omim_phenotypes(x)),
        lambda x: assoc(x, "gene", parse_omim_gene(x)),
        # name_mapping(NAME_MAPPING_PRE),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.OMIM,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.OMIM.value),
        # lambda x: merge(x, parse_omim_phenotypes(x)),
    ),
    is_header=True,
)
