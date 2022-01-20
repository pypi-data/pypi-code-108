import argparse
import sys
import os
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import umap
import pandas as pd
from scipy import stats
from scipy.stats.mstats import f_oneway as aov
from scipy.stats import ttest_ind as ttest
from scipy.stats import chisquare
from scipy.stats import chi2,chi2_contingency
from scipy.stats.contingency import margins
from copy import deepcopy

from mana_clust.common_functions import write_table, process_dir, get_sample_k_lists, import_dict, correct_pvalues_for_multiple_testing, do_louvain_merger
from mana_clust.mana_clust import *

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

def get_per_ome_feat_select_labels(subjects, meta_ome, ome_name = ''):
    feat_labels = []
    for subj in subjects:
        if subj in meta_ome.label_dict:
            feat_labels.append(meta_ome.label_dict[subj])
        else:
            feat_labels.append("NA")
            print("WARNING: there is a subject in ome:\n\t"+ome_name+"\nthat we couldn't find in the meta_ome")
    return(feat_labels)


def get_within_ome_similarity(feat_select_labels, ome, out_dir):
    print("\ttesting whether there are overall pairwise differences in affinities")
    #print(feat_select_labels)
    F_mat = np.zeros((len(feat_select_labels),len(feat_select_labels)))
    p_mat = np.zeros((len(feat_select_labels),len(feat_select_labels)))
    ## set the diagonal to one beacuse everything is equal to itself
    for i in range(p_mat.shape[0]):
        p_mat[i,i]=1.0
    for i in range(0,len(feat_select_labels)):
        first_indices = feat_select_labels[i]
        for j in range(i, len(feat_select_labels)):
            if i != j:
                second_indices = feat_select_labels[j]
                if len(second_indices)>=3 and len(first_indices)>=3:
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
                if len(first_indices)<3 and len(second_indices)<3:
                    ## this means that these groups are both missing from this ome, so they can be considered equivalent
                    F_mat[i,j]=0
                    F_mat[j,i]=0
                    p_mat[i,j]=1
                    p_mat[j,i]=1
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


def write_one_hot(consensus_out_list, num_consensus, out_file):
    """
    Takes in the consensus group sample annotations:
    sample_1    0
    sample_2    1
    sample_3    0
    ...

    and writes to the out_file the one-hot encoded version. Note that this has a header, whereas the original input does not
    sample      consensus_group_0   consensus_group_1   ....
    sample_1    1                   0                   ....
    sample_2    0                   1                   ....
    sample_3    1                   0                   ....
    ....
    """
    
    ## set up the outfile header
    out_summary =[["samples"]]
    for i in range(num_consensus):
        out_summary[0].append("consensus_group_"+str(i))
    ## go through the 
    for i in range(len(consensus_out_list)):
        temp_one_hot_out_mat = np.zeros(num_consensus, dtype = int).tolist()
        temp_one_hot_out_mat[consensus_out_list[i][1]] = 1
        temp_one_hot_out_mat = [consensus_out_list[i][0]] + temp_one_hot_out_mat
        out_summary.append(temp_one_hot_out_mat)
    write_table(out_summary, out_file)
    return


def get_ome_consensus_types(ome_group_probs, temp_sample_k_lists, subjects, out_dir, one_hot = False):
    out_dir = process_dir(out_dir)
    print(ome_group_probs.shape)
    ome_type_k_lists, new_mergers, partition_dict = do_louvain_merger(ome_group_probs, temp_sample_k_lists, cutoff = 0.05)
    print('\tWe found',len(new_mergers), 'consensus groups:')
    out_summary = []
    for i in range(len(new_mergers)):
        temp_list = new_mergers[i]
        out_summary.append(["consensus_group_"+str(i), '||'.join(list(map(str, temp_list)))])
        print(out_summary[-1])
    ## get the updated lists
    consensus_out_list = convert_sample_k_list_to_out_table(subjects, ome_type_k_lists)
    write_table(deepcopy(consensus_out_list), out_dir+'sample_level_consensus_type_annotations.tsv')
    write_table(deepcopy(out_summary), out_dir+'final_cluster_level_consensus_type_annotations.tsv')
    if one_hot:
        write_one_hot(deepcopy(consensus_out_list), len(new_mergers), out_dir+'sample_level_consensus_type_annotations_one_hot.tsv')
    return(ome_type_k_lists, consensus_out_list, new_mergers)


