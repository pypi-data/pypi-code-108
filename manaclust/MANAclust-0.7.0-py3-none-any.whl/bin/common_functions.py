"""
A library of functions that are used in the Scripts for PyMiner's auxilary scripts.  Reduced code duplication and makes
maintenance easier. """

import pickle
import os
import numpy as np
import networkx as nx
import community
from subprocess import check_call, Popen, PIPE

def process_dir(in_dir):
	## process the output dir
	if in_dir[-1]!='/':
		in_dir+='/'
	if not os.path.isdir(in_dir):
		os.makedirs(in_dir)
	return(in_dir)


def run_cmd(in_message, com=True, stdout=None):

    print('\n', " ".join(in_message), '\n')
    if stdout:
        with open(stdout, 'w') as out:
            process = Popen(in_message, stdout=PIPE)
            while True:
                line = process.stdout.readline().decode("utf-8")
                out.write(line)
                if line == '' and process.poll() is not None:
                    break
    if com:
        Popen(in_message).communicate()
    else:
        check_call(in_message)


def read_file(temp_file, lines_o_raw='lines', quiet=False):
    """ basic function library """

    lines = None
    if not quiet:
        print('reading', temp_file)
    file_handle = open(temp_file, 'r')
    if lines_o_raw == 'lines':
        lines = file_handle.readlines()
        for i, line in enumerate(lines):
            lines[i] = line.strip('\n')
    elif lines_o_raw == 'raw':
        lines = file_handle.read()
    file_handle.close()
    return lines


def make_file(contents, path):
    file_handle = open(path, 'w')
    if isinstance(contents, list):
        file_handle.writelines(contents)
    elif isinstance(contents, str):
        file_handle.write(contents)
    file_handle.close()


# def flatten_2D_table(table, delim):
#     # print(type(table))
#     if str(type(table)) == "<class 'numpy.ndarray'>":
#         out = []
#         for i, row in enumerate(table):
#             out.append([])
#             for j, cell in enumerate(row):
#                 try:
#                     str(cell)
#                 except ValueError:
#                     print(cell)
#                 else:
#                     out[i].append(str(cell))
#             out[i] = delim.join(out[i]) + '\n'
#         return out
#     else:
#         for i, row in enumerate(table):
#             for j, cell in enumerate(row):
#                 try:
#                     str(row)
#                 except ValueError:
#                     print(row)
#                 else:
#                     table[i][j] = str(cell)
#             table[i] = delim.join(row) + '\n'
#         return table

def flatten_2D_table(table, delim):
    # print(type(table))
    if str(type(table)) == "<class 'numpy.ndarray'>":
        out = []
        for i in range(0, len(table)):
            out.append([])
            for j in range(0, len(table[i])):
                try:
                    str(table[i][j])
                except:
                    print(table[i][j])
                else:
                    out[i].append(str(table[i][j]))
            out[i] = delim.join(out[i]) + '\n'
        return out
    else:
        for i in range(0, len(table)):
            for j in range(0, len(table[i])):
                try:
                    str(table[i][j])
                except:
                    print(table[i][j])
                else:
                    table[i][j] = str(table[i][j])
            table[i] = delim.join(table[i]) + '\n'
        # print(table[0])
        return table


def strip_split(line, delim='\t'):
    return line.strip('\n').split(delim)


def make_table(lines, delim, range_min=0):
    for i in range(range_min, len(lines)):
        lines[i] = lines[i].strip()
        lines[i] = lines[i].split(delim)
        for j in range(range_min, len(lines[i])):
            try:
                float(lines[i][j])
            except ValueError:
                lines[i][j] = lines[i][j].replace('"', '')
            else:
                lines[i][j] = float(lines[i][j])
    return lines


def get_file_path(in_path):
    in_path = in_path.split('/')
    in_path = in_path[:-1]
    in_path = '/'.join(in_path)
    return in_path + '/'


def read_table(file, sep='\t'):
    return make_table(read_file(file, 'lines'), sep)


def write_table(table, out_file, sep='\t'):
    make_file(flatten_2D_table(table, sep), out_file)


def import_dict(file_handle):
    file_handle = open(file_handle, 'rb')
    data = pickle.load(file_handle)
    file_handle.close()
    return data


def save_dict(data, path):
    file_handle = open(path, 'wb')
    pickle.dump(data, file_handle)
    file_handle.close()


