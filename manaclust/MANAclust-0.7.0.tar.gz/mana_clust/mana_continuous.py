#!/usr/env python3
import os
import sys
import h5py
import argparse
import numpy as np
import seaborn as sns
import pandas as pd
import scipy
from time import time
from math import ceil
from copy import deepcopy
from statistics import mean, stdev
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
import multiprocessing
from sklearn.metrics import pairwise
from scipy.stats import spearmanr as spear
from scipy.stats import pearsonr
from scipy.stats import rankdata
from scipy.stats import mstats_basic
from scipy.stats.mstats import f_oneway as aov
from scipy.stats import ttest_ind as ttest

from mana_clust.common_functions import read_table, write_table, correct_pvalues_for_multiple_testing, get_sample_k_lists, process_dir

euc = pairwise.euclidean_distances

threads = multiprocessing.cpu_count()



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
    rs = np.array(np.corrcoef(ar, br, rowvar=axisout), dtype = np.float16)
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
    vect = np.array(vect,dtype = np.float32)
    temp_max = np.max(vect)
    temp_min = np.min(vect)
    print('min:',temp_min)
    print('max:',temp_max)
    vect = np.nan_to_num(vect)
    temp_max = np.max(vect)
    temp_min = np.min(vect)
    print('min:',temp_min)
    print('max:',temp_max)
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
    vect = np.clip(vect, -1, 1)
    temp_max = np.max(vect)
    temp_min = np.min(vect)
    print('min:',temp_min)
    print('max:',temp_max)
    print("# inf:",np.sum(np.array(np.isinf(vect),dtype=int)))
    print("# -inf:",np.sum(np.array(np.isneginf(vect),dtype=int)))
    vect = vect[~np.isinf(vect)]
    vect = vect[~np.isneginf(vect)]
    print("# inf:",np.sum(np.array(np.isinf(vect),dtype=int)))
    print("# -inf:",np.sum(np.array(np.isneginf(vect),dtype=int)))
    ## get the mean, & SD
    v_mean = np.mean(vect)
    v_std = np.std(vect)
    cutoff = min([0.98,v_std * z])
    if not positive:
        cutoff *= -1
    print('mean:',v_mean)
    print("StDev:",v_std)
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


