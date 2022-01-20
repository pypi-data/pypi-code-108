
import argparse
import random
import seaborn as sns
from matplotlib import pyplot as plt
from copy import deepcopy
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
from sklearn.metrics import mutual_info_score

from mana_clust.simulate_datasets import make_all_datasets
from mana_clust.mana_clust import cluster_omes, write_ome_results, plot_ome_results
from mana_clust.simulate_datasets import process_dir
from mana_clust.common_functions import write_table
from mana_clust.mana_cat import get_contingency_table




###########################################################################
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-out_dir',
        default = "/home/scott/bin/manaclust/lib/synthetic_data/",
        type=str)

    parser.add_argument(
        '-iters','-iterations',
        default = 2,
        type=int)

    parser.add_argument(
        '-num_cat_groups',
        default = 2,
        type=int)

    parser.add_argument(
        '-num_cat_datasets','-cat_dat',
        default = 1,
        type=int)

    parser.add_argument(
        '-cat_missing','-cat_missing',
        default = .50,
        type=float)

    parser.add_argument(
        '-cat_noise',
        default = .50,
        type=float)

    parser.add_argument(
        '-num_cat_rand_feat',
        default = 150,
        type=int)

    parser.add_argument(
        '-num_cat_real_feat',
        default = 15,
        type=int)

    parser.add_argument(
        '-num_num_groups',
        default = 3,
        type=int)

    parser.add_argument(
        '-num_num_datasets','-num_dat',
        default = 2,
        type=int)

    parser.add_argument(
        '-samples','-s',
        default = 1000,
        type=int)

    parser.add_argument(
        '-seed',
        default = 123456789,
        type=int)

    args = parser.parse_args()
    return(args)
###########################################################################    

def do_mi_line_plot(mi_df, paired_t_test_t, paired_t_test_p, out_dir, y="mutual information", name="clustering_results", size = 5, y_min = None, y_max = None):
    ax = sns.pointplot(x="method", y=y, hue = "iter",
                       data = mi_df, 
                       size=size, 
                       scale = 3,
                       legend = False,
                       alpha = 0.5,
                       dodge = True)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    ax.get_legend().remove()
    out_dir = process_dir(out_dir)
    out_file = out_dir+name+"_"+y.replace(' ','_')+"_lines.png"
    sns.set(font_scale=1.75)

    if y_min != None and y_max != None:
        plt.ylim(y_min,y_max)
    
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf()
    return



def get_purity(contingency_matrix, true_axis = 1):
    ## takes in a contingency table where the ground truth is in the rows, and the 
    ## clustering results are in the columns and returns the purity
    purity = np.sum(np.amax(contingency_matrix, axis = true_axis)) / np.sum(contingency_matrix)
    return(purity)


def get_real_random_feat_stats(selected_features, all_features, iteration, method = "MANAclust"):
    ## make the contingency table of real vs random features

    ## Make dicts for the selected and non-selected features
    selected_dict = {feature:index for index, feature in enumerate(selected_features)}
    non_selected = []
    non_selected_dict = {}
    real_features = []
    random_features = []
    for feature in all_features:
        try:
            selected_dict[feature]
        except:
            non_selected.append(feature)
            non_selected_dict[feature]=len(non_selected)-1
        if feature[-4:] == 'real':
            real_features.append(feature)
        else:
            random_features.append(feature)
    ## Go through each of the features making the contingency table 
    cont_table = np.zeros((2,2))
    ##################################################
    ################   | Actual = Yes  |  Actual = No
    ## predicted = Yes |     X         |     X        
    ## predicted = No  |     X         |     X

    for feat in real_features:
        if feat in selected_dict:
            cont_table[0,0]+=1
        else:
            cont_table[1,0]+=1
    for feat in random_features:
        if feat in selected_dict:
            cont_table[0,1]+=1
        else:
            cont_table[1,1]+=1
    
    TP = cont_table[0,0]
    FP = cont_table[0,1]
    FN = cont_table[1,0]
    TN = cont_table[1,1]
    accuracy = (TP + TN) / np.sum(cont_table)
    recall = TP / (TP + FN)
    precision = TP / (TP + FP)
    specificity = TN / (TN + FP)
    F_one = (2 * precision * recall) / (precision + recall)
    if np.isnan(F_one):
        F_one = 0
    print('\tfeature selection stats:')
    print('\t\tTP:',TP)
    print('\t\tFP:',FP)
    print('\t\tFN:',FN)
    print('\t\tTN:',TN)
    print('\t\taccuracy:',accuracy)
    print('\t\trecall:',recall)
    print('\t\tprecision:',precision)
    print('\t\tspecificity:',specificity)
    print('\t\tF1:',F_one)
    temp_result_dict = {"method":[method],
                        "iter":[iteration],
                        "TP":[TP],
                        "FP":[FP],
                        "FN":[FN],
                        "TN":[TN],
                        "accuracy":[accuracy],
                        "recall":[recall],
                        "precision":[precision],
                        "specificity":[specificity],
                        "F1":[F_one]}
    temp_result_df = pd.DataFrame(temp_result_dict)
    return(temp_result_df)

