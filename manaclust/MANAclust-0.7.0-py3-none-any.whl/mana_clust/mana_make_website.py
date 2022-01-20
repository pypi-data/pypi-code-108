#!/usr/bin/env python3
import sys,time,glob,os,pickle,fileinput,argparse
from subprocess import Popen
from operator import itemgetter
import gc, fileinput
import numpy as np
from PIL import Image

from mana_clust.common_functions import *

########################################################

########################################################
########################################################

########################################################
############# add the various elements #################

def get_img_dims(img):
    image = Image.open(img)
    w, h = image.size
    ## reduce size so it fits on the screne
    reduction_factor = w/600
    return(int(w/reduction_factor), int(h/reduction_factor))

def add_h1(title):
    return("\n\t<h1>"+str(title)+"</h1>\n")

def add_h2(title):
    return("\n\t<h2>"+str(title)+"</h2>\n")

def add_h3(title):
    return("\n\t<h3>"+str(title)+"</h3>\n")

def add_p(p):
    return('\t\t\t<p>'+str(p)+'</p>\n')

def add_file_link(f,name):
    if not os.path.isfile(f):
        print("\n\tWARNING: couldn't find file:",f,"\n")
    return('<a href='+str(f)+'>'+str(name)+'</a>\n')

def add_file_link_list(f,name):
    return('<li><a href='+str(f)+'>'+str(name)+'</a></li>\n')

def add_br():
    return('<br></br>\n')

def add_img(img,alt, base_dir= None):
    if os.path.isfile(img):
        w, h = get_img_dims(img)
        return('<div><img src="'+str(img)+'" alt="'+str(alt)+'" width="'+str(w)+'" height="'+str(h)+'"></div>\n')
    else:
        if base_dir != None:
            curr_dir = os.getcwd()
            os.chdir(base_dir)
            final_text = add_img(img, alt)
            os.chdir(curr_dir)
            return(final_text)
        print("\tWARNING: couldn't find:"+img)
        return(add_br())

def add_button_head(text):
    return("""<button class="collapsible">"""+str(text)+"""</button>
<div class="content">""")

def add_table(in_table):
    ## start the table
    out_table_str = """<table style="width:100%">\n"""
    for i in range(len(in_table)):
        out_table_str+="\t<tr>\n"
        for j in range(len(in_table[i])):
            out_table_str+="\t<th>"+str(in_table[i][j])+"</th>\n"
        out_table_str+="\t</tr>\n"
    out_table_str+="</table>\n"
    return(out_table_str)


def parse_file_name(img):
    old_name = img[:-4]
    temp_name = old_name.split('_')
    temp_name = ' '.join(temp_name)
    return(old_name,temp_name)



def add_clustering(base_dir):
    os.chdir(base_dir)
    cluster_str = ""

    #cluster_str+=add_h2('Clustering')
    cluster_str+=add_button_head('Clustering')
    ## check if anti_correlation clustering was done
    if os.path.isfile(base_dir+'sig_neg_count_vs_total_neg_count.png'):
        ## if it is, start annotating
        cluster_str+=add_h3("Negative Control Bootstrap Shuffling")
        cluster_str+=add_p("Here, MANAclust shuffled up your data to make it randomized. This will maintain the overall distribution of your data, while at the same time randomizing it so that we can come up with a reasonable cutoff for performing the anti-correlation based feature selection. Shown below is the distribution of all randomized Spearman rhos.")
        cluster_str+=add_img("boostrap_cor_rhos.png", 'boot_all')
        cluster_str+=add_p("Here are just the negative correlations from the shuffled up dataset.")
        cluster_str+=add_img("boostrap_neg_cor_rhos.png", 'boot_neg')
        cluster_str+=add_p("Here is a scatter plot that shows the number of total negative correlations observed for each gene (y-axis), and the log2 number of significant negative correlations (x-axis). All of the genes to the left/below the black line were used for clustering.")
        cluster_str+=add_img("sig_neg_count_vs_total_neg_count.png","sig_vs_total_neg")
        cluster_str+=add_p("Similarly, here is a plot showing the ratio of significant to non-sigificant. Everything to the right was used for clustering.")

    ## link to the file with all of the sample annotations
    cluster_str+=add_h3("Clustering Results:")
    cluster_str+=add_file_link("sample_clustering_and_summary/sample_k_means_groups.txt",'sample group annotations')

    ## get the images from the sample_clustering_and_summary folder
    os.chdir(base_dir+"sample_clustering_and_summary/")
    additional_images=[]
    for item in glob.glob("*.png"):
        additional_images.append(item)
    os.chdir(base_dir)
    if len(additional_images)>0:
        cluster_str+=add_h3('Here are some additional images:')
        for img in additional_images:
            old_name = img[:-4]
            temp_name = old_name.split('_')
            temp_name = ' '.join(temp_name)
            cluster_str+=add_p(temp_name)
            cluster_str+=add_img("sample_clustering_and_summary/"+img,old_name)
    
    static_files = []
    cluster_str+='\n</div>\n'
    os.chdir(base_dir)
    return(cluster_str)



def add_statistics(base_dir):
    stats_str = ""
    #stats_str+=add_h2("Statistics")
    stats_str+=add_button_head("Statistics")
    stats_str+=add_h3("basic stats")
    stats_str+=add_p("If you find some interesting genes that are different between groups, here are the:")
    stats_str+=add_file_link("sample_clustering_and_summary/k_group_means.txt",'group means')
    stats_str+=add_p('and...')
    stats_str+=add_file_link("sample_clustering_and_summary/k_group_sd.txt",'group standard deviations')
    stats_str+=add_p('as well as the')
    # stats_str+=add_file_link("sample_clustering_and_summary/sample_var_enrichment_Zscores.txt",'sample-wise Z-scores')
    # stats_str+=add_p('and...')
    stats_str+=add_file_link("sample_clustering_and_summary/k_group_enrichment.txt",'group level Z-scores')
    stats_str+=add_h3("statistical comparisons")
    sig_dir = "sample_clustering_and_summary/significance/"

    stats_str+=add_file_link(sig_dir+'groups_1way_anova_results.txt',"Benjamini-Hoschberg corrected 1-way Anovas")
    stats_str+='\n</div>\n'
    return(stats_str)

