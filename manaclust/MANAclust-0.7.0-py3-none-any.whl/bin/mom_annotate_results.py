import argparse
import sys
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import umap
import pandas as pd
from scipy import stats
from scipy.stats.mstats import f_oneway as aov
from scipy.stats import ttest_ind as ttest
from bin.common_functions import write_table, process_dir, get_sample_k_lists, import_dict, correct_pvalues_for_multiple_testing, do_louvain_merger
from bin.mom_clust import *

##########################################################
## stats functions


def get_anova(expression_vect, group_vect, num_in_each_group):
    global full_expression, list_of_k_sample_indices
    if np.sum(full_expression[index,:]) == 0:
        return([np.nan,np.nan])
    list_of_group_values = []## keeps track of the values of each group's expression values
    for group in range(0,len(list_of_k_sample_indices)):
        if len(list_of_k_sample_indices[group]) > 0:
            list_of_group_values.append(full_expression[index,list_of_k_sample_indices[group]])
    ## go through and check for empty lists
    return_val = list(aov(*list_of_group_values))
    return(return_val)




###############################################################

def get_per_ome_feat_select_labels(subjects, meta_ome):
    feat_labels = []
    for subj in subjects:
        feat_labels.append(meta_ome.label_dict[subj])
    return(feat_labels)


def get_within_ome_similarity(feat_select_labels, ome, out_dir):
    print("\ttesting whether there are overall pairwise differences in affinities")
    #print(feat_select_labels)
    F_mat = np.zeros((len(feat_select_labels),len(feat_select_labels)))
    p_mat = np.ones((len(feat_select_labels),len(feat_select_labels)))
    for i in range(0,len(feat_select_labels)):
        first_indices = feat_select_labels[i]
        if len(first_indices)>=3:
            for j in range(i, len(feat_select_labels)):
                if i != j:
                    second_indices = feat_select_labels[j]
                    if len(second_indices)>=3:
                        ## subset within group affinities
                        #print(ome.affinity_matrix[:3,:3])
                        temp_first_within = ome.affinity_matrix[first_indices,:]
                        temp_first_within = temp_first_within[:,first_indices]
                        #print(temp_first_within[:3,:3])
                        temp_second_within = ome.affinity_matrix[second_indices,:]
                        temp_second_within = temp_second_within[:,second_indices]
                        ## to remove duplicates (from matrix symmetry), just get the upper triangle
                        temp_first_within = temp_first_within[np.tril_indices(temp_first_within.shape[0], k=-1)].tolist()
                        temp_second_within = temp_second_within[np.tril_indices(temp_second_within.shape[0], k=-1)].tolist()
                        ## combine them
                        combined_within_group_affinities = temp_first_within + temp_second_within
                        #print(combined_within_group_affinities)
                        
                        ## now get the across group affinities
                        across_group_affinities = ome.affinity_matrix[first_indices,:]
                        across_group_affinities = across_group_affinities[:,second_indices].flatten().tolist()

                        f, p = list(aov(*[combined_within_group_affinities, across_group_affinities]))
                        #print(f)
                        #print(p)
                        F_mat[i,j]=f
                        F_mat[j,i]=f
                        p_mat[i,j]=p
                        p_mat[j,i]=p
    ## correct p values
    #print(p_mat)
    uncorrected_p = p_mat.flatten()
    corrected_p = np.array(correct_pvalues_for_multiple_testing(uncorrected_p)).reshape(p_mat.shape)
    #print(corrected_p)
    corrected_p = np.nan_to_num(corrected_p)
    ## had to clip for visualization; led to errors in dendrogram creation 
    corrected_p = np.clip(corrected_p, 1e-310, 1)
    #print(corrected_p)
    neg_log_ten_p = -np.log10(corrected_p)
    sns.clustermap(F_mat)
    plt.savefig(out_dir+ome.name+"_affinity_F_statistic_matrix.png",
            dpi=600,
            bbox_inches='tight')
    sns.clustermap(corrected_p)
    plt.savefig(out_dir+ome.name+"_affinity_BH_p_val_matrix.png",
            dpi=600,
            bbox_inches='tight')
    sns.clustermap(neg_log_ten_p)
    plt.savefig(out_dir+ome.name+"_affinity_neg_log10_BH_p_val_matrix.png",
            dpi=600,
            bbox_inches='tight')
    print(corrected_p.shape)
    print(corrected_p)
    return(corrected_p)