def get_accuracy_of_feat_select(meta_ome, iteration):
    for i in range(len(meta_ome.cat_omes)):
        select_cat_names = meta_ome.cat_omes[i].feature_names
        full_cat_names = meta_ome.cat_omes_full[i].feature_names
        #print(select_cat_names)
        #print(full_cat_names)
        ## now run the same thing, but with a random selection of features
        num_select = len(select_cat_names)
        random_select_feats = np.random.choice(full_cat_names, size = num_select, replace = False)
        random_feat_select = get_real_random_feat_stats(random_select_feats, full_cat_names, iteration, method = "random")
        real_cat_feat_select = get_real_random_feat_stats(select_cat_names, full_cat_names, iteration)
        cat_feat_select = random_feat_select.append(real_cat_feat_select, ignore_index=True)
    for ome in meta_ome.num_omes:
        select_num_names = ome.feature_names[ome.anti_cor_indices]
        full_num_names = ome.feature_names
        #print(select_num_names)
        #print(full_num_names)
        ## now run the same thing, but with a random selection of features
        num_select = len(select_num_names)
        random_select_feats = np.random.choice(full_num_names, size = num_select, replace = False)
        random_feat_select = get_real_random_feat_stats(random_select_feats, full_num_names, iteration, method = "random")
        real_num_feat_select = get_real_random_feat_stats(select_num_names, full_num_names, iteration)
        num_feat_select = random_feat_select.append(real_num_feat_select, ignore_index=True)
    return(cat_feat_select, num_feat_select)

def get_performance_stats(ground_truth, meta_ome, out_dir):
    out_dir = process_dir(out_dir)
    ## get contingency table from feature selected
    feat_select_cont, feat_select_row, feat_select_col = get_contingency_table_stats(ground_truth, meta_ome.labels, out_dir+"contingency_table_feature_selected.png")
    ## and full
    full_cont, full_row, full_col = get_contingency_table_stats(ground_truth, meta_ome.labels_full, out_dir+"contingency_table_full.png")

    ## get the mutual information
    feat_select_mi = mutual_info_score(None, None, contingency = feat_select_cont)
    full_mi = mutual_info_score(None, None, contingency = full_cont)

    ## get the purity
    feat_select_purity = get_purity(feat_select_cont)
    full_purity = get_purity(full_cont)
    return(feat_select_mi, full_mi, feat_select_purity, full_purity)


def re_order_cont_df(in_df):
    pass
    # already_used = []
    # for i in range(0,in_df.shape[0]):
    #     np.argmax(in_df, axis = 1)


def get_contingency_table_stats(ground_truth, cluster_vect, out_file):
    # cont_table = get_contingency_table(ground_truth, cluster_vect, return_ids = False)
    # print(cont_table)
    cont_table, row_ids, col_ids = get_contingency_table(ground_truth, cluster_vect, return_ids = True)
    row_sums = np.sum(cont_table,axis=1)
    col_sums = np.sum(cont_table,axis=0)
    row_order = np.argsort(row_sums)
    col_order = np.argsort(col_sums)
    col_names_reordered = np.array(col_ids)[col_order]
    row_names_reordered = np.array(row_ids)[row_order]
    reordered_cont_table = cont_table[row_order,:]
    reordered_cont_table= reordered_cont_table[:,col_order]
    cont_df = pd.DataFrame(reordered_cont_table)
    cont_df.columns = col_names_reordered
    index_dict={key:value for key,value in enumerate(row_names_reordered)}
    cont_df.rename(index=index_dict, inplace=True)
    sns.heatmap(cont_df)
    ## re-order the columns to be on the diagonal
    plt.savefig(out_file,
                dpi=600,
                bbox_inches='tight')
    plt.clf()
    return(cont_table, row_ids, col_ids)


def get_group_from_clust_ome(meta_ome):
    all_subjects = meta_ome.all_subjects
    all_groups = []
    for subj in all_subjects:
        all_groups.append(subj.split('|')[-1])
    return(all_groups)