def add_gene_enrichment(base_dir):
    os.chdir(base_dir)
    sig_dir = "sample_clustering_and_summary/significance/"
    enrich_str = ""
    #enrich_str+=add_h2("Gene Enrichment in Groups")
    enrich_str+=add_button_head("Gene enrichment in groups")
    enrich_str+=add_h3("Significantly enriched genes in each group")
    enrich_str+=add_p("Below is a file that contains a table with genes on the left, and groups in columns. If a gene is considered significantly enriched, that means that the BH corrected 1-way Anova was significant, and the gene had a high Z-score in that particular group. If a gene is significantly enriched in that group, the value is True in the corresponding cell in the table, False if it was not significantly enriched.")
    enrich_str+=add_file_link(sig_dir+"/significant_and_enriched_boolean_table.txt","True/False significantly enriched table")
    enrich_str+=add_p("alternatively, you can use these separated files that simply have the list of significantly enriched genes for each group:")
    enrich_str+=add_button_head('Genes enriched in each group')
    os.chdir(sig_dir)
    enrich_files=[]
    for item in glob.glob("*_significant_enriched.txt"):
        enrich_files.append(item)
    enrich_files = sorted(enrich_files)
    if len(enrich_files)>0:
        enrich_str+="\t\t\t\t<ul>\n"
        for img in enrich_files:
            old_name = img[:-4]
            temp_name = old_name.split('_')
            temp_name = ' '.join(temp_name)
            #enrich_str+=add_p(temp_name)
            enrich_str+=add_file_link(sig_dir+img,old_name)
            enrich_str+=add_br()

        enrich_str+="\t\t\t\t</ul>\n"

    enrich_str+="\t\t</div>"# end the sub-button
    enrich_str+=add_br()

    os.chdir(base_dir)
    pathway_dir = sig_dir+'gprofiler/'
    os.chdir(pathway_dir)
    enrich_path=[]
    for item in glob.glob("*.txt"):
        enrich_path.append(item)
    os.chdir(base_dir)
    enrich_path = sorted(enrich_path)
    if len(enrich_path)>0:
        #enrich_str+=add_h3('Pathway Enrichment for Each Group:')
        enrich_str+=add_button_head('Pathway enrichment for each group')
        if os.path.isfile(sig_dir+"/combined_neg_log10p_gprofiler.txt"):
            enrich_str+=add_p("Below is a combined file with all of the pathways that came out of the analysis of the above genes, enriched in the different groups. We've also created a new algorithm for ranking the importance of these pathways (not to boast, but I'm kind of proud of it). It's based on the information/entropy of the -log10(p-vals). If you look at the -log10(p-vals) at the top of the list, you should find pathways that are really high in some groups and really low in other groups. The overall formula is calculated by taking the sum(KL-divergance)*range(-log10(p-vals)). The KL-divergence is looking for a difference in the distribution between the observed -log10(p-vals) and the distribution expected from an uninformative vector of -log10(p-vals) (this is a Gaussian null hypothesis). Then we multiply the sum(KL-divergance) by the range of -log10(p-vals) to let the most significant pathways with lots of information/low entropy rise to the top.")
            enrich_str+=add_file_link(sig_dir+"/combined_neg_log10p_gprofiler.txt",'combined pathway analyses')
            enrich_str+=add_p("and here is a file that has a normalized metric that ranks each pathway for their individual importance within each group. It would be useful to sort each of these and see what rises to the top for each 'cell type' or whatever your groups are.")
            enrich_str+=add_file_link(sig_dir+'/individual_class_importance.txt', 'individual class importance')
            enrich_str+=add_p("Below are all of the individual results so that you find which genes were in which pathways in individual groups:")
            enrich_str+=add_button_head("individual pathway files")
        enrich_str+="\t\t\t\t<ul>\n"
        for img in enrich_path:
            old_name = img[:-4]
            temp_name = old_name.split('_')
            temp_name = ' '.join(temp_name)
            #enrich_str+=add_p(temp_name)
            enrich_str+=add_file_link(pathway_dir+img,old_name)
            enrich_str+=add_br()


        if os.path.isfile(sig_dir+"/combined_neg_log10p_gprofiler.txt"):
            enrich_str+="\n\t\t</div>\n"

        enrich_str+="\t\t\t\t</ul>\n"
        enrich_str+="\n\t\t</div>\n"#end the sub-button
        enrich_str+=add_br()

    enrich_str+='\n</div>\n'
    return(enrich_str)


def add_community_pathway_annotation(com, individual_class_importance_table):
    if type(individual_class_importance_table) != np.ndarray:
        return(add_br())
    print(individual_class_importance_table)
    ## get the top 5 pathways
    ## first get the right column
    header = individual_class_importance_table[0,:]
    temp_col = np.where(header == com+"_gprofiler.txt")[0]
    print(temp_col)
    print(com,individual_class_importance_table[1:,temp_col])
    most_sig_order = np.argsort(np.array(individual_class_importance_table[1:,temp_col].tolist(),dtype=np.float32), axis = 0)[::-1] + 1
    #print(individual_class_importance_table[most_sig_order,temp_col])
    #print(most_sig_order)
    keep_rows = []
    for i in range(0,5):
        temp_row = most_sig_order[i]
        ## check if it's actually significant first
        print(individual_class_importance_table[temp_row,temp_col])
        if float(individual_class_importance_table[temp_row,temp_col]) > 0:
            keep_rows.append(temp_row)
    ## go through the rows that we're keeping & summarize them
    out_table = [["term_id","term_def","importance_metric"]]
    for i in keep_rows:
        temp_line = [individual_class_importance_table[i,1][0],individual_class_importance_table[i,3][0],individual_class_importance_table[i,temp_col][0]]
        out_table.append(temp_line)
    return(add_table(out_table)+add_br())


def add_community_top_markers(base_dir, com, community_annotations_file, top_n_markers = 15):
    com_marker_str = ""
    com_marker_str += add_button_head("top marker genes of "+com+" (defined by high Local PageRank)")
    ## read in the community annotations file
    try:
        com_anno_table = read_table(community_annotations_file)
    except:
        cur_dir = os.getcwd()
        os.chdir(base_dir)
        com_anno_table = read_table(community_annotations_file)
        os.chdir(cur_dir)
    else:
        com_anno_table = read_table(community_annotations_file)
    num_lines = min([len(com_anno_table),top_n_markers])
    temp_table = com_anno_table[:num_lines]
    # for i in range(len(temp_table)):
    #     print(temp_table[i])

    com_marker_str += add_p("this is a list of the top genes that are most central to this hub, and will therefore likely make good marker genes.")
    com_marker_str += add_table(temp_table)
    # print(add_table(temp_table))
    # sys.exit()
    com_marker_str += "</div>"## ends the button tab


    return(com_marker_str)



def add_community_str(base_dir, com, individual_class_importance_table):
    com_str = ""
    com_str += add_h3("Community module usage")
    com_str += add_community_pathway_annotation(com, individual_class_importance_table)
    com_dir = os.path.join(os.path.join("pos_cor_graphs/community_analysis/",com))
    community_annotations_file = os.path.join(com_dir,"community_ids_annotated.tsv")
    com_str += add_community_top_markers(base_dir, com, community_annotations_file)
    com_str += add_file_link(community_annotations_file,"This is the list of genes in the community.")
    com_str += add_br()
    com_str += add_file_link(os.path.join(com_dir,"TukeyHSD.tsv"),"This is the differential module usage across groups")
    com_str += add_p("And here is a plot showing the module usage across groups.")
    com_str += add_img(os.path.join(com_dir,"group_z_scores.png"),"Group Z-scores", base_dir = base_dir)
    com_str += add_br()
    com_str += add_p("This is where this community is in the network graph.")
    com_str += add_img(os.path.join(com_dir,"community.png"),"community subset", base_dir = base_dir)
    return(com_str)



