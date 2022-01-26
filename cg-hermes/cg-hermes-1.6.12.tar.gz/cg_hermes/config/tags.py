ALIGNMENT_COMMON = {
    "bam": {
        "description": "Alignment file in BAM format",
    },
    "bam-index": {
        "description": "Index file for alignment file in BAM format",
    },
    "bam-mt": {
        "description": "Alignment file in BAM format holding the reaads from chrMT",
    },
    "cram": {
        "description": "Alignment file in CRAM format",
    },
    "cram-index": {
        "description": "Index file for alignment file in CRAM format",
    },
}

RAW_DATA = {
    "fastq": {"description": "Files with raw data in fastq format"},
    "fasta": {"description": "Files with raw data in fasta format"},
    "forward-strand": {"description": "Reads from forward strand"},
    "reverse-strand": {"description": "Reads from reverse strand"},
    "unpaired-reads": {"description": "Reads that could not be paired"},
}


VARIANT_COMMON = {
    "cnv": {"description": "Copy number variants"},
    "normal": {"description": "Associated with normal sample"},
    "germline": {"description": "Associated with germline variants"},
    "somatic": {"description": "Associated with somatic variants"},
    "rhocall-viz": {"description": "Runs of homozygosity index"},
    "smn-calling": {"description": "Copy number calls for the SMN gene"},
    "snv": {"description": "Single nucleotide variants and short indels"},
    "snv-bcf": {"description": "Gvcf including all SNV variants"},
    "snv-gbcf": {"description": "Gvcf including all SNV variants"},
    "sv-bcf": {"description": "Gvcf including all SV variants"},
    "sv-vcf": {"description": "Variant call formated file with structural variants"},
    "sv-vcf-index": {"description": "Following index"},
    "telomere-calling": {"description": "Variants from telomere calling"},
    "tmb": {"description": "Tumor mutational burden information"},
    "tumor": {"description": "Associated with tumor sample"},
    "upd": {"description": "Uniparental disomy variants"},
    "vcf": {"description": "Variant call formated file"},
    "vcf-index": {"description": "Following index"},
    "vcf-snv-filtered": {"description": "SNV variants filtered by BALSAMIC"},
    "vcf-snv-filtered-index": {"description": "Following index"},
    "vcf-snv-clinical": {"description": "SNV variants from clinical panels"},
    "vcf-snv-clinical-index": {"description": "Following index"},
    "vcf-snv-research": {"description": "SNV variants from whole genome"},
    "vcf-snv-research-index": {"description": "Following index"},
    "vcf-str": {"description": "Short tandem repeat variants"},
    "vcf-str-index": {"description": "Following index"},
    "vcf-sv-clinical": {"description": "SV variants from clinical panels"},
    "vcf-sv-clinical-index": {"description": "Following index"},
    "vcf-sv-research": {"description": "SV variants from whole genome"},
    "vcf-sv-research-index": {"description": "Following index"},
    "vcf2cytosure": {"description": "Conversion from vcf format to cytosure format"},
    "variants": {"description": "File pertaining variant information in some way"},
}

FAMILY_COMMON = {
    "pedigree": {"description": "Pedigree information"},
    "ped": {"description": "Pedigree information"},
}

REPORTING_COMMON = {
    "csv": {"description": "Comma separated values"},
    "deliverable": {"description": "Deliverables file"},
    "delivery-report": {"description": "Delivery report with result for upload to Scout"},
    "multiqc-html": {"description": "Multiqc report for the run in html format"},
    "multiqc-json": {"description": "Multiqc report for the run in json format"},
    "pdf": {"description": "Portable document format"},
    "qc-report": {"description": "Results and QC"},
    "sambamba-depth": {"description": "Coverage information from sambamba"},
    "summary": {"description": "Overview file without detailed information"},
    "tsv": {"description": "Tab separated values"},
    "vcf-report": {"description": "Results and QC from variant calling"},
    "software-versions": {"description": "Versions of software used in analysis"},
}

VALIDATIONS_COMMON = {
    "ped-check": {"description": "Results from pedigree validation"},
    "qc-metrics": {"description": "QC metrics from analysis"},
    "sex-check": {"description": "Results from sex validation"},
}

ANALYSIS_COMMON = {
    "assembly": {"description": "Assembly"},
    "autozyg": {"description": "Autozygous region"},
    "bed": {"description": "Bed file"},
    "bed-index": {"description": "Following index"},
    "bigwig": {"description": "Bigwig formated file"},
    "clinical": {"description": "Clinical subset"},
    "config": {"description": "Config file"},
    "coverage": {"description": "Output with coverage information"},
    "diagram": {"description": "Data diagram"},
    "filtered": {"description": "Filtered data"},
    "fracsnp": {"description": "Fraction of reads with snp"},
    "fusion": {"description": "Fusion transcripts"},
    "genes": {"description": "Related to genes"},
    "junction": {"description": "Junction data"},
    "metrics": {"description": "Data metrics"},
    "first-pass": {"description": "Data metrics first pass"},
    "second-pass": {"description": "Data metrics second pass"},
    "reference-info": {"description": "Information about references used in analysis"},
    "regions": {"description": "Output for regions"},
    "research": {"description": "Research set"},
    "segments": {"description": "Output for segments"},
    "sites": {"description": "Output for sites"},
    "tcov": {"description": "Coverage output"},
    "tiddit-coverage": {"description": "Coverage output from tiddit"},
    "visualization": {"description": "Visualizes data"},
}

