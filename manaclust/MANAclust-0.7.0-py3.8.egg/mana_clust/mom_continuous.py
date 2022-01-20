#!/usr/env python3
import os
import sys
import h5py
import argparse
import numpy as np
import seaborn as sns
import pandas as pd
import scipy
from copy import deepcopy
from sklearn.metrics import mutual_info_score
from sklearn.cluster import AffinityPropagation as ap
from sklearn.metrics import log_loss
from sklearn.preprocessing import LabelEncoder as label_maker
from sklearn.preprocessing import OneHotEncoder as onehot
from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from matplotlib import pyplot as plt
from multiprocessing.dummy import Pool as ThreadPool
from sklearn.metrics import pairwise
from scipy.stats import spearmanr as spear
from scipy.stats import pearsonr
from bin.common_functions import read_table 
from scipy.stats import rankdata
from scipy.stats import mstats_basic
from scipy.stats.mstats import f_oneway as aov
from scipy.stats import ttest_ind as ttest

from bin.common_functions import write_table, correct_pvalues_for_multiple_testing, get_sample_k_lists

euc = pairwise.euclidean_distances


threads = 48



def _chk_asarray(a, axis):
    if axis is None:
        a = np.ravel(a)
        outaxis = 0
    else:
        a = np.asarray(a)
        outaxis = axis
    if a.ndim == 0:
        a = np.atleast_1d(a)
    return a, outaxis


def _contains_nan(a, nan_policy='propagate'):
    policies = ['propagate', 'raise', 'omit']
    if nan_policy not in policies:
        raise ValueError("nan_policy must be one of {%s}" %
                         ', '.join("'%s'" % s for s in policies))
    try:
        # Calling np.sum to avoid creating a huge array into memory
        # e.g. np.isnan(a).any()
        with np.errstate(invalid='ignore'):
            contains_nan = np.isnan(np.sum(a))
    except TypeError:
        # If the check cannot be properly performed we fallback to omiting
        # nan values and raising a warning. This can happen when attempting to
        # sum things that are not numbers (e.g. as in the function `mode`).
        contains_nan = False
        nan_policy = 'omit'
        warnings.warn("The input array could not be properly checked for nan "
                      "values. nan values will be ignored.", RuntimeWarning)
    if contains_nan and nan_policy == 'raise':
        raise ValueError("The input contains nan values")
    return contains_nan, nan_policy


def ss(a, axis=0):
    return(np.sum(a*a, axis))


def no_p_pear(x,y):
    x = np.asarray(x)
    y = np.asarray(y)
    n = len(x)
    mx = x.mean()
    my = y.mean()
    xm, ym = x-mx, y-my
    r_num = np.add.reduce(xm * ym)
    r_den = np.sqrt(ss(xm) * ss(ym))
    r = r_num / r_den

    # Presumably, if abs(r) > 1, then it is only some small artifact of floating
    # point arithmetic.
    r = max(min(r, 1.0), -1.0)
    return r



def no_nan_cor(a, axis = 0, method="pearson"):
    """ takes in the matrix and returns the nan omitted pearson correlation """
    if method not in ['pearson', 'spearman']:
        print('method must equal "pearson" or "spearman"')
        sys.exit()
    if axis == 1:
        a=np.transpose(a)
    a_is_num = np.array(~np.isnan(a),dtype=int)
    out_pear_mat = np.zeros((a.shape[0],a.shape[0]))
    np.fill_diagonal(out_pear_mat,1)
    for i in range(a.shape[0]):
        for j in range(i,a.shape[0]):
            if i!=j:
                usable_indices = np.array(a_is_num[i,:] * a_is_num[j,:], dtype=bool)
                if np.sum(usable_indices) > 0:
                    if method == "pearson":
                        temp_r = no_p_pear(a[i,usable_indices], a[j,usable_indices])
                    elif method == "spearman":
                        temp_r = no_p_spear(a[i,usable_indices], a[j,usable_indices])
                    out_pear_mat[i,j] =temp_r
                    out_pear_mat[j,i] =temp_r
    return(out_pear_mat)


