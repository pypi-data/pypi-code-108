#!/usr/env python3
import os
import sys
import argparse
import numpy as np
import seaborn as sns
import pandas as pd
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

from mana_clust.common_functions import read_table 

euc = pairwise.euclidean_distances

##############################################################################

## hyperparameters
threads = 42


##############################################################################
def get_sd_from_beta(vect,cutoff=1):
	vect = np.array(list(vect)+list(vect*-1))
	m = np.mean(vect)
	s = np.std(vect)
	return(m+s*cutoff)


def one_hot(data):
	values = np.array(data)
	## catelogue where all of the Nones are
	none_idxs = np.where(values==None)[0]
	cat_idxs = np.where(values!=None)[0]
	integer_encoded = np.zeros((values.shape[0]))
	# integer encode
	label_encoder = LabelEncoder()
	integer_encoded = label_encoder.fit_transform(values[cat_idxs])
	
	#print(integer_encoded)
	# binary encode
	onehot_encoder = OneHotEncoder(sparse=False,categories='auto')
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
		temp_col_entries = temp_col_entries[temp_col_entries != None]
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
		if np.sum(np.array(temp_row==None,dtype=int))==all_none_cutoff:
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


class categorical_ome():
	""" this class is for any categorical ome """
	def __init__(self, in_mat, path = None, name = None):
		## rows are subjects, columns are features
		if name != None:
			self.name = name
		elif path != None:
			self.name = os.path.splitext(path)[0]
		else:
			self.name = None
		self.original_mat = filter_none_subjects(in_mat)
		self.randomized_original_mat = filter_none_subjects(in_mat)
		self.feature_names = self.original_mat[0,1:]
		self.num_features = self.feature_names.shape[0]
		self.full_cat_data = self.original_mat[1:,1:]
		self.subjects = self.original_mat[1:,0]
		self.num_subjects = np.shape(self.subjects)[0]

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

		# self.all_spear,dummy = spear(self.all_log_loss)
		# del dummy

		# self.affinity_matrix = -euc(self.all_spear,squared=True)
		self.affinity_matrix = -euc(self.all_log_loss, squared=True)
		self.affinity_matrix = self.affinity_matrix/(np.abs(np.min(self.affinity_matrix)/100))

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
		temp_a = temp_a[mask,:]
		temp_b = temp_b[mask,:]
		#print(temp_a)
		#print(temp_b)
		return(temp_a, temp_b,num_features)

	def get_log_loss(self, indices):
		#global all_encodings#, all_log_loss
		i, j = indices
		#print(all_encodings[:,i,:])
		#print(all_encodings[:,j,:])
		temp_a = self.all_encodings[:,i,:]
		temp_b = self.all_encodings[:,j,:]

		temp_a, temp_b, num_features = self.filter_out_nones(temp_a,temp_b)
		ll = log_loss(temp_a,temp_b)/num_features
		#print(ll)
		#all_log_loss[i,j] = ll
		#all_log_loss[j,i] = ll
		return(ll)

	def get_good_features(self, rand_iters = 10, percent_better_than_random=0.9):
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
		sns.clustermap(self.min_diff)
		plt.show()
		plt.clf()
		sns.distplot(self.max_of_min_diff)
		plt.show()
		plt.clf()
		self.max_of_min_diff
		self.good_feature_indices = np.where(self.max_of_min_diff>0.1)[0]#get_sd_from_beta(self.max_of_min_diff))[0]
		print('\n\nfound',self.good_feature_indices.shape[0],'good features out of',self.max_of_min_diff.shape[0])
		return(categorical_ome(self.original_mat[:,np.array([0]+list(self.good_feature_indices+1),dtype=int)]))
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
			f1_not_missing = np.array(feat1.label_array!=None, dtype=int)
			f2_not_missing = np.array(feat2.label_array!=None, dtype=int)
			present_in_both = np.array(f1_not_missing * f2_not_missing, dtype=bool)
			f1_labels = feat1.label_array[present_in_both]
			f2_labels = feat2.label_array[present_in_both]
			df = pd.DataFrame({"f1":f1_labels,
				               "f2":f2_labels})
			## get the cross tab frequencies
			freq = pd.crosstab(index=df["f1"], 
			                   columns=df["f2"])

			mi = mutual_info_score(None, None, contingency = freq)
			#print(freq, mi)
		return(mi)


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
	for index, row in enumerate(in_mat):
		for idx2, element in enumerate(row):
			if row[idx2] == missing_str:
				row[idx2] = None
		in_mat[index] = row
	return(np.array(in_mat))


def do_clust(cat_ome):
	am = cat_ome.affinity_matrix
	af = ap(preference = np.min(am,axis=1),affinity="precomputed").fit(am)
	labels = af.labels_
	for idx, subject in enumerate(cat_ome.subjects):
		print(cat_ome.subjects[idx]+'\t'+str(labels[idx]))


def plot_stuff(cat_ome,do_cluster=True):
	## plot the log loss
	sns.clustermap(cat_ome.all_log_loss,row_cluster = do_cluster, col_cluster = do_cluster)
	plt.show()
	plt.clf()

	# ## get the spearman correlations
	# sns.clustermap(cat_ome.all_spear)
	# plt.show()
	# plt.clf()

	## make the normalized affinity matrix
	sns.clustermap(cat_ome.affinity_matrix, row_cluster = do_cluster, col_cluster = do_cluster)
	plt.show()
	plt.clf()

##############################################################################
## be able to do it for more than one cat ome
def do_cat_ome(infile,missing_str, do_cluster = True):
	in_mat = get_in_mat(infile, missing_str)


	## test with low none input
	cat_ome = categorical_ome(in_mat, name = infile)
	important_cat_ome = cat_ome.get_good_features()
	print("high info mat:",important_cat_ome.original_mat.shape)
	print(important_cat_ome.original_mat)
	cat_ome.process_cat_ome()
	important_cat_ome.process_cat_ome()

	if args.plot:
		print('plotting original')
		plot_stuff(cat_ome)

		print('plotting high info')
		plot_stuff(important_cat_ome)

	if args.clust:
		print("\n\n\n\ndoing clustering on full mat")
		do_clust(cat_ome)
		print("\n\n\n\ndoing clustering on important mat")
		do_clust(important_cat_ome)

	return(important_cat_ome)

def do_all_cat_omes(infile_list, missing_str):
	all_cat_omes = []
	for infile in args.infile:
		all_cat_omes.append(do_cat_ome(infile, missing_str))
	return(all_cat_omes)


##############################################################################

if __name__ == "__main__":
	## set up the parser
	args = parse_args(sys.argv)
	all_cat_omes = do_all_cat_omes(args.infile, args.missing_str)
	if args.plot:
		for cat in all_cat_omes:
			plot_stuff(cat)
	if args.clust:
		for cat in all_cat_omes:
			do_clust(cat)