def add_graph(base_dir):
    graph_str=""
    #graph_str+=add_h2("Expression graphs")
    graph_str+=add_button_head("Expression graphs")
    graph_str+=add_h3("Adjacency Lists:")
    adj_list_list = []
    os.chdir(base_dir)
    for f in glob.glob("*"):
        if 'adj_list' in f:
            adj_list_list.append(f)
    print(adj_list_list)
    for f in adj_list_list:
        if '_pos.tsv' in f:
            pos_adj = f
        elif '_neg.tsv' in f:
            neg_adj = f
        else:
            total_adj = f
    # graph_str+=add_p('Full adjacency list:')[:-6]+'</p>'
    # print(base_dir+total_adj)
    graph_str+="\t\t\t\t<ul>\n"
    graph_str+=add_file_link(total_adj,'Full adjacency list')
    graph_str+=add_br()
    graph_str+=add_file_link(pos_adj,'Positive correlation (co-expression) adjacency list')
    graph_str+=add_br()
    graph_str+=add_file_link(neg_adj,'Negative correlation adjacency list')
    graph_str+=add_br()
    graph_str+="\t\t\t\t</ul>\n"

    graph_str+=add_h2("Co-expression graph plots:")
    coexpression_graph_dir = "pos_cor_graphs/"
    graph_str+=add_h3("This is a 'hairball' view of a Spearman coexpression network of your data, where each point represents a gene, and the lines are whether or not a gene is correlated with another gene. The closer two genes are to each other, the more correlated they are.")
    graph_str+=add_img(coexpression_graph_dir+"full_graph.png",'Co-expression graph')
    if os.path.isfile(coexpression_graph_dir+"community.png"):
        graph_str+=add_h3("This is a graph of all the communities of genes that are coordinately regulated in your dataset")
        graph_str+=add_img(coexpression_graph_dir+"community.png",'communities')

    ## 
    community_dir = os.path.join(coexpression_graph_dir,"community_analysis")
    if os.path.isdir(community_dir):
        graph_str+=add_button_head('Analysis of individual communities')
        os.chdir(community_dir)
        ## first add the significance and pathway files
        graph_str+=add_br()
        graph_str+=add_file_link(os.path.join(base_dir, community_dir, "global_statistics.tsv"),"Here are the stats (BH corrected 1-way anova) for differential module usage among groups.")
        graph_str+=add_br()
        graph_str+=add_file_link(os.path.join(base_dir, community_dir, "combined_neg_log10p_gprofiler.txt"),"-log10(p-val) for the pathways associated with each module")
        graph_str+=add_br()
        individual_class_importance_file = os.path.join(base_dir, community_dir, "individual_class_importance.txt")
        graph_str+=add_file_link(individual_class_importance_file,"The unique pathways of each module (individual class importance).")
        graph_str+=add_br()
        ## second add the folders for each individual community
        print(os.getcwd())
        community_dirs = []
        for file in glob.glob('*'):
            if os.path.isdir(file):
                if file != 'gprofiler':
                    print(file)
                    community_dirs.append(file)

        ## catelogue how many genes are in each community
        com_num_dict = {}
        com_num_list = []
        for com in community_dirs:
            com_num_dict[com] = len(read_file(os.path.join(com,"community_ids.txt"),"lines"))
            com_num_list.append(com_num_dict[com])

        ## sort based on size
        new_order = np.argsort(np.array(com_num_list))[::-1]
        community_dirs = np.array(community_dirs)[new_order].tolist()
        if os.path.isfile(individual_class_importance_file):
            individual_class_importance_table = np.array(read_table(individual_class_importance_file))
        else:
            individual_class_importance_table = "None"
        for com in community_dirs:
            graph_str+=add_button_head(com+" ("+str(com_num_dict[com])+" nodes)")
            graph_str+=add_community_str(base_dir, com, individual_class_importance_table)
            graph_str+="\n\t\t</div>\n"
            #graph_str+=add_br()


        #graph_str+="\n\t\t</div>\n"
        graph_str+=add_br()
        graph_str+="\n\t</div>\n"
        os.chdir('../..')
        print(os.getcwd())

    if os.path.isfile(coexpression_graph_dir+"PageRank.png"):
        graph_str+=add_h3("PageRank is a metric for how well connected a gene is in the coexpression network")
        graph_str+=add_img(coexpression_graph_dir+"PageRank.png",'Page-Rank')
    if os.path.isfile(coexpression_graph_dir+"LPR.png"):
        graph_str+=add_h3("Local PageRank is a derivative of both Louvain-modularity based community detection and PageRank. It essentially calculates a normalized PageRank within each module to quantify local connectivy throughout the graph.")
        graph_str+=add_img(coexpression_graph_dir+"LPR.png",'Local PageRank')
    graph_str+=add_h3("Here are the Z-scores for each group overlaid on the co-expression graph (red means it's enriched in that group, blue means it's low expression or not expressed):")

    ## find all of the pertinent files, and
    graph_str+=add_button_head('Z-score overlaid co-expression graphs')
    os.chdir(coexpression_graph_dir)
    extra_images = []
    for file in glob.glob('*.png'):
        if 'sample_group' in file:
            extra_images.append(file)
    extra_images = sorted(extra_images)
    os.chdir(base_dir)
    for img in extra_images:
        new,old = parse_file_name(img)
        graph_str+=add_p(new)
        graph_str+=add_img(coexpression_graph_dir+img, new)
    graph_str+="\n\t\t</div>\n"
    graph_str+=add_br()
    graph_str+="\n\t</div>\n"
    return(graph_str)


def add_img_list(list_of_images,temp_dir):
    output = ""
    for img in list_of_images:
        new,old = parse_file_name(img)
        output+=add_p(new)
        output+=add_img(temp_dir+img, new)
    return(output)


def add_genes_of_interest(base_dir):
    goi_str=""
    goi_dir = 'genes_of_interest/'
    if os.path.isdir(goi_dir):
        goi_str+=add_button_head('Genes of interest')
        goi_str+=add_p("An interesting way to use the structure of the graphs generated by MANAclust is looking at how far away all genes in your dataset are away from your genes of interest. We've shown in the MANAclust paper that there are many types of functional enrichment that correlate with how far away a gene is from another gene in the graph network. For example, close to a transcription factor are more likely to have a binding site for that transcription factor when compared to a gene that's father away from it. There is also an increased probability that two genes will encoded proteins that have a physical intereaction when those two genes are directly connected (i.e. 1-degree of separation).")
        goi_str+=add_p('below is a file containing a table that has the distance of all genes in the genome away from your gene(s) of interest.')
        goi_str+=add_file_link(goi_dir+'genes_of_interest_shortest_path_list.txt','Shortest path of all genes away from your genes of interest')
        goi_str+=add_p('Below is a heatmap of your genes of interest:')
        goi_str+=add_img(goi_dir+'genes_of_interest_subset_heatmap.png','genes of interest heatmap')

        ## collect the other images
        os.chdir(goi_dir)
        additional_images = []
        for f in glob.glob('*.png'):
            if f != 'genes_of_interest_subset_heatmap.png':
                additional_images.append(f)
        goi_str+=add_button_head("additional plots for your genes of interest")
        os.chdir(base_dir)
        goi_str+=add_img_list(sorted(additional_images),goi_dir)
        goi_str+='\n\t\t</div>\n'

        goi_str+="\n</div>\n"

    return(goi_str)


