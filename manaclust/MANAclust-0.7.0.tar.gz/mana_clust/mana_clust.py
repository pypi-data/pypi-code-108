import argparse
import sys
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.cluster import AffinityPropagation as ap
import matplotlib.cm as cm
import umap
import random
import networkx as nx
import community
import pandas as pd
from sklearn.metrics import pairwise
from scipy import stats
from copy import deepcopy
from time import time

from mana_clust.common_functions import write_table, process_dir, get_sample_k_lists, save_dict
from mana_clust.mana_continuous import do_all_numeric_omes, no_p_spear, no_nan_cor, process_data_file, num_ome
from mana_clust.mana_cat import do_all_cat_omes, categorical_ome, get_in_mat
from mana_clust.mana_annotate_results import *
from mana_clust.mana_make_website import make_webpage

euc = pairwise.euclidean_distances


def get_unique_list(in_list):
    subj_list = sorted(list(set(in_list)))
    subject_idx_hash = {value:key for key, value in enumerate(subj_list)}
    return(subj_list, subject_idx_hash)


def process_ome_affinity_matrix(subject_idx_hash, all_subjects, ome):
    re_processed_am = np.zeros((len(all_subjects),len(all_subjects)))
    re_processed_am[:,:] = np.nan
    for i in range(0,len(ome.subjects)):
        subj_1_idx = subject_idx_hash[ome.subjects[i]]
        for j in range(0,len(ome.subjects)):
            subj_2_idx = subject_idx_hash[ome.subjects[j]]
            #print(subj_1_idx)
            #print(subj_2_idx)
            #print(re_processed_am)
            #print(ome.affinity_matrix)
            #print("setting:",re_processed_am[subj_1_idx,subj_2_idx],"to",ome.affinity_matrix[i,j])
            if np.isnan(ome.affinity_matrix[i,j]):
                print('found a nan')
            re_processed_am[subj_1_idx,subj_2_idx] = ome.affinity_matrix[i,j]
    return(re_processed_am)


def do_louvain_clust(am, mask_cutoff):
    ## get the mask
    mask = np.where(am<mask_cutoff)
    ## drop everything below the cutoff to -100
    am /= -mask_cutoff / 100
    ## convert the affinity matrix to weighted edges
    ## first we'll log and non-neg-ify it
    am = am * -1
    #am = np.log(am+1)## this is the log squared Euclidean distance
    ## diagonal should be zero, so we need to add one before inverting it
    am += 1
    ## second, we'll invert it
    am = 1 / am
    ## now mask it to highlight local similarity
    am[mask]=0
    ## set the diagonal back to zero
    ## whether or not to do this is debatable
    ## can't make up my mind right now
    np.fill_diagonal(am,0)
    ## normalize
    am /= np.max(am)
    print(am)
    ## make the graph
    G = nx.from_numpy_matrix(am)
    ## louvain modularity
    partition = community.best_partition(G)
    ## make the output labels
    out_labels = []
    for i in range(am.shape[0]):
        out_labels.append(partition[i])
    return(out_labels)

def do_ap_merger(am, labels):
    label_array = np.array(labels)
    ## check which groups have only one member
    singlet_group_indices = []
    for i in range(np.max(label_array)):
        if np.sum(np.array(label_array==i, dtype = int)) == 1:
            singlet_group_indices.append(i)
    ## if there are no singlet groups, we're good to go
    if len(singlet_group_indices) <= 1:
        return(labels)
    print('\nfound singlets from affinity propagation\n')
    print('\t',singlet_group_indices)
    print('\tdoing merger procedure')
    ## otherwise, regroup the singlets to make sure they belong on their own
    ## make the sample_k_lists
    temp_sample_k_lists = get_sample_k_lists(labels)
    ## then 
    final_sample_k_lists = []
    re_group_original_indices = []
    for i in range(len(temp_sample_k_lists)):
        if i in singlet_group_indices:
            re_group_original_indices += temp_sample_k_lists[i]
        else:
            final_sample_k_lists.append(temp_sample_k_lists[i])
    ## now re-cluster just the singlets
    temp_am = am[re_group_original_indices,:]
    temp_am = temp_am[:,re_group_original_indices]
    temp_labels = do_louvain_clust(temp_am, np.median(am))
    ## these are the indices from the rearranged affinity matrix subset
    ## now we need to re-transform them into their original indices
    intermediate_sample_k_lists = get_sample_k_lists(temp_labels)
    re_group_original_indices = np.array(re_group_original_indices)
    for intermediate in intermediate_sample_k_lists:
        final_sample_k_lists.append(re_group_original_indices[np.array(intermediate)].tolist())
    ## now we need to re-convert them to the linear label vectors
    final_labels = []
    for i in range(len(labels)):
        ## I know this is lazy and inefficient , but it's late
        for j in range(0,len(final_sample_k_lists)):
            if i in final_sample_k_lists[j]:
                final_labels.append(j)
    return(final_labels)


