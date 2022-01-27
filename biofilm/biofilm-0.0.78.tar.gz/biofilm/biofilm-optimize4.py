import dirtyopts as opts
import biofilm.util.data as datautil
import binsearch as bs
import numpy as np
import structout as so
from sklearn.metrics import  f1_score
from sklearn.model_selection import RandomizedSearchCV as RSCV
import biofilm.searchspace as ss
from pprint import pprint
import matplotlib
matplotlib.use('module://matplotlib-sixel')

from matplotlib import pyplot as plt

optidoc='''
--method str ExtraTrees  whatever is specified in searchspace.py
--out str numpycompressdumpgoeshere_lol
--features str whereIdumpedMyFeatures
'''

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingRandomSearchCV as HRSCV
import copy
from lmz import *

from scipy.stats import randint, uniform
import scipy

def optimize(X,Y,x,y, args):
    clf, params = ss.classifiers[args.method]
    searcher = bs.binsearch.binsearch(clf,
                params,
                n_iter=30,
                scoring='f1',
                n_jobs=5,
                cv=3,
                refit=True,
                random_state=None,
                error_score=np.nan,
                return_train_score=True)
    searcher.fit(X,Y)
    res = f1_score(y, searcher.predict(x))
    return res, searcher.best_params_
    if False:
        print(res)
        exit()
        la = clf.set_params(**searcher.binlog[1]).fit(X,Y).predict(x)
        scr = f1_score(y,la)
        print(res, max(searcher.cv_results_['mean_test_score']), searcher.binlog[0], scr)
        exit()
    return res


def mergedi(di):
    d = {}
    for k in di[0].keys():
        d[k] = [dd[k] for dd in di]
    return d


if __name__ == "__main__":
    args = opts.parse(optidoc)
    data = datautil.getfolds()
    res = [optimize(X,Y,x,y,args) for X,Y,x,y in data]
    res, di = Transpose(res)
    #pprint(mergedi(di))
    print(np.mean(res), res)
    dat = opts.parse(datautil.datadoc)
    np.savez_compressed(args.out,np.mean(res))


# print avg in the end
# maybe train 10 on full / prune x3 and done