def add_autocrine_paracrine(base_dir):
    ap_dir = "autocrine_paracrine_signaling/"
    ap_str=""
    if not os.path.isdir(ap_dir):
        return(ap_str)
    else:
        ap_str+=add_button_head("Autocrine/paracrine signaling")
        ap_str+=add_p("Below are the predicted signaling networks")
        ap_str+=add_file_link(ap_dir+'all_cell_cell_interaction_summary.txt','Number of interactions between all of the groups')
        ap_str+=add_br()
        ap_str+=add_file_link(ap_dir+'all_cell_type_specific_interactions.txt','A detailed summary of each autocrine/paracrine interaction')
        ap_str+=add_br()
        ap_str+=add_file_link(ap_dir+'all_cell_type_specific_interactions_gprofiler.txt','A detailed summary of the pathways signaling across and within groups')
        ap_str+=add_br()
        ap_str+=add_file_link(ap_dir+'combined_neg_log10p_gprofiler.txt','A table of negative log10 p-values that for each pathway in each interaction. (Zero just means it did not reach signficance)')
        ap_str+=add_br()
        ap_str+=add_file_link(ap_dir+'individual_class_importance.txt','A table of the individual importance of each pathway for the given group')
        
    return(ap_str)
        #combined_neg_log10p_gprofiler.txt
        #individual_class_importance.txt


def add_gene_annotations(base_dir):
    anno_str=""
    if os.path.isfile("annotations.tsv"):
        anno_str+=add_p("Here are the annotations for your genes. You can use this in excel using v-lookup if you want to get gene symbols or definitions for any of the other files.")
        anno_str+=add_file_link("annotations.tsv","Annotation file")
    if os.path.isfile("human_orthologues.tsv"):
        anno_str+=add_br()
        anno_str+=add_file_link("human_orthologues.tsv","Human orthologues to your genes")
    anno_str+=add_br()
    return(anno_str)

def add_high_marker_genes(base_dir):
    marker_str = ""
    marker_dir = "sample_clustering_and_summary/significance/high_markers/"
    if not os.path.isfile(marker_dir+'marker_gene_annotations.tsv'):
        return("")
    else:
        marker_str+=add_button_head("Highly expressed group-specific markers")
        marker_str+=add_p("MANAclust analyzes the mean expression of each sample group and then looks for genes that meet three criteria.")
        #marker_str+=add_br()
        marker_str+=add_p("\t1) The gene is significant by 1-way ANOVA (after BH correction, alpha=0.05).")
        #marker_str+=add_br()
        marker_str+=add_p("\t2) The distance between the group with highest mean expression and second highest expression is calculated. If a gene is in the top 90th percentile of this calculation, it can make it through.")
        #marker_str+=add_br()
        marker_str+=add_p("\t3) A metric called the q-value is calculated (usually to identify outliers). The q-value is the ratio of the value calculated in number 2 compared to the range of sample group means. It's essentially what percent of the range is attributable to the distance between the highest expressing group vs the second highest expressing group.")
        #marker_str+=add_br()
        marker_str+=add_p("If all three of these criteria are, met you'll find it with an annotated group in the file below. Note that if you have several very closely related groups, there might not be many highly expressed genes that are exclusivly expressed in an individual group. In this case, you might need several markers at once to descriminate them.")
        #marker_str+=add_br()
        marker_str+=add_file_link(marker_dir+'marker_gene_annotations.tsv',"Highly expressed marker genes")
        marker_str+=add_img(marker_dir+'genes_of_interest_subset_heatmap.png',"High expression marker genes")
        marker_str+='\n</div>\n'
        return(marker_str)


###########################################################

def clean_dirs(in_dirs):
    return([d.replace('/','') for d in in_dirs])



def get_input_file_names(base_dir):
    """
    takes in the base_dir and gets you (1) a list of the categorical input files and (2) a list of the numeric input files

    example:
    input:
    get_input_file_names(base_dir)
    output:
    ["cat_1", "cat_2"], ["num_1", "num_2"]
    """
    
    ## first get the categorical ones
    cat_files = []
    for temp_file in glob.glob('*_high_info_labels.tsv'):
        cat_files.append(temp_file)
    ## strip them
    for i in range(len(cat_files)):
        cat_files[i]=cat_files[i].replace('_high_info_labels.tsv','')
    cat_files = sorted(list(set(cat_files)))

    ## now the numeric files
    num_files = []
    for temp_file in glob.glob('*_labels.tsv'):
        if not '_high_info_' in temp_file:
            #print(temp_file)
            num_files.append(temp_file)
    ## strip them
    for i in range(len(num_files)):
        num_files[i]=num_files[i].replace('_labels.tsv','')
    num_files = sorted(list(set(num_files)))

    cat_files = clean_dirs(cat_files)
    num_files = clean_dirs(num_files)
    return(cat_files, num_files)

###########################################################


def add_single_cat_feat(dataset):
    cat_feat = ""
    cat_feat += add_button_head(dataset+"'s feature selection")
    cat_feat += add_h2(dataset+"'s affinity matrix when calculated withOUT feature selection:")
    cat_feat += add_img(dataset+"_without_feature_selection.png",dataset+"w.o_feat")
    cat_feat += add_h2(dataset+"'s affinity matrix when calculated WITH feature selection:")
    cat_feat += add_img(dataset+"_high_info_with_feature_selection.png",dataset+"w._feat")
    cat_feat += '\n</div>\n'
    return(cat_feat)


def add_single_num_feat(dataset):
    num_feat = ""
    num_feat += add_button_head(dataset+"'s feature selection")
    num_feat += add_h2(dataset+"'s affinity matrix when calculated withOUT feature selection:")
    num_feat += add_img(dataset+"_without_feature_selection.png",dataset+"w.o_feat")
    num_feat += add_h2(dataset+"'s affinity matrix when calculated WITH feature selection:")
    num_feat += add_img(dataset+"_with_feature_selection.png",dataset+"w._feat")
    ## now heatmaps
    num_feat += add_h2("A heatmap for "+dataset+" withOUT feature selection:")
    num_feat += add_img(os.path.join(dataset,dataset+"_sample_of_all_features.png"),dataset+"w.o_feat_heat")
    num_feat += add_h2("A heatmap for "+dataset+" WITH feature selection:")
    num_feat += add_img(os.path.join(dataset,dataset+"_selected_features.png"),dataset+"w._feat_heat")
    num_feat += '\n</div>\n'
    return(num_feat)


def add_tab_header(section_name, default_open=False):
    out_head = "<div id='"+section_name+"' class='w3-container w3-border city'"
    if not default_open:
        out_head += ' style="display:none"'
    else:
        out_head += ' style="display: block;"'
    out_head += '>'
    return(out_head)