def get_sample_k_lists(group_numeric_vector, total_groups = None):
    if total_groups == None:
        total_groups = max(group_numeric_vector)+1
    group_index_lists = [[] for i in range(total_groups)]
    for i in range(0,len(group_numeric_vector)):
        temp_group = group_numeric_vector[i]
        group_index_lists[temp_group].append(i)
    return(group_index_lists)


def convert_vect_to_mi_bins(in_vect):
    out_vect = np.array(in_vect, dtype = str)
    ## first get all the unique values
    all_vals = list(set(list(in_vect)))
    ## next get all the numeric convertable values
    ## or return the original vect if there are none
    all_num_vals = []
    all_num_idxs=[]
    for i in range(len(in_vect)):
        try:
            float(in_vect[i])
        except:
            pass
        else:
            temp_val = float(in_vect[i])
            if not np.isnan(temp_val):
                all_num_vals.append(temp_val)
                all_num_idxs.append(i)
    ## if there aren't enough numeric values to warrant conversion, then don't
    if len(all_num_vals) < 10:
        return in_vect
    ## calculate the number of bins
    bin_num = max([2,int(np.sqrt(len(all_num_vals)/5))])
    ## min-max linear normalize the vector
    all_num_vals = np.array(all_num_vals)
    all_num_vals -= np.min(all_num_vals)
    all_num_vals = all_num_vals / np.max(all_num_vals)
    ## calculate the bin interval
    bins = np.arange(bin_num)/bin_num
    digitized_num_vals = np.digitize(all_num_vals, bins)
    print(digitized_num_vals)
    ## now update the original vector to return it
    for i in range(0,len(all_num_idxs)):
        original_idx = all_num_idxs[i]
        new_val = digitized_num_vals[i]
        out_vect[original_idx] = str(new_val)
    return out_vect


def digitize_for_max_info(in_mat):
    ## takes in a full input matrix & digitizes the numeric values of the colums
    in_mat = np.array(in_mat,dtype=str)
    ncol = np.shape(in_mat)[1]
    nrow = np.shape(in_mat)[0]
    for i in range(1,ncol):
        in_mat[1:nrow,i] = convert_vect_to_mi_bins(in_mat[1:nrow,i])
    return in_mat


## this function was adopted from emre's stackoverflow answer found here:
## https://stackoverflow.com/questions/7450957/how-to-implement-rs-p-adjust-in-python
def correct_pvalues_for_multiple_testing(pvalues, correction_type = "Benjamini-Hochberg"):                
    """                                                                                                   
    consistent with R - print correct_pvalues_for_multiple_testing([0.0, 0.01, 0.029, 0.03, 0.031, 0.05, 0.069, 0.07, 0.071, 0.09, 0.1]) 
    """
    from numpy import array, empty
    pvalues = array(pvalues)
    n = int(pvalues.shape[0])
    new_pvalues = empty(n)
    if correction_type == "Bonferroni":
        new_pvalues = n * pvalues
    elif correction_type == "Bonferroni-Holm":
        values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
        values.sort()
        for rank, vals in enumerate(values):
            pvalue, i = vals
            new_pvalues[i] = (n-rank) * pvalue
    elif correction_type == "Benjamini-Hochberg":
        values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
        values.sort()
        values.reverse()
        new_values = []
        for i, vals in enumerate(values):
            rank = n - i
            pvalue, index = vals
            new_values.append((n/rank) * pvalue)
        for i in range(0, int(n)-1):
            if new_values[i] < new_values[i+1]:
                new_values[i+1] = new_values[i]
        for i, vals in enumerate(values):
            pvalue, index = vals
            new_pvalues[index] = new_values[i]
    return new_pvalues


def do_louvain_merger(in_mat, sample_k_lists):
    ## take in the BH corrected p-values for whether 
    ## the groups are significantly different for this ome
    ## at the level of the feature selected affinity matrix
    
    ## make the fully connected, weighted matrix
    G = nx.from_numpy_matrix(in_mat)
    partition = community.best_partition(G)
    ## this is a dictionary with the original group index as the keys
    ## and the new group index as the 
    print(partition)
    ## make the empty lists for holding all of the 
    ## new sample group lists
    new_groups = []
    new_group_annotations = []
    for i in range(len(set(partition.values()))):
        new_groups.append([])
        new_group_annotations.append([])
    for i in range(in_mat.shape[0]):
        new_groups[partition[i]]+=sample_k_lists[i]
        new_group_annotations[partition[i]].append(i)
    return(new_groups,new_group_annotations, partition)










