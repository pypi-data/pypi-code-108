#!/usr/env python3
import os
import sys
import argparse
import numpy as np
import seaborn as sns
import pandas as pd
from sklearn.metrics import mutual_info_score
from sklearn.cluster import AffinityPropagation as ap
#from sklearn.metrics import log_loss
from sklearn.preprocessing import LabelEncoder as label_maker
from sklearn.preprocessing import OneHotEncoder as onehot
from numpy import array
from numpy import argmax
from copy import deepcopy
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from matplotlib import pyplot as plt
from multiprocessing.dummy import Pool as ThreadPool
from sklearn.metrics import pairwise
from scipy.stats import spearmanr as spear
from scipy.stats import rankdata, fisher_exact, chisquare, mode

from bin.common_functions import write_table, read_table, digitize_for_max_info, get_sample_k_lists, correct_pvalues_for_multiple_testing

euc = pairwise.euclidean_distances

##############################################################################

## hyperparameters
threads = 48

##############################################################################

##############################################################################
def get_sd_from_beta(vect,cutoff=1):
    vect = np.array(list(vect)+list(vect*-1))
    m = np.mean(vect)
    s = np.std(vect)
    return(m+s*cutoff)


def one_hot(data):
    values = np.array(data)
    ## catelogue where all of the Nones are
    none_idxs = np.where(values=="MISSING_DATA")[0]
    cat_idxs = np.where(values!="MISSING_DATA")[0]
    integer_encoded = np.zeros((values.shape[0]))
    # integer encode
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values[cat_idxs])
    
    #print(integer_encoded)
    # binary encode
    try:
        onehot_encoder = OneHotEncoder(sparse=False, categories='auto')
    except:
        onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    ## make the final one hot encoded to account for Nones
    #print(onehot_encoded.shape)
    final_one_hot_encoded = np.zeros((values.shape[0],onehot_encoded.shape[1]))
    for i in range(0,cat_idxs.shape[0]):
        temp_idx = cat_idxs[i]
        final_one_hot_encoded[temp_idx] = onehot_encoded[i]
    #print(onehot_encoded)
    return(integer_encoded, final_one_hot_encoded,label_encoder)
##############################################################################
class feature():

    def __init__(self, data_vect, name):
        self.labels = list(data_vect)
        self.label_array = np.array(self.labels)
        self.label_num, self.label_embedding, self.label_encoder = one_hot(data_vect)
        self.name = name

    def get_name(self):
        return(self.name)

    def set_name(self, new_name):
        self.name = new_name

    def get_label_num(self):
        return(self.label_num)

    def get_embedding(self):
        return(self.label_embedding)

    def get_dim(self):
        return(self.get_embedding().shape)

    def get_col_dim(self):
        return(self.get_dim()[1])

    def inflate_embedding(self,col_dim):
        ## check that it's a valid inflation
        if col_dim < self.get_col_dim():
            err_str = 'cannot inflate the embedding for '+self.get_name()+". Orig dim:"+str(self.get_dim())+'. Tried to set it to:'+str(col_dim)
            sys.exit(err_str)
        new_embedding = np.zeros((len(self.labels),col_dim))
        #print(new_embedding)
        for col in range(self.get_col_dim()):
            new_embedding[:,col] = self.label_embedding[:,col]
        #print(new_embedding)
        self.label_embedding = new_embedding

    def __str__(self):
        print_str = "feature object: "+self.get_name()
        print_str += "\n\t"+str(self.get_embedding())
        return(print_str)


##############################################################################
def remove_invarainat_features(in_mat):
    keep_col_vect = [True]*in_mat.shape[1]
    for i in range(1,in_mat.shape[1]):
        ## after removing missing data how many unique values are there?
        feature_name = in_mat[0,i]
        temp_col_entries = in_mat[1:,i]
        temp_col_entries = temp_col_entries[temp_col_entries != "MISSING_DATA"]
        num_unique_values = len(list(set(temp_col_entries)))
        if num_unique_values == 1 or num_unique_values == temp_col_entries.shape[0]:
            keep_col_vect[i]=False
            print('removing:',feature_name,num_unique_values,temp_col_entries)
    print("keeping",np.sum(keep_col_vect)-1,'features that have some variance')
    rm_vect = np.array(-1* (np.array(keep_col_vect,dtype=int)-1),dtype=bool)
    print('removing:',in_mat[0,rm_vect])
    return(in_mat[:,keep_col_vect])