def do_clust(meta_ome, am = None, full = False):
    if type(am) == np.ndarray:
        pass
    else:
        if not full:
            am = meta_ome.affinity_matrix
        else:
            am = meta_ome.affinity_matrix_full
    print(am)
    #labels = do_louvain_clust(am, np.median(am))
    af = ap(preference = np.min(am,axis=1),affinity="precomputed").fit(am)
    labels = af.labels_
    if meta_ome == None:
        return(labels)
    labels = do_ap_merger(am, labels)
    subj_label_pairs = []
    for idx, subject in enumerate(meta_ome.all_subjects):
        subj_label_pairs.append([subject,labels[idx]])
        print(subj_label_pairs[-1][0]+'\t'+str(subj_label_pairs[-1][1]))
    ## make the label dictionary
    label_dict = {subj:group for subj, group in subj_label_pairs}
    return(labels, subj_label_pairs, label_dict)

class cluster_omes(object):
    def __init__(self, cat_omes = None, num_omes = None, out_dir=None, do_plot=False, missing_str = 'NA', processes = 1, bin_size = 5000, force = True, no_h5 = False, store_16bit = False, process_mem = None):
        if cat_omes == None and num_omes == None:
            print("we need to have some kind of omes fed in. Try something like cluster_omes(cat_omes = ['pat_characteristics.txt'], num_omes = ['microbiome.txt','transcriptome.txt'])")
            sys.exit()
        else:
            self.processes = processes
            self.out_dir = out_dir
            self.cat_ome_files = cat_omes
            self.num_ome_files = num_omes
            self.cat_omes_full, self.cat_omes = do_all_cat_omes(cat_omes, missing_str)
            if store_16bit:
                self.num_omes_full, self.num_omes = do_all_numeric_omes(num_omes, processes = self.processes, bin_size = bin_size, force = force, no_h5 = no_h5, dtype = np.float16, process_mem = process_mem, out_dir = out_dir)
            else:
                self.num_omes_full, self.num_omes = do_all_numeric_omes(num_omes, processes = self.processes, bin_size = bin_size, force = force, no_h5 = no_h5, process_mem = process_mem, out_dir = out_dir)
            
            ## get all of the subjects
            self.all_subjects = []
            for ome in self.cat_omes:
                self.all_subjects += ome.subjects.tolist()
            for ome in self.num_omes:
                self.all_subjects += ome.subjects.tolist()
            self.all_subjects, self.subject_idx_hash = get_unique_list(self.all_subjects)

            ############################################
            ## reprocess the FEATUER SELECTED affinity matrices
            self.affinity_matrices = []
            for ome in self.cat_omes:
                self.affinity_matrices.append(process_ome_affinity_matrix(self.subject_idx_hash, self.all_subjects, ome))
            for ome in self.num_omes:
                self.affinity_matrices.append(process_ome_affinity_matrix(self.subject_idx_hash, self.all_subjects, ome))

            ## 3D affinity matrix [ome, subject, subject]
            self.affinity_matrices = np.array(self.affinity_matrices)

            self.affinity_matrix = get_nan_norm_am(self.affinity_matrices)
            # ## get the final affinity matrix
            # self.affinity_matrix = np.nanmean(self.affinity_matrices, axis=0)

            # ## some individual pairs will be missing in both. We therefore calculate the missing value squared euclidean distance
            # ## of the combined affinity matrix
            # #self.affinity_matrix = np.nansum((self.affinity_matrix - self.affinity_matrix[:, None]) ** 2, axis=2)

            # ## Used to replace it with the mean, but the above should be better - as it yeild essentially the same results
            # self.affinity_matrix[np.isnan(self.affinity_matrix)] = np.nanmean(self.affinity_matrices)

            print("\nfinal feature selected affinity matrix:")
            print(self.affinity_matrix)

            ############################################

            ############################################
            ## reprocess the FULL affinity matrices
            self.affinity_matrices_full = []
            for ome in self.cat_omes_full:
                self.affinity_matrices_full.append(process_ome_affinity_matrix(self.subject_idx_hash, self.all_subjects, ome))
            for ome in self.num_omes_full:
                self.affinity_matrices_full.append(process_ome_affinity_matrix(self.subject_idx_hash, self.all_subjects, ome))

            ## 3D affinity matrix [ome, subject, subject]
            self.affinity_matrices_full = np.array(self.affinity_matrices_full)

            self.affinity_matrix_full = get_nan_norm_am(self.affinity_matrices_full)

            # ## get the final affinity matrix
            # self.affinity_matrix_full = np.nanmean(self.affinity_matrices_full, axis=0)

            # ## some individual pairs will be missing in both. We therefore calculate the missing value squared euclidean distance
            # ## of the combined affinity matrix
            # self.affinity_matrix_full[np.isnan(self.affinity_matrix_full)] = np.nanmean(self.affinity_matrices_full)
            # #self.affinity_matrix_full = np.nansum((self.affinity_matrix_full - self.affinity_matrix_full[:, None]) ** 2, axis=2)
            print("\nfinal full affinity matrix:")
            print(self.affinity_matrix_full)
            
            ############################################

            if do_plot:
                print(self.affinity_matrix.shape)
                sns.clustermap(self.affinity_matrix)
                plt.show()
                plt.clf()

                print(self.affinity_matrix_full.shape)
                sns.clustermap(self.affinity_matrix_full)
                plt.show()
                plt.clf()



            self.labels, self.label_pairs, self.label_dict = do_clust(self, full=False)
            self.labels_full, self.label_pairs_full, self.label_dict_full = do_clust(self, full=True)
    def __str__(self):
        out_str = "MANAclust object"
        out_str += "\nObjects of interest:"
        out_str += "\n\t<object>.affinity_matrices: The '3D stack' of all affinity matrices that went\n\t\tinto making the final affinity matrix. These are in the same order as the input,\n\t\twith categorical datasets first, then numeric."
        out_str += "\n\t<object>.affinity_matrices_full: Same as the above, but without feature selection"
        out_str += "\n\t<object>.affinity_matrix: The final merged affinity matrix from which the \n\t\tfinal clusters were determined. Note that the subject IDs\n\t\t(in the same orders as the rows/columns) is in <object>.all_subjects"
        out_str += "\n\t<object>.affinity_matrix_full: Same as the above, but without feature selection"
        out_str += "\n\t<object>.all_subjects: The list of Subject IDs that line up with the affinity matrices."
        out_str += "\n\t<object>.cat_ome_files: The original list of files fed in for clustering."
        out_str += "\n\t<object>.cat_omes: A list of all categorical ome object files that you \n\t\tcan explore, just like this one."
        out_str += "\n\t<object>.cat_omes_full: Same as the above, but without feature selection"
        out_str += "\n\t<object>.label_dict: A dictionary with keys corresponding to subject IDs, and "
        out_str += "\n\t<object>.label_dict_full: Same as the above, but without feature selection"
        # out_str += "\n\t<object>.label_pairs: "
        # out_str += "\n\t<object>.label_pairs_full: Same as the above, but without feature selection"
        out_str += "\n\t<object>.labels: A list of the final cluster IDs \n\t\t(sorted in line with the <object>.all_subjects entries)"
        out_str += "\n\t<object>.labels_full: Same as the above, but without feature selection"
        out_str += "\n\t<object>.num_ome_files: The input files for the numeric omes."
        out_str += "\n\t<object>.num_omes: A list of all categorical ome object files that you \n\t\tcan explore, just like this one."
        out_str += "\n\t<object>.num_omes_full: Same as the above, but without feature selection"
        # out_str += "\n\t<object>.out_dir: "
        out_str += "\n\t<object>.subject_idx_hash: A potentially useful dictionary object, with \n\t\tthe keys corresponding to the subject IDs, returning the index within \n\t\tthe affinity matrix that the subject belongs to."
        return(out_str)

    def __repr__(self):
        #return("ap_obj('""')")
        return("MANAclust meta-ome object")