def get_shared_list(consensus_list_1, consensus_list_2):
    ## gets the list of shared subjects
    set_1 = set(np.array(consensus_list_1)[:,0].tolist())
    set_2 = set(np.array(consensus_list_2)[:,0].tolist())
    shared = list(set_1.intersection(set_2))
    print('\tfound',len(shared),'shared subjects out of',len(set_1.union(set_2)),'total')
    return(shared)


def set_up_cont_mat(consensus_list_1, consensus_list_2):
    ## set up the empty cont mat
    ## first figure out how many groups there are in the first and second
    len_1 = len(set(np.array(consensus_list_1)[:,1].tolist()))
    len_2 = len(set(np.array(consensus_list_2)[:,1].tolist()))
    print(len_1,len_2)
    return(np.zeros((len_1,len_2)))


def subject_list_to_dict(subj_list):
    """
    Takes in 2D list of pairs of keys and values. Returns dict of them
    """
    out_dict = {}
    for line in subj_list:
        out_dict[line[0]]=line[1]
    return(out_dict)


def get_cont_mat_from_consensus_lists(consensus_list_1, consensus_list_2):
    ## first get the list of shared subjects
    common_subjects = get_shared_list(consensus_list_1, consensus_list_2)
    if len(common_subjects) < 5:
        print("\n\n\t\tWARNING! We found less than 5 shared subjects across these omes. Skipping comparison.")
        return(None)
    ## set up the empty contingency matrix
    cont_mat = set_up_cont_mat(consensus_list_1, consensus_list_2)
    subj_1_dict = subject_list_to_dict(consensus_list_1)
    subj_2_dict = subject_list_to_dict(consensus_list_2)
    for subject in common_subjects:
        row_idx = subj_1_dict[subject]
        col_idx = subj_2_dict[subject]
        cont_mat[row_idx, col_idx] += 1
    return(cont_mat)


def do_comparison(first_ome_name, second_ome_name, consensus_type_dict):
    print("\n\ncomparing",first_ome_name, "to", second_ome_name)
    consensus_list_1 = consensus_type_dict[first_ome_name]["consensus_out_list"]
    consensus_list_2 = consensus_type_dict[second_ome_name]["consensus_out_list"]
    cont_mat = get_cont_mat_from_consensus_lists(consensus_list_1, consensus_list_2)
    if not type(cont_mat)== np.ndarray:
        return
    ## make the subject-wise dictionary
    print(cont_mat)
    chi, p = chisquare(cont_mat, axis = None)
    
    ## now get cell-wise p-values
    #cell_wise_p = 
    return cont_mat, chi, p


########################################################################
########## these stats functions were borrowed from PyMINEr ############
## PyMINEr available at: www.sciencescott.com/pyminer
########################################################################

## statistics functions 
def residuals(observed, expected):
     return (observed - expected) / np.sqrt(expected)

def stdres(observed, expected):
     n = observed.sum()
     rsum, csum = margins(observed)
     v = csum * rsum * (n - rsum) * (n - csum) / n**3
     return (observed - expected) / np.sqrt(v)

def adj_res(observed,expected=None):
    ## https://journals.sagepub.com/doi/pdf/10.1177/0013164403251280
    n=observed.sum()
    rsum, csum =  margins(observed)
    #print("margins\n",rsum,csum)
    if type(expected)!=type(None):
        F=expected
    else:
        F=rsum*csum/n
    #print("F\n",F)
    res = (observed-F)/np.sqrt(F)
    z_adj_res = res/np.sqrt((1-rsum/n)*(1-csum/n))
    return(z_adj_res)

def res_to_p(residual, dof):
    chi = residual**2
    p = 1 - chi2.cdf(chi, dof)
    return(p)

