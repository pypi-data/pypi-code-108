
from lmz import Map, Range

import biofilm.algo.feature_selection
from biofilm import util
import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt
from biofilm.algo import feature_selection
import pandas as pd
from biofilm.util import draw
import networkx as nx


__doc__ = '''
# cluster features  / select highly correlating ones from each cluster...

- we want to make a umap projection of the features

- draw and color by correlation
- or make a clustermap if the numft is low..

- cluster with gmm and select numclust based on something

- is there a way to ballance uniqueness and correlation?
'''



def ft(x,y, feat):
    print(f"{feat=}")
    if x.shape[1] > 200:
        score, _ = feature_selection._forest(x, y, class_weight ='balanced')
        x = select(x,score,10000)

    corr  = spearman(x,y)
    # delete empty lines:
    xt = np.transpose(util.zehidense(x))
    xt = xt[~biofilm.algo.feature_selection.all(xt == 0, axis=1).A1]
    xt = np.abs(np.corrcoef(xt))

    '''
    draw some projections of the data... PCA UMAP  and a heatmap
    '''
    from umap import UMAP
    import seaborn as sns
    if True:
        elist = [(a,b) for a in Range(xt.shape[0]) for b in Range(xt.shape[0]) if xt[a,b] > .9]
        grph = nx.Graph()
        grph.add_edges_from(elist)
        for comp in nx.connected_components(grph):
            print("#########")
            for e in comp:
                print(feat[e])
        plt.title('aggloclust')
        draw.dendro(xt)
        plt.show(); plt.close()


        plt.title("PCA")
        xt2d = PCA(n_components=2).fit_transform(xt)
        sc= plt.scatter(xt2d[:,0],xt2d[:,1],c=corr)
        plt.colorbar(sc)
        plt.show(); plt.close()

        plt.title("UMAP")
        xt2d = UMAP(n_components=2,n_neighbors=int(np.sqrt(x.shape[1]))).fit_transform(xt)
        sc = plt.scatter(xt2d[:,0],xt2d[:,1],c=corr)
        plt.colorbar(sc)
        plt.show(); plt.close()

        xt2 = np.array(xt)
        for e,v in zip(Range(xt2.shape[0]),corr):
            xt2[e,e] = v

        frame = pd.DataFrame(xt2,columns= feat)
        sns.clustermap(frame)
        plt.show(); plt.close()

        plt.title("corrcoeff of features, sorted... i think this is relevant to find cutoff")
        plt.plot(np.sort(corr))
        plt.show(); plt.close()

    exit()
    print("start clustering..")
    print(f"{ xt.shape=}")
    xt = UMAP(n_components=10).fit_transform(xt)
    nc = Range(2,int(np.sqrt(xt.shape[0])),3)
    nc = Range(2,10000,100)
    clusterings = [GaussianMixture(n_components=i,n_init =10).fit_predict(xt) for i in nc ]
    #clusterings = ba.mpmap(cluster,[(n,xt) for n in nc], poolsize = 20)
    print(f"{ xt.shape=}")

    # each nc gets the average of the maxcorrPerCluster
    def avgmaxcorr(labels):
        topscr = lambda l: np.max(corr[labels == l])
        #return np.mean(Map(topscr, np.unique(labels)))
        return Map(topscr, np.unique(labels))

    avgMaxCorPerClust = Map(avgmaxcorr,clusterings)

    plt.scatter([z for z in  nc for i in range(z)], [i for a in avgMaxCorPerClust for i in a])
    plt.show(); plt.close()
    exit()


def cluster(z):
    i,xt = z
    return GaussianMixture(n_components=i).fit_predict(xt)

def select(X,scores,num):
    return X[:,np.argsort(scores)[-num:]]


def spearman(x,y):
    spear = lambda ft: np.abs(spearmanr(ft.T,y)[0])
    x = util.zehidense(x)
    re = Map(spear,x.T)
    return np.array(re)


