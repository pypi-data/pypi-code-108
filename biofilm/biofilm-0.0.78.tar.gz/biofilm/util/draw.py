
import matplotlib.pyplot as plt
import structout as so
import numpy as np
from lmz import *



def lasso(model,X,y):
    from sklearn.linear_model import Lasso
    m =[ Lasso(alpha=a).fit(X,y).coef_ for a in model.alphas_]
    coe = [sum(abs(mm)>.00001) for mm in m]
    e = model.mse_path_.mean(axis=1)
    so.bins(e,minmax=False)
    so.lprint(coe) # i should make this work




from scipy.cluster.hierarchy import dendrogram
from sklearn.datasets import load_iris
from sklearn.cluster import AgglomerativeClustering


def plot_dendrogram(model, **kwargs):
    # STRAIGHT FROM THE SKLEARN DOCUMENTATION :)
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


def dendro(X):
    # setting distance_threshold=0 ensures we compute the full tree.
    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
    model = model.fit(X)
    plot_dendrogram(model, truncate_mode="level", p=3)