def cont_to_p_independent(observed,leave_out = None):
    if leave_out != None:
        row_vect = np.arange(np.shape(observed)[0]).tolist()
        ## remove the left out index
        row_vect.pop(leave_out)
        row_vect = np.array(row_vect)
        observed = observed[row_vect,:]
    try:
        chi2, p, dof, expected = chi2_contingency(observed)
    except:
        print("\n\nWARNING: stats will be approximate due to missing data\n\n")
        temp_observed = np.array(deepcopy(observed))+1
        temp_observed = temp_observed.tolist()
        chi2, p, dof, expected = chi2_contingency(temp_observed)
    #print("traditional expected\n",expected)
    adjusted_residuals = adj_res(observed)
    p = res_to_p(adjusted_residuals,dof)
    p = correct_pvalues_for_multiple_testing(p)
    return(p, adjusted_residuals)
########################################################################

def format_res_p_merged(res_mat,p_mat):
    p_mat = p_mat.tolist()
    out_mat = deepcopy(res_mat.tolist())
    for i in range(len(out_mat)):
        for j in range(len(out_mat[i])):
            ## first change the 
            out_mat[i][j] = "{:.3g}".format(out_mat[i][j])
            p_mat[i][j] = "{:.3g}".format(p_mat[i][j])
            out_mat[i][j] = out_mat[i][j] + "\n(" +p_mat[i][j] + ")"
    return(np.array(out_mat))

def write_consensus_chi_table_results(first_ome_name, second_ome_name, cont_mat, adj_res_mat, p_mat, temp_out_dir):
    ## write the output table of statistics for the chi-square results
    out_table = [["group_1_ID", "group_2_ID", "number_in_both","adjusted_residuals","BH_corrected_p_vals","P(Grp2|Grp1)","P(Grp1|Grp2)","P(Grp2|Grp1)-P(Grp1|Grp2)"]]
    ## rows are the first group, columns are the second group
    for i in range(len(cont_mat)):## first group
        first_con_grp_name = first_ome_name+"||consensus_group_"+str(i)
        num_grp_1 = np.sum(np.array(cont_mat)[i,:])
        for j in range(len(cont_mat[i])):
            second_con_grp_name = second_ome_name+"||consensus_group_"+str(j)
            ## now append all of the results!
            num_grp_2 = np.sum(np.array(cont_mat)[:,j])
            prob_given_grp1 = cont_mat[i,j]/num_grp_1
            prob_given_grp2 = cont_mat[i,j]/num_grp_2
            prob_dif = prob_given_grp1 - prob_given_grp2
            out_table.append([first_con_grp_name, second_con_grp_name, cont_mat[i,j], adj_res_mat[i,j],p_mat[i,j], prob_given_grp1, prob_given_grp2, prob_dif])
            out_table.append([second_con_grp_name, first_con_grp_name, cont_mat[i,j], adj_res_mat[i,j],p_mat[i,j], prob_given_grp2, prob_given_grp1, -1*prob_dif])
    ## write a copy of the table
    write_table(deepcopy(out_table),os.path.join(temp_out_dir, "cross_ome_concordance_discordance_statistics.tsv"))
    ## return the contents
    return(out_table[1:])



def do_consensus_chi_analysis(first_ome_name, second_ome_name, consensus_type_dict, temp_out_dir):
    ## first make the directory for the output
    temp_out_dir = process_dir(os.path.join(temp_out_dir, first_ome_name+"_vs_"+second_ome_name))
    ## do the analysis
    cont_mat, chi, p = do_comparison(first_ome_name, second_ome_name, consensus_type_dict)
    p_mat, adjusted_residuals = cont_to_p_independent(cont_mat)
    ## plot the results
    print(chi, p)
    plt.rcParams.update({'font.size': 22})
    ax = sns.heatmap(cont_mat, annot = True)
    ax.set_title("chi="+str("{:.4g}".format(chi))+'\np='+str("{:.4g}".format(p)))
    ax.set(xlabel=second_ome_name+"\nconsensus groups", ylabel=first_ome_name+"\nconsensus groups")
    plt.savefig(temp_out_dir+"contingency_table.png",
            dpi=600,
            bbox_inches='tight')
    plt.clf()

    ax = sns.heatmap(adjusted_residuals, annot = format_res_p_merged(adjusted_residuals,p_mat), fmt = '')
    ax.set_title("chi adjusted residuals\n(BH-corrected p-value)")
    ax.set(xlabel=second_ome_name+"\nconsensus groups", ylabel=first_ome_name+"\nconsensus groups")
    plt.savefig(temp_out_dir+"chi_adjusted_residuals.png",
            dpi=600,
            bbox_inches='tight')
    plt.clf()
    print(p_mat)
    ax = sns.heatmap(p_mat, annot = True)
    ax.set_title("cell-wise adjusted p-values")
    ax.set(xlabel=second_ome_name+"\nconsensus groups", ylabel=first_ome_name+"\nconsensus groups")
    plt.savefig(temp_out_dir+"adjusted_p_values.png",
            dpi=600,
            bbox_inches='tight')
    plt.clf()

    out_table = write_consensus_chi_table_results(first_ome_name, second_ome_name, cont_mat, adjusted_residuals, p_mat, temp_out_dir)
    return(out_table)


