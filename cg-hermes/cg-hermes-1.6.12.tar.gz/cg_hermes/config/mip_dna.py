"""Tag map for MIP-dna deliverables file"""

MIP_DNA_TAGS = {
    frozenset(["chanjo_sexcheck"]): {
        "tags": ["chanjo", "sex-check"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["chromograph_upd", "sites"]): {
        "tags": ["chromograph", "upd", "sites"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["chromograph_upd", "regions"]): {
        "tags": ["chromograph", "upd", "regions"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["chromograph_cov", "tcov"]): {
        "tags": ["chromograph", "tcov"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["chromograph_cov", "tcov"]): {
        "tags": ["chromograph", "tcov"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["chromograph_rhoviz", "autozyg"]): {
        "tags": ["chromograph", "autozyg"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["chromograph_rhoviz", "fracsnp"]): {
        "tags": ["chromograph", "fracsnp"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["endvariantannotationblock", "clinical"]): {
        "tags": ["vcf-snv-clinical"],
        "index_tags": ["vcf-snv-clinical-index"],
        "is_mandatory": True,
        "bundle_id": True,
        "used_by": ["scout"],
    },
    frozenset(["endvariantannotationblock", "research"]): {
        "tags": ["vcf-snv-research"],
        "index_tags": ["vcf-snv-research-index"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["expansionhunter", "sv_str"]): {
        "tags": ["vcf-str"],
        "index_tags": ["vcf-str-index"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["glnexus_merge"]): {
        "tags": ["deepvariant","snv", "vcf"],
        "index_tags": ["deepvariant", "snv", "vcf-index"],
        "is_mandatory": False,
        "used_by": ["storage"],
    },
    frozenset(["markduplicates"]): {
        "tags": ["cram"],
        "index_tags": ["cram-index"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["gatk_combinevariantcallsets"]): {
        "tags": ["snv-gbcf", "snv-bcf"],
        "index_tags": ["gbcf-index"],
        "is_mandatory": True,
        "used_by": ["genotype"],
    },
    frozenset(["mip_analyse", "config"]): {
        "tags": ["mip-analyse", "config"],
        "is_mandatory": True,
        "used_by": ["cg", "audit"],
    },
    frozenset(["mip_analyse", "config_analysis"]): {
        "tags": ["mip-config"],
        "is_mandatory": True,
        "used_by": ["cg", "audit"],
    },
    frozenset(["mip_analyse", "log"]): {
        "tags": ["mip-log"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["mip_analyse", "pedigree"]): {
        "tags": ["pedigree-yaml"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["mip_analyse", "pedigree_fam"]): {
        "tags": ["pedigree"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["mip_analyse", "references_info"]): {
        "tags": ["mip-analyse", "reference-info"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["mip_analyse", "sample_info"]): {
        "tags": ["sample-info"],
        "is_mandatory": True,
        "used_by": ["cg", "audit"],
    },
    frozenset(["multiqc_ar", "html"]): {
        "tags": ["multiqc-html"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["multiqc_ar", "json"]): {
        "tags": ["multiqc-json"],
        "is_mandatory": True,
        "used_by": ["vogue"],
    },
    frozenset(["mitodel"]): {
        "tags": ["mitodel"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["peddy_ar", "ped_check"]): {
        "tags": ["peddy", "ped-check"],
        "is_mandatory": True,
        "used_by": ["audit", "scout"],
    },
    frozenset(["peddy_ar", "peddy"]): {
        "tags": ["peddy", "ped"],
        "is_mandatory": True,
        "used_by": ["audit", "scout"],
    },
    frozenset(["peddy_ar", "sex_check"]): {
        "tags": ["peddy", "sex-check"],
        "is_mandatory": True,
        "used_by": ["audit", "scout"],
    },
    frozenset(["qccollect_ar"]): {
        "tags": ["qc-metrics"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["rhocall_viz"]): {
        "tags": ["rhocall-viz"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["sambamba_depth", "coverage"]): {
        "tags": ["coverage", "sambamba-depth"],
        "is_mandatory": True,
        "used_by": ["chanjo"],
    },
    frozenset(["samtools_subsample_mt"]): {
        "tags": ["bam-mt"],
        "index_tags": ["bam-mt-index"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["smncopynumbercaller"]): {
        "tags": ["smn-calling"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["star_caller"]): {
        "tags": ["cyrius"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["sv_combinevariantcallsets"]): {
        "tags": ["sv-bcf"],
        "index_tags": ["sv-bcf-index"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["sv_reformat", "clinical"]): {
        "tags": ["vcf-sv-clinical"],
        "index_tags": ["vcf-sv-clinical-index"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["sv_reformat", "research"]): {
        "tags": ["vcf-sv-research"],
        "index_tags": ["vcf-sv-research-index"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["telomerecat_ar"]): {
        "tags": ["telomere-calling"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["tiddit_coverage"]): {
        "tags": ["tiddit-coverage", "bigwig"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["upd_ar", "regions"]): {
        "tags": ["upd", "regions"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["upd_ar", "sites"]): {
        "tags": ["upd", "sites"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
    frozenset(["version_collect_ar"]): {
        "tags": ["exe-ver"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["vcf2cytosure_ar"]): {
        "tags": ["vcf2cytosure"],
        "is_mandatory": False,
        "used_by": ["scout"],
    },
}