def add_feat_select(base_dir, cat_files, num_files):
    feat_str = ""
    feat_str += add_tab_header("Feature Selection", default_open=False)
    #feat_str+=add_button_head("Feature selection results")
    feat_str+=add_p("\nOne of the first things that MANAclust does is feature selection. Often times, for unsupervised clustering, one doesn't know which features will be imporant and which ones are just randomly adding unpatterned variance. MANAclust tackles this problem for both categorical datasets and numeric datasets, which are listed below:")
    if len(cat_files)>0:
        feat_str+=add_button_head("Categorical datasets")
        ## add the documentation for each of the categorical datasets
        feat_str+=add_p("\nCategorical feature selection is based on the pairwise feature-feature mutual information, when compared to a shuffled version of the dataset comparing your real data to a null distribution. Below are depictions of the sample-sample affinity matrix as calculated through the sum of the log-loss or categorical cross entropy between subjects. There is one affinity matrix showing what the dataset looks like before feature selection, then another that shows the affinity matrix after.")
        for cat_file in cat_files:
            feat_str+=add_single_cat_feat(cat_file)
        feat_str+='\n</div>\n'
    if len(num_files)>0:
        feat_str+=add_button_head("Numeric datasets")
        ## add the documentation for each of the numeric datasets
        feat_str+=add_p("\nNumeric feature selection is based on the pairwise feature-feature mutual information, when compared to a shuffled version of the dataset comparing the distribution of negative Spearman Rhos to your actual dataset, selecting features that have notably more negative correlatoins than expected by chance. Below are depictions of the sample-sample affinity matrix as calculated through the normalized negative squared Eculidean distance across samples. There is one affinity matrix showing what the dataset looks like before feature selection, then another that shows the affinity matrix after. Also included below are heatmaps of the datasets pre- and post- feature selection.")
        for num_file in num_files:
            feat_str+=add_single_num_feat(num_file)
        feat_str+='\n</div>\n' 


    #feat_str+=add_br()
    feat_str+=add_button_head("Final Merged Datasets")
    feat_str+=add_p("MANAclust calculates a final merged affinity matrix through normalizing each of the input & taking the missing-value compatible mean of all affinity matrices. In this way, subtle differences that are consistent across datasets will re-inforce each other, while large differences in a single dataset will still split off a new final cluster. Similarly, strong concordance in a single dataset won't over-power consistent differences across other datasets. Imporantly, because it's a missing-value compatible calculation, you can use it in a real-word context where this is the norm rather than the exception!")+add_p("\n")+add_p("Below we show the merged affinity matrix with and without feature selection. We also show a 2D projection (using the UMAP) algorithm of the affinity matrices.")
    feat_str+=add_h2("Below is the final affinity matrix and UMAP projection if we DIDN'T do feature selection")
    feat_str+=add_p("Merged affinity matrix without feature selection:")
    feat_str+=add_img("final_affinity_matrix_without_feature_selection.png","final_affinity_matrix_without_feature_selection")
    feat_str+=add_p("2D projection of merged affinity matrix without feature selection:")
    feat_str+=add_img("final_affinity_matrix_umap_without_feature_selection_clustering.png","final_affinity_matrix_umap_without_feature_selection_clustering")
    feat_str+=add_h2("Below is the final affinity matrix if we DO use feature selection")
    feat_str+=add_p("Merged affinity matrix WITH feature selection:")
    feat_str+=add_img("final_affinity_matrix_with_feature_selection.png","final_affinity_matrix_with_feature_selection")
    feat_str+=add_p("2D projection of merged affinity matrix WITH feature selection:")
    feat_str+=add_img("final_affinity_matrix_umap_with_feature_selection_clustering.png","final_affinity_matrix_umap_with_feature_selection_clustering")
    #feat_str+=add_br()
    feat_str+='\n</div>\n'

    feat_str+='\n</div>\n'

    feat_str+='\n</div>\n'
    #feat_str+=add_br()
    return(feat_str)


def add_final_cluster_sections(base_dir, cat_files, num_files, with_feat = True):
    group_annotatoins
    if with_feat:
        image_ender = "with_feature_selection.png"
        label_ender = "_labels.tsv"
    else:
        image_ender = "without_feature_selection.png"
        label_ender = "_labels_full.tsv"
    ## first do the final clustering results

    ## first do the cat files

    ## then do the num files

    ## then add the images
    return()

def add_group_annotations(base_dir, cat_files, num_files):
    ##
    group_str = ""
    group_str+=add_tab_header("Sample Groups")
    #group_str+=add_button_head("Sample groups - both the final clusters & the consensus groups from the input datasets")
    #group_str+=add_br()
    group_str += add_h2("Final clusters:")
    group_str += add_p("Below are the annotatoins for each sample/subject and their ")
    group_str += add_file_link("sample_final_cluster_and_consensus_group_annotations.tsv", "Each sample's final cluster and data-set level consensus group IDs")
    group_str += add_h2("Final cluster to Consensus Group Mappings:")
    group_str += add_p("Every final cluster maps to a unique combination of the consnesus groups from your input datasets. Below is the table that maps from the final clusters to the consensus groups for the input datasets. If you're looking for some pretty plots, there are some of those in the feature selection tab that plots the samples/subjects as affinity matrices and 2D UMAP projections of those affinity matrices. Note that if a subject was missing an ome, it of course won't have a consensus group label for that dataset, instead it will say 'NA'.")
    group_str += add_file_link("final_clusters_to_consensus_group_annotations.tsv","File with mappings between final clusters and consensus groups.")
    group_str += add_table(read_table(os.path.join("final_clusters_to_consensus_group_annotations.tsv"))) + add_br()

    group_str+='\n</div>\n'
    group_str+='\n</div>\n'
    #group_str+=add_br()
    return(group_str)




def add_between_con_groups(base_dir, cat_files, num_files):
    ##
    btw_con_group_str = ""
    btw_con_group_str+=add_button_head("What is the relationship between each of the consensus groups?")
    ## first add a paragraph describing what this means

    ## then go through each of the 



    btw_con_group_str+='\n</div>\n'
    btw_con_group_str+=add_br()
    return(btw_con_group_str)

def add_stats_results(dataset_dir, dataset_name, consensus=False):
    if consensus:
        leader = os.path.join(dataset_dir, "consensus_groups", dataset_name)
    else:
        leader = os.path.join(dataset_dir, dataset_name)
    temp_str = ""
    temp_str += add_file_link(leader+"_global_statistical_differences.tsv","\nAll global statistics")
    temp_str += add_p("\n")
    temp_str += add_file_link(leader+"_all_significant_postHocs.tsv","\nSignificant pair-wise post-hoc tests")
    temp_str += add_p("\nThe total number of signficant post-hoc differences across the groups:")
    temp_str += add_img(leader+"_number_different_across_groups.png", "num_dif")
    return(temp_str)