def compare_consensus_omes(consensus_type_dict, cluster_ome_names, test_ome_names, out_dir):
    """
    This function does tests of independence for each ome.
    """
    if len(cluster_ome_names) + len(test_ome_names) <= 1:
        return
    print("checking to see which consensus types are related to each other\n")
    print("this is basically just doing Chi-squareds test of independence \non the counts for how many subjects are in each pair of consensus omes.")
    
    ## make the output directory
    consensus_comp_dir = process_dir(os.path.join(out_dir , "between_ome_consensus_group_comparisons"))

    ## go through the list of all omes & do the tests of independence
    all_cross_ome_results = [["group_1_ID", "group_2_ID", "number_in_both","adjusted_residuals","BH_corrected_p_vals","P(Grp2|Grp1)","P(Grp1|Grp2)","P(Grp2|Grp1)-P(Grp1|Grp2)"]]
    if len(cluster_ome_names) > 1:
        temp_out_dir = process_dir(os.path.join(consensus_comp_dir, "between_clustering_omes"))
        between_clustering_omes_results_table = [["group_1_ID", "group_2_ID", "number_in_both","adjusted_residuals","BH_corrected_p_vals", "P(Grp2|Grp1)","P(Grp1|Grp2)","P(Grp2|Grp1)-P(Grp1|Grp2)"]]
        ## first make the output directory
        for i in range(len(cluster_ome_names)):
            first_ome_name = cluster_ome_names[i]
            for j in range(i,len(cluster_ome_names)):
                if i != j:
                    second_ome_name = cluster_ome_names[j]
                    between_clustering_omes_results_table += do_consensus_chi_analysis(first_ome_name, second_ome_name, consensus_type_dict, temp_out_dir)
        write_table(deepcopy(between_clustering_omes_results_table),os.path.join(temp_out_dir, "cross_ome_concordance_discordance_statistics.tsv"))
        all_cross_ome_results += between_clustering_omes_results_table[1:]
    ## if there are test omes, do those comparisons too
    if len(test_ome_names) > 1:
        temp_out_dir = process_dir(os.path.join(consensus_comp_dir, "between_test_omes"))
        cross_test_ome_results = [["group_1_ID", "group_2_ID", "number_in_both","adjusted_residuals","BH_corrected_p_vals", "P(Grp2|Grp1)","P(Grp1|Grp2)","P(Grp2|Grp1)-P(Grp1|Grp2)"]]
        ## first make the output directory
        for i in range(len(test_ome_names)):
            first_ome_name = test_ome_names[i]
            for j in range(i,len(test_ome_names)):
                if i != j:
                    second_ome_name = test_ome_names[i]
                    cross_test_ome_results += do_consensus_chi_analysis(first_ome_name, second_ome_name, consensus_type_dict, temp_out_dir)
        write_table(deepcopy(cross_test_ome_results),os.path.join(temp_out_dir, "cross_ome_concordance_discordance_statistics.tsv"))
        all_cross_ome_results += cross_test_ome_results[1:]
    
    ## compare across test and clustering omes
    if len(test_ome_names) >= 1 and len(cluster_ome_names) >= 1:
        temp_out_dir = process_dir(os.path.join(consensus_comp_dir, "between_cluster_and_test_omes"))
        clust_to_test_results = [["group_1_ID", "group_2_ID", "number_in_both","adjusted_residuals","BH_corrected_p_vals", "P(Grp2|Grp1)","P(Grp1|Grp2)","P(Grp2|Grp1)-P(Grp1|Grp2)"]]
        ## first make the output directory
        for i in range(len(test_ome_names)):
            first_ome_name = test_ome_names[i]
            for j in range(len(cluster_ome_names)):
                second_ome_name = cluster_ome_names[j]
                clust_to_test_results = do_consensus_chi_analysis(first_ome_name, second_ome_name, consensus_type_dict, temp_out_dir)
        write_table(deepcopy(clust_to_test_results),os.path.join(temp_out_dir, "cross_ome_concordance_discordance_statistics.tsv"))
        all_cross_ome_results += clust_to_test_results[1:]

    ## make the output table annotating all of the subjects and their consensus groups
    write_table(deepcopy(all_cross_ome_results),os.path.join(consensus_comp_dir, "all_combined_cross_ome_concordance_discordance_statistics.tsv"))
    return


