import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
from xpd import *

import xplt

monkey_patch()
xplt.monkey_patch()


def xplot_scatter(data, feature, target, per_categ=None):
    fig, ax = plt.subplots(figsize=(10, 6))

    if per_categ:
        subsets = data[per_categ].unique()
        for s in subsets:
            temp = data[data[per_categ]==s]
            ax.scatter( temp[feature], temp[target], label = s)
    else:
        ax.scatter(data[feature], data[target])
    xplt.update_axes(feature, target)
    xplt.decorate(title= feature + ' vs. ' + target, show=True)


def xplot_feature_distribution(data, feature, target):

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = data[target].unique()
    for l in labels:
        values = data[data[target]==l][feature]
        values = values.sort_values()
        mean = np.mean(values)
        std = np.std(values)
        pdf = stats.norm.pdf(values, mean, std)
        ax.plot(values, pdf, label=l)

    xplt.update_axes(target, target + ' pdf')
    xplt.decorate(title='Distribution of '+feature + ' per ' + target + ' values', show=True)


def xsee_data(data, target, target_type='class', show='all'):

    features = list(data.columns)
    features.remove(target)
    if target_type == 'class':
        for feat in features:
            if data[feat].dtype.kind in 'iufc':
                xplot_feature_distribution(data, feat, target)

    elif target_type =='continuous':
        for feat in features:
            if data[feat].dtype.kind in 'iufc':
                xplot_scatter(data, feat, target)
            else:
                xplot_feature_distribution(data, target, feat)



def runtoy():

    data = pd.read_csv('../toy_data/student-mat.csv')
    print(data.columns)
    xsee_data(data, 'G3', 'continuous')

if __name__ == "__main__":
    runtoy()