def quantileNormalize(in_mat):
    df_input = pd.DataFrame(in_mat)
    df = df_input.copy()
    #compute rank
    dic = {}
    for col in df:
        dic.update({col : sorted(df[col])})
    sorted_df = pd.DataFrame(dic)
    rank = sorted_df.mean(axis = 1).tolist()
    #sort
    for col in df:
        t = np.searchsorted(np.sort(df[col]), df[col])
        df[col] = [rank[i] for i in t]
    return np.array(df)

def get_nan_norm_am(am, method = 'pearson'):
    ## go through each affinity matrix, and replace missing values with the median
    ## of each affinity matrix.
    for i in range(am.shape[0]):
        print("getting nan median for am matrix #",i)
        temp_med = np.nanmedian(am[i])
        ## replace the missing values with the median of this affinity matrix
        am[i][np.isnan(am[i])] = temp_med

    ## takes in the 3D affinity matrices & returns the final affinity matrix
    am = np.nanmean(am, axis=0)

    ## renormalize the matrix
    am -= np.max(am[~np.eye(am.shape[0], dtype=bool)])
    am /= -(np.min(am[~np.eye(am.shape[0], dtype=bool)])/100)

    np.fill_diagonal(am,0)


    # ## get the nan omitted correlation matrix
    # am = no_nan_cor(am, method = method)

    # ## get the -Euclidean Distance matrix
    # am = -euc(am)

    ## quantile normalize the matrix ensure that each sample has the same distribution of
    ## affinities. This helps to blunt the effect of different distributions across each
    ## given ome input

    return(am)

    # ## figure out how many acutal comparisons everything has
    # is_numeric_mat = (np.array(np.isnan(am),dtype = int)-1) * -1
    # # sns.clustermap(is_numeric_mat)
    # # plt.show()

    # ## get the average distances
    # new_am = am = -1 * np.nansum((am - am[:, None]) ** 2, axis=2)

    # ## get the number of numeric comparisons for each pair
    # num_comparisons = np.sum(is_numeric_mat * is_numeric_mat[:, None], axis = 2)
    # # sns.clustermap(num_comparisons)
    # # plt.show()
    
    # ## normalize for the number of comparisons
    # new_am /= num_comparisons

    # sns.clustermap(new_am)
    # plt.show()

    #return(new_am)

    # final_am = am[np.isnan(am)] = np.nanmean(am)
    # return(final_am)