def filter_none_subjects(in_mat):
    if isinstance(in_mat,list):
        in_mat = np.array(in_mat)
    ## get rid of invariant features
    in_mat = remove_invarainat_features(in_mat)

    ## get rid of subjects with all missing data
    
    out_mat = [in_mat[0,:].tolist()]
    all_none_cutoff = in_mat.shape[1]-1
    rm_subject = []
    for i in range(1,in_mat.shape[0]):
        temp_row = in_mat[i,1:]
        if np.sum(np.array(temp_row=="MISSING_DATA",dtype=int))==all_none_cutoff:
            rm_subject.append(in_mat[i,0])
        else:
            out_mat.append(in_mat[i,:].tolist())
    out_mat = np.array(out_mat)
    print("removed subjects:",rm_subject)
    #out_mat = remove_invarainat_features(out_mat)
    return(out_mat)


def get_randome(randome):
        ## make a randomized version of this categorical ome
        ## shuffle up the labels in each feature
        for i in range(1,np.shape(randome)[1]):
            np.random.shuffle(randome[1:,i])
            #randome[1:,i] = np.random.shuffle(randome[1:,i])
        print(randome)
        randome = categorical_ome(randome)
        return(randome)


def get_contingency_table(group_vector_1, group_vector_2, return_ids = False):
    ## check that they're the same length
    if len(group_vector_1)!=len(group_vector_2):
        sys.exit('get_contingency_table got two vectors of differing lengths')
    ## get the sets, their indices, and make the cont table
    if return_ids:
        grp1_set = sorted(list(set(group_vector_1)))
        grp2_set = sorted(list(set(group_vector_2)))
    else:
        grp1_set = set(group_vector_1)
        grp2_set = set(group_vector_2)
    grp1_set_idx_hash = {value:key for key, value in enumerate(grp1_set)}
    grp2_set_idx_hash = {value:key for key, value in enumerate(grp2_set)}
    ## make the cont table axis0=group1, axis1=group2
    cont_table = np.zeros((len(grp1_set), len(grp2_set)))
    for i in range(len(group_vector_1)):
        row = grp1_set_idx_hash[group_vector_1[i]]
        col = grp2_set_idx_hash[group_vector_2[i]]
        cont_table[row,col]+=1
    if not return_ids:
        return(cont_table)
    if return_ids:
        return(cont_table, grp1_set, grp2_set)



def log_loss(y_true, y_pred, eps = 1e-15):
    if not isinstance(y_true, np.ndarray) or not isinstance(y_pred, np.ndarray):
        print("\n\n",y_true,"\n",y_pred,"\n\n")
        print("didn't get arrays for y_true and y_pred")
        return(None)
    if np.shape(y_true)!=np.shape(y_pred):
        sys.exit('y_true and y_pred are not equal shape')
    ## now do the calculation for the log loss
    y_pred = np.clip(y_pred, eps, 1 - eps)
    y_true = np.clip(y_true, eps, 1 - eps)
    ll = np.sum(-y_true*np.log(y_pred) - (1-y_true)*np.log(1-y_pred))
    ## check for a weird result
    if np.isnan(ll) or np.isinf(ll) or np.isneginf(ll):
        print('got a weirdo')
        print(ll)
        sys.exit()
    return(ll)


