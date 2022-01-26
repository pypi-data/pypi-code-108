"""Tag map for MIP-rna deliverables file"""

MIP_RNA_TAGS = {
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
    frozenset(["mip_analyse", "pedigree_fam"]): {
        "tags": ["pedigree"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["multiqc_ar", "html"]): {
        "tags": ["multiqc-html"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["multiqc_ar", "json"]): {
        "tags": ["multiqc-json"],
        "is_mandatory": True,
        "used_by": ["vogue"],
    },
    frozenset(["qccollect_ar"]): {
        "tags": ["qc-metrics"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["version_collect_ar"]): {
        "tags": ["exe-ver"],
        "is_mandatory": True,
        "used_by": ["audit"],
    },
    frozenset(["salmon_quant"]): {
        "tags": ["salmon-quant"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["blobfish"]): {
        "tags": ["deseq2"],
        "is_mandatory": False,
        "used_by": ["storage"],
    },
    frozenset(["star_fusion"]): {
        "tags": ["fusion", "star-fusion"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["arriba_ar"]): {
        "tags": ["fusion", "arriba"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["megafusion_ar"]): {
        "tags": ["fusion", "vcf"],
        "index_tags": ["fusion", "vcf-index"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["svdb_merge_fusion"]): {
        "tags": ["fusion", "vcf"],
        "index_tags": ["fusion", "vcf-index"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["merge_fusion_reports", "research"]): {
        "tags": ["fusion", "research", "pdf"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["merge_fusion_reports", "clinical"]): {
        "tags": ["fusion", "pdf", "clinical"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["build_sj_tracks", "coverage"]): {
        "tags": ["coverage", "bigwig"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["build_sj_tracks", "junction"]): {
        "tags": ["junction", "bed"],
        "index_tags": ["junction", "bed-index"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["markduplicates"]): {
        "tags": ["cram"],
        "index_tags": ["cram-index"],
        "is_mandatory": True,
        "used_by": ["scout"],
    },
    frozenset(["stringtie_ar"]): {
        "tags": ["stringtie", "assembly"],
        "is_mandatory": False,
        "used_by": ["storage"],
    },
    frozenset(["gffcompare_ar"]): {
        "tags": ["gffcompare"],
        "is_mandatory": False,
        "used_by": ["storage"],
    },
    frozenset(["gatk_asereadcounter"]): {
        "tags": ["asereadcounter"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["vcfparser_ar", "research"]): {
        "tags": ["vcf-snv-research"],
        "index_tags": ["vcf-snv-research-index"],
        "is_mandatory": True,
        "used_by": ["storage"],
    },
    frozenset(["vcfparser_ar", "clinical"]): {
        "tags": ["vcf-snv-clinical"],
        "index_tags": ["vcf-snv-clinical-index"],
        "is_mandatory": True,
        "bundle_id": True,
        "used_by": ["storage"],
    },
}