##############################################################################
## analysis and writing results

def get_per_ome_labels(subjects, meta_ome):
    feat_labels = []
    labels_full = []
    for subj in subjects:
        feat_labels.append([subj, meta_ome.label_dict[subj]])
        labels_full.append([subj, meta_ome.label_dict_full[subj]])
    return(feat_labels, labels_full)

def write_per_ome_labels(results_dir, meta_ome):
    results_dir = process_dir(results_dir)
    for ome in meta_ome.cat_omes+meta_ome.num_omes:
        feat_labels, full_labels = get_per_ome_labels(ome.subjects, meta_ome)
        temp_out_file = results_dir + ome.name+"_labels.tsv"
        write_table(feat_labels, temp_out_file)
        temp_out_file = results_dir + ome.name+"_labels_full.tsv"
        write_table(full_labels, temp_out_file)
    return()


def prep_ome_for_saving(meta_ome):
    #meta_ome_out = deepcopy(meta_ome)
    for num_ome in meta_ome.num_omes + meta_ome.num_omes_full:
        if 'spear_out_hdf5' in dir(num_ome):
            print('removing hdf5 for saving')
            del num_ome.spear_out_hdf5
            del num_ome.spear_f
    return(meta_ome)


def write_ome_results(results_dir, meta_ome):
    results_dir = process_dir(results_dir)
    write_table(meta_ome.label_pairs, results_dir+'labels_with_feature_selection.tsv')
    write_table(meta_ome.label_pairs_full, results_dir+'labels_without_feature_selection.tsv')
    write_per_ome_labels(results_dir, meta_ome)
    save_dict(prep_ome_for_saving(meta_ome), results_dir+'meta_ome_results.pkl')
    return(results_dir)


