MICROSALT_COMMON_TAGS = {
    frozenset({"sampleinfo", "analysis"}): {
        "is_mandatory": True,
        "bundle_id": True,
        "tags": ["config"],
        "used_by": ["storage", "audit"],
    },
    frozenset({"microsalt-qc", "result_aggregation"}): {
        "is_mandatory": True,
        "tags": ["qc-report", "visualization"],
        "used_by": ["deliver"],
    },
    frozenset({"microsalt-type", "result_aggregation"}): {
        "is_mandatory": False,
        "tags": ["typing-report", "visualization"],
        "used_by": ["deliver"],
    },
    frozenset({"microsalt-json", "result_aggregation"}): {
        "is_mandatory": False,
        "tags": ["typing-report", "qc-metrics"],
        "used_by": ["vogue"],
    },
    frozenset({"runtime-settings", "analysis"}): {
        "is_mandatory": True,
        "tags": ["microsalt-config"],
        "used_by": ["storage", "audit"],
    },
    frozenset({"assembly"}): {"is_mandatory": False, "tags": ["assembly"], "used_by": ["storage"]},
    frozenset({"concatination", "trimmed-forward-reads"}): {
        "is_mandatory": False,
        "tags": ["fastq", "forward-strand"],
        "used_by": ["storage"],
    },
    frozenset({"trimmed-reverse-reads", "concatination"}): {
        "is_mandatory": False,
        "tags": ["fastq", "reverse-strand"],
        "used_by": ["storage"],
    },
    frozenset({"trimmed-unpaired-reads", "concatination"}): {
        "is_mandatory": False,
        "tags": ["fastq", "unpaired-reads"],
        "used_by": ["storage"],
    },
    frozenset({"analysis", "logfile"}): {
        "is_mandatory": False,
        "tags": ["microsalt-log"],
        "used_by": ["audit"],
    },
    frozenset({"quast-results", "assembly"}): {
        "is_mandatory": False,
        "tags": ["qc-metrics", "assembly"],
        "used_by": ["audit"],
    },
    frozenset({"alignment", "reference-alignment-sorted"}): {
        "is_mandatory": False,
        "tags": ["bam"],
        "used_by": ["storage"],
    },
    frozenset({"picard-insertsize", "insertsize_calc"}): {
        "is_mandatory": False,
        "tags": ["qc-metrics", "picard"],
        "used_by": ["audit"],
    },
}