def get_cross_ome_group_mapping(source_ome_consensus_out_list, target_ome_subject_list):
    consensus_group_source_dict = {key[0]:key[1] for value, key in enumerate(source_ome_consensus_out_list)}
    out_int_list = []
    for subject in target_ome_subject_list:
        if subject in consensus_group_source_dict:
            out_int_list.append(consensus_group_source_dict[subject])
        else:
            out_int_list.append("NA")
    return(out_int_list)


def get_test_ome_differences_by_consensus_goups(out_dir, 
                                                consensus_type_dict,
                                                alpha,
                                                test_cat = [],
                                                test_num = [],
                                                processes = 1):
    """
    Take in the test omes, and assess the statistical differences of the consensus groups defined by the clustering omes
    """
    temp_top_dir = process_dir(os.path.join(out_dir, 'test_ome_differences_by_consensus_groups'))
    consensus_names = sorted(list(consensus_type_dict.keys()))
    ## go through each of the 
    for ome in test_cat + test_num:
        temp_top_test_ome_dir = process_dir(os.path.join(temp_top_dir, ome.name))
        for consensus_name in consensus_names:
            if ome.name != consensus_name:
                ## do the analysis
                temp_out_dir = process_dir(os.path.join(temp_top_test_ome_dir, consensus_name+"_consensus_groups"))
                temp_labels = consensus_type_dict[consensus_name]["consensus_out_list"]
                temp_labels = get_cross_ome_group_mapping(temp_labels, ome.subjects)
                print(temp_labels)
                ome.do_stats(temp_labels, temp_out_dir, alpha = alpha, processes = processes)
    return


def write_final_cluster_to_consensus_group_mapping_file(all_clustering_ome_consensus_list_of_list_dict, out_dir):
    """
    Takes in the dictionary that holds all of the input clustering file names & 
    """

    ## get all the unique datasets
    all_input_datasets = sorted(list(all_clustering_ome_consensus_list_of_list_dict.keys()))

    ## get all the unique final groups
    all_list_of_lists = list(all_clustering_ome_consensus_list_of_list_dict.values())
    all_final_cluster_annotations = []
    for temp_dataset_list in all_list_of_lists:
        for temp_final_cluster_list in temp_dataset_list:
            all_final_cluster_annotations += temp_final_cluster_list
    all_final_cluster_annotations = sorted(list(set(all_final_cluster_annotations)))

    ## set up the header
    header = ['final_clusters']
    for dataset in all_input_datasets:
        header.append(dataset+"_consensus_group")

    ## set up the first column
    first_col = []
    for final_cluster in all_final_cluster_annotations:
        first_col.append("sample_group_"+str(final_cluster))

    ## go through all the lists of lists & annotate for the final groups
    all_annotation_table_wo_headers = []
    for dataset in all_input_datasets:
        temp_annotations = ['NA'] * len(first_col)
        temp_consensus_list_of_lists = all_clustering_ome_consensus_list_of_list_dict[dataset]
        for i in range(len(temp_consensus_list_of_lists)):
            for j in range(len(temp_consensus_list_of_lists[i])):
                ## i is consensus group
                ## temp_consensus_list_of_lists[i][j] is final group
                temp_annotations[temp_consensus_list_of_lists[i][j]] = i
        all_annotation_table_wo_headers.append(temp_annotations)

    ## transpose the annotations
    all_annotation_table_wo_headers = np.transpose(np.array(all_annotation_table_wo_headers)).tolist()
    out_table = [header]
    for i in range(len(first_col)):
        new_line = [first_col[i]] + all_annotation_table_wo_headers[i]
        out_table.append(new_line)
    write_table(out_table, os.path.join(out_dir, "final_clusters_to_consensus_group_annotations.tsv"))
    return