def do_am_heatmap(out_file, ome, x_color_dict = None, y_color_dict = None):
    if x_color_dict == None:
        if isinstance(ome,np.ndarray):
            sns.clustermap(ome)
        else:
            sns.clustermap(ome.affinity_matrix)
    else:
        if y_color_dict == None:
            y_color_dict = x_color_dict
        if isinstance(ome,np.ndarray):
            sns.clustermap(ome, col_colors = x_color_dict["color_vector"],  row_colors = y_color_dict["color_vector"])
        else:
            sns.clustermap(ome.affinity_matrix, col_colors = x_color_dict["color_vector"],  row_colors = y_color_dict["color_vector"])
    plt.savefig(out_file,
                dpi=600,
                bbox_inches='tight')
    plt.clf()
    return


def plot_2d(projection, out_plot, dpi=600, color_dict = None, x_ax = '',y_ax = ''):
    global sample_id_hash, sample_k_lists, colors, args, ax, plt, temp
    print("\tPlotting",out_plot)
    sample_k_lists = color_dict["group_index_lists"]
    colors = color_dict["master_color_vect"]
    group_name_list = color_dict["group_names"]
    plt.clf()
    for i in range(0,len(sample_k_lists)):
        #temp_idxs = ids_to_idxs(sample_k_lists[i])
        temp_idxs = sample_k_lists[i]
        print(temp_idxs)
        plt.scatter(projection[temp_idxs,0],projection[temp_idxs,1],label=group_name_list[i],color=colors[i],s=10)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel(x_ax)
    plt.ylabel(y_ax)
    if out_plot != None:
        plt.savefig(out_plot,
            dpi=dpi,
            bbox_inches='tight')
    return()


def get_umap_coords(in_mat):
    print("getting UMAP projection")
    model = umap.UMAP(n_neighbors=5,
                      min_dist=0.3,
                      metric='correlation')
    projection = model.fit_transform(in_mat)
    return(projection)


def plot_umap(out_file, in_mat = None, projection = None, color_dict = None):
    
    # if color_dict == None:
    #     ## just plot in black
    #     color_vector = ['k']*in_mat.shape[0]
    if not isinstance(projection, np.ndarray):
        projection = get_umap_coords(in_mat)

    plot_2d(projection, out_file, color_dict = color_dict, x_ax = 'UMAP1', y_ax = 'UMAP2')

    plt.savefig(out_file,
                dpi=600,
                bbox_inches='tight')
    plt.clf()
    return(projection)



def group_vector_to_color(group_vector):
    print("\nmaking group color vector:\n",group_vector[:5],"...")
    group_set_list = sorted(list(set(group_vector)))
    group_numeric_mapping = {value:key for key, value in enumerate(group_set_list)}
    group_numeric_vector = [group_numeric_mapping[group] for group in group_vector]
    colors = cm.nipy_spectral(np.arange(len(group_set_list))/len(group_set_list))
    group_color_dict = {group:colors[idx] for idx, group in enumerate(group_set_list)}
    color_vector = [group_color_dict[group] for group in group_vector]
    ## make the group_index_lists
    group_index_lists = get_sample_k_lists(group_numeric_vector)
    ## make the dictionary and return it
    full_color_dict = {"group_color_dict":group_color_dict,
                       "color_vector":color_vector,
                       "group_index_lists":group_index_lists,
                       "group_names":group_set_list,
                       "master_color_vect":colors}
    return(full_color_dict)