class categorical_ome():
    """ this class is for any categorical ome """
    def __init__(self, in_mat, path = None, name = None, plot = False):
        ## rows are subjects, columns are features
        if name != None:
            self.name = name
        elif path != None:
            self.name = os.path.splitext(path)[0].split('/')[-1]
            print('\t',self.name)
        else:
            self.name = None
        self.original_mat = filter_none_subjects(in_mat)
        self.randomized_original_mat = deepcopy(self.original_mat)
        self.feature_names = self.original_mat[0,1:]
        self.all_feature_names = deepcopy(self.feature_names)
        self.num_features = self.feature_names.shape[0]
        self.full_cat_data = self.original_mat[1:,1:]
        self.subjects = self.original_mat[1:,0]
        self.num_subjects = np.shape(self.subjects)[0]
        self.plot = plot
        self.all_diff = None
        self.real_mi_mat = None
        self.min_diff = None
        self.max_of_min_diff = None

        self.all_features = []
        for index, temp_feature in enumerate(self.feature_names):
            #print(one_hot(full_cat_data[:,index]))
            self.all_features.append(feature(self.full_cat_data[:,index],temp_feature))

    def get_noise_factor(self,division_factor=1):
        non_zero = self.all_log_loss>1e-10
        #sns.distplot(self.all_log_loss[non_zero])
        #plt.show()
        #plt.clf()
        return(np.min(self.all_log_loss[non_zero]/division_factor))
        #return(np.mean(self.all_log_loss)/division_factor)

    def smooth_log_loss(self,smooth_iters = 1):
        noise_factor = self.get_noise_factor()
        temp_log_loss = self.all_log_loss[:]
        for i in range(smooth_iters):
            temp_log_loss+=np.random.normal(loc=0.0,scale=noise_factor,size=self.all_log_loss.shape)
        self.all_log_loss = temp_log_loss

    def process_cat_ome(self):
        ## go through each feature, finding the highest col_dim
        self.all_col_dim = []
        for f in self.all_features:
            self.all_col_dim.append(f.get_col_dim())


        ## go through each feature, inflating the one hot encoding matrices to enable concatenation
        self.max_col_dim = max(self.all_col_dim)
        print('max embedding dim:',self.max_col_dim)
        for f in self.all_features:
            self.all_col_dim.append(f.inflate_embedding(self.max_col_dim))

        ## make the encoded matrix
        ## dimtions are: [feature,subject,class within feature]
        self.all_encodings = []
        for f in self.all_features:
            #print(f.get_embedding())
            self.all_encodings.append(f.get_embedding())
        self.all_encodings = np.array(self.all_encodings)

        ## get all of the log_loss distances
        self.all_log_loss = np.zeros((self.num_subjects,self.num_subjects))
        ## generate the index pairs for doing the mapping
        index_pairs = []
        for i in range(0,self.num_subjects):
            for j in range(i,self.num_subjects):
                if i!=j:
                    index_pairs.append([i,j])

        #################################################
        ## parallelize the log losses
        print("getting log losses")

        pool = ThreadPool(threads)
        ll_pairs = pool.map(self.get_log_loss,index_pairs)
        pool.close()
        pool.join()

        #print(ll_pairs)
        #print(list(self.all_log_loss))
        print("finished getting log losses. Generating affinity matrix")
        for k in range(0,len(index_pairs)):
            i = index_pairs[k][0]
            j = index_pairs[k][1]
            self.all_log_loss[i,j] = ll_pairs[k]
            self.all_log_loss[j,i] = ll_pairs[k]


        self.smooth_log_loss()

        print(self.all_log_loss)

        ## adjust log loss to accomodate subjects that had no overlapping variables
        print('inf')
        print(np.where(np.isinf(self.all_log_loss)))
        print('neg inf')
        print(np.where(np.isneginf(self.all_log_loss)))
        print('nan')
        print(np.where(np.isnan(self.all_log_loss)))
        none_row, none_col = np.where(self.all_log_loss==None)
        nan_row, nan_col = np.where(np.isnan(self.all_log_loss))
        # for i in range(neg_inf_row.shape[0]):
        #   print(self.get_log_loss([neg_inf_row[i], neg_inf_col[i]], verbose=True))

        mean_log_loss = np.nanmean(self.all_log_loss)
        print(self.all_log_loss[nan_row, nan_col])
        # if nan_row.shape[0] > 0:
        #   for i in range(nan_row.shape[0]):
        #       self.all_log_loss[nan_row[i],nan_col[i]] = mean_log_loss
        # if none_row.shape[0] > 0:
        #   for i in range(none_row.shape[0]):
        #       self.all_log_loss[none_row[i],none_col[i]] = mean_log_loss
        self.all_log_loss[nan_row, nan_col] = mean_log_loss
        self.all_log_loss[none_row, none_col] = mean_log_loss
        print(self.all_log_loss[nan_row, nan_col])

        print('should all be fixed now:')
        print(np.where(np.isinf(self.all_log_loss)))
        print(np.where(np.isneginf(self.all_log_loss)))
        print(np.where(np.isnan(self.all_log_loss)))
        # self.all_spear,dummy = spear(self.all_log_loss)
        # del dummy

        # self.affinity_matrix = -euc(self.all_spear,squared=True)
        self.affinity_matrix = -euc(self.all_log_loss, squared=True)
        # self.affinity_matrix = -1*np.reshape(rankdata(self.affinity_matrix.flatten()),self.affinity_matrix.shape)
        # print(self.affinity_matrix)
        # print(self.affinity_matrix.shape)
        non_diag_indices = ~np.eye(self.affinity_matrix.shape[0],dtype=bool)
        non_diag_max = np.max(self.affinity_matrix[non_diag_indices])
        ## subtracting the negative, so it brings the max up to zero
        self.affinity_matrix[non_diag_indices] -= non_diag_max
        self.affinity_matrix = self.affinity_matrix/(np.min(self.affinity_matrix)/-100)
        print(self.affinity_matrix)
        print(np.min(self.affinity_matrix))

    def filter_out_nones(self,temp_a,temp_b):
        """ this takes in subject a and b & filteres out any features that have missing values """
        #print('looking at a/b')
        #print(temp_a)
        #print(temp_b)
        ## sum across the feature axis to figure out which features are missing a class
        temp_a_sum = np.sum(temp_a,axis=1)
        temp_b_sum = np.sum(temp_b,axis=1)
        ## if either are zero, then don't consider them
        either_non = temp_a_sum * temp_b_sum
        num_features = np.sum(either_non)
        #print(temp_a_sum)
        #print(temp_b_sum)
        #print(either_non)
        #print(num_features)
        ## sum them from both individuals

        mask = np.array(either_non,dtype=bool)
        #print(mask)
        #print(temp_a)
        #print(temp_b)
        masked_temp_a = temp_a[mask,:]
        masked_temp_b = temp_b[mask,:]
        #print(temp_a)
        #print(temp_b)
        # if not isinstance(masked_temp_a,np.ndarray) or not isinstance(masked_temp_b,np.ndarray):
        #   print("found the place where there are non-arrays")
        # print('\n')
        # print(temp_a)
        # print(temp_b)
        # print(masked_temp_a, masked_temp_b)
        # print(num_features)
        return(masked_temp_a, masked_temp_b,num_features)

    def get_log_loss(self, indices,verbose=False):
        #global all_encodings#, all_log_loss
        i, j = indices
        #print(all_encodings[:,i,:])
        #print(all_encodings[:,j,:])
        temp_a = self.all_encodings[:,i,:]
        temp_b = self.all_encodings[:,j,:]

        temp_a_masked, temp_b_masked, num_features = self.filter_out_nones(temp_a,temp_b)
        if num_features==0:
            return(None)
        else:
            ll = log_loss(temp_a_masked,temp_b_masked)/num_features
            return(ll)
        # if verbose:
        #   print(temp_a)
        #   print(temp_b)
        #   print(num_features)
        #   print(temp_a_masked)
        #   print(temp_b_masked)
        #   print(ll)
        #all_log_loss[i,j] = ll
        #all_log_loss[j,i] = ll
    
    def plot_all_and_good_features(self, do_cluster = True, out_dir = None):
        sns.clustermap(self.real_mi_mat,row_cluster = do_cluster, col_cluster = do_cluster)
        plt.show()
        plt.clf()

        sns.clustermap(self.real_mi_mat - self.all_diff[0,:,:], row_cluster = do_cluster, col_cluster = do_cluster)
        plt.show()
        plt.clf()

        sns.clustermap(self.all_diff[0,:,:],row_cluster = do_cluster, col_cluster = do_cluster)
        plt.show()
        plt.clf()

        sns.clustermap(self.min_diff)
        plt.show()
        plt.clf()

        sns.distplot(self.max_of_min_diff)
        plt.show()
        plt.clf()




    def get_good_features(self, rand_iters = 10, percent_better_than_random=0.9, do_plot = False):
        ## first calculate the observed mutual information across all features
        print('getting information for real features')
        self.real_mi_mat = self.get_cross_feature_info()
        temp_original_mat = self.randomized_original_mat[:]
        print('actual original:\n',temp_original_mat)
        #sys.exit()
        ## make rand_iters number of random datasets, catelogueing the mutual
        ## information across each of the features
        self.all_diff = np.zeros((rand_iters,self.num_features,self.num_features))
        for i in range(rand_iters):
            print('\tgetting rand-ome information: iter',i)
            temp_randome = get_randome(self.randomized_original_mat[:])
            temp_mi = temp_randome.get_cross_feature_info()
            self.all_diff[i,:,:] = self.real_mi_mat - temp_mi

        print('actual original:\n',self.original_mat)
        print('new original:\n',self.original_mat)
        print(temp_original_mat == self.original_mat)
        
        ## now get the features that look good!
        num_better_than_random = int(percent_better_than_random * rand_iters)
        self.min_diff = np.min(self.all_diff,axis=0)
        self.max_of_min_diff = np.max(self.min_diff,axis=0)
        self.all_diff_bool = self.all_diff > 0
        self.num_times_pair_better_than_random = np.sum(self.all_diff_bool, axis=0)
        if do_plot:
            self.plot_all_and_good_features()
            
        self.good_feature_indices = np.where(self.max_of_min_diff>0.15)[0]#get_sd_from_beta(self.max_of_min_diff))[0]
        print('\n\nfound',self.good_feature_indices.shape[0],'good features out of',self.max_of_min_diff.shape[0])
        return(categorical_ome(self.original_mat[:,np.array([0]+list(self.good_feature_indices+1),dtype=int)], name = self.name+"_high_info"))
        # sns.clustermap(self.num_times_pair_better_than_random)
        # plt.show()
        # plt.clf()

        #per_feature_avg_signficance = np.mean(self.num_times_pair_better_than_random,percent_better_than_random)


    def get_cross_feature_info(self):
        ## 
        print("\n\ngetting cross feature information:",len(self.all_features),"features")
        feature_index_pairs = []
        for i in range(0,len(self.all_features)):
            for j in range(i,len(self.all_features)):
                if i != j:
                    feature_index_pairs.append([i,j])
        print('\n\n\t\t',len(feature_index_pairs),"comparisons")
        pool = ThreadPool(threads)
        mi_pairs = pool.map(self.cross_feature_mutual_info,feature_index_pairs)
        pool.close()
        pool.join()

        ## log all of the mutual information across pairs of features
        pairwise_mi = np.zeros((self.num_features,self.num_features))
        for k in range(0,len(feature_index_pairs)):
            i = feature_index_pairs[k][0]
            j = feature_index_pairs[k][1]
            pairwise_mi[i,j] = mi_pairs[k]
            pairwise_mi[j,i] = mi_pairs[k]
        return(pairwise_mi)

    def cross_feature_mutual_info(self, indices):
        """Takes in two features & make a cont table & get the mutual information"""
        feat1_idx, feat2_idx = indices
        feat1 = self.all_features[feat1_idx]
        feat2 = self.all_features[feat2_idx]

        if feat1.label_array.shape != feat2.label_array.shape:
            sys.exit("feature dimentions don't match when trying to make cont table")
        else:
            f1_not_missing = np.array(feat1.label_array!="MISSING_DATA", dtype=int)
            f2_not_missing = np.array(feat2.label_array!="MISSING_DATA", dtype=int)
            present_in_both = np.array(f1_not_missing * f2_not_missing, dtype=bool)
            if np.sum(present_in_both)==0:
                ## if there is no overlap in feature presence, then return 0,
                ## because there is no information
                return(0)
            f1_labels = feat1.label_array[present_in_both]
            f2_labels = feat2.label_array[present_in_both]

            # df = pd.DataFrame({"f1":f1_labels,
            #                  "f2":f2_labels})
            # ## get the cross tab frequencies
            # freq = pd.crosstab(index=df["f1"], 
            #                    columns=df["f2"])
            freq = get_contingency_table(f1_labels, f2_labels)
            mi = mutual_info_score(None, None, contingency = freq)
            #print(freq, mi)
        return(mi)


    ############################
    def get_feature_by_group_contingency_table(self, index, labels = None):
        ## if there aren't labels given, assume it's a fully crossed all groups, all labels cont-table
        if labels == None:
            labels = self.sample_k_list_labels

        temp_vect = self.full_cat_data[:,index]
        all_entries = sorted(list(set(temp_vect)))
        #print(all_entries)

        if "MISSING_DATA" in all_entries:
            all_entries_array = np.array(all_entries)
            all_entries = all_entries_array[all_entries_array!="MISSING_DATA"].tolist()
            #print(all_entries)
        else:
            pass

        all_entry_position_dict = {value:key for key, value in enumerate(all_entries)}
        cont_mat = np.zeros((len(labels), len(all_entries)))

        for i in range(len(labels)):
            for j in range(len(labels[i])):
                temp_entry = temp_vect[labels[i][j]]
                #print(temp_entry)
                if temp_entry != "MISSING_DATA":
                    col_idx = all_entry_position_dict[temp_entry]
                    cont_mat[i,col_idx] += 1

        return(cont_mat)


    def single_fisher(self, index):
        #print(index)
        cont_mat = self.get_feature_by_group_contingency_table(index)
        #print(cont_mat)
        stat, p = chisquare(cont_mat, axis = None)
        return([stat, p])


    def get_two_group_chi(self, first, second):
        all_groups = list(set(first+second))
        group_indexes = {value:key for key, value in enumerate(all_groups)}
        cont_table = np.zeros((2,len(all_groups)))
        for i in range(len(first)):
            cont_table[0,group_indexes[first[i]]] += 1
        for i in range(len(second)):
            cont_table[1,group_indexes[second[i]]] += 1
        chi, p = chisquare(cont_table, axis = None)
        return(chi, p)


    def do_pairwise(self, index):
        temp_name = self.feature_names[index]
        temp_data = self.full_cat_data[:,index]
        temp_results = []
        for i in range(0,len(self.sample_k_list_labels)):
            if len(self.sample_k_list_labels[i])>=5:
                for j in range(i,len(self.sample_k_list_labels)):
                    if i!=j:
                        if len(self.sample_k_list_labels[j])>=5:
                            first = temp_data[self.sample_k_list_labels[i]]
                            first = first[np.where(first!="MISSING_DATA")[0]].tolist()
                            second = temp_data[self.sample_k_list_labels[j]]
                            second = second[np.where(second!="MISSING_DATA")[0]].tolist()
                            if len(first)>=5 and len(second)>=5:
                                mode_1 = mode(first)[0][0]
                                mode_2 = mode(second)[0][0]
                                if mode_1 != mode_2:
                                    temp_chi, temp_p = self.get_two_group_chi(first, second)
                                    temp_results.append([temp_name,
                                                         'sample_group_'+str(i),
                                                         'sample_group_'+str(j),
                                                         mode_1,
                                                         mode_2,
                                                         temp_chi,
                                                         temp_p])
        return(temp_results)


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


    def do_stats(self, labels, out_dir, alpha=0.05):
        idx_list = list(range(self.full_cat_data.shape[1]))
        self.sample_k_list_labels = get_sample_k_lists(labels)
        arg_list = []
        for i in idx_list:
            arg_list.append(i)
        pool = ThreadPool(threads)
        global_fishers = pool.map(self.single_fisher,arg_list)
        pool.close()
        pool.join()
        # global_fishers = []
        # for i in arg_list:
        #     global_fishers.append(self.single_fisher(i))
        #     print(global_fishers[-1])
        global_fishers_array = np.array(global_fishers)
        self.statistic = global_fishers_array[:,0]
        self.uncorrected_p = global_fishers_array[:,1]
        self.corrected_p = correct_pvalues_for_multiple_testing(self.uncorrected_p.tolist())
        self.global_sig_indices = np.where(self.corrected_p < alpha)[0]
        print('\tfound',self.global_sig_indices.shape[0] , 'significant differences')

        ## write the results as a table
        feature_names = np.concatenate((np.array(['features']),self.feature_names))
        statistic = np.concatenate((np.array(['chi_statistic']),self.statistic))
        uncorrected_p  = np.concatenate((np.array(['uncorrected_p_value']),self.uncorrected_p))
        corrected_p  = np.concatenate((np.array(['BH_corrected_p_value']),self.corrected_p))
        global_out_table = np.transpose(np.concatenate((feature_names[None,:],statistic[None,:], uncorrected_p[None,:], corrected_p[None,:]), axis = 0))
        write_table(global_out_table,out_dir+self.name+"_global_statistical_differences.tsv")

        print("\tstarting to do protected pairwise analyses")

        pool = ThreadPool(threads)
        pairwise_results = pool.map(self.do_pairwise,self.global_sig_indices)
        pool.close()
        pool.join()

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
        header = np.array(([['feature_name','group_1','group_2','mode_1','mode_2','chi_statistic','uncorrected_p','BH_corrected_p']]))
        final_output = np.concatenate((header, final_output))
        write_table(final_output,out_dir+self.name+"_all_significant_postHocs.tsv")

        return

    ############################

    def plot_heatmaps(self, do_cluster=True, out_dir = None):
        ## plot the log loss


        sns.clustermap(self.all_log_loss,row_cluster = do_cluster, col_cluster = do_cluster)
        plt.show()
        plt.clf()


        # sns.clustermap(self.real_mi_mat,row_cluster = do_cluster, col_cluster = do_cluster)
        # plt.show()
        # plt.clf()

        # sns.clustermap(self.real_mi_mat - self.all_diff[0,:,:],row_cluster = do_cluster, col_cluster = do_cluster)
        # plt.show()
        # plt.clf()

        # sns.clustermap(self.all_diff[0,:,:],row_cluster = do_cluster, col_cluster = do_cluster)
        # plt.show()
        # plt.clf()

        # sns.clustermap(self.min_diff)
        # plt.show()
        # plt.clf()

        # sns.distplot(self.max_of_min_diff)
        # plt.show()
        # plt.clf()

        # sns.clustermap(self.all_log_loss,row_cluster = do_cluster, col_cluster = do_cluster)
        # plt.show()
        # plt.clf()
        

        return


