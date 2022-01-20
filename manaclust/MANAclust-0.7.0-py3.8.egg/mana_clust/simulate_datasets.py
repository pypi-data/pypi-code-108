import os
import random
import numpy as np
import seaborn as sns
import argparse
from matplotlib import pyplot as plt

from mana_clust.mana_clust import cluster_omes
from mana_clust.common_functions import write_table, process_dir



def get_group_assignments(num_groups = 4, samples = 300, Gaussian=True):
	if Gaussian:
		p = np.ones(num_groups)/num_groups
	else:
		p = np.arange(num_groups)+1/num_groups
	group_selection_vector = np.arange(num_groups)
	all_group_annotations = []
	for i in range(samples):
		temp_group = np.random.choice(group_selection_vector, p=p)
		all_group_annotations.append(temp_group)
	return(all_group_annotations)


def get_col_names(all_features, real_features):
	## get the column names
	col_names = []
	for i in range(all_features):
		temp_name = "feature_"+str(i)+"_"
		if i < real_features:
			temp_name+="real"
		else:
			temp_name+="random"
		col_names.append(temp_name)
	col_names = np.array([col_names])
	return(col_names)


def get_cat_dataset(num_groups = 2, samples = 300, random_features = 150, percent_noise = .20, percent_missing = .25, real_features = 15):
	ome_array = np.chararray((samples, random_features+real_features), itemsize=2)
	all_features = real_features + random_features
	## first figure out which sample will go_with_which group
	temp_group_assignemnts = get_group_assignments(samples = samples, num_groups = num_groups)
	
	col_names = get_col_names(all_features, real_features)

	## generate the data
	real = list("ABCDEFGHIJKLMNOPQRSTUVWXY")
	for i in range(samples):
		for j in range(all_features):
			if j < real_features:
				## assign real features
				temp_group = temp_group_assignemnts[i]
				temp_val = real[temp_group]
				ome_array[i,j]=temp_val
			else:
				## assign the random features
				temp_val = random.choice(real[:num_groups])
				ome_array[i,j]=temp_val
	
	## introduce random noise
	num_noise = int(samples * all_features * percent_noise)
	rows = np.arange(ome_array.shape[0])
	cols = np.arange(ome_array.shape[1])
	for m in range(num_noise):
		## 
		temp_row = random.choice(rows)
		temp_col = random.choice(cols)
		ome_array[temp_row, temp_col]="Z"

	## introduce random missing values
	num_missing = int(samples * all_features * percent_missing)
	rows = np.arange(ome_array.shape[0])
	cols = np.arange(ome_array.shape[1])
	for m in range(num_missing):
		## 
		temp_row = random.choice(rows)
		temp_col = random.choice(cols)
		ome_array[temp_row, temp_col]="NA"

	## concatenate with title
	ome_array = np.concatenate((col_names, ome_array), axis = 0)

	return(temp_group_assignemnts, ome_array)


def get_num_dataset(samples = 300, num_groups = 3, random_features = 10000, real_features = 200, do_plotting = False):
	all_features = random_features+real_features
	ome_array = np.zeros((random_features+real_features, samples))
	master_points = np.zeros((random_features+real_features, num_groups))
	master_points[:real_features,:] += np.random.rand(real_features, num_groups)*1
	#print(master_points.shape)
	
	row_names = get_col_names(all_features, real_features)

	## first figure out which sample will go_with_which group
	temp_group_assignemnts = get_group_assignments(samples = samples, num_groups = num_groups)
	#print(temp_group_assignemnts)

	## go through each point, and generate it's simulated 'ome'
	for i in range(samples):
		temp_group = temp_group_assignemnts[i]
		ome_array[:,i] += master_points[:,temp_group] + np.random.rand(all_features,)

	if do_plotting:
		sns.clustermap(ome_array[:(real_features+real_features),:])
		plt.show()
		plt.clf()

		sns.clustermap(ome_array)
		plt.show()
		plt.clf()

	## concatenate with features_names
	ome_array = np.concatenate((np.transpose(row_names), np.array(ome_array,dtype=str)), axis = 1)

	return(temp_group_assignemnts, ome_array)


def get_all_final_groups(group_listings):
	group_listings = np.transpose(np.array(group_listings,dtype=str))
	final_group_names = ['variables']
	only_group = []
	for i in range(group_listings.shape[0]):
		temp_group = '_'.join(group_listings[i,:].tolist())
		final_group_names.append("subject_"+str(i)+"|"+temp_group)
		only_group.append(temp_group)
	return(np.array([final_group_names]), only_group)