def plot_ome_results(meta_ome, out_dir, ground_truth_vector = None):
    ## get the colorization for the clustering results
    cluster_color_dict_feature_selected_dict = group_vector_to_color(meta_ome.labels)
    cluster_color_dict_full_dict = group_vector_to_color(meta_ome.labels_full)

    ## if there is a ground truth vector, colorize that as well
    if ground_truth_vector != None:
        ## get the color vector
        ground_truth_color_dict_full_dict = group_vector_to_color(ground_truth_vector)

    out_dir = process_dir(out_dir)
    for ome in meta_ome.cat_omes + meta_ome.num_omes:
        out_png = out_dir+ome.name+"_with_feature_selection.png"
        do_am_heatmap(out_png, ome)

    for ome in meta_ome.cat_omes_full+meta_ome.num_omes_full:
        out_png = out_dir+ome.name+"_without_feature_selection.png"
        do_am_heatmap(out_png, ome)

    do_am_heatmap(out_dir+"final_affinity_matrix_with_feature_selection.png", meta_ome.affinity_matrix, x_color_dict = cluster_color_dict_feature_selected_dict)
    do_am_heatmap(out_dir+"final_affinity_matrix_without_feature_selection.png", meta_ome.affinity_matrix_full, x_color_dict = cluster_color_dict_full_dict)
    if ground_truth_vector != None:
        do_am_heatmap(out_dir+"final_affinity_matrix_with_feature_selection_ground_truth_cols_clust_rows.png", meta_ome.affinity_matrix, x_color_dict = ground_truth_color_dict_full_dict, y_color_dict = cluster_color_dict_feature_selected_dict)
        do_am_heatmap(out_dir+"final_affinity_matrix_without_feature_selection_ground_truth_cols_clust_rows.png", meta_ome.affinity_matrix_full, x_color_dict = ground_truth_color_dict_full_dict, y_color_dict = cluster_color_dict_feature_selected_dict)


    ## do the umap projection with feature selection
    png = out_dir+"final_affinity_matrix_umap_with_feature_selection_clustering.png"
    feature_selected_umap = plot_umap(png, in_mat = meta_ome.affinity_matrix, color_dict = cluster_color_dict_feature_selected_dict)
    if ground_truth_vector != None:
        png = out_dir+"final_affinity_matrix_umap_with_feature_selection_ground_truth.png"
        plot_umap(png, projection = feature_selected_umap, color_dict = ground_truth_color_dict_full_dict)
    
    ## do the umap projection without feature selection
    png = out_dir+"final_affinity_matrix_umap_without_feature_selection_clustering.png"
    feature_selected_umap = plot_umap(png, in_mat = meta_ome.affinity_matrix_full, color_dict = cluster_color_dict_full_dict)
    if ground_truth_vector != None:
        png = out_dir+"final_affinity_matrix_umap_without_feature_selection_ground_truth.png"
        plot_umap(png, projection = feature_selected_umap, color_dict = ground_truth_color_dict_full_dict)

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
        '-no_post',
        dest='do_post_hoc_analyses',
        action='store_false')

    parser.add_argument(
        '-no_plots',
        dest='do_plots',
        action='store_false')

    parser.add_argument(
        '-no_force',
        dest='force',
        help="should we force recomputation of everthing or assume the temp files are correct",
        action='store_false')

    parser.add_argument(
        '-no_h5',
        help="in some scenarios it may be faster (on a cluster), to not store some of the data permanently, to minimize cross-node data transfer when going in parallel. Note that this option also requires parallel (processes >2)",
        action='store_true')


    parser.add_argument(
        '-store_16bit',
        help="If you need to save on memory, try storing the numeric omes as 16 bit floating points rather than 32 bit. Be warned that this might cause some errors down the line though. If not, you're good to go.",
        action='store_true')


    parser.add_argument(
        '-out_dir',
        default = "/home/scott/bin/mana_clust/lib/synthetic_data/",
        type=str)

    parser.add_argument(
        '-alpha',
        help="the cutoff for significance testing. Default = 0.001 - In my experience, this yeilds many good results & cuts down on false positives.",
        default = 0.001,
        type=float)

    parser.add_argument(
        '-processes', '-p',
        help="how many processes to use for anti-correlation based feature selection",
        default = 1,
        type=int)

    parser.add_argument(
        '-mem_per_node', '-mem',
        help="How much memory can each process handle (in GB)? Default = 20Gigs",
        default = 20,
        type=float)

    parser.add_argument(
        '-bin_size', '-bs',
        help="how many variables should be clumped together when getting the correlation matrix? Default = 5000",
        default = 5000,
        type=int)

    parser.add_argument(
        '-one_hot',
        help = "This boolean flag will tell MANAclust to create a boolean 0/1 table of sample annotations for all of the consensus groups. This can be useful for feeding results into other machine learning pipelines",
        action = "store_true",
        default = False)

    parser.add_argument(
        '-seed',
        help="random seed",
        default = 123456789,
        type=int)

    args = parser.parse_args()
    return(args)