##############################################################################

##############################################################################
def parse_args(args):
    ##########################################################################
    parser = argparse.ArgumentParser()

    ## global arguments
    parser.add_argument(
        '-infile','-in','-i','-input',
        dest='infile',
        nargs='+',
        type=str)

    parser.add_argument(
            '-missing_data','-missing','-md','-ms',
            dest='missing_str',
            help = "The string that should be interpreted as missing data. (Case sensitive)",
            default = "NA",
            type=str)

    parser.add_argument(
            '-do_clust',
            dest='clust',
            help='if you want to do ap clustering here directly',
            action='store_true')

    parser.add_argument(
            '-plot',
            dest='plot',
            help='if you want to make some plots',
            action='store_true')

    args = parser.parse_args()
    return(args)
##############################################################################
## process the input file
def get_in_mat(infile,missing_str):
    in_mat = read_table(infile)
    in_mat = digitize_for_max_info(in_mat)
    for index, row in enumerate(in_mat):
        for idx2, element in enumerate(row):
            if row[idx2] == missing_str:
                row[idx2] = "MISSING_DATA"
        in_mat[index] = row
    return(np.array(in_mat))


def do_clust(cat_ome):
    am = cat_ome.affinity_matrix
    af = ap(preference = np.min(am,axis=1),affinity="precomputed").fit(am)
    labels = af.labels_
    for idx, subject in enumerate(cat_ome.subjects):
        print(cat_ome.subjects[idx]+'\t'+str(labels[idx]))



