
def query_vcf(vcf_file, queries):
    from pysam import VariantFile

    data_dict = dict()
    for ix in range(len(queries)):
        data_dict[ix] = list()

    bcf_in = VariantFile(vcf_file)

    for record in bcf_in.fetch():
        for ix, query in enumerate(queries):
            to_add = process_record(record, query)
            if len(to_add) > 0:
                data_dict[ix].append(to_add)

    return(data_dict)



def process_record(record, query):
    AC_str = "AC_" + query['ancestry']
    AF_str = "AF_" + query['ancestry']
    AN_str = "AN_" + query['ancestry']

    # checks whether variant applies to ancestry
    if record.info[AC_str][0] == 0: 
        return ()

    if query['PASS'] is not None:
            if ("PASS" in list(record.filter)) != query['PASS']:
                return ()

    if query['variant_type'] is not None:
        if record.info['variant_type'] != query['variant_type']:
            return ()

    # flip ref & alt in MAF > 0.5
    if (record.info[AF_str][0] <= 0.5):
        out = (record.contig, record.start, record.stop, record.ref, record.alts[0],\
            str(record.info[AC_str][0]), str(record.info[AN_str]))
    else:
        out = (record.contig, record.start, record.stop, record.alts[0], record.ref,\
            str(record.info[AN_str] - record.info[AC_str][0]), str(record.info[AN_str]))

    return out



def get_reliable_sites(coverage_file, fail_vars, pop_split):
    import pyranges as pr

    covered_loci_list = filter_coverage(coverage_file)
    covered_loci = coordlist_to_pyranges(covered_loci_list)
    covered_loci_mgd = covered_loci.merge()

    reliable_sites = covered_loci_mgd.subtract(fail_vars)

    return reliable_sites



# assumes format chrX:pos, mean, median, over_1, over_5, over_10, over_15, over_20, over_25, over_30, over_50, over_100
def filter_coverage(coverage_file, pop_split):
    import gzip

    f = gzip.open(coverage_file, 'r') 
    headers = next(f).rstrip().split(b'\t')

    over_15_col = [ix for ix, col in enumerate(headers) if col==b"over_15"][0]
    over_100_col = [ix for ix, col in enumerate(headers) if col==b"over_100"][0]

    out_l = []
    for line in f:
        line_spl = line.decode().split('\t')
        chrom, pos = line_spl[0].split(':')

        over_15_threshold = 0.9
        if chrom == "chrX": 
            if (int(pos) >= 10001) or (int(pos) <= 2781479): # PAR1
                over_15_threshold = 0.9 
            elif (int(pos) >= 155701383) or (int(pos) <= 156030895): #PAR2
                over_15_threshold = 0.9
            else:
                over_15_threshold = (pop_split["XX"] * 0.9 + pop_split["XY"] * 0.5)/(pop_split["XX"] + pop_split["XY"])
 
        if (float(line_spl[over_15_col]) >= over_15_threshold) and (float(line_spl[over_100_col]) <= 0.1):
            pos = line_spl[0].split(':')
            out_l.append((pos[0], int(pos[1])-1, int(pos[1])))

    return out_l



def get_training_loci(reliable_sites, phyloP_bw, ensembl_ftp, nonsingleton_snvs):
    import pyranges as pr
    
    phylop_filtered_list = filter_phyloP(phyloP_bw)
    phylop_filtered = coordlist_to_pyranges(phylop_filtered_list)
    phylop_filtered_mgd = phylop_filtered.merge()

    exons = query_ensembl(ensembl_ftp, "exon")

    training_loci = reliable_sites.intersect(phylop_filtered_mgd)\
                                  .subtract(exons)\
                                  .subtract(nonsingleton_snvs)
    
    return training_loci