def no_p_spear(a, b=None, axis=0, nan_policy='propagate'):
    ## nan_policy = 'omit' doesn't even behave as expected in original distribution...
    a, axisout = _chk_asarray(a, axis)
    contains_nan, nan_policy = _contains_nan(a, nan_policy)
    if contains_nan and nan_policy == 'omit':
        a = np.ma.masked_invalid(a)
        if not isinstance(b, np.ndarray):
            b = np.ma.masked_invalid(b)
        else:
            b = a
        return mstats_basic.spearmanr(a, b, axis)
    if a.size <= 1:
        return SpearmanrResult(np.nan, np.nan)
    ar = np.apply_along_axis(rankdata, axisout, a)
    br = None
    if b is not None:
        b, axisout = _chk_asarray(b, axis)
        contains_nan, nan_policy = _contains_nan(b, nan_policy)
        if contains_nan and nan_policy == 'omit':
            b = ma.masked_invalid(b)
            return mstats_basic.spearmanr(a, b, axis)
        br = np.apply_along_axis(rankdata, axisout, b)
    # n = a.shape[axisout]
    rs = np.corrcoef(ar, br, rowvar=axisout)
    olderr = np.seterr(divide='ignore')  # rs can have elements equal to 1
    # try:
    # clip the small negative values possibly caused by rounding
    # errors before taking the square root
    # t = rs * np.sqrt(((n - 2) / ((rs + 1.0) * (1.0 - rs))).clip(0))
    # finally:
    np.seterr(**olderr)
    print(np.shape(rs), np.min(rs))
    #print('\n\n',np.min(rs),'\n\n')
    if rs.shape == (2, 2):
        return rs[1, 0]
    else:
        return rs





##################################################################
## functions for getting the empirical false positive rate
def get_Z_cutoff(vect,z=3):
    ## this is for a half distribution, so mult by -1 to make it 'normal'
    temp_max = np.max(vect)
    temp_min = np.min(vect)
    if temp_min < 0 and temp_max > 0:
        sys.exit('error in get_Z_cutoff: not split distirbution')
    elif temp_max > 0:
        positive = True
    elif temp_min < 0:
        positive = False
    else:
        sys.exit('all zeros fed into get_Z_cutoff')

    vect = list(vect)
    vect += list(np.array(vect)*-1)
    vect = np.array(vect)
    ## get the mean, & SD
    v_mean = np.mean(vect)
    v_std = np.std(vect)
    cutoff = v_std * z
    if not positive:
        cutoff *= -1
    print('cutoff:',cutoff)
    expected_freq_of_fp = scipy.stats.norm.sf(z)
    return(cutoff, expected_freq_of_fp)


def get_shuffled(num_ome, bin_size = 5000):
    in_mat = num_ome.in_mat
    if in_mat.shape[0] <= bin_size:
        shuff_mat = deepcopy(in_mat)
    else:
        ## get a random sample of the matrix
        neg_control_sample_idxs = np.arange(in_mat.shape[0])
        np.random.shuffle(neg_control_sample_idxs)
        shuff_mat = deepcopy(in_mat[neg_control_sample_idxs[:bin_size],:])
        print(shuff_mat)
    ## now shuffle it
    for i in range(shuff_mat.shape[0]):
        np.random.shuffle(shuff_mat[i,:])
    return(shuff_mat)



############################################################################