def convert_sample_k_list_to_out_table(subjects, temp_sample_k_lists):
    ## create
    consensus_out_list = [[temp_sample] for temp_sample in subjects]
    for i in range(0,len(temp_sample_k_lists)):
        temp_group = temp_sample_k_lists[i]
        print(temp_group)
        for j in range(len(temp_group)):
            print(temp_group[j])
            consensus_out_list[temp_group[j]].append(i)
    return(consensus_out_list)


def get_ome_consensus_types(ome_group_probs, temp_sample_k_lists, subjects, out_dir):
    out_dir = process_dir(out_dir)
    print(ome_group_probs.shape)
    ome_type_k_lists, new_mergers, partition_dict = do_louvain_merger(ome_group_probs, temp_sample_k_lists)
    print('\tWe found',len(new_mergers), 'consensus groups:')
    out_summary = []
    for i in range(len(new_mergers)):
        temp_list = new_mergers[i]
        out_summary.append(["consensus_group_"+str(i), '||'.join(list(map(str, temp_list)))])
        print(out_summary[-1])
    ## get the updated lists
    consensus_out_list = convert_sample_k_list_to_out_table(subjects, ome_type_k_lists)
    write_table(deepcopy(consensus_out_list), out_dir+'sample_level_consensus_type_annotations.tsv')
    write_table(out_summary, out_dir+'final_group_level_consensus_type_annotations.tsv')
    return(ome_type_k_lists, consensus_out_list)


def analyze_group_differences(meta_ome, out_dir, alpha):
    out_dir = process_dir(out_dir)
    all_consensus_out_tabels = []
    for ome in meta_ome.cat_omes_full + meta_ome.num_omes_full:
        temp_out_dir = process_dir(out_dir + ome.name)
        print("working on numeric ome:", ome.name)
        feat_select_labels = get_per_ome_feat_select_labels(ome.subjects, meta_ome)
        ## list of lists index in first list is sample group number, entry within these are indices 
        ## of the samples within this particular ome
        temp_sample_k_lists = get_sample_k_lists(feat_select_labels)
        ## find the consensus types
        ome_group_probs = get_within_ome_similarity(temp_sample_k_lists, ome, temp_out_dir)
        consensus_group_labels, consensus_out_list = get_ome_consensus_types(ome_group_probs, temp_sample_k_lists, ome.subjects, temp_out_dir)
        all_consensus_out_tabels.append(consensus_out_list)
        consensus_group_vect = np.array(consensus_out_list)[:,1].tolist()
        
        ome.do_stats(feat_select_labels, temp_out_dir, alpha = alpha)
        # print(feat_select_labels)
        # print(consensus_group_vect)
        consensus_group_vect = list(map(int, consensus_group_vect))
        ## do the same statistical analyses as before, but with the updated consensus groups
        temp_out_dir_types = process_dir(temp_out_dir + 'consensus_types')
        ome.do_stats(consensus_group_vect, temp_out_dir_types, alpha = alpha)
        print('\n\n')


##############################################################################


def parse_args():
    parser = argparse.ArgumentParser()

    ## global arguments
    parser.add_argument(
        '-cat','-c',
        default=[],
        dest='cat',
        nargs='*',
        type=str)

    parser.add_argument(
            '-missing_data','-missing','-md','-ms',
            dest='missing_str',
            help = "The string that should be interpreted as missing data. (Case sensitive)",
            default = "NA",
            type=str)

    parser.add_argument(
        '-num','-n',
        default=[],
        dest='num',
        nargs='*',
        type=str)

    parser.add_argument(
        '-meta_ome_results','-ome_results','-results',
        dest='meta_ome_file',
        help = "If you already did the clustering & have the this is the 'meta_ome_results.pkl' file, and just want to annotate these results.",
        type=str)

    parser.add_argument(
        '-alpha',
        help = "The cutoff to use for signficance. Default = 0.05",
        type=float,
        default = 0.05)

    parser.add_argument(
        '-out_dir',
        default = "/home/scott/bin/momcluster/lib/synthetic_data/",
        type=str)

    args = parser.parse_args()
    return(args)


def main(args):
    if args.meta_ome_file == None:
        meta_ome = cluster_omes(cat_omes = args.cat, num_omes = args.num, missing_str = args.missing_str)
    else:
        meta_ome = import_dict(args.meta_ome_file)
    analyze_group_differences(meta_ome, args.out_dir, args.alpha)


###############################################################################

if __name__ == "__main__":
    ## set up the parser
    args = parse_args()
    main(args)

