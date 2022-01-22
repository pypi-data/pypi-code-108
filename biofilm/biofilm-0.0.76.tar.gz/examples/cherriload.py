#import RNA_RNA_binding_evaluation.get_features as cri
import eden.graph as eg
import networkx as nx
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix, hstack, load_npz, save_npz, vstack
partner =  {a:b for a,b in zip("({[<",")}]>")  }
from ubergauss import tools
from lmz import *
import pandas as pd

def mkgraph(sequence, structure):
    graph = nx.Graph()
    lifo = defaultdict(list)
    cut = structure.index("&")

    structure = structure.replace("&","")
    sequence = sequence.replace("&","")
    for i,(s,n) in enumerate(zip(structure, sequence)):
        graph.add_node(i, label=n)
        if i > 0 and  i != cut:
            graph.add_edge(i, i-1, label='-')

        # ADD PAIRED BASES
        if s in ['(','[','<']:
            lifo[partner[s]].append(i)
        if s in [')',']','>']:
            j = lifo[s].pop()
            graph.add_edge(i, j, label='=')
    return graph
    #return eg.vectorize([graph], discrete = False) # keep here in case i want nested edges ...

def mkgr(x):
    return mkgraph(*x)

def convert(negname, posname, outname, graphfeatures=True):
    # d1 = cri.loadDF(negname)
    # d2 = cri.loadDF(posname)
    d1 = pd.read_csv(negname)
    d2 = pd.read_csv(posname)


    # making y is easy
    y = np.array([0]*len(d1)+[1]*len(d2))

    # convert the dataframes, deleting the 'object' dtypes as they are strings ...
    X = np.vstack(( d1.to_numpy(), d2.to_numpy()))
    X = X[:,d1.dtypes != 'object']
    X=csr_matrix(X.astype(np.float64))

    col_namez= [name for name,ok in zip(d1.columns.tolist(), d1.dtypes) if ok != 'object']


    if graphfeatures:
        #graphs = [mkgraph(seq, stru) for d in [d1,d2] for seq,stru in  zip(d['subseqDP'],d['hybridDP'])  ]
        graphs = tools.xmap(mkgr,  [a  for d in [d1,d2] for a in  zip(d['subseqDP'],d['hybridDP'])],32)
        #X2 = eg.vectorize(graphs)
        X2 = csr_matrix(vstack(tools.xmap(eg.vectorize,[[g] for g in graphs])))
        X= csr_matrix(hstack((X,X2)))
        X= X.todense()

    tools.ndumpfile( [ X,y, col_namez + Range(X.shape[1] - len(col_namez))], outname)















def makedata_test():
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/test_context_feat/"
    d1 = p+'test_con300_neg.csv'
    d2 = p+"test_con300_pos.csv"
    convert(d1,d2,'cherry')

def makedata2291HU_garbage_cheat_data():
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/2291hu/"
    d1 = p+'feature_paris_HEK293T_context_150_pos_occ_neg.csv'
    d1 = p+'HEKT293T_neg.csv'
    d2 = p+"feature_paris_HEK293T_context_150_pos_occ_pos.csv"
    convert(d1,d2,'2291HUNOGR', graphfeatures=False)

def makedata2291HU():
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/2291hu/feature_filtered_paris_HEK293T_context_150_pos_occ_"
    d1 = p+'neg.csv'
    d2 = p+"pos.csv"
    convert(d1,d2,'2291HU', graphfeatures=True)

def makedata2291HUNOG():
    # there is inf in the DATA
    # sed -i '/inf/d' feature_filtered_paris_HEK293T_context_150_pos_occ_neg.csv
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/2291hu/feature_filtered_paris_HEK293T_context_150_pos_occ_"
    d1 = p+'neg.csv'
    d2 = p+"pos.csv"
    convert(d1,d2,'2291HUNOG', graphfeatures=False)

def makedata1923MO():
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/mouse1923/feature_filtered_paris_mouse_context_150_pos_occ_"
    d1 = p+'neg.csv'
    d2 = p+"pos.csv"
    convert(d1,d2,'1923MO', graphfeatures=True)

def makedata1923MONOG():
    # there is inf in the DATA
    # sed -i '/inf/d' feature_filtered_paris_HEK293T_context_150_pos_occ_neg.csv
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/mouse1923/feature_filtered_paris_mouse_context_150_pos_occ_"
    d1 = p+'neg.csv'
    d2 = p+"pos.csv"
    convert(d1,d2,'1923MONOG', graphfeatures=False)

def makedataHUMANRBPNOG():
    # there is inf in the DATA
    # sed -i '/inf/d' feature_filtered_paris_HEK293T_context_150_pos_occ_neg.csv
    p = "/home/ubuntu/repos/RNA_RNA_binding_evaluation/test_data/training/humanRBP/"
    d1 = p+'neg.csv'
    d2 = p+"pos.csv"
    convert(d1,d2,'HUMANRBPNOG', graphfeatures=False)



#X,y,_,sd = read('cherry')
#makedata2291HU()