def add_single_dataset_stats(dataset_dir, dataset_name):
    leader = dataset_name.replace('/','')
    #print(leader)
    single_dataset_str=""
    ## add button for dataset
    single_dataset_str+=add_button_head(str(dataset_dir))
    #### add button for final groups
    single_dataset_str+=add_button_head("Stats for '"+str(dataset_dir)+"' based on the final clusters")
    #### add paragraph about the next results that are testing the final groups
    single_dataset_str+=add_p("\nThese are the statistics for '"+str(dataset_dir)+"' based on the final clusters. Note that there could be some groups that have essentially no difference. When this happens, it's becuase these groups were essentially the same by this dataset (and likely came out in the same consensus group), but they were orthogonal to each other by a different dataset. If you're interested in seeing the consensus group results, they're on the next button down. That tab also shows how many significant differences there were between the final clusters & the statistics that led to the creation of the consensus groups.")
    #### add the final group stats for this ome
    single_dataset_str+=add_stats_results(dataset_dir, leader, consensus = False)



    ## add br
    single_dataset_str+='\n</div>\n'

    single_dataset_str+=add_button_head("Stats for '"+str(dataset_dir)+"' based on the consensus groups")
    #### add button for consensus group analysis
    single_dataset_str+=add_p("\nThese are the statistics for '"+str(dataset_dir)+"' based on the consensus groups for this ome. We also have below the statistics of the final-groups that led to some of them (perhaps) being merged into single consensus groups.")

    #### first add the images and descriptions about how the consensus groups are made
    single_dataset_str+=add_p("\n\tThis shows each of the final clusters & the probability that their members came from the same distribution within this ome. This was calculated by comparing the within-final-group to across final-group affinities for this dataset by ANOVA, then Benjamini-Hochberg correcting this probability for all of these comparisons. This gives us a final probability that these subjects came from the same distribution. This matrix was then transformed into a p-value weighted network graph, that was subjected to Louvain-modularity analysis to determine the consensus groups for this dataset.")
    single_dataset_str+=add_img(os.path.join(dataset_dir,leader+"_affinity_BH_p_val_matrix.png"), "BH_p_val")

    single_dataset_str+=add_p("\n\tThis is the negative log10 p-values of the probabilities from above.")
    single_dataset_str+=add_img(os.path.join(dataset_dir,leader+"_affinity_neg_log10_BH_p_val_matrix.png"), "BH_p_val")

    single_dataset_str+=add_p("\n\tThis shows the F statistic for the ANOVAs calculated above.")
    single_dataset_str+=add_img(os.path.join(dataset_dir,leader+"_affinity_F_statistic_matrix.png"), "F_stat")

    single_dataset_str+=add_p("\n\tBelow are the global and pairwise statistics for each of the consensus group level comparisons for this dataset:")
    #### then add the consensus group folder
    single_dataset_str+=add_stats_results(dataset_dir, leader, consensus = True)

    single_dataset_str+='\n</div>\n'

    single_dataset_str+='\n</div>\n'
    single_dataset_str+=add_br()    
    return(single_dataset_str)


def add_sig_dif_between_groups(base_dir):
    ##
    sig_dif_str = ""
    sig_dif_str+=add_tab_header("Significant Differences")
    #sig_dif_str+=add_button_head("What are the significant differences between these groups?")
    ## add a paragraph about what each 
    sig_dif_str+=add_p('\n')+add_p("For each of your input datasets (including the 'test' datasets that weren't used for clustering - if there were any), below are the traditional statistics comparing each of the 'final clusters' to each other as well as the within-dataset consensus group differences. This can help find biomarkers for consensus groups or final clusters.")
    sig_dif_str+=add_p('\n')+add_p("For all catagorical datasets, we first do a global chi-square test in which we look at the frequency of each category relative to each of the final or consensus groups. These are then Benjamini-Hochberg FDR corrected. Anything that was signficant (default is FDR-q<0.001, set by the '-alpha' parameter) is then passed through to do pairwise Chi-squares, again BH-FDR corrected. Note that in mixed numeric/categorical datasets that were fed in as categorical datasets, the numeric or mixed variables are converted to binned values & treated as categrical - this can be seen as similar to doing a maximum-informatoin style test on numeric datasets, except it's just chi-square.")
    sig_dif_str+=add_p('\n')+add_p("For the numeric datasets, a similar procedure is done as with the above categorical datasets, except they're tested by ANOVAs instead of chi-square.")

    ## make a button for each input dataset & list out & describe the files/images
    dataset_dirs = []
    for temp_path in glob.glob('*'):
        if os.path.isdir(temp_path):
            if temp_path not in ["test_ome_differences_by_consensus_groups", "between_ome_consensus_group_comparisons"]:
                dataset_dirs.append(temp_path)
    dataset_dirs = clean_dirs(sorted(dataset_dirs))
    for temp_dir in dataset_dirs:
        sig_dif_str+=add_single_dataset_stats(temp_dir,temp_dir)

    sig_dif_str+='\n</div>\n'
    sig_dif_str+='\n</div>\n'
    #sig_dif_str+=add_br()
    return(sig_dif_str)


def add_single_test_ome(test_ome_dir):
    test_ome_dir = os.path.join("test_ome_differences_by_consensus_groups",test_ome_dir)
    test_ome_name = os.path.basename(os.path.normpath(test_ome_dir))
    dataset_dirs = []
    for temp_path in glob.glob(os.path.join(str(test_ome_dir))+os.path.sep+'*'):
        #print(temp_path,'in',test_ome_dir)
        if os.path.isdir(temp_path):
            dataset_dirs.append(temp_path)
            #print("\t\t",dataset_dirs[-1])
    
    out_str = ""
    for temp_sub_dataset in dataset_dirs:
        temp_name = os.path.basename(os.path.normpath(temp_sub_dataset))
        out_str+=add_button_head(temp_name)
        #print("\n\n",temp_sub_dataset)
        out_str+=add_stats_results(temp_sub_dataset, test_ome_name)
        out_str+='\n</div>\n'

    return(out_str)



def add_test_omes(base_dir):
    #print("\ndoing test omes")
    #test_dir = os.path.join(base_dir,"test_ome_differences_by_consensus_groups")
    test_dir = "test_ome_differences_by_consensus_groups"
    test_v_con_str = ""
    test_v_con_str+= add_tab_header("Test Ome Significant Differences")
    if not os.path.isdir(test_dir):
        test_v_con_str += add_h2("No test omes were used in this analysis")
        test_v_con_str+='\n</div>\n'
        return(test_v_con_str)
    test_v_con_str+=add_h2("How do the consensus groups based on your input datasets differ in the test datasets?")
    test_v_con_str+= add_p("In these statistical comparisons, we assessed each variable in each of the test datasets based on their group membership based on all of the consensus groups from the other omes. In this way, you can find out what 'If we take the consensus groups from ome X, what would be the sinificant differences in ome Y?'")

    dataset_dirs = []
    for temp_path in glob.glob('test_ome_differences_by_consensus_groups'+os.path.sep+'*'):
        if os.path.isdir(temp_path):
            dataset_dirs.append(temp_path.replace("test_ome_differences_by_consensus_groups/",''))


    for dataset in dataset_dirs:
        ## add button
        #print('\t',dataset)
        test_v_con_str+=add_button_head(dataset)
        test_v_con_str+=add_p("\nBelow are how the above test ome was different when using the consensus groups as defined by the following input datasets used for clustering:")
        test_v_con_str+=add_single_test_ome(dataset)
        test_v_con_str+='\n</div>\n'


    test_v_con_str+='\n</div>\n'
    test_v_con_str+='\n</div>\n'

    #test_v_con_str+=add_br()
    return(test_v_con_str)