def process_test_omes(test_cat = [], 
                      test_num = [], 
                      missing_str = 'NA',
                      processes = 1, 
                      bin_size = 5000, 
                      process_mem = 20,
                      out_dir = None,
                      include_subjects = None):
    ## process the test omes if present
    test_cat_omes = []
    for cat in test_cat:
        print('\n\nprocessing test cat ome:\n',cat)
        test_cat_omes.append(categorical_ome(get_in_mat(cat, missing_str), path=cat, include_subjects = include_subjects))
        test_cat_omes[-1].process_cat_ome()
    test_num_omes = []
    for infile in test_num:
        print('processing test num ome:\n',infile)
        in_mat, feature_names, subjects = process_data_file(infile, include_subjects = include_subjects)
        test_num_omes.append(num_ome(in_mat, feature_names, subjects, all_features=True, infile = infile, processes = processes, bin_size = bin_size, process_mem = process_mem, out_dir = out_dir))
    return(test_cat_omes, test_num_omes)


def mana_clust(out_dir,
               cat = [],
               missing_str = 'NA',
               num = [],
               alpha = 0.001,
               processes = 1,
               bin_size = 5000,
               force = True,
               no_h5 = False,
               mem_per_node = 20,
               do_plots = True,
               do_post_hoc_analyses = True,
               test_cat = [],
               test_num = [],
               seed = 123456789):
    
    ## make create the outdir if it doesn't exist
    args.out_dir = process_dir(args.out_dir)
    
    ## set the seed for reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)

    ## process the meta ome and do the clustering
    meta_ome = cluster_omes(cat_omes = cat, 
                            num_omes = num, 
                            missing_str = missing_str, 
                            processes = processes, 
                            bin_size = bin_size, 
                            force = force, 
                            no_h5 = no_h5, 
                            process_mem = mem_per_node,
                            out_dir = out_dir)
    ## write the results
    write_ome_results(out_dir, meta_ome)
    
    ## make the plots if we need to
    if args.do_plots:
        plot_ome_results(meta_ome, args.out_dir)

    ## if we need to do the post-hoc analyses, do them
    if args.do_post_hoc_analyses:
        ## first process the test omes that weren't used for clustering
        test_cat_omes, test_num_omes = process_test_omes(test_cat = args.test_cat, 
                                                         test_num = args.test_num,
                                                         missing_str = args.missing_str,
                                                         processes = args.processes, 
                                                         bin_size = args.bin_size, 
                                                         process_mem = args.mem_per_node,
                                                         out_dir = args.out_dir,
                                                         include_subjects = meta_ome.all_subjects)
        ## now do all of the analyses
        analyze_group_differences(meta_ome, 
                                  args.out_dir, 
                                  args.alpha, 
                                  args.processes, 
                                  test_cat = test_cat_omes, 
                                  test_num = test_num_omes,
                                  one_hot = args.one_hot)
    make_webpage(out_dir)
    print("\n\n\n",meta_ome)
    return(meta_ome)


def main(args):
    start = time()
    mana_clust(out_dir = args.out_dir,
               cat = args.cat,
               missing_str = args.missing_str,
               num = args.num,
               alpha = args.alpha,
               processes = args.processes,
               bin_size = args.bin_size,
               force = args.force,
               no_h5 = args.no_h5,
               mem_per_node = args.mem_per_node,
               do_plots = args.do_plots,
               do_post_hoc_analyses = args.do_post_hoc_analyses,
               test_cat = args.test_cat,
               test_num = args.test_num,
               seed = args.seed)
    end = time()
    print('\n\nFinished all analyses!\n\nMANAclust took:',(end-start)/60,"minutes\n")



##############################################################################

if __name__ == "__main__":
    ## set up the parser
    args = parse_args()
    
    main(args)