TOOLS = {
    "arriba": {"description": "Fusion caller"},
    "asereadcounter": {"description": "Count reads mapping to heterozygous sites"},
    "chanjo": {"description": "Tool to keep track of coverage over specific regions"},
    "chromograph": {"description": "Tool to create PNG images from BED and WIG files from mikaell"},
    "cnvkit": {"description": "Tool to call copy number variations"},
    "ascatngs": {"description": "Tool to identify somatically acquired copy-number alterations"},
    "delly": {"description": "Cancer structural variant prediction tool"},
    "cyrius": {"description": "Tool to call the problematic CYP2D6 gene"},
    "deseq2": {"description": "Differential expression analysis with DESeq2"},
    "deepvariant": {"description": "Variantcaller"},
    "dnascope": {"description": "Call snv indels"},
    "genotyper": {"description": "SNV indel caller from sention"},
    "gffcompare": {"description": "Compare gff files"},
    "haplotype-caller": {"description": "Call snv and indels"},
    "manta": {"description": "Tool to call structural variants"},
    "mitodel": {"description": "Tool to identify mitochondrial deletion signatures"},
    "peddy": {"description": "Tool to check pedigree and ancestral relations"},
    "picard": {"description": "Picard set of bioinformatic tools"},
    "salmon-quant": {"description": "Transcript quantification"},
    "sention": {"description": "Sention algorithm"},
    "star-fusion": {"description": "Fusion caller"},
    "stringtie": {"description": "Transcript assembler"},
    "tnscope": {"description": "Call snv indels"},
    "tnscope-umi": {"description": "Call snv indels for umi"},
    "upd": {"description": "Uniparent disomy caller from bjhall"},
    "vardict": {"description": "Cancer variant caller"},
    "wisecondor": {"description": "NIPT caller"},
}

MIP_SPECIFIC = {
    "exe-ver": {"description": "Executable versions"},
    "mip-analyse": {"description": "MIP information about analysis"},
    "mip-config": {"description": "MIP configs for analysis"},
    "mip-log": {"description": "Logs for MIP analysis"},
    "pedigree-yaml": {"description": "YAML file with pedigree information"},
    "sample-info": {"description": "MIP info file about samples"},
}

BALSAMIC_SPECIFIC = {
    "balsamic-config": {"description": "Balsamic configs for analysis"},
    "balsamic-dag": {"description": "Balsamic run schema"},
    "balsamic-report": {"description": "Report from analysis"},
}

MICROSALT_SPECIFIC = {
    "microsalt-config": {"description": "Config settings for microsalt analysis"},
    "microsalt-log": {"description": "SLURM log for microsalt analysis"},
    "typing-report": {"description": "Results from bacterial typing"},
}

MUTANT_SPECIFIC = {
    "mutant-config": {"description": "Config settings for mutant analysis"},
    "mutant-log": {"description": "SLURM log for mutant analysis"},
    "pangolin": {"description": "Pangolin specific output"},
    "typing-report": {"description": "Results from typing"},
    "typing-summary": {"description": "Summary of results from typing"},
    "fohm-delivery": {"description": "Relevant for FoHM"},
    "ks-delivery": {"description": "Relevant for Karolinska hospital/microbial routine"},
    "komplettering": {"description": "Filetype specific for national uploading of microbial data"},
    "consensus": {"description": "Consensus sequence"},
    "ks-results": {"description": "KS modification of pangolin typing results"},
    "ks-aux-results": {"description": "KS modification of pangolin called variants"},
    "pangolin-typing": {"description": "Pangolin typing results"},
    "artic-sum": {"description": "GMS-Artic summary file"},
    "artic-var": {"description": "GMS-Artic variant file"},
    "artic-type": {"description": "GMS-Artic typing file"},
    "artic-qc": {"description": "GMS-Artic QC file"},
    "artic-json": {"description": "GMS-Artic json file"},
    "vcf-covid": {"description": "VCF file containing covid data. Distinction req. by production"},
    "instrument-properties": {"description": "Sequencing metadata"},
    "consensus-sample": {"description": "Separate sample consensus fasta"},
    "pangolin-typing-fohm": {"description": "Pangolin typing report with only qc_pass samples included"},
}

AVAILABLE_USAGES = {
    "audit",
    "cg",
    "chanjo",
    "deliver",
    "genotype",
    "nipt",
    "scout",
    "storage",
    "vogue",
}

COMMON_TAG_CATEGORIES = {
    "alignment_tags": ALIGNMENT_COMMON,
    "analysis_tags": ANALYSIS_COMMON,
    "family_tags": FAMILY_COMMON,
    "raw_data": RAW_DATA,
    "reporting_tags": REPORTING_COMMON,
    "tool_tags": TOOLS,
    "validation_tags": VALIDATIONS_COMMON,
    "variant_tags": VARIANT_COMMON,
}

ALL_TAG_CATEGORIES = [
    ALIGNMENT_COMMON,
    ANALYSIS_COMMON,
    BALSAMIC_SPECIFIC,
    FAMILY_COMMON,
    MIP_SPECIFIC,
    MICROSALT_SPECIFIC,
    MUTANT_SPECIFIC,
    RAW_DATA,
    REPORTING_COMMON,
    TOOLS,
    VALIDATIONS_COMMON,
    VARIANT_COMMON,
]

ALL_TAGS = {tag for category in ALL_TAG_CATEGORIES for tag in category.keys()}


if __name__ == "__main__":
    print(ALL_TAGS)
