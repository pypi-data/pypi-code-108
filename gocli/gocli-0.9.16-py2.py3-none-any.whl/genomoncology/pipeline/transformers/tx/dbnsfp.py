from cytoolz.curried import assoc, compose, merge

from genomoncology import kms
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import (
    register,
    name_mapping,
    rename,
    split_value,
)
from gosdk import logger


SPLIT_CHARS = ":;"


def set_chr_start(value):
    if value.get("build", "").endswith("38"):
        value = rename("#chr", "chr", value)
        value = rename("pos(1-based)", "start", value)
    else:
        value = rename("hg19_chr", "chr", value)
        value = rename("hg19_pos(1-based)", "start", value)

    return value


def get_largest_value(value):
    return max(value) if value else None


def additional_clean_up(value):
    genes = split_value(value.get("gene", []), split_chars=SPLIT_CHARS)

    updates = dict(gene=genes)

    return merge(value, updates)


def filter_out_empty_chr_start(value):
    if value.get("chr") is None and value.get("start") is None:
        return None
    return value


NAME_MAPPING = {
    # critical
    "chr": "chr",
    "start": "start",
    "ref": "ref",
    "alt": "alt",
    "build": "build",
    "gene": "genename",
    # baylor
    "1000Gp3_AC__int": "1000Gp3_AC",
    "1000Gp3_AF__float": "1000Gp3_AF",
    "1000Gp3_AFR_AC__int": "1000Gp3_AFR_AC",
    "1000Gp3_AFR_AF__float": "1000Gp3_AFR_AF",
    "1000Gp3_AMR_AC__int": "1000Gp3_AMR_AC",
    "1000Gp3_AMR_AF__float": "1000Gp3_AMR_AF",
    "1000Gp3_EAS_AC__int": "1000Gp3_EAS_AC",
    "1000Gp3_EAS_AF__float": "1000Gp3_EAS_AF",
    "1000Gp3_EUR_AC__int": "1000Gp3_EUR_AC",
    "1000Gp3_EUR_AF__float": "1000Gp3_EUR_AF",
    "1000Gp3_SAS_AC__int": "1000Gp3_SAS_AC",
    "1000Gp3_SAS_AF__float": "1000Gp3_SAS_AF",
    "cds_strand__mstring": "cds_strand",
    "MutationTaster_AAE__mstring": "MutationTaster_AAE",
    "MutationTaster_converted_rankscore__float": "MutationTaster_converted_rankscore",  # noqa E501
    "MutationTaster_model__mstring": "MutationTaster_model",
    "MutationTaster_pred__mstring": "MutationTaster_pred",
    "MutationTaster_score__mfloat": "MutationTaster_score",
    "SIFT_converted_rankscore__mfloat": "SIFT_converted_rankscore",
    "SIFT_pred__mstring": "SIFT_pred",
    "SIFT_score__mfloat": "SIFT_score",
    # not used (yet)
    "PROVEAN_converted_rankscore__float": "PROVEAN_converted_rankscore",
    "PROVEAN_pred__mstring": "PROVEAN_pred",
    "PROVEAN_score__mfloat": "PROVEAN_score",
    "codonpos__mint": "codonpos",
    "codon_degeneracy__mstring": "codon_degeneracy",
    "Ancestral_allele__string": "Ancestral_allele",
    "AltaiNeandertal__string": "AltaiNeandertal",
    "Denisova__string": "Denisova",
    "Ensembl_geneid__mstring": "Ensembl_geneid",
    "Ensembl_transcriptid__mstring": "Ensembl_transcriptid",
    "Ensembl_proteinid__mstring": "Ensembl_proteinid",
    "LRT_score__float": "LRT_score",
    "LRT_converted_rankscore__float": "LRT_converted_rankscore",
    "LRT_pred__string": "LRT_pred",
    "LRT_Omega__float": "LRT_Omega",
    "MutationAssessor_score__mstring": "MutationAssessor_score",
    "MutationAssessor_pred__mstring": "MutationAssessor_pred",
    "FATHMM_score__mfloat": "FATHMM_score",
    "FATHMM_converted_rankscore__float": "FATHMM_converted_rankscore",
    "FATHMM_pred__mstring": "FATHMM_pred",
    "MetaSVM_score__float": "MetaSVM_score",
    "MetaSVM_rankscore__float": "MetaSVM_rankscore",
    "MetaSVM_pred__string": "MetaSVM_pred",
    "MetaLR_score__float": "MetaLR_score",
    "MetaLR_rankscore__float": "MetaLR_rankscore",
    "MetaLR_pred__string": "MetaLR_pred",
    "Reliability_index__float": "Reliability_index",
    "M-CAP_score__float": "M-CAP_score",
    "M-CAP_rankscore__float": "M-CAP_rankscore",
    "M-CAP_pred__string": "M-CAP_pred",
    "MutPred_score__string": "MutPred_score",
    "MutPred_rankscore__string": "MutPred_rankscore",
    "MutPred_protID__string": "MutPred_protID",
    "MutPred_AAchange__string": "MutPred_AAchange",
    "MutPred_Top5features__mstring": "MutPred_Top5features",
    "fathmm-MKL_coding_score__float": "fathmm-MKL_coding_score",
    "fathmm-MKL_coding_rankscore__float": "fathmm-MKL_coding_rankscore",
    "fathmm-MKL_coding_pred__string": "fathmm-MKL_coding_pred",
    "fathmm-MKL_coding_group__string": "fathmm-MKL_coding_group",
    "Eigen-raw__float": "Eigen-raw_coding",
    "Eigen-phred__float": "Eigen-pred_coding",
    "Eigen-raw_rankscore__float": "Eigen-raw_coding_rankscore",
    "Eigen-PC-raw__float": "Eigen-PC-raw_coding",
    "Eigen-PC-phred__float": "Eigen-PC-phred_coding",
    "Eigen-PC-raw_rankscore__float": "Eigen-PC-raw_coding_rankscore",
    "integrated_fitCons_score__float": "integrated_fitCons_score",
    "integrated_confidence_value__float": "integrated_confidence_value",
    "GM12878_fitCons_score__float": "GM12878_fitCons_score",
    "GM12878_fitCons_rankscore__float": "GM12878_fitCons_rankscore",
    "GM12878_confidence_value__float": "GM12878_confidence_value",
    "H1-hESC_fitCons_score__float": "H1-hESC_fitCons_score",
    "H1-hESC_fitCons_rankscore__float": "H1-hESC_fitCons_rankscore",
    "H1-hESC_confidence_value__float": "H1-hESC_confidence_value",
    "HUVEC_fitCons_score__float": "HUVEC_fitCons_score",
    "HUVEC_fitCons_rankscore__float": "HUVEC_fitCons_rankscore",
    "HUVEC_confidence_value__float": "HUVEC_confidence_value",
    "GERP++_NR__float": "GERP++_NR",
    "GERP++_RS__float": "GERP++_RS",
    "GERP++_RS_rankscore__float": "GERP++_RS_rankscore",
    "phyloP100way_vertebrate__float": "phyloP100way_vertebrate",
    "phyloP100way_vertebrate_rankscore__float": "phyloP100way_vertebrate_rankscore",  # noqa E501
    "phyloP30way_mammalian__float": "phyloP30way_mammalian",
    "phyloP30way_mammalian_rankscore__float": "phyloP30way_mammalian_rankscore",  # noqa E501
    "phastCons100way_vertebrate__float": "phastCons100way_vertebrate",
    "phastCons100way_vertebrate_rankscore__float": "phastCons100way_vertebrate_rankscore",  # noqa E501
    "phastCons30way_mammalian__float": "phastCons30way_mammalian",
    "phastCons30way_mammalian_rankscore__float": "phastCons30way_mammalian_rankscore",  # noqa E501
    "SiPhy_29way_pi__mfloat": "SiPhy_29way_pi",
    "SiPhy_29way_logOdds__float": "SiPhy_29way_logOdds",
    "SiPhy_29way_logOdds_rankscore__float": "SiPhy_29way_logOdds_rankscore",
    "TWINSUK_AC__int": "TWINSUK_AC",
    "TWINSUK_AF__float": "TWINSUK_AF",
    "ALSPAC_AC__int": "ALSPAC_AC",
    "ALSPAC_AF__float": "ALSPAC_AF",
    "Interpro_domain__mstring": "Interpro_domain",
    "GTEx_V7p_gene__string": "GTEx_V7_gene",
    "GTEx_V7p_tissue__string": "GTEx_V7_tissue",
    "MutationAssessor_score_rankscore__string": "MutationAssessor_rankscore",  # noqa E501
    "HGVSc_ANNOVAR__mstring": "HGVSc_ANNOVAR",
    "HGVSp_ANNOVAR__mstring": "HGVSp_ANNOVAR",
    "HGVSc_snpEff__mstring": "HGVSc_snpEff",
    "HGVSp_snpEff__mstring": "HGVSp_snpEff",
    "HGVSc_VEP__mstring": "HGVSc_VEP",
    "HGVSp_VEP__mstring": "HGVSp_VEP",
    "Polyphen2_HDIV_pred__mstring": "Polyphen2_HDIV_pred",
    "Polyphen2_HDIV_rankscore__float": "Polyphen2_HDIV_rankscore",
    "Polyphen2_HDIV_score__mfloat": "Polyphen2_HDIV_score",
    "Polyphen2_HVAR_pred__mstring": "Polyphen2_HVAR_pred",
    "Polyphen2_HVAR_rankscore__float": "Polyphen2_HVAR_rankscore",
    "Polyphen2_HVAR_score__mfloat": "Polyphen2_HVAR_score",
    "SIFT4G_converted_rankscore__float": "SIFT4G_converted_rankscore",
    "SIFT4G_pred__mstring": "SIFT4G_pred",
    "SIFT4G_score__mfloat": "SIFT4G_score",
    # CADD
    "CADD_raw__float": "CADD_raw",
    "CADD_raw_rankscore__float": "CADD_raw_rankscore",
    "CADD_phred__float": "CADD_phred",
    "CADD_raw_hg19__float": "CADD_raw_hg19",
    "CADD_raw_rankscore_hg19__float": "CADD_raw_rankscore_hg19",
    "CADD_phred_hg19__float": "CADD_phred_hg19",
}