def write_sample_level_final_and_consensus_group_annotations(label_pairs, censensus_out_annotations_dict, out_dir):
    """

    """
    ## get the names of all of the datasets
    ## fix label_pairs. COuldn't find where this was broken earlier
    for i in range(len(label_pairs)):
        label_pairs[i] = label_pairs[i].strip()
        label_pairs[i] = label_pairs[i].split('\t')
    ## annotate all of the datasets
    all_datasets = sorted(list(censensus_out_annotations_dict.keys()))
    consensus_group_labels = np.zeros((len(label_pairs),len(all_datasets)),dtype = '<U10')
    consensus_group_labels[:,:] = "NA"
    header = ['sample', 'final_cluster']
    for col in range(len(all_datasets)):
        dataset = all_datasets[col]
        header.append(dataset+"_consensus_group")
        temp_consensus_lists = censensus_out_annotations_dict[dataset]
        temp_lookup_dict = {value[0]:value[1] for value in temp_consensus_lists}
        for row in range(len(label_pairs)):
            temp_sample_id = label_pairs[row][0]
            if temp_sample_id in temp_lookup_dict:
                consensus_group_labels[row,col] = str(temp_lookup_dict[temp_sample_id])
    ## make the output file
    consensus_group_labels = consensus_group_labels.tolist()
    out_table = [header]
    for i in range(len(label_pairs)):
        #print(label_pairs[i])
        #print(consensus_group_labels[i])
        #print(label_pairs[i] + consensus_group_labels[i])
        out_table.append(label_pairs[i] + consensus_group_labels[i])
    write_table(out_table, os.path.join(out_dir, "sample_final_cluster_and_consensus_group_annotations.tsv"))
    return