def filter_phyloP(phyloP_bw, phyloP_range=[-1.3,0]):
    import pyBigWig

    bw = pyBigWig.open(phyloP_bw)

    out_l = []
    for chrom in bw.chroms().keys():
        vals = bw.intervals(chrom)
        l = [(chrom, record[0], record[1]) for record in vals\
            if ((record[2] >= phyloP_range[0]) and (record[2] <= phyloP_range[1]))]
        out_l.extend(l)

    return out_l



# gtf format uses inclusive range 
def query_ensembl(ensembl_ftp, annot):
    import pandas as pd
    import pyranges as pr

    data = pd.read_csv(ensembl_ftp, sep='\t', header=None,\
        names=['Chromosome', 'source', 'type', 'Start', 'End', 'score', 'strand',\
        'phase', 'attributes'], skiprows=[i for i in range(5)], compression="gzip")
    data['Start'] = data['Start'] - 1 

    data_correct_type = data.loc[data['type']==annot]
    data_correct_type["Chromosome"] = ["chr" + str(chrom) for chrom in data_correct_type["Chromosome"]]

    data_correct_type_pr = pr.PyRanges(data_correct_type)

    return data_correct_type_pr



def query_sequence(gr, flank, genome, reference_fasta):
    import pandas as pd
    import numpy as np
    import pyranges as pr

    chr_list = gr.Chromosome[~gr.Chromosome.duplicated()]       # unique chromosomes, but in order

    ix = 0
    out = np.empty(shape=(np.sum(2 * gr.lengths() - 1), 4*flank+1, 5), dtype=np.int8)
    for chrom in chr_list:
        chrom_gr = pr.from_dict({'Chromosome': [chrom], 'Start': [0], 'End': [genome[chrom][1]]})
        chrom_seq = pr.get_fasta(chrom_gr, reference_fasta)[0]

        seqs = [chrom_seq[(pos.Start-flank):(pos.End+flank)] for pos in gr[chrom].as_df().itertuples()]
        seqs_upper = ["X".join(seq.upper()) for seq in seqs]
        seqs_upper_split = [[seq[i:(i+4*flank+1)] for i in np.arange(len(seq)-4*flank)] for seq in seqs_upper]
        seqs_upper_flattened = [item for sublist in seqs_upper_split for item in sublist]

        nucs = [list(seq) for seq in seqs_upper_flattened]
        nucs_df = pd.DataFrame(nucs)

        # one hot encode the sequences
        nucs_cat = nucs_df.apply(lambda x: pd.Categorical(x, categories = ['A', 'C', 'X', 'G', 'T']))
        nucs_bin = pd.get_dummies(nucs_cat)
        nucs_rshpd = np.array(nucs_bin, dtype=np.int8).reshape(nucs_bin.shape[0], 4*flank+1, 5) 

        n_seqs = nucs_rshpd.shape[0]
        out[ix:(ix+n_seqs)] = nucs_rshpd
        ix += n_seqs

    return out



def correct_refs(gr, snvs_pr, seq):
    import numpy as np
    import pandas as pd
    import pyranges as pr

    flank = seq.shape[1]//2

    gr_spl = gr.tile(1)
    row_ix = pd.Series(range(len(gr_spl)), name="id")
    gr_spl = gr_spl.insert(row_ix)

    gr_spl_on_snvs_hits = gr_spl.join(snvs_pr)
    
    anyHits = (gr_spl_on_snvs_hits.length != 0)
    
    if anyHits:
        gr_spl_hit_ids = gr_spl_on_snvs_hits.id

        nucs_df = pd.DataFrame(gr_spl_on_snvs_hits.ref)
        nucs_cat = nucs_df.apply(lambda x: pd.Categorical(x, categories = ['A', 'C', 'X', 'G', 'T']))
        
        refs_from_vcf_ohe = np.array(pd.get_dummies(nucs_cat))
        seq[gr_spl_hit_ids, flank] = refs_from_vcf_ohe
     
    return 
    