def get_all_datasets(num_cat = 1, 
	                 num_num = 2, 
	                 samples= 1000, 
	                 num_cat_groups = 2, 
	                 num_cat_rand_feat = 100,
	                 num_cat_real_feat = 5,
	                 cat_noise = 0.20,
	                 cat_percent_missing = 0.25):
	cat_datasets = []
	cat_datasets_groups = []
	num_datasets = []
	num_datasets_groups = []
	for i in range(num_cat):
		temp_group, temp_cat = get_cat_dataset(samples = samples,
			                                   num_groups = num_cat_groups,
			                                   random_features = num_cat_rand_feat,
			                                   percent_noise = cat_noise,
			                                   percent_missing = cat_percent_missing,
			                                   real_features = num_cat_real_feat)
		cat_datasets.append(temp_cat)
		cat_datasets_groups.append(temp_group)
	for i in range(num_num):
		temp_group, temp_num = get_num_dataset(samples = samples)
		num_datasets.append(temp_num)
		num_datasets_groups.append(temp_group)
	

	final_groups, only_group = get_all_final_groups(cat_datasets_groups+num_datasets_groups)
	## concatenate final sample names to each ome
	for i in range(len(cat_datasets)):
		cat_datasets[i] = np.concatenate((np.transpose(final_groups),cat_datasets[i]), axis = 1)
	for i in range(len(num_datasets)):
		num_datasets[i] = np.concatenate((final_groups,num_datasets[i]), axis = 0)

	return(cat_datasets,num_datasets, only_group)


def write_datasets(num_cat = 1, 
	               num_num = 2, 
	               samples = 1000, 
	               num_cat_groups = 2, 
	               num_cat_rand_feat = 100,
	               num_cat_real_feat = 5,
	               cat_noise = 0.20,
	               cat_percent_missing = 0.25,
	               output_dir="/home/scott/bin/momcluster/lib/synthetic_data"):
	## process the output dir
	if output_dir[-1]!='/':
		output_dir+='/'
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)
	## write the data
	cat_data, num_data, group_vector = get_all_datasets(num_cat = num_cat, 
		                                                num_num = num_num, 
		                                                samples = samples,
		                                                num_cat_groups = num_cat_groups, 
										                num_cat_rand_feat = num_cat_rand_feat,
										                num_cat_real_feat = num_cat_real_feat,
										                cat_noise = cat_noise,
										                cat_percent_missing = cat_percent_missing)
	for cat in cat_data:
		print(cat)
	for num in num_data:
		print(num)
	cat_files = []
	for i in range(len(cat_data)):
		cat_files.append(output_dir+'categorical_data_file_'+str(i)+'.tsv')
		write_table(cat_data[i],cat_files[-1])
	num_files = []
	for i in range(len(num_data)):
		num_files.append(output_dir+'numeric_data_file_'+str(i)+'.tsv')
		write_table(num_data[i],num_files[-1])
	return(cat_files, num_files, group_vector)

def parse_args():
	parser = argparse.ArgumentParser()

	parser.add_argument(
		'-out_dir',
		type=str)

	parser.add_argument(
		'-iters','-iterations',
		type=int)

	parser.add_argument(
		'-seed',
		default = 123456789,
		type=int)

	args = parser.parse_args()
	return(args)

# def process_dir(in_dir):
# 	## process the output dir
# 	if in_dir[-1]!='/':
# 		in_dir+='/'
# 	if not os.path.isdir(in_dir):
# 		os.makedirs(in_dir)
# 	return(in_dir)


def make_all_datasets(out_dir, 
	                  iters, 
	                  num_cat = 1, 
	                  num_num = 2, 
	                  samples = 1000,
		              num_cat_groups = 2, 
		              num_cat_rand_feat = 100,
		              num_cat_real_feat = 5,
		              cat_noise = 0.20,
		              cat_percent_missing = 0.25):
	master_output_dir = process_dir(out_dir)
	all_datasets = []
	all_group_vectors = []
	for i in range(iters):
		next_out_dir = process_dir(master_output_dir+"/"+str(i))
		cat_files, num_files, group_vector=write_datasets(num_cat = num_cat, 
			                                              num_num = num_num, 
			                                              samples = samples, 
			                                              output_dir=next_out_dir,
			                                              num_cat_groups = num_cat_groups,
			                                              num_cat_rand_feat = num_cat_rand_feat,
											              num_cat_real_feat = num_cat_real_feat,
											              cat_noise = cat_noise,
											              cat_percent_missing = cat_percent_missing)
		all_datasets.append({'cat':cat_files, 'num':num_files})
		all_group_vectors.append(group_vector)
	return(all_datasets, all_group_vectors)


def sim_data_main():
	args = parse_args()
	seed = args.seed
	random.seed(seed)
	np.random.seed(seed)
	all_datasets = make_all_datasets(args.out_dir, args.iters)

if __name__ == '__main__':
	sim_data_main()

