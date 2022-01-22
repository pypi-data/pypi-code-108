import os
from nerkit.triples.ltp import *
from quick_crawler.page import *
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

def generate_triples_from_files(input_folder,output_folder="", return_all_results=False,
                                relation_field="relation", subject_field="subject", object_field="object",triple_id_field="file_id",
                                ltp_data_folder='./ltp_data'):
    extractor = get_ltp_triple_instance(ltp_data_folder=ltp_data_folder)
    list_result_all=[]
    for file in tqdm(os.listdir(input_folder)):
        print(file)
        list_result = []
        text = open(os.path.join(input_folder, file), 'r', encoding='utf-8').read()
        list_event = get_ltp_triple_list(extractor=extractor, text=text)
        filename, file_extension = os.path.splitext(file)
        file_id = filename
        for rel in list_event:
            model = {
                triple_id_field: file_id,
                subject_field: rel[0],
                relation_field: rel[1],
                object_field: rel[2],
            }
            print(model)
            list_result.append(model)
        if return_all_results:
            list_result_all+=list_result
        if output_folder!="":
            if not os.path.exists(output_folder):
                os.mkdir(output_folder)
            quick_save_csv(f"{output_folder}/{file_id}.csv", [triple_id_field, subject_field, relation_field, object_field], list_result)
        print()
    return list_result_all

def visualize_triples(triple_csv_file,filter_rel="",sample_size=-1, max_obj_len=-1,
              relation_field="relation",subject_field="subject",object_field="object",revised_if_in_subject=None,
              node_dist=0.8,save_figure_path="",show_figure=True,save_dpi=600):
    df = pd.read_csv(triple_csv_file)
    if filter_rel!="":
        df = df[(df[relation_field] == filter_rel) ]
    if sample_size!=-1:
        df = df.sample(sample_size)

    edges = []
    edge_labels = {}
    for index, row in df.iterrows():
        if max_obj_len!=-1:
            if len(row[object_field]) > max_obj_len:
                continue
        if revised_if_in_subject!=None:
            for s in revised_if_in_subject:
                if s in row[subject_field]:
                    row[subject_field]=s

        edges.append([row[subject_field], row[object_field]])
        edge_labels[(row[subject_field], row[object_field])] = row[relation_field]

    G = nx.Graph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, k=node_dist)
    # pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(
        G, pos, edge_color='black', width=1, linewidths=1, font_size=8,
        node_size=500, node_color='pink', alpha=0.6,
        labels={node: node for node in G.nodes()}
    )
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_color='red',
        font_size=8,
        arrow=True,
        arrowstyle='-|>'
    )
    plt.axis('off')
    if save_figure_path!="":
        plt.savefig(save_figure_path, dpi=save_dpi)
    if show_figure:
        plt.show()