def split_data(training_regions, chrXnonPAR, singleton_variants, sequence, pop_split):
    import numpy as np
    import pandas as pd
    import pyranges as pr

    n_sites = training_regions.length
    flank = sequence.shape[1]//2

    training_sites = training_regions.tile(1)
    row_ix = pd.Series(range(n_sites), name="id")
    training_sites = training_sites.insert(row_ix)

    # address chrX and chrY
    training_sites = training_sites[training_sites.Chromosome != "chrY"]
    chrXnonPAR_id = training_sites.join(chrXnonPAR).id

    neutral_singleton_variants = singleton_variants.join(training_sites)

    AC = np.array(neutral_singleton_variants.ac, dtype=int)
    AC_skew = np.random.binomial(n=AC, p=0.6)                       # 60% of alternates dedicated to skewed splits
    AC_bal = AC - AC_skew                                           # remaining 40% to balanced split

    AN = np.repeat(2 * (pop_split['XY'] + pop_split['XX']), n_sites)    # In abuse of notation, AN refers to reference allele count 
    AN[chrXnonPAR_id] = pop_split['XY'] + 2 * pop_split['XX']

    AN[neutral_singleton_variants.id] = neutral_singleton_variants.an - 1   # -1 due to singleton

    AN_skew = np.random.binomial(AN, p=0.6)                         # 60% of references dedicated to skewed splits
    AN_rem = AN - AN_skew
    AN_bal = balance_data(AN_rem, AC_bal)                           # subset of remaining 40% for balanced split

    N_bal = np.concatenate([AN_bal, AC_bal])
    N_skew = np.concatenate([AN_skew, AC_skew])

    N_cal = np.random.binomial(N_skew, p=2/3)                       # 2:1 split in calibration set versus test set
    N_test = N_skew - N_cal

    alts_ohe = np.array(pd.get_dummies(pd.Categorical(neutral_singleton_variants.alt, categories = ['A', 'C', 'X', 'G', 'T'])))
    refs_ohe = sequence[:,flank,:]
    nuc = np.concatenate([refs_ohe, alts_ohe])

    indices = np.concatenate((np.arange(n_sites), neutral_singleton_variants.id), axis=0)

    return indices, nuc, np.c_[N_bal, N_cal, N_test]



def balance_data(AN, AC):
    import collections
    import numpy as np

    samples = np.random.choice(len(AN), sum(AC), p=AN/sum(AN))
    counts = collections.Counter(samples)
    
    keys = [int(key) for key in counts.keys()]
    vals = [int(val) for val in counts.values()]

    AN_out = np.repeat(0, len(AN))
    AN_out[keys] = vals

    return AN_out



def coordlist_to_pyranges (pos_l, entryNames = ["Chromosome", "Start", "End"]):
    assert len(pos_l[0]) == len(entryNames), "not enough entry names provided"

    import pyranges as pr 

    values_by_entry = zip(*pos_l)
    pos_dict = {entry: values for entry, values in zip(entryNames, values_by_entry)}
    pos_pr = pr.from_dict(pos_dict)

    return pos_pr 



def sample_loci_from_pr (gr, n_loci):
    import pyranges as pr
    import numpy as np

    N = gr.length
    gr_spl = gr.tile(1)

    ix = np.random.choice(range(N), n_loci, replace=False)
    sample_pr = pr.PyRanges(gr_spl.as_df().iloc[ix,:])

    return sample_pr.sort()



def load_variants(fn):
    import pyranges as pr

    gr = pr.read_bed(fn) 
    gr.columns = ["Chromosome", "Start", "End", "ref", "alt", "ac", "an"]
    gr.ac = gr.ac.astype(int)

    return gr



def writeToBed(gr, fn):
    import pandas as pd
    import os

    fn_tmp = fn + ".tmp"
    gr.as_df().to_csv(fn_tmp, header=False, index=False, sep='\t')
    
    os.system("sort-bed " + fn_tmp + " > " + fn)
    os.system("rm " + fn_tmp)

    return

