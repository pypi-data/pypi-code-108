MUTANT_COMMON_TAGS = {
    frozenset({"sampleinfo", "runinfo"}): {
        "is_mandatory": True,
        "bundle_id": True,
        "tags": ["config"],
        "used_by": ["storage", "audit"],
    },
    frozenset({"instrument-properties", "report"}): {
        "is_mandatory":False,
        "tags": ["fohm-delivery","instrument-properties"],
        "used_by": ["storage", "audit"],
    },
    frozenset({"runtime-settings", "runinfo"}): {
        "is_mandatory": True,
        "tags": ["mutant-config"],
        "used_by": ["storage", "audit"],
    },
    frozenset({"software-versions", "runinfo"}): {
        "is_mandatory": True,
        "tags": ["software-versions"],
        "used_by": ["storage", "audit"],
    },
    frozenset({"runinfo", "logfile"}): {
        "is_mandatory": True,
        "tags": ["mutant-log"],
        "used_by": ["audit"],
    },
    frozenset({"concatination", "forward-reads"}): {
        "is_mandatory": True,
        "tags": ["fastq", "forward-strand"],
        "used_by": ["storage"],
    },
    frozenset({"reverse-reads", "concatination"}): {
        "is_mandatory": True,
        "tags": ["fastq", "reverse-strand"],
        "used_by": ["storage"],
    },
    frozenset({"SARS-CoV-2-info", "report"}): {
        "is_mandatory": False,
        "tags": ["fohm-delivery", "komplettering", "visualization"],
        "used_by": ["deliver"],
    },
    frozenset({"SARS-CoV-2-qc", "result_aggregation"}): {
        "is_mandatory": False,
        "tags": ["fohm-delivery", "pangolin-typing", "csv", "visualization"],
        "used_by": ["audit"],
    },
    frozenset({"pangolin-typing", "report"}): {
        "is_mandatory": False,
        "tags": ["fohm-delivery", "pangolin-typing", "visualization", "csv"],
        "used_by": ["audit"],
    },
    frozenset({"pangolin-typing-fohm", "report"}): {
        "is_mandatory": False,
        "tags": ["fohm-delivery", "pangolin-typing-fohm", "csv"],
        "used_by": ["deliver"],
    },
    frozenset({"alignment", "reference-alignment-sorted"}): {
        "is_mandatory": False,
        "tags": ["bam"],
        "used_by": ["storage"],
    },
    frozenset({"vcf-covid", "genotyping"}): {
        "is_mandatory": False,
        "tags": ["vcf", "vcf-report", "fohm-delivery"],
        "used_by": ["deliver"],
    },
    frozenset({"vcf-covid", "variant-calling"}): {
        "is_mandatory": False,
        "tags": ["tsv", "vcf-report"],
        "used_by": ["deliver"],
    },
    frozenset({"metrics", "result_aggregation"}): {
        "is_mandatory": False,
        "tags": ["metrics"],
        "used_by": ["vogue"],
    },
    frozenset({"multiqc-json", "report"}): {
        "is_mandatory": True,
        "tags": ["multiqc-json"],
        "used_by": ["vogue"],
    },
    frozenset({"ks-results", "report"}): {
        "is_mandatory": True,
        "tags": ["ks-delivery", "ks-results", "typing-report", "visualization", "csv"],
        "used_by": ["deliver"],
    },
    frozenset({"ks-aux-results", "report"}): {
        "is_mandatory": True,
        "tags": ["ks-delivery", "ks-aux-results", "typing-report", "visualization", "csv"],
        "used_by": ["deliver"],
    },
    frozenset({"consensus", "analysis"}): {
        "is_mandatory": True,
        "tags": ["ks-delivery", "fastq", "consensus"],
        "used_by": ["deliver", "storage"],
    },
    frozenset({"consensus-sample", "consensus"}): {
        "is_mandatory": False,
        "tags": ["fohm-delivery", "fasta", "consensus-sample"],
        "used_by": ["deliver", "storage"],
    },
    frozenset({"multiqc-html", "report"}): {
        "is_mandatory": True,
        "tags": ["ks-delivery", "multiqc-html"],
        "used_by": ["deliver"],
    },
    frozenset({"SARS-CoV-2-sum", "report"}): {
        "is_mandatory": False,
        "tags": ["artic-sum", "csv"],
        "used_by": ["audit"],
    },
    frozenset({"SARS-CoV-2-var", "report"}): {
        "is_mandatory": False,
        "tags": ["artic-var", "csv"],
        "used_by": ["audit"],
    },
    frozenset({"SARS-CoV-2-type", "typing"}): {
        "is_mandatory": False,
        "tags": ["artic-type", "csv"],
        "used_by": ["audit"],
    },
}