def analyze_group_differences(meta_ome, 
                              out_dir,
                              alpha, 
                              processes = 1, 
                              test_cat = [], 
                              test_num = [],
                              one_hot = False):
    """
    Takes in the meta ome and other test omes along with a few params to do the consensus
    typing as well as the statistics within each ome and post-hoc analyses
    """
    out_dir = process_dir(out_dir)

    ## catelogue the names of the omes for organizing data later
    cluster_ome_names = [ome.name for ome in meta_ome.cat_omes_full + meta_ome.num_omes_full]
    test_ome_names = []
    if len(test_cat) + len(test_num) > 0:
        test_ome_names = [ome.name for ome in test_cat + test_num]

    ## set up the dictionary to log the consensus types
    all_consensus_out_tabels = []
    consensus_type_dict = {}

    ## do all of the analyses
    per_ome_directories = []
    all_omes = meta_ome.cat_omes_full + test_cat + meta_ome.num_omes_full + test_num
    ome_type_annotations = ["clustering"]*len(meta_ome.cat_omes_full) + ["test"] * len(test_cat) + ["clustering"] * len(meta_ome.num_omes_full) + ["test"] * len(test_num)
    all_clustering_ome_consensus_list_of_list_dict = {}
    censensus_out_annotations_dict = {}
    for i in range(len(all_omes)):
        ome = all_omes[i]
        temp_out_dir = process_dir(out_dir + ome.name)
        per_ome_directories = []
        print("working on ome:", ome.name)
        feat_select_labels = get_per_ome_feat_select_labels(ome.subjects, meta_ome, ome_name = ome.name)
        ## list of lists index in first list is sample group number, entry within these are indices 
        ## of the samples within this particular ome
        temp_sample_k_lists = get_sample_k_lists(feat_select_labels)

        ## find the consensus types
        ome_group_probs = get_within_ome_similarity(temp_sample_k_lists, ome, temp_out_dir)
        consensus_group_labels, consensus_out_list, consensus_list_of_lists = get_ome_consensus_types(ome_group_probs, temp_sample_k_lists, ome.subjects, temp_out_dir, one_hot = one_hot)
        print(ome_type_annotations)
        if ome_type_annotations[i] == "clustering":
            all_clustering_ome_consensus_list_of_list_dict[ome.name] = consensus_list_of_lists
            censensus_out_annotations_dict[ome.name] = consensus_out_list
        all_consensus_out_tabels.append(consensus_out_list)
        consensus_group_vect = np.array(consensus_out_list)[:,1].tolist()
        consensus_group_vect_list_int = list(map(int, deepcopy(consensus_group_vect)))

        ## log the results in the dictionary
        consensus_type_dict[ome.name] = {"ome_group_probs":ome_group_probs,
                                         "consensus_group_labels":consensus_group_labels,
                                         "consensus_out_list":consensus_out_list,
                                         "consensus_group_vect_list_int":consensus_group_vect_list_int}

        ome.do_stats(feat_select_labels, temp_out_dir, alpha = alpha, processes = processes)
        # print(feat_select_labels)
        # print(consensus_group_vect)
        ## do the same statistical analyses as before, but with the updated consensus groups
        temp_out_dir_types = process_dir(temp_out_dir + 'consensus_groups')
        ome.do_stats(consensus_group_vect_list_int, temp_out_dir_types, alpha = alpha, processes = processes, prepend_str = "consensus_group_")
        print('\n\n')

    ## TODO
    ## write the table that hosts the final group to consensus group annotations
    # use all_clustering_ome_consensus_list_of_list_dict
    write_final_cluster_to_consensus_group_mapping_file(all_clustering_ome_consensus_list_of_list_dict, out_dir)

    ## TODO
    ## write the sample_wise level annotations of final groups and consensus groups
    # use censensus_out_annotations_dict
    write_sample_level_final_and_consensus_group_annotations(meta_ome.label_pairs, censensus_out_annotations_dict, out_dir)

    compare_consensus_omes(consensus_type_dict, cluster_ome_names, test_ome_names, out_dir)
    get_test_ome_differences_by_consensus_goups(out_dir, 
                                                consensus_type_dict,
                                                alpha,
                                                test_cat = test_cat,
                                                test_num = test_num,
                                                processes = processes)
    return


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
        '-test_cat','-tc',
        default=[],
        dest='test_cat',
        nargs='*',
        type=str)

    parser.add_argument(
        '-test_num','-tn',
        default=[],
        dest='test_num',
        nargs='*',
        type=str)

    parser.add_argument(
        '-processes', '-p',
        help="how many processes to use for anti-correlation based feature selection",
        default = 1,
        type=int)

    parser.add_argument(
        '-bin_size', '-bs',
        help="how many variables should be clumped together when getting the correlation matrix? Default = 5000",
        default = 5000,
        type=int)


    parser.add_argument(
        '-mem_per_node', '-mem',
        help="How much memory can each process handle (in GB)? Default = 20Gigs",
        default = 20,
        type=float)


    parser.add_argument(
        '-meta_ome_results','-ome_results','-results',
        dest='meta_ome_file',
        help = "If you already did the clustering & have the this is the 'meta_ome_results.pkl' file, and just want to annotate these results.",
        type=str)

    parser.add_argument(
        '-alpha',
        help = "The cutoff to use for signficance. Default = 0.001. With such high dimentionality as in multi-omics, you should still see plenty of results with this cutoff.",
        type=float,
        default = 0.001)

    parser.add_argument(
        '-one_hot',
        help = "This boolean flag will tell MANAclust to create a boolean 0/1 table of sample annotations for all of the consensus groups. This can be useful for feeding results into other machine learning pipelines",
        action = "store_true",
        default = False)

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
    test_cat_omes, test_num_omes = process_test_omes(test_cat = args.test_cat,
                                                     test_num = args.test_num, 
                                                     missing_str = args.missing_str,
                                                     processes = args.processes, 
                                                     bin_size = args.bin_size, 
                                                     process_mem = args.mem_per_node,
                                                     out_dir = args.out_dir,
                                                     include_subjects = meta_ome.all_subjects)
    analyze_group_differences(meta_ome, 
                              args.out_dir, 
                              args.alpha, 
                              args.processes, 
                              test_cat = test_cat_omes, 
                              test_num = test_num_omes,
                              one_hot = args.one_hot)



###############################################################################

if __name__ == "__main__":
    ## set up the parser
    args = parse_args()
    main(args)