def get_mi_stats(all_feat_mi, 
                 all_full_mi, 
                 feat_select_purity, 
                 full_purity, 
                 out_dir):
    size = 7
    all_feat_mi = list(all_feat_mi)
    all_full_mi = list(all_full_mi)
    paired_t_test_t, paired_t_test_p = ttest_rel(all_feat_mi, all_full_mi)
    print("mutual information paired t-test:",paired_t_test_t, paired_t_test_p)
    method = ["full dataset"]*len(all_full_mi)+["feature selection"]*len(all_feat_mi)
    iteration_vect = np.arange(len(all_full_mi)).tolist()
    iteration_vect = iteration_vect + iteration_vect
    mutual_information = all_full_mi + all_feat_mi
    purity = full_purity + feat_select_purity
    mi_df = pd.DataFrame({"iter":iteration_vect,
                          "method":method,
                          "mutual information":mutual_information,
                          "purity":purity})
    
    ## plot mi violin plot
    out_dir = process_dir(out_dir)
    out_file = out_dir+"clustering_results_mutual_information.png"
    
    ax = sns.violinplot(x="method", y="mutual information", data = mi_df,
                        scale = 'width', 
                        size = size)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf()

    ax = sns.violinplot(x="method", y="mutual information", data = mi_df,
                        scale = 'width', 
                        size = size)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf()

    sns.violinplot(x="method", y="mutual information", data = mi_df,
                        scale = 'width', 
                        size = size)
    ax = sns.swarmplot(x="method", y="mutual information",# hue="method",
                  data=mi_df, palette="muted",
                  edgecolor = 'white', linewidth=1, s=22)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf()
    
    ## do the mi line plot
    do_mi_line_plot(mi_df, paired_t_test_t, paired_t_test_p, out_dir, size = size)
    plt.clf()
    do_mi_line_plot(mi_df, paired_t_test_t, paired_t_test_p, out_dir, size = size)
    plt.clf()

    #### plot purity
    paired_t_test_t, paired_t_test_p = ttest_rel(feat_select_purity, full_purity)
    print("purity paired t-test:",paired_t_test_t, paired_t_test_p)
    ## make the plot
    sns.violinplot(x="method", y="purity", data = mi_df, 
                        scale = "width",
                        size = size)
    ax = sns.swarmplot(x="method", y="purity",# hue="method",
                  data=mi_df, palette="muted",
                  edgecolor = 'white', linewidth=1, s=22)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    out_dir = process_dir(out_dir)
    out_file = out_dir+"clustering_results_purity.png"
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf()
    do_mi_line_plot(mi_df, paired_t_test_t, paired_t_test_p, out_dir, y="purity", size = size)  
    plt.clf()

    ## replot mi violin... 
    paired_t_test_t, paired_t_test_p = ttest_rel(all_feat_mi, all_full_mi)
    out_file = out_dir+"clustering_results_mutual_information.png"
    sns.violinplot(x="method", y="mutual information", data = mi_df, 
                        scale = "width",
                        size = size)
    ax = sns.swarmplot(x="method", y="mutual information",# hue="method",
                  data=mi_df, palette="muted",
                  edgecolor = 'white', linewidth=1, s=22)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf() 
    mi_df.to_csv(out_dir+'clustering_results_summary.tsv',sep='\t')
    return(mi_df)


def do_feat_select_plot(in_stats, var, out_dir, feature_type):
    ## get the methods vectors
    unique_methods = set(in_stats["method"])
    rand_row = in_stats["method"]=="random"
    mom_row = in_stats["method"]=="MANAclust"
    random_results = in_stats[var][rand_row]
    MANAclust_results = in_stats[var][mom_row]
    MANAclust_results[MANAclust_results==np.nan]=0
    random_results[random_results==np.nan]=0
    paired_t_test_t, paired_t_test_p = ttest_rel(MANAclust_results, random_results)
    print(MANAclust_results)
    print(random_results)
    print(var,"paired t-test:",paired_t_test_t, paired_t_test_p)

    plt.clf()
    sns.violinplot(x="method", y=var,# hue="method",
                        scale = 'width', 
                        data=in_stats, palette="muted")
    out_file = out_dir + feature_type + '_feature_selection_'+var+".png"
    print('\n\n',var,var in ['specificity', 'accuracy'],'\n\n')
    # if var not in ['specificity', 'accuracy']:
    #     plt.ylim(0,1.05)
    # else:
    #     plt.ylim(0.8,1.05)
    ax = sns.swarmplot(x="method", y=var,# hue="method",
                  data=in_stats, palette="muted",
                  edgecolor = 'white', linewidth=1, s=22)
    ax.set_title("t="+str(paired_t_test_t)+"\np="+str(paired_t_test_p))
    plt.savefig(out_file,
            dpi=600,
            bbox_inches='tight')
    plt.clf()

    if var != 'specificity':
        do_mi_line_plot(in_stats, paired_t_test_t, paired_t_test_p, out_dir, 
                        y=var, name=feature_type, y_min = 0, y_max = 1.05)
    else:
        do_mi_line_plot(in_stats, paired_t_test_t, paired_t_test_p, out_dir, 
                        y=var, name=feature_type, y_min = 0.8, y_max = 1.05)
    
    plt.clf()