def add_alteration(ann):
    alterations = set()
    genes = ann.get("gene", [])
    p_dots = ann.get("HGVSp_ANNOVAR__mstring", [])
    if len(genes) != len(p_dots):
        error_message = (
            f"{ann.get('hgvs_g', '')} has {len(genes)} "
            f"genes and {len(p_dots)} p_dots. These must match."
        )
        logger.get_logger().warning(error_message)
        return []
    # clean p_dots --> replace X with * and strip out "p."
    cleaned_p_dots = []
    for p_dot in p_dots:
        if p_dot is not None:
            p_dot = p_dot.split("p.")[-1].replace("X", "*")
        cleaned_p_dots.append(p_dot)
    for i in range(0, len(genes)):
        if genes[i] is not None and cleaned_p_dots[i] is not None:
            alterations.add(f"{genes[i]} {cleaned_p_dots[i]}")
    return list(alterations)


def clean_genes(ann):
    return ann.get("gene", "").split(";")


register(
    input_type=DocType.TSV,
    output_type=DocType.DBNSFP,
    transformer=compose(
        filter_out_empty_chr_start,
        additional_clean_up,
        lambda x: assoc(x, "alterations", add_alteration(x)),
        lambda x: assoc(x, "csra", kms.annotations.to_csra(x)),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, "gene", clean_genes(x)),
        lambda x: assoc(x, __TYPE__, DocType.DBNSFP.value),
        name_mapping(
            NAME_MAPPING, empty_values=(None, "."), split_chars=SPLIT_CHARS
        ),
        set_chr_start,
    ),
)

register(
    input_type=DocType.TSV,
    output_type=DocType.DBNSFP,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.GNOMAD.value)),
    is_header=True,
)