##############################################################################
## be able to do it for more than one cat ome
def do_cat_ome(infile,missing_str, do_cluster = True, plot = False, clust = False):
    in_mat = get_in_mat(infile, missing_str)


    ## test with low none input
    cat_ome = categorical_ome(in_mat, path = infile)
    important_cat_ome = cat_ome.get_good_features(do_plot = plot)

    print("high info mat:",important_cat_ome.original_mat.shape)
    print(important_cat_ome.original_mat)
    cat_ome.process_cat_ome()
    important_cat_ome.process_cat_ome()


    if plot:
        important_cat_ome.plot_heatmaps()


    # if plot:
    #     print('plotting original')
    #     plot_stuff(cat_ome)

    #     print('plotting high info')
    #     plot_stuff(important_cat_ome)

    if clust:
        print("\n\n\n\ndoing clustering on full mat")
        do_clust(cat_ome)
        print("\n\n\n\ndoing clustering on important mat")
        do_clust(important_cat_ome)

    return(cat_ome, important_cat_ome)

def do_all_cat_omes(infile_list, missing_str, plot = False):
    all_full_cat_omes = []
    all_cat_omes = []
    for infile in infile_list:
        temp_full_cat_ome, temp_important_cat_ome = do_cat_ome(infile, missing_str, plot = plot)
        all_full_cat_omes.append(temp_full_cat_ome)
        all_cat_omes.append(temp_important_cat_ome)
    return(all_full_cat_omes, all_cat_omes)


##############################################################################

if __name__ == "__main__":
    ## set up the parser
    args = parse_args(sys.argv)
    all_full_cat_omes, all_cat_omes = do_all_cat_omes(args.infile, args.missing_str, plot = args.plot)
    # if args.plot:
    #     for cat in all_cat_omes:
    #         cat.plot_heatmaps()