def get_feat_selection_stats(in_stats, name, out_dir):
    print('\n\t\tname:',name)
    print(in_stats)
    ## compare MANAclust
    #     "accuracy":[accuracy],
    # "recall":[recall],
    # "precision":[precision],
    # "specificity":[specificity],
    # "F1":[F_one]}
    variables = ["accuracy","recall","precision","specificity","F1"]
    for variable in variables:
        do_feat_select_plot(in_stats,
                            variable,
                            out_dir,
                            name)
    in_stats.to_csv(out_dir+name+'_feature_selection_stats.tsv',sep='\t')


def main():
    args = parse_args()

    seed = args.seed
    random.seed(seed)
    np.random.seed(seed)
    out_dir = process_dir(args.out_dir)
    results_dir = process_dir(out_dir+"/results")
    print('making the datasets')

    all_datasets, all_group_vectors = make_all_datasets(out_dir, 
                                                        args.iters, 
                                                        num_cat = args.num_cat_datasets, 
                                                        num_num = args.num_num_datasets, 
                                                        samples = args.samples,
                                                        num_cat_groups = args.num_cat_groups, 
                                                        num_cat_rand_feat = args.num_cat_rand_feat,
                                                        num_cat_real_feat = args.num_cat_real_feat,
                                                        cat_noise = args.cat_noise,
                                                        cat_percent_missing = args.cat_missing)
    all_feat_mi=[]
    all_full_mi=[]
    all_feat_purity = []
    all_full_purity = []
    cat_feat_select_stats = None
    num_feat_select_stats = None
    for i in range(len(all_datasets)):
        ## perform the clustering on the synthetic datset
        print('\n\n\nclustering ome #',i,"\n\n\n")
        temp_outdir = process_dir(out_dir + str(i))
        temp_results = process_dir(temp_outdir+'/results')
        temp_clustered_ome = cluster_omes(all_datasets[i]["cat"],all_datasets[i]["num"], out_dir = temp_outdir)
        temp_group_vector = get_group_from_clust_ome(temp_clustered_ome)
        ## write the results and plot some stats at the per-ome level
        write_ome_results(temp_results, temp_clustered_ome)
        plot_ome_results(temp_clustered_ome, temp_results, temp_group_vector)
        ## get clusteringa accuracy statistics 
        temp_feat_mi, temp_full_mi, feat_select_purity, full_purity = get_performance_stats(temp_group_vector, temp_clustered_ome, temp_results)
        all_feat_mi.append(temp_feat_mi)
        all_full_mi.append(temp_full_mi)
        all_feat_purity.append(feat_select_purity)
        all_full_purity.append(full_purity)
        ## check accuracy of feature selection
        temp_cat_df, temp_num_df = get_accuracy_of_feat_select(temp_clustered_ome, i)
        if type(cat_feat_select_stats) != pd.core.frame.DataFrame:
            cat_feat_select_stats = deepcopy(temp_cat_df)
            num_feat_select_stats = deepcopy(temp_num_df)
        else:
            cat_feat_select_stats = cat_feat_select_stats.append(temp_cat_df, ignore_index = True)
            num_feat_select_stats = num_feat_select_stats.append(temp_num_df, ignore_index = True)
    print(len(all_feat_mi))
    print(len(all_full_mi))
    print(len(all_feat_purity))
    print(len(all_full_purity))
    get_mi_stats(all_feat_mi, all_full_mi, all_feat_purity, all_full_purity, results_dir)

    ## get the stats for the feature selection process
    get_feat_selection_stats(cat_feat_select_stats, "categorical", results_dir)
    get_feat_selection_stats(num_feat_select_stats, "numeric", results_dir)


if __name__ == '__main__':
    main()