class num_ome(object):
    def __init__(self, in_mat, feature_names, sample_names, 
                 name=None, 
                 all_features=False,
                 infile = None, 
                 bin_size = 5000,
                 multiplier = None,
                 processes = 1,
                 force = True, 
                 no_h5 = False,
                 process_mem = None,
                 out_dir = None):
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
        self.out_dir = out_dir
        self.process_mem = process_mem
        self.no_h5 = no_h5
        self.force = force
        self.processes = processes
        self.in_mat = np.nan_to_num(in_mat)
        self.feature_names = feature_names
        self.sample_names = sample_names
        self.subjects = sample_names
        self.infile = infile
        self.bin_size = bin_size
        self.all_features = all_features
        self.all_feature_names = deepcopy(self.all_features)
        ## get the bins
        print(self.in_mat)
        print(in_mat)
        self.get_good_features_and_norm(all_features = self.all_features)
        self.get_affinity_matrix()


    def plot_all_and_good_features(self):
        temp_out_dir = process_dir(os.path.join(self.out_dir,self.name))
        num_row = min([self.in_mat.shape[0], 20000])
        if num_row == self.in_mat.shape[0]:
            sns.clustermap(self.in_mat[:,:])
            plt.savefig(temp_out_dir+self.name+'_sample_of_all_features.png',
                        dpi=600,
                        bbox_inches='tight')
        else:
            sample_row = np.arange(num_row)
            np.random.shuffle(sample_row)
            sample_row = sample_row[:num_row]
            sample_row = np.array(sorted(sample_row.tolist()),dtype = int)
            try:
                sns.clustermap(self.in_mat[sample_row,:])
            except:
                print('something went wrong with plotting all features')
            else:
                plt.savefig(temp_out_dir+self.name+'_sample_of_all_features.png',
                            dpi=600,
                            bbox_inches='tight')
        plt.clf()
        try:
            sns.clustermap(self.in_mat[self.anti_cor_indices,:])
        except:
            print('something went wrong with plotting the selected features')
        else:
            plt.savefig(temp_out_dir+self.name+'_selected_features.png',
                    dpi=600,
                    bbox_inches='tight')
        plt.clf()
        return


    def get_affinity_matrix(self, out_dir = None, do_plot=True):
        ## check if there are any significant features
        if self.anti_cor_indices.shape[0] == 0:
            print("\n no selected indices!")
            self.affinity_matrix = np.zeros((self.sample_names.shape[0],self.sample_names.shape[0]))
        else:
            ## first get the spearman correlations of all samples with each other
            #print('anti-correlated indices:',self.anti_cor_indices)
            #print('subset matrix:\n',self.in_mat[self.anti_cor_indices,:])
            if do_plot and not self.all_features:
                self.plot_all_and_good_features()
            ## if there are more than ten indices, then we can do the spearman correlation first
            ## if not we have to jump right to the -Euc. Dist. Mat
            if self.anti_cor_indices.shape[0] > 10:
                sample_spear = no_p_spear(self.in_mat[self.anti_cor_indices,:])
                self.affinity_matrix = -euc(sample_spear)
            else:
                self.affinity_matrix = -euc(np.transpose(self.in_mat[self.anti_cor_indices,:]))
            #print('spear:\n',sample_spear)
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


    def get_good_features_and_norm(self, all_features = False):
        """ takes the input matrix (features in rows, samples in columns) """
        if not all_features:
            variable_indices = self.get_variant_indices()
            print(self.in_mat)
            self.in_mat = self.in_mat[variable_indices,:]
            print(self.in_mat)
            self.feature_names = self.feature_names[variable_indices]
            if len(variable_indices)<2:
                print("\n\nWE ONLY FOUND",len(variable_indices),"VARIABLE(S) WITH VARIANCE, so we'll just use them all")
        self.bins = self.get_bins(bin_size = self.bin_size)
        
        ## min-max normalize the rows
        print(self.in_mat.shape)
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
        self.spear_out_hdf5[self.bins[i]:self.bins[i+1],self.bins[i]:self.bins[i+1]] = r[:self.bin_size,:self.bin_size]
        ## top right
        self.spear_out_hdf5[self.bins[i]:self.bins[i+1],self.bins[j]:self.bins[j+1]] = r[:self.bin_size,self.bin_size:]
        ## bottom left
        self.spear_out_hdf5[self.bins[j]:self.bins[j+1],self.bins[i]:self.bins[i+1],] = r[self.bin_size:,:self.bin_size]
        ## bottom right
        self.spear_out_hdf5[self.bins[j]:self.bins[j+1],self.bins[j]:self.bins[j+1]] = r[self.bin_size:,self.bin_size:]
        #print(self.spear_out_hdf5 == 0)
        #print(np.sum(self.spear_out_hdf5, axis=1))
        return()


    def add_to_spear_mat(self):
        if self.processes <= 2:
            for i in range(0,(len(self.bins)-1)):
                for j in range(i,(len(self.bins)-1)):
                    if (i!=j) or (len(self.bins) == 2):
                        print('working on',self.bins[i],self.bins[i+1],'vs',self.bins[j],self.bins[j+1])
                        r=no_p_spear(self.in_mat[self.bins[i]:self.bins[i+1],:],self.in_mat[self.bins[j]:self.bins[j+1],:], axis = 1)
                        self.set_spear_bins(r, i, j)
        else:
            ## use Ray package to do multi-processing
            import ray
            if self.process_mem != None:
                ray.init(object_store_memory=int(self.process_mem*1000000000))
            else:
                ray.init()
            @ray.remote
            def get_remote_spear(in_mat1, in_mat2, force = True):
                return(no_p_spear(in_mat1,in_mat2, axis = 1))


            ## set up the intermediate numpy matrix saving directory
            #save_dir = process_dir(self.infile+"_rho_pieces/")
            ## make the i, j pairs
            r_jobs = []
            all_i_j = []
            cur_i_j = []
            ## this will make a list leading to the paths of all of the saved matrices
            r_paths = []
            num_blocks = len(self.bins)
            total_num_block_pair_estimate = (num_blocks**2 / 2 - num_blocks)
            for i in range(0,(len(self.bins)-1)):
                for j in range(i,(len(self.bins)-1)):
                    if (i!=j) or (len(self.bins) == 2):
                        all_i_j.append([i,j])
                        #save_path = save_dir+str(i)+"_"+str(j)+".npy"
                        ## if the number of jobs exceeds the total number of processes, start a new job queue
                        if len(r_jobs) == self.processes:
                            print("submitting jobset for next",len(r_jobs))
                            temp_r_results = ray.get(r_jobs)
                            print("\t~ %",len(all_i_j)/total_num_block_pair_estimate * 100)
                            print("\tfinished gathering results, now we're saving")
                            for w in range(len(cur_i_j)):
                                i, j = cur_i_j[w]
                                start = time()
                                self.set_spear_bins(temp_r_results[w], i, j)
                                print('\t\tsetting bin took:',(time()-start),'seconds')
                            r_jobs = []
                            cur_i_j = []
                        r_jobs.append(get_remote_spear.remote(self.in_mat[self.bins[i]:self.bins[i+1],:], self.in_mat[self.bins[j]:self.bins[j+1],:], force = self.force))
                        cur_i_j.append([i, j])
            
            ## if there are leftover jobs not done yet, do them
            if len(r_jobs) > 0:
                print("submitting jobset for next",len(r_jobs))
                temp_r_results = ray.get(r_jobs)
                print("\t~ %",len(all_i_j)/total_num_block_pair_estimate * 100)
                print("\tfinished gathering results, now we're saving")
                for w in range(len(cur_i_j)):
                    i, j = cur_i_j[w]
                    self.set_spear_bins(temp_r_results[w], i, j)
                
            ray.shutdown()
            
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
        for i in range(0,min([100,len(self.total_neg_cor)])):
            print(self.total_neg_cor[i],
                  self.expected_neg_cor[i],
                  self.sig_neg_cor[i])
        print('\n\nfound',len(self.anti_cor_indices),'anti-correlated features\n\n')
        return()


    def get_anti_cor_features_no_h5(self):
        ## set up the needed variables
        self.total_neg_cor = []
        self.expected_neg_cor = []
        self.sig_neg_cor = []
        self.passing = []
        self.anti_cor_indices = []

        ## set up the ray parallel function
        import ray
        if self.process_mem != None:
            ray.init(object_store_memory=int(self.process_mem*1000000000))
        else:
            ray.init()
        @ray.remote
        def ray_anti_cor(in_mat, indices, expected_prob, multiplier, neg_cutoff):
            temp_total_neg_cor = []
            temp_expected_neg_cor = []
            temp_sig_neg_cor = []
            temp_passing = []
            temp_anti_cor_indices = []
            for idx in indices:
                ## this the pearson correlation coeff of the rank transformed data
                ## note that the rank transform was done prior to parallelization to prevent 
                ## repeatedly computing this
                temp_rhos = np.zeros((in_mat.shape[0]),dtype = np.float16)
                for i in range(in_mat.shape[0]):
                    temp_rhos[i] = no_p_pear(in_mat[idx,:],in_mat[i,:])
                #print(temp_rhos)
                ## filter for the negative correlations
                temp_neg_cor = np.where(temp_rhos<0)[0]
                temp_total_neg_cor.append(len(temp_neg_cor))
                temp_expected_neg_cor.append(temp_total_neg_cor[-1]*expected_prob)
                #print(temp_neg_cor.shape[0],)
                temp_sig_neg_cor.append(len(np.where(temp_rhos<neg_cutoff)[0]))
                index_passes = temp_sig_neg_cor[-1] > temp_expected_neg_cor[-1]*multiplier
                temp_passing.append(index_passes)
                if index_passes:
                    temp_anti_cor_indices.append(idx)
            
            #######################################

            print('\t\tin current process, we found ',len(temp_anti_cor_indices),'anti-correlated indices')
            return(temp_total_neg_cor, 
                   temp_expected_neg_cor,
                   temp_sig_neg_cor,
                   temp_passing,
                   temp_anti_cor_indices)

        ## set up the ray jobs
        print('rank transforming for spearman calc')
        temp_in_mat_ranked = np.apply_along_axis(rankdata, 1, self.in_mat)
        ## decrease size as much as possible
        max_ranked = np.max(temp_in_mat_ranked)
        if max_ranked <= 255:
            print('converting ranked matrix to uint8')
            temp_in_mat_ranked = np.array(temp_in_mat_ranked, dtype = np.uint8)
        elif max_ranked <= 65535:
            print('converting ranked matrix to uint16')
            temp_in_mat_ranked = np.array(temp_in_mat_ranked, dtype = np.uint16)
        elif max_ranked <= 4294967295:
            print('converting ranked matrix to uint32')
            temp_in_mat_ranked = np.array(temp_in_mat_ranked, dtype = np.uint32)
        else:
            print('converting ranked matrix to uint64')
            temp_in_mat_ranked = np.array(temp_in_mat_ranked, dtype = np.uint64)


        ## put the matrix in shared memory 
        ray_in_mat = ray.put(temp_in_mat_ranked)
        process_lines = self.get_process_lines(list(range(self.in_mat.shape[0])), self.processes)
        r_jobs = []
        for temp_indices in process_lines:
            #r_jobs.append(ray_anti_cor.remote(ray_in_mat, temp_indices, self.expected_prob, self.multiplier, self.neg_cutoff))
            r_jobs.append(ray_anti_cor.remote(temp_in_mat_ranked, temp_indices, self.expected_prob, self.multiplier, self.neg_cutoff))

        ## execute and collate
        print('executing parallel anti-correlation based feature selection')
        all_results = ray.get(r_jobs)
        ray.shutdown()
        

        for result in all_results:
            self.total_neg_cor += result[0]
            self.expected_neg_cor += result[1]
            self.sig_neg_cor += result[2]
            self.passing += result[3]
            self.anti_cor_indices += result[4]

        print('\n\nfound',len(self.anti_cor_indices),'anti-correlated features\n\n')

        # self.total_neg_cor = np.array()
        # self.expected_neg_cor = np.array()
        # self.sig_neg_cor = np.array()
        # self.passing = np.array()
        self.anti_cor_indices = np.array(self.anti_cor_indices)

        return


    def get_anti_cor_feature_mat(self):
        ## get the full spearman matrix
        ## first set up the hdf5 file to take in the spearman values
        if self.no_h5 and self.processes >2:
            ## first make dummy variables so there aren't any errors later
            self.hdf5_spear_out_file = None
            self.spear_f = None
            self.spear_out_hdf5 = None
            self.get_anti_cor_features_no_h5()
            return()
        else:
            if self.no_h5:
                print('-no_h5 requires >=3 processes - defaulting to h5 non-parallel')
            start = time()
            self.make_spearman_out()

            ## then populate it 
            self.add_to_spear_mat()

            ## get the total number of negative correlations
            ## and get the total number less than the cutoff of these negatives
            self.get_anti_cor_features()

            ## don't forget to close the spearman file when you're done with it
            self.spear_f.close()
        return()


    def get_anti_correlated_features(self, cutoff_multiplier = 15, min_num_features = 20):
        print('original in mat shape:',self.in_mat.shape)
        if self.in_mat.shape[0] > min_num_features:
            ## get the bootstrap shuffled null distribution
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
            start = time()
            self.get_anti_cor_feature_mat()
            print('\n\nFinished feature selection\n\n',(time()-start)/60,"minutes\n\n")
            #sys.exit()
        else:
            print("not enough variables to do feature selection - skipping with this dataset.")
            self.anti_cor_indices = np.arange(self.in_mat.shape[0])
            print('in mat shape:',self.in_mat.shape)
        return(self.anti_cor_indices)


    def single_anova(self, idx):
        list_of_group_values=[]
        for group in range(0,len(self.sample_k_list_labels)):
            if len(self.sample_k_list_labels[group]) > 0:
                list_of_group_values.append(self.in_mat[idx,self.sample_k_list_labels[group]])
        return(list(aov(*list_of_group_values)))


    def summarize_pairwise_group_differences(self, final_output, out_dir, prepend_str = "sample_group_"):
        num_diff_mat = np.zeros((len(self.sample_k_list_labels),len(self.sample_k_list_labels)))
        group_names = []
        for i in range(len(self.sample_k_list_labels)):
            group_names.append(prepend_str+str(i))
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
        return


    def do_pairwise(self, index):
        prepend_str = self.temp_prepend
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
                                                 prepend_str+str(i),
                                                 prepend_str+str(j),
                                                 mean_1,
                                                 mean_2,
                                                 temp_t,
                                                 temp_p])
        return(temp_results)


    def get_process_lines(self, line_vect, processes):
        ## figure out how many lines each process should get
        num_lines_per_process = max([1,ceil((len(line_vect)+1) / processes)])
        print("\twe're going to be doing ~", num_lines_per_process, "lines per process")
        process_lines = [[]]## this is a list that has which lines each process is going to work on
        for i in range(len(line_vect)):
            if len(process_lines[-1]) == num_lines_per_process:
                process_lines.append([])
            process_lines[-1].append(line_vect[i])
        # print('input processes:',processes)
        # print('using processes:',len(process_lines))
        # for process in process_lines:
        #     print(process)
        # print(line_vect)
        return(process_lines)


    def do_parallel_pairwise(self, processes, prepend_str = "sample_group_"):
        process_lines = self.get_process_lines(self.global_sig_indices, processes)
        print('initializing parallel pairwise comparisons on globally significant results')

        import ray
        if self.process_mem != None:
            ray.init(object_store_memory=int(self.process_mem*1000000000))
        else:
            ray.init()
        @ray.remote
        def ray_do_pairwise(indices, in_mat_full, feature_names, sample_k_list_labels, prepend_str = "sample_group_"):
            ## in_mat is the matrix of the subset of significant indices going to this processes
            in_mat = in_mat_full[np.array(indices),:]
            temp_results = []
            for i in range(0,len(indices)):
                index = indices[i]
                temp_name = feature_names[index]
                temp_data = in_mat[i,:]
                for i in range(0,len(sample_k_list_labels)):
                    if len(sample_k_list_labels[i])!=0:
                        for j in range(i,len(sample_k_list_labels)):
                            if i!=j:
                                if len(sample_k_list_labels[j])!=0:
                                    first = temp_data[sample_k_list_labels[i]].tolist()
                                    mean_1 = np.mean(temp_data[sample_k_list_labels[i]])
                                    second = temp_data[sample_k_list_labels[j]].tolist()
                                    mean_2 = np.mean(temp_data[sample_k_list_labels[j]])
                                    temp_t, temp_p = ttest(first, second, equal_var = False)
                                    temp_results.append([temp_name,
                                                         prepend_str+str(i),
                                                         prepend_str+str(j),
                                                         mean_1,
                                                         mean_2,
                                                         temp_t,
                                                         temp_p])
            return(temp_results)

        ## now we'll start the processes
        ray_in_mat = ray.put(self.in_mat)
        r_jobs = []
        for i in range(len(process_lines)):
            ## first get the expression subset
            print('pairwise process #',i)
            if len(process_lines[i]) > 0:
                print('\t',process_lines[i][0],'through',process_lines[i][-1])
                r_jobs.append(ray_do_pairwise.remote(indices = process_lines[i], 
                                                     in_mat_full = ray_in_mat, 
                                                     feature_names = self.feature_names,
                                                     sample_k_list_labels = self.sample_k_list_labels,
                                                     prepend_str = prepend_str))
        print('\n\ninitializing parallel pairwise comparisons\n')
        all_process_aov_results = ray.get(r_jobs)
        ray.shutdown()
        ## now we have to reorganize 
        print('finished getting the parallel pairwise comparisons: collating results')
        final_results = []
        for i in range(len(all_process_aov_results)):
            final_results += all_process_aov_results[i]
        final_results = np.array(final_results)
        return(final_results)


    def ray_aov(self, processes):
        ## use Ray package to do multi-processing
        import ray
        if self.process_mem != None:
            ray.init(object_store_memory=int(self.process_mem*1000000000))
        else:
            ray.init()
        @ray.remote
        def get_ray_aov(in_mat, sample_k_list_labels):
            temp_out_results = []
            for idx in range(in_mat.shape[0]):
                list_of_group_values=[]
                for group in range(0,len(sample_k_list_labels)):
                    if len(sample_k_list_labels[group]) > 0:
                        list_of_group_values.append(in_mat[idx,sample_k_list_labels[group]])
                temp_out_results.append(list(aov(*list_of_group_values)))
            return(temp_out_results)

        process_lines = self.get_process_lines(list(range(self.in_mat.shape[0])), processes)

        ## now we'll start the processes
        r_jobs = []
        for i in range(len(process_lines)):
            ## first get the expression subset
            if i != len(process_lines)-1:
                print('process #',i)
                print('\t',process_lines[i][0],'through',process_lines[i][-1])
                temp_mat = self.in_mat[process_lines[i][0]:process_lines[i][-1]+1,:]
                print(temp_mat.shape)
                r_jobs.append(get_ray_aov.remote(temp_mat, self.sample_k_list_labels))
            else:
                print('last process #',i)
                print('\t',process_lines[i][0],'through',self.in_mat.shape[0]-1)
                temp_mat = self.in_mat[process_lines[i][0]:,:]
                print(temp_mat.shape)
                r_jobs.append(get_ray_aov.remote(temp_mat, self.sample_k_list_labels))
        print('\n\ninitializing parallel anovas\n')
        all_process_aov_results = ray.get(r_jobs)
        ray.shutdown()
        ## now we have to reorganize 
        print('finished getting the parallel anovas: collating results')
        final_aov_results = []
        for i in range(len(all_process_aov_results)):
            print('\t\t\t','in process',i,'we have',len(all_process_aov_results[i]), 'results logged')
            for j in range(len(all_process_aov_results[i])):
                final_aov_results.append(all_process_aov_results[i][j])
                #print(final_aov_results[-1])
        print('\t\t in final aov results we have',len(final_aov_results),'results')
        return(final_aov_results)


    def do_stats(self, labels, out_dir, alpha = 0.05, processes = 1, prepend_str = "sample_group_"):
        print(self.all_features)
        print("starting to do the statistics for",self.name)
        idx_list = list(range(self.in_mat.shape[0]))
        self.sample_k_list_labels = get_sample_k_lists(labels)
        arg_list = []
        for i in idx_list:
            arg_list.append(i)

        if processes <= 2:
            ## get the global statistics
            pool = ThreadPool(threads)
            global_aov = pool.map(self.single_anova,arg_list)
            pool.close()
            pool.join()
        else:
            ## this means that we're doing ray parallelization
            global_aov = self.ray_aov(processes)


        ## correct p-values
        global_aov_array = np.array(global_aov)
        self.statistic = global_aov_array[:,0]
        self.uncorrected_p = global_aov_array[:,1]
        #print(self.uncorrected_p)
        self.corrected_p = correct_pvalues_for_multiple_testing(self.uncorrected_p)
        self.global_sig_indices = list(np.where(self.corrected_p < alpha)[0])
        self.global_sig_indices += list(np.where(self.corrected_p == 0. )[0])## for whatever reason, zeros weren't coming out...
        self.global_sig_indices = np.array(sorted(list(set(self.global_sig_indices))),dtype = int)
        print('\tfound',self.global_sig_indices.shape[0] , 'significant differences')
        #print('\t\t',self.global_sig_indices)


        ## write the results as a table
        feature_names = np.concatenate((np.array(['features']),self.feature_names))
        statistic = np.concatenate((np.array(['F_statistic']),self.statistic))
        uncorrected_p  = np.concatenate((np.array(['uncorrected_p_value']),self.uncorrected_p))
        corrected_p  = np.concatenate((np.array(['BH_corrected_p_value']),self.corrected_p))
        global_out_table = np.transpose(np.concatenate((feature_names[None,:],statistic[None,:], uncorrected_p[None,:], corrected_p[None,:]), axis = 0))
        write_table(global_out_table,out_dir+self.name+"_global_statistical_differences.tsv")

        print("\tstarting to do protected pairwise analyses")
        self.temp_prepend = prepend_str
        if processes <= 2:
            pool = ThreadPool(threads)
            pairwise_results = pool.map(self.do_pairwise,self.global_sig_indices)
            pool.close()
            pool.join()
            ## reformat and correct p-vals for pairwise results
            while len(pairwise_results)>1:
                pairwise_results[0] = pairwise_results[0]+pairwise_results[1]
                del pairwise_results[1]
            if len(pairwise_results) > 0:
                pairwise_results = np.array(pairwise_results[0])
        else:
            pairwise_results = self.do_parallel_pairwise(processes, prepend_str = prepend_str)

        if len(pairwise_results) > 0:
            temp_uncorrected_p = np.array(pairwise_results[:,-1], dtype = float).tolist()
            temp_corrected_p = correct_pvalues_for_multiple_testing(temp_uncorrected_p)
            ## filter out all of the results that weren't significant
            final_output = []
            for i in range(0,len(temp_corrected_p)):
                if temp_corrected_p[i] < alpha:
                    temp_line = pairwise_results[i,:].tolist()+[temp_corrected_p[i]]
                    final_output.append(temp_line)
        else:
            final_output = []
        
        print('\ttotal of',len(final_output),'signficant post-hocs')

        ## summarize the number of differences between each group
        self.summarize_pairwise_group_differences(final_output, out_dir, prepend_str = prepend_str)

        ## write the summary table
        header = np.array(([['feature_name','group_1','group_2','mean_1','mean_2','t_statistic','uncorrected_p','BH_corrected_p']]))
        if len(final_output)>0:
            final_output = np.concatenate((header, final_output))
        write_table(final_output, out_dir+self.name+"_all_significant_postHocs.tsv")

        return


    def __str__(self):
        out_str = "MANAnum object"
        out_str += "\nObjects of interest:"
        # out_str += "\n\t<object>.add_to_spear_mat: "
        out_str += "\n\t<object>.affinity_matrix: The affinity matrix for this input dataset."
        # out_str += "\n\t<object>.all_feature_names: "
        out_str += "\n\t<object>.all_features: A True/False variable corresponding to whether or not \n\t\tthis input dataset underwent feature selection or not. When all_features is True,\n\t\tthis means feature selection was foregone & all features were included."
        out_str += "\n\t<object>.anti_cor_indices: The indices that correspond to the selected features."
        # out_str += "\n\t<object>.bin_size: "
        # out_str += "\n\t<object>.bins: "
        # out_str += "\n\t<object>.do_pairwise: "
        # out_str += "\n\t<object>.do_parallel_pairwise: "
        # out_str += "\n\t<object>.do_stats: "
        # out_str += "\n\t<object>.expected_neg_cor: "
        # out_str += "\n\t<object>.expected_prob: "
        out_str += "\n\t<object>.feature_names: The name of all features (selected and not). If you want\n\t\tto look at which features were selected do this:\n\t\t\t<object>.feature_names[<object>.anti_cor_indices]"
        # out_str += "\n\t<object>.force: "
        # out_str += "\n\t<object>.get_affinity_matrix: "
        # out_str += "\n\t<object>.get_anti_cor_feature_mat: "
        # out_str += "\n\t<object>.get_anti_cor_features: "
        # out_str += "\n\t<object>.get_anti_cor_features_no_h5: "
        # out_str += "\n\t<object>.get_anti_correlated_features: "
        # out_str += "\n\t<object>.get_bins: "
        # out_str += "\n\t<object>.get_good_features_and_norm: "
        # out_str += "\n\t<object>.get_process_lines: "
        # out_str += "\n\t<object>.get_variant_indices: "
        # out_str += "\n\t<object>.hdf5_spear_out_file: "
        out_str += "\n\t<object>.in_mat: The input dataset matrix"
        out_str += "\n\t<object>.infile: The input file that generated this object."
        # out_str += "\n\t<object>.is_variant_feature: "
        # out_str += "\n\t<object>.make_spearman_out: "
        # out_str += "\n\t<object>.multiplier: "
        out_str += "\n\t<object>.name: The name of this dataset."
        # out_str += "\n\t<object>.neg_cutoff: "
        # out_str += "\n\t<object>.no_h5: "
        # out_str += "\n\t<object>.out_dir: "
        out_str += "\n\t<object>.passing: A True/False vector corresponding to whether or not the\n\t\tgiven feature was selected for clustering."
        # out_str += "\n\t<object>.plot_all_and_good_features: "
        # out_str += "\n\t<object>.process_mem: "
        # out_str += "\n\t<object>.processes: "
        # out_str += "\n\t<object>.ray_aov: "
        # out_str += "\n\t<object>.sample_names: "
        # out_str += "\n\t<object>.set_spear_bins: "
        # out_str += "\n\t<object>.sig_neg_cor: "
        # out_str += "\n\t<object>.single_anova: "
        out_str += "\n\t<object>.subjects: All Subject IDs"
        # out_str += "\n\t<object>.summarize_pairwise_group_differences: "
        # out_str += "\n\t<object>.total_neg_cor: "
        return(out_str)

    def __repr__(self):
        #return("ap_obj('""')")
        return("MANAclust numeric_ome object")



