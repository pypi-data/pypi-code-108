
# functions to correct multiallelic inverted sites (inconsistencies exist in allele counts and refs)
def insert_corrected_snvs (correction, snvs):
    import pyranges as pr
    import pandas as pd

    no_correction_required = snvs.subtract(correction)
    no_correction_required.columns = no_correction_required.columns.str.replace("old_ref", "ref")

    inserted_df = pd.concat([no_correction_required.as_df(), correction.as_df()], axis=0)
    sorted_gr = pr.PyRanges(inserted_df).sort()

    sorted_gr = sorted_gr[sorted_gr.ac.astype(int)>0]
    
    return sorted_gr



def correct_inverted_multiallelics(snvs):
    snvs.columns = snvs.columns.str.replace("ref", "old_ref")

    multiallelic_loci = get_multiallelic_sites (snvs)
    inverted_multiallelic_sites = filter_for_inverted_sites (multiallelic_loci, snvs)
    annot_with_major_allele = get_major_alleles(inverted_multiallelic_sites, snvs)
    out = correct_allele_count (annot_with_major_allele)

    out = out.drop(['ix', 'old_ref'])

    return out



# find multiallelic sites
def get_multiallelic_sites (snvs):
    loci = snvs[['Chromosome', 'Start', 'End']].as_df()

    multiallelic_loci = loci[loci.duplicated(keep='first')].drop_duplicates()\
                                                           .reset_index(drop=True)
    return multiallelic_loci



# find inverted multiallelic sites
def filter_for_inverted_sites (multiallelic_loci, snvs):
    import pyranges as pr
    import pandas as pd

    multiallelic_loci_gr = pr.PyRanges(multiallelic_loci)

    index = pd.Series(range(len(multiallelic_loci_gr)), name='ix')
    multiallelic_loci_gr = multiallelic_loci_gr.insert(index)

    multiallelic_loci_annot = multiallelic_loci_gr.join(snvs)
    is_inverted_indicator = multiallelic_loci_annot.as_df().groupby('ix')['old_ref'].agg(is_inverted)

    inverted_multiallelic_sites = pr.PyRanges(multiallelic_loci.loc[is_inverted_indicator])

    return inverted_multiallelic_sites



def is_inverted (alleles):
    import numpy as np

    return len(np.unique(alleles)) != 1



# query correct refs
def get_major_alleles (inverted_multiallelic_sites, snvs):
    import pandas as pd

    index_inverted = pd.Series(range(len(inverted_multiallelic_sites)), name='ix')
    inverted_multiallelic_sites = inverted_multiallelic_sites.insert(index_inverted)

    out = inverted_multiallelic_sites.join(snvs).drop(['Start_b', 'End_b'])
    correct_refs = out.as_df().groupby('ix').apply(get_correct_ref)
    correct_refs_expanded = pd.Series(correct_refs[out.ix], name="ref")

    out = out.insert(correct_refs_expanded)

    return out



def get_correct_ref (x):
    import pandas as pd
    import numpy as np

    refs = np.array(x['old_ref'])
    alts = np.array(x['alt'])
    
    hg38_ref = np.array(list(set(refs).intersection(set(alts))))
    inversion_ix = np.where([alt in hg38_ref for alt in alts])[0]
    correct_ref = refs[inversion_ix][0]
    
    return correct_ref



# correct AC
def correct_allele_count (out):
    import numpy as np
    import pyranges as pr

    ac_correction = out[out.old_ref!=out.ref].as_df().groupby('ix')['ac'].sum().reset_index(drop=True)

    tmpDf = out.as_df()
    tmpDf = tmpDf.astype({"ac": int})

    tmpDf.loc[tmpDf.old_ref==tmpDf.ref, 'ac'] -= np.array(ac_correction.astype(int))

    out = pr.PyRanges(tmpDf)

    return out