class num_ome():
    def __init__(self, in_mat, feature_names, sample_names, 
                 name=None, 
                 all_features=False,
                 infile = None, 
                 bin_size = 5000,
                 multiplier = None):
        if name != None:
            self.name = name
        elif infile != None:
            self.name = os.path.splitext(infile)[0].split('/')[-1]
        else:
            self.name = None
        if multiplier == None:
            ## default is natural log of the number of samples
            ## clipped between 2 and 10
            log = np.log(len(sample_names)) / np.log(3.5)
            self.multiplier = min([10,max([2,log])])
            print("multiplier:",self.multiplier)
        else:
            self.multiplier = multiplier
        self.in_mat = in_mat
        self.feature_names = feature_names
        self.sample_names = sample_names
        self.subjects = sample_names
        self.infile = infile
        self.bin_size = bin_size
        self.all_features = all_features
        self.all_feature_names = deepcopy(self.all_features)
        ## get the bins
        self.get_good_features_and_norm(all_features = self.all_features)
        self.get_affinity_matrix()


    def plot_all_and_good_features(self, out_dir = None):
        sns.clustermap(self.in_mat[:5000,:])
        plt.show()
        plt.clf()
        sns.clustermap(self.in_mat[self.anti_cor_indices,:])
        plt.show()
        plt.clf()
        return


    def get_affinity_matrix(self, out_dir = None, do_plot=False):
        ## check if there are any significant features
        if self.anti_cor_indices.shape[0] == 0:
            self.affinity_matrix = np.zeros((self.sample_names.shape[0],self.sample_names.shape[0]))
        else:
            ## first get the spearman correlations of all samples with each other
            sample_spear = no_p_spear(self.in_mat[self.anti_cor_indices,:])
            self.affinity_matrix = -euc(sample_spear)
            # self.affinity_matrix = -1*np.reshape(rankdata(self.affinity_matrix.flatten()),self.affinity_matrix.shape)
            # print(self.affinity_matrix)
            # print(self.affinity_matrix.shape)
            non_diag_indices = ~np.eye(self.affinity_matrix.shape[0],dtype=bool)
            non_diag_max = np.max(self.affinity_matrix[non_diag_indices])
            ## subtracting the negative, so it brings the max up to zero
            self.affinity_matrix[non_diag_indices] -= non_diag_max
            self.affinity_matrix = self.affinity_matrix/(np.min(self.affinity_matrix)/-100)
            print('affinity matrix:\n',self.affinity_matrix)
            print(np.min(self.affinity_matrix))
            if do_plot:
                self.plot_all_and_good_features()


    def get_good_features_and_norm(self, all_features = False):
        """ takes the input matrix (features in rows, samples in columns) """
        if not all_features:
            variable_indices = self.get_variant_indices()
            self.in_mat = self.in_mat[variable_indices,:]
            self.feature_names = self.feature_names[variable_indices]
        self.bins = self.get_bins(bin_size = self.bin_size)
        
        ## min-max normalize the rows
        self.in_mat -= np.transpose(np.array([np.min(self.in_mat, axis=1)]))
        self.in_mat /= np.transpose(np.array([np.max(self.in_mat, axis=1)]))

        ## set the matrix to only the anti-correlated features
        if not all_features:
            self.get_anti_correlated_features()
            #self.in_mat = self.in_mat[anti_cor_indices,:]
        else:
            self.anti_cor_indices = np.arange(self.in_mat.shape[0])
        return()


    def is_variant_feature(self,i):
        variable = np.sum(self.in_mat[i,:] == self.in_mat[i,0]) < self.in_mat.shape[1]
        return(variable)


    def get_variant_indices(self):
        is_variable = list(map(self.is_variant_feature,list(range((self.in_mat.shape[0])))))
        return(is_variable)


    def get_bins(self, bin_size = 5000):
        print('\n\ngetting bins\n\n')
        total_vars = self.in_mat.shape[0]
        if total_vars/2 <= self.bin_size:
            ## we have to do this because there is a special case where the spearman function returns a different sized matrix if the # bins less than total vars
            print(total_vars/2,self.bin_size)
            self.bin_size = int(total_vars/2)+1
            print('new bin size:',self.bin_size)
        bins = []
        cur_bin = 0
        while cur_bin<total_vars:
            bins.append(min(cur_bin, total_vars))
            cur_bin += self.bin_size
            print(bins[-1])
        bins.append(total_vars)
        return(bins)


    def set_spear_bins(self, r, i, j):
        ## top left
        self.spear_out_hdf5[self.bins[i]:self.bins[i+1],self.bins[i]:self.bins[i+1]] = np.array(r[:self.bin_size,:self.bin_size],dtype=np.float16)
        ## top right
        self.spear_out_hdf5[self.bins[i]:self.bins[i+1],self.bins[j]:self.bins[j+1]] = np.array(r[:self.bin_size,self.bin_size:],dtype=np.float16)
        ## bottom left
        self.spear_out_hdf5[self.bins[j]:self.bins[j+1],self.bins[i]:self.bins[i+1],] = np.array(r[self.bin_size:,:self.bin_size],dtype=np.float16)
        ## bottom right
        self.spear_out_hdf5[self.bins[j]:self.bins[j+1],self.bins[j]:self.bins[j+1]] = np.array(r[self.bin_size:,self.bin_size:],dtype=np.float16)
        #print(self.spear_out_hdf5 == 0)
        #print(np.sum(self.spear_out_hdf5, axis=1))
        return()


    def add_to_spear_mat(self):
        for i in range(0,(len(self.bins)-1)):
            for j in range(i,(len(self.bins)-1)):
                if (i!=j) or (len(self.bins) == 2):
                    print('working on',self.bins[i],self.bins[i+1],'vs',self.bins[j],self.bins[j+1])
                    r=no_p_spear(self.in_mat[self.bins[i]:self.bins[i+1],:],self.in_mat[self.bins[j]:self.bins[j+1],:], axis = 1)
                    self.set_spear_bins(r, i, j)
        return()


    def make_spearman_out(self):
        self.hdf5_spear_out_file = self.infile + "_spearman.hdf5"
        print(self.hdf5_spear_out_file)
        self.spear_f = h5py.File(self.hdf5_spear_out_file, "w")
        self.spear_out_hdf5 = self.spear_f.create_dataset("infile", (self.in_mat.shape[0], self.in_mat.shape[0]), dtype=np.float16)


    def get_anti_cor_features(self):
        self.total_neg_cor = []
        self.expected_neg_cor = []
        self.sig_neg_cor = []
        self.passing = []
        self.anti_cor_indices = []
        for i in range(self.spear_out_hdf5.shape[0]):
            temp_neg_cor = np.where(self.spear_out_hdf5[i,:]<0)[0]
            self.total_neg_cor.append(len(temp_neg_cor))
            self.expected_neg_cor.append(self.total_neg_cor[-1]*self.expected_prob)
            self.sig_neg_cor.append(len(np.where(self.spear_out_hdf5[i,:]<self.neg_cutoff)[0]))
            index_passes = self.sig_neg_cor[-1] > self.expected_neg_cor[-1]*self.multiplier
            self.passing.append(index_passes)
            if index_passes:
                self.anti_cor_indices.append(i)
        self.anti_cor_indices = np.array(self.anti_cor_indices)
        for i in range(0,100):
            print(self.total_neg_cor[i],
                  self.expected_neg_cor[i],
                  self.sig_neg_cor[i])
        print('\n\nfound',len(self.anti_cor_indices),'anti-correlated features\n\n')
        return()


    def get_anti_cor_feature_mat(self):
        ## get the full spearman matrix
        ## first set up the hdf5 file to take in the spearman values
        self.make_spearman_out()

        ## then populate it 
        self.add_to_spear_mat()

        ## get the total number of negative correlations
        ## and get the total number less than the cutoff of these negatives
        self.get_anti_cor_features()

        ## don't forget to close the spearman file when you're done with it
        self.spear_f.close()
        return()


    def get_anti_correlated_features(self, cutoff_multiplier = 15):
        ## get the bootstrap shuffled null distribution
        print('original in mat shape:',self.in_mat.shape)
        rand_mat = get_shuffled(self, bin_size = self.bin_size)
        random_rhos = no_p_spear(rand_mat,axis=1).flatten()
        print(random_rhos)
        print(np.shape(random_rhos))
        random_pos_rhos = random_rhos[random_rhos>0]
        random_neg_rhos = random_rhos[random_rhos<0]
        print(random_neg_rhos)
        self.neg_cutoff, self.expected_prob = get_Z_cutoff(random_neg_rhos)
        #self.expected_number_exceeding = int(self.in_mat.shape[0])/self.expected_freq
        #self.cutoff_for_inclusion = expected_number_exceeding * cutoff_multiplier
        #print("features must have this many negative corrs:",self.cutoff_for_inclusion)
        print('in mat shape:',self.in_mat.shape)
        self.get_anti_cor_feature_mat()
        return(self.anti_cor_indices)


    def single_anova(self, idx):
        list_of_group_values=[]
        for group in range(0,len(self.sample_k_list_labels)):
            if len(self.sample_k_list_labels[group]) > 0:
                list_of_group_values.append(self.in_mat[idx,self.sample_k_list_labels[group]])
        return(list(aov(*list_of_group_values)))


    def summarize_pairwise_group_differences(self, final_output, out_dir):
        num_diff_mat = np.zeros((len(self.sample_k_list_labels),len(self.sample_k_list_labels)))
        group_names = []
        for i in range(len(self.sample_k_list_labels)):
            group_names.append("sample_group_"+str(i))
        group_index_dict = {value:key for key, value in enumerate(group_names)}
        for line in final_output:
            grp1_idx = group_index_dict[line[1]]
            grp2_idx = group_index_dict[line[2]]
            num_diff_mat[grp1_idx, grp2_idx] += 1
            num_diff_mat[grp2_idx, grp1_idx] += 1
        sns.clustermap(num_diff_mat)
        plt.savefig(out_dir+self.name+'_number_different_across_groups.png',
                dpi=600,
                bbox_inches='tight')
        plt.clf()


    def do_pairwise(self, index):
        temp_name = self.feature_names[index]
        temp_data = self.in_mat[index,:]
        temp_results = []
        for i in range(0,len(self.sample_k_list_labels)):
            if len(self.sample_k_list_labels[i])!=0:
                for j in range(i,len(self.sample_k_list_labels)):
                    if i!=j:
                        if len(self.sample_k_list_labels[j])!=0:
                            first = temp_data[self.sample_k_list_labels[i]].tolist()
                            mean_1 = np.mean(temp_data[self.sample_k_list_labels[i]])
                            second = temp_data[self.sample_k_list_labels[j]].tolist()
                            mean_2 = np.mean(temp_data[self.sample_k_list_labels[j]])
                            temp_t, temp_p = ttest(first, second, equal_var = False)
                            temp_results.append([temp_name,
                                                 'sample_group_'+str(i),
                                                 'sample_group_'+str(j),
                                                 mean_1,
                                                 mean_2,
                                                 temp_t,
                                                 temp_p])
        return(temp_results)


    def do_stats(self, labels, out_dir, alpha = 0.05):
        print(self.all_features)
        print("starting to do the statistics for",self.name)
        idx_list = list(range(self.in_mat.shape[0]))
        self.sample_k_list_labels = get_sample_k_lists(labels)
        arg_list = []
        for i in idx_list:
            arg_list.append(i)

        ## get the global statistics
        pool = ThreadPool(threads)
        global_aov = pool.map(self.single_anova,arg_list)
        pool.close()
        pool.join()

        ## correct p-values
        global_aov_array = np.array(global_aov)
        self.statistic = global_aov_array[:,0]
        self.uncorrected_p = global_aov_array[:,1]
        self.corrected_p = correct_pvalues_for_multiple_testing(self.uncorrected_p)
        self.global_sig_indices = np.where(self.corrected_p < alpha)[0]
        print('\tfound',self.global_sig_indices.shape[0] , 'significant differences')


        ## write the results as a table
        feature_names = np.concatenate((np.array(['features']),self.feature_names))
        statistic = np.concatenate((np.array(['F_statistic']),self.statistic))
        uncorrected_p  = np.concatenate((np.array(['uncorrected_p_value']),self.uncorrected_p))
        corrected_p  = np.concatenate((np.array(['BH_corrected_p_value']),self.corrected_p))
        global_out_table = np.transpose(np.concatenate((feature_names[None,:],statistic[None,:], uncorrected_p[None,:], corrected_p[None,:]), axis = 0))
        write_table(global_out_table,out_dir+self.name+"_global_statistical_differences.tsv")

        print("\tstarting to do protected pairwise analyses")
        
        pool = ThreadPool(threads)
        pairwise_results = pool.map(self.do_pairwise,self.global_sig_indices)
        pool.close()
        pool.join()

        ## reformat and correct p-vals for pairwise results
        while len(pairwise_results)>1:
            pairwise_results[0] = pairwise_results[0]+pairwise_results[1]
            del pairwise_results[1]
        pairwise_results = np.array(pairwise_results[0])
        temp_uncorrected_p = np.array(pairwise_results[:,-1], dtype = float).tolist()
        temp_corrected_p = correct_pvalues_for_multiple_testing(temp_uncorrected_p)
        ## filter out all of the results that weren't significant
        final_output = []
        for i in range(0,len(temp_corrected_p)):
            if temp_corrected_p[i] < alpha:
                temp_line = pairwise_results[i,:].tolist()+[temp_corrected_p[i]]
                final_output.append(temp_line)
        
        
        print('\ttotal of',len(final_output),'signficant post-hocs')

        ## summarize the number of differences between each group
        self.summarize_pairwise_group_differences(final_output, out_dir)

        ## write the summary table
        header = np.array(([['feature_name','group_1','group_2','mean_1','mean_2','t_statistic','uncorrected_p','BH_corrected_p']]))
        final_output = np.concatenate((header, final_output))
        write_table(final_output, out_dir+self.name+"_all_significant_postHocs.tsv")

        return



########################################################################
def process_data_file(in_path):
    in_mat_full = np.array(read_table(in_path))
    in_mat = np.array(in_mat_full[1:,1:],dtype=float)
    subjects = in_mat_full[0,1:]
    feature_names = in_mat_full[1:,0]
    return(in_mat, feature_names, subjects)


def do_all_numeric_omes(infile_list):
    all_num_omes_full = []
    all_num_omes = []
    for infile in infile_list:
        in_mat, feature_names, subjects = process_data_file(infile)
        all_num_omes.append(num_ome(in_mat, feature_names, subjects, infile = infile))
        all_num_omes_full.append(num_ome(in_mat, feature_names, subjects, all_features=True, infile = infile))
    return(all_num_omes_full, all_num_omes)


def parse_args():
    parser = argparse.ArgumentParser()

    ## global arguments
    parser.add_argument(
        '-infile','-in','-i','-input',
        dest='infile',
        nargs='+',
        type=str)

    args = parser.parse_args()
    return(args)


if __name__ == "__main__":
    
    args = parse_args()

    all_numeric_omes_full, all_numeric_omes = do_all_numeric_omes(args.infile)
    for ome in all_numeric_omes:
        ome.plot_all_and_good_features()
    