def add_pre_button_header(base_dir):
    pre_button_header = ""
    ## add a short paragraph about MANAclust, what it does & what the results are below.


    ## add the final group annotatoins

    return(pre_button_header)


def add_final_level_cross_ome_comparison(final_dir, final_name):
    final_layer_cross_ome_str = ""
    ## add the button
    final_layer_cross_ome_str += add_button_head(" -- VS -- ".join(final_name.split("_vs_")))
    ## first add the contingency table
    final_layer_cross_ome_str += add_h3("Contingency table:")
    final_layer_cross_ome_str += add_img(os.path.join(final_dir,"contingency_table.png"),"cont_table")
    ## then residuals
    final_layer_cross_ome_str += add_h3("Chi-squared adjusted residuals:")
    final_layer_cross_ome_str += add_p("Chi-squared adjusted residuals is kind of like a 'Z-score' for chi-quared analyses. So a high positive the number in the below matrix means that we observed far more samples/subjects here than we would expect by chance. A very negative number means that these two consensus groups were unexpectedly discordant.")
    final_layer_cross_ome_str += add_img(os.path.join(final_dir,"chi_adjusted_residuals.png"),"chi_adj_res")
    ## then p-values
    final_layer_cross_ome_str += add_h3("BH-FDR corrected p-values:")
    final_layer_cross_ome_str += add_img(os.path.join(final_dir,"adjusted_p_values.png"),"p-vals")
    ## close the button
    final_layer_cross_ome_str +='\n</div>\n'
    return(final_layer_cross_ome_str)


def add_subdir_cross_ome(in_base):
    subdir_str = ""
    dataset_dirs = []
    comparison_names = []
    print('\n\nDoing',in_base+os.path.sep+'*')
    for temp_path in glob.glob(in_base+os.path.sep+'*'):
        #print('\tChecking:',temp_path)
        if os.path.isdir(temp_path):
            dataset_dirs.append(temp_path)
            temp_name = os.path.basename(os.path.normpath(temp_path))
            comparison_names.append(temp_name)
    for i in range(len(dataset_dirs)):
        print('\t',comparison_names[i])
        subdir_str += add_final_level_cross_ome_comparison(dataset_dirs[i], comparison_names[i])
    return(subdir_str)


def add_cross_ome_stats():
    cross_ome_str=""
    base = "between_ome_consensus_group_comparisons"
    sub_dirs = ["between_cluster_and_test_omes",
                "between_clustering_omes",
                "between_test_omes"]
    cross_ome_comparison_dirs = [os.path.join(base,temp_dir) for temp_dir in sub_dirs]
    ## first make the top button
    cross_ome_str += add_tab_header("Cross Ome Concordance")
    #cross_ome_str += add_button_head("How concordant/discordant are consensus groups with each other?")
    ## add a paragraph describing what's below
    cross_ome_str += add_p("\nHere, we look at the subjects that lie in each consensus group from each of the datasets & look for how concordant/discordant the members from each of these datasets are. For example, take the hypothetical that two input datasets essentially carry the same information (ie: subjects that are similar to each other in one dataset are also similar to each other in the other dataset); the subjects in dataset #1, consensus cluster #1 might be the same subjects that are present in dataset #2 consnesus cluster #3. We assess this concordance/discordance through chi-squared tests. Below are the Chi-square results for the comparison of consensus groups from the input datasets used for clustering, input vs test datasets, and test vs test datasets.")+add_p("\n")+add_p("The contingency tables list the number of subjects belonging to each of the pairwise groups.")+add_p("\n")+add_p("The adjusted residuals table can be interpreted like Z-scores for the contingency table, indicating how over- or under- abundant a given cell in the matrix is.")+add_p("\n")+add_p("These are then used to calculate the cell-wise p-values, which are BH-FDR corrected for multiple comparisons.")
    cross_ome_str += add_file_link(os.path.join(base,"all_combined_cross_ome_concordance_discordance_statistics.tsv"),"Here is a summary of all of the datasets & their consensus group concordance/discordance.")
    cross_ome_str += add_p("This includes the 'adacency list' with Bayesian statistics showing the probability of being in one consensus group of from one data type, given that you're a member \
        of another consensus group in a different datatype. For example: P(A|B) means the probability of being in group A, given that you're a member of group B. \
     In this scenario, this might equate to: What's the probability of being in Transcriptome consensus group 0, given that you're in Methylome consensus group 3? This probability can range from 0, to 1, \
     In the before example, if P(Transcriptome||consensus_group_1 | Methylome||consensus_group_3) = 1, that means that ALL of the Methylome||consensus_group_3 members were also members of Transcriptome||consensus_group_1. This can be loosly interpreted as direcitonality, \
     but in reality, you'd need an intervention/experiment to prove it.")
    cross_ome_str += add_p("In each of the sub-tabs below, there are subsets of the above combined results.")
    cross_ome_str += add_p("You can also use this file as a 'Bayesian-like network' (although, it's a little different) - it could be very useful to import \
        this into [cytoscape](https://cytoscape.org/download.html), and create some filters to *suggest* causal relationships. \
        You can do this, by setting up some filters, like: ")
    cross_ome_str += add_p("\t1) keeping only edges that are signficant by BH-corrected p-values from the Chi-squared")
    cross_ome_str += add_p("\t2) keeping only edges that have a positive adjusted residuals (this means that these two groups are positively concordant, rather than discordant)")
    cross_ome_str += add_p("\t3) keeping edges that have a P(group2|group1)-P(group1|group2) value > -0.15 (or something like that). This allows for some 'ties' in directionality, \
        where the probility of going in one direction is fairly similar to going in the other direction.")
    cross_ome_str += add_p("I also like to plot the edge width based on the P(group2|group1) value as this shows the magnitude of the effect.")
    ## second
    cross_ome_str += add_button_head("Input clustering datasets -- VS -- other input clustering datasets")
    cross_ome_str += add_br()
    cross_ome_str += add_file_link(os.path.join(cross_ome_comparison_dirs[1],"cross_ome_concordance_discordance_statistics.tsv"),"Here is a summary of all of the clustering datasets & their consensus group concordance/discordance")
    cross_ome_str += add_br()
    cross_ome_str += add_subdir_cross_ome(cross_ome_comparison_dirs[1])
    cross_ome_str += "\n</div>\n"
    ## first
    cross_ome_str += add_button_head("Input clustering datasets -- VS -- those used for testing")
    cross_ome_str += add_br()
    cross_ome_str += add_file_link(os.path.join(cross_ome_comparison_dirs[0],"cross_ome_concordance_discordance_statistics.tsv"),"Here is a summary of all of the clustering vs test datasets & their consensus group concordance/discordance")
    cross_ome_str += add_br()
    cross_ome_str += add_subdir_cross_ome(cross_ome_comparison_dirs[0])
    cross_ome_str += "\n</div>\n"
    ## third
    cross_ome_str += add_button_head("Test dataset consnensus groups -- VS -- other test datasets")
    cross_ome_str += add_br()
    cross_ome_str += add_file_link(os.path.join(cross_ome_comparison_dirs[2],"cross_ome_concordance_discordance_statistics.tsv"),"Here is a summary of all of the test datasets & their consensus group concordance/discordance")
    cross_ome_str += add_br()
    cross_ome_str += add_subdir_cross_ome(cross_ome_comparison_dirs[2])
    cross_ome_str += "\n</div>\n"
    cross_ome_str += "\n</div>\n"

    ## close this sub-set
    cross_ome_str += "\n</div>\n"
    return(cross_ome_str)


