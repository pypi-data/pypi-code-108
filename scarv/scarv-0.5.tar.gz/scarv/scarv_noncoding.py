from scarv import scarv_queries

def getNonCodingPathogenic(exon_flank, ensembl_ftp, hgmd_vcf, annotation_table_fn):
    import pyranges as pr

    exons = scarv_queries.query_ensembl(ensembl_ftp, "exon")
    transcripts = scarv_queries.query_ensembl(ensembl_ftp, "transcript")
    introns = transcripts.subtract(exons)

    exons_extensions = exons.slack(exon_flank)\
                            .intersect(introns)

    hgmd_snvs = VCFtoPyRanges_HGMD(hgmd_vcf)

    hgmd_snvs_noncoding = hgmd_snvs.subtract(exons)\
                                   .subtract(exons_extensions)

    out = filterForRegulatory(hgmd_snvs_noncoding, annotation_table_fn)

    return out


# function that converts HGMD vcf to pybedtool object
# filters for: 1) snvs, 2) CLASS=="DM" or "DM?"
def VCFtoPyRanges_HGMD(vcf_file):
    from pysam import VariantFile

    HGMD_out_l = []
    bcf_in = VariantFile(vcf_file)

    for record in bcf_in.fetch():
        is_snv = (len(record.ref)==1 and len(record.alts[0])==1)
        is_dm = record.info['CLASS'] in ['DM', 'DM?']
        if (is_snv and is_dm):
            HGMD_out_l += [(record.contig, record.start, record.stop, record.alts[0])]

    HGMD_bed = scarv_queries.coordlist_to_pyranges(HGMD_out_l, entryNames = ["Chromosome", "Start", "End", "Alt"])
    HGMD_bed.Chromosome = ["chr" + str(chrom) for chrom in HGMD_bed.Chromosome]

    HGMD_bed = HGMD_bed[~HGMD_bed.as_df().duplicated()] # remove duplicates
    out = HGMD_bed.sort()
     
    return out


def filterForRegulatory(gr, annotation_table_fn):
    import pandas as pd
    import pyranges as pr

    annotation = pd.read_csv(annotation_table_fn, sep='\t')

    correct_type = (annotation['mutype'] == 'regulatory')
    regulatory_snvs_annotation = annotation[correct_type] 
    regulatory_snvs_annotation['chrom'] = ["chr" + str(chrom) for chrom in regulatory_snvs_annotation['chrom']]
    
    regulatory_snvs_annotation_unduplicated = regulatory_snvs_annotation[~regulatory_snvs_annotation[['chrom', 'pos','alt']].duplicated()]

    filtered_snvs = pd.merge(gr.as_df(), regulatory_snvs_annotation_unduplicated, left_on=['Chromosome', 'End', 'Alt'],\
        right_on=['chrom', 'pos','alt'], how='inner')

    return pr.PyRanges(filtered_snvs[['Chromosome', 'Start', 'End', 'Alt']])