########################################################################
def filter_num_subjects(in_mat_full, include_subjects):
    print("Filtering numeric dataset for appropriate subjects:",in_mat_full.shape)
    rm_col = []
    for i in range(1,in_mat_full.shape[1]):
        if in_mat_full[0,i] not in include_subjects:
            rm_col.append(i)
    out_mat = np.delete(in_mat_full, rm_col, axis = 1)
    print(out_mat.shape)
    return(out_mat)


def process_data_file(in_path, dtype = np.float32, include_subjects = None):
    in_mat_full = np.array(read_table(in_path))
    if include_subjects is not None:
        in_mat_full = filter_num_subjects(in_mat_full, include_subjects)
    in_mat = np.array(in_mat_full[1:,1:],dtype=dtype)
    subjects = in_mat_full[0,1:]
    feature_names = in_mat_full[1:,0]
    return(in_mat, feature_names, subjects)


def do_all_numeric_omes(infile_list, processes = 1, bin_size = 5000, force = True, no_h5 = False, process_mem = None, out_dir = None):
    all_num_omes_full = []
    all_num_omes = []
    for infile in infile_list:
        in_mat, feature_names, subjects = process_data_file(infile)
        if subjects.shape[0]==0:
            print("\n\n\n","WARNING: WE DIDN'T FIND ANY MATCHING SUBJECT IDS IN:",infile,"\n")
            print("try checking the subject IDs or whether the input file needs to be transposed")
        all_num_omes.append(num_ome(in_mat, feature_names, subjects, infile = infile, processes = processes, bin_size = bin_size, force = force, no_h5 = no_h5, process_mem = process_mem, out_dir = out_dir))
        all_num_omes_full.append(num_ome(in_mat, feature_names, subjects, all_features=True, infile = infile, processes = processes, bin_size = bin_size, process_mem = process_mem, out_dir = out_dir))
    return(all_num_omes_full, all_num_omes)


def parse_args():
    parser = argparse.ArgumentParser()

    ## global arguments
    parser.add_argument(
        '-infile','-in','-i','-input',
        dest='infile',
        nargs='+',
        type=str)

    parser.add_argument(
        '-processes','-p',
        dest='processes',
        default = 1,
        type=int)

    parser.add_argument(
        '-store_16bit',
        help="If you need to save on memory, try storing the numeric omes as 16 bit floating points rather than 32 bit. Be warned that this might cause some errors down the line though. If not, you're good to go.",
        action='store_true')

    args = parser.parse_args()
    return(args)


if __name__ == "__main__":
    
    args = parse_args()
    if args.store_16bit:
        all_numeric_omes_full, all_numeric_omes = do_all_numeric_omes(args.infile, processes = args.processes, dtype=np.float16, process_mem = args.process_mem)
    else:
        all_numeric_omes_full, all_numeric_omes = do_all_numeric_omes(args.infile, processes = args.processes, process_mem = args.process_mem)
    # for ome in all_numeric_omes:
    #     ome.plot_all_and_good_features()
    