def add_summary():
    summary_str = ""
    summary_str += add_tab_header("Summary",default_open=True)
    summary_str += add_h2("Welcome to the MANAclust output walkthrough!")
    summary_str += add_p("MANAclust works in several stages, which each has a tab located above. Here's a brief description of what each of those tabs holds and what it means.")
    summary_str += add_h3("Feature Selection")
    summary_str += add_p("In brief, MANAclust took your input numeric and categorical datasets, found which of the features were adding structure to those datasets, \
        converted the datastes into cross-subject affinity matrices (how similar subjects are to each other), merged them together and clustered them using affinity propagation. \
        This tab has plots of the affinity matrices for each ome with and without feature selection \
        as well as plots showing the final clusters.")
    summary_str += add_h3("Sample Groups")
    summary_str += add_p("Once the clustering has been completed, the final clusters (which used all of the input datasets) as well as the 'consensus groups' which are \
     the within-dataset groups are annotated. The files and tables in this tab annotate which subject belongs to which final cluster as well as the consensus groups within each dataset.")
    summary_str += add_h3("Significant Differences")
    summary_str += add_p("For each dataset, MANAclust went through and calculated signficant differences of all of the features of each dataset, comparing (1) final clusters to each other, and \
        (2) consensus groups for the given ome.")
    summary_str += add_h3("Test Ome Significant Differences")
    summary_str += add_p("Similar to the above described significant differences, except, in this tab, we assessed signficant differences in the held-out test omes (if any were used),\
     and ran comparisons for the consensus groups of the other input datasets. \
     So for example, if you performed clustering using the methylome and transcriptome, but had a dataset A (categorical or numeric) that you wanted to use, not for clustering, but just to look at the differences in \
     based on the clustering results from methylome & transcriptome - this is where you'd find those statistical comparisons.")
    summary_str += add_h3("Cross Ome Concordance: How do these different datasets weave together?")
    summary_str += add_p("One imprtant aspect of multi-omics is determining whether or not your input datasets had shared components of variance, or of they were actually orthogonal to each other, providing \
        completely different information. MANAclust went through each one of your consensus groups from each pair of input datasets & assessed whether any of these consensus groups were significantly concordant with each other \
        or significantly discordant. For example, in Dataset1, if all of the subjects in consensus group 0, were all the same people in Dataset2 consensus group 3, you'd have a signficant result here. This is measured by \
        Chi-squared analysis, using the Chi-squared adjusted residuals to show over-abundance (positive value), or discordance between two groups (negative value).")
    summary_str += add_p("Furthermore, we also automated generation of Bayesian statistics. This lets you build a Bayesian-like network to hypothesize potential causal relationships across omes. Check out the tab for more details!")
    summary_str += "\n</div>\n"
    return(summary_str)

###########################################################

def make_webpage(base_dir):
    #out_file = os.path.join(base_dir, "MANAclust_summary.html")
    out_file = "MANAclust_summary.html"
    os.chdir(base_dir)


    ## first add the generic heading
    out_web = """<!DOCTYPE html>
    <html>

    <title>MANAclust Results</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    .collapsible {
        background-color: #777;
        color: white;
        cursor: pointer;
        padding: 18px;
        width: 100%;
        border: none;
        text-align: left;
        outline: none;
        font-size: 15px;
    }

    .active, .collapsible:hover {
        background-color: #555;
    }

    .content {
        padding: 0 18px;
        display: none;
        overflow: hidden;
        background-color: #f1f1f1;
    }
    table {
      font-family: arial, sans-serif;
      border-collapse: collapse;
      width: 100%;
    }

    td, th {
      border: 1px solid #dddddd;
      text-align: left;
      padding: 8px;
    }

    tr:nth-child(even) {
      background-color: #dddddd;
    }
    </style>
    </head>

    <body>





    <div class="w3-container w3-teal">
       <h1>MANAclust Results</h1>
    </div>


    <div class="w3-container">
      
      <div class="w3-bar w3-black">
        <button class="w3-bar-item w3-button tablink w3-red" onclick="openCity(event,'Summary')">Summary</button>
        <button class="w3-bar-item w3-button tablink" onclick="openCity(event,'Feature Selection')">Feature Selection</button>
        <button class="w3-bar-item w3-button tablink" onclick="openCity(event,'Sample Groups')">Sample Groups</button>
        <button class="w3-bar-item w3-button tablink" onclick="openCity(event,'Significant Differences')">Significant Differences</button>
        <button class="w3-bar-item w3-button tablink" onclick="openCity(event,'Test Ome Significant Differences')">Test Ome Significant Differences</button>
        <button class="w3-bar-item w3-button tablink" onclick="openCity(event,'Cross Ome Concordance')">Cross Ome Concordance</button>
      </div>
      
    </div>


    """

    ## get all of the input datasets
    cat_files, num_files = get_input_file_names(base_dir)

    ## print out the categorical ones
    if len(cat_files)>0:
        print("found",len(cat_files), "categorical files")
        for c in cat_files:
            print("\t",c)

    ## print out the numeric ones
    if len(num_files)>0:
        print("found",len(num_files), "numeric files")
        for c in num_files:
            print("\t",c)

    ## add the bulk of the content
    out_web+=add_pre_button_header(base_dir)
    out_web+=add_summary()
    out_web+=add_feat_select(base_dir, cat_files, num_files)
    out_web+=add_group_annotations(base_dir, cat_files, num_files)
    out_web+=add_sig_dif_between_groups(base_dir)
    out_web+=add_test_omes(base_dir)
    out_web+=add_cross_ome_stats()

    out_web+="""


    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
    </script>


    <script>
    function openCity(evt, cityName) {
      var i, x, tablinks;
      x = document.getElementsByClassName("city");
      for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
      }
      tablinks = document.getElementsByClassName("tablink");
      for (i = 0; i < x.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
      }
      document.getElementById(cityName).style.display = "block";
      evt.currentTarget.className += " w3-red";
    }
    </script>




    </body>
    </html>



    """


    out_web = out_web.replace('//','/')
    out_web = out_web.replace(base_dir,'')


    make_file(out_web,out_file)
    
    return()

###########################################################

if __name__ == "__main__":
    ####################
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-base_dir','-in','-i','-input',
        dest='base_dir',
        type=str)
    args = parser.parse_args()
    ####################
    base_dir = os.path.join(args.base_dir)


    make_webpage(base_dir)