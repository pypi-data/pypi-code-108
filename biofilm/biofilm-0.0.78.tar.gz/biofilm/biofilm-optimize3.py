import dirtyopts as opts
import biofilm.util.data as datautil
import numpy as np
import structout as so
from sklearn.metrics import  f1_score
from sklearn.model_selection import RandomizedSearchCV as RSCV
import biofilm.searchspace as ss
from skopt import BayesSearchCV
optidoc='''
--method str ExtraTrees  whatever is specified in searchspace.py
--out str numpycompressdumpgoeshere_lol
--features str whereIdumpedMyFeatures
'''

# DEV VERSION WORKS :) 

def optimize(X,Y,x,y, args):
    clf, params = ss.classifiers[args.method]
    # Randomized search on hyper parameters
    #https://scikit-optimize.github.io/stable/auto_examples/sklearn-gridsearchcv-replacement.html
    searcher = BayesSearchCV(clf,params,n_iter=20,cv=3,n_jobs=30)
    searcher.fit(X, Y )
    #print (searcher.__dict__)
    r=f1_score(y, searcher.predict(x))
    print(r)
    return r

if __name__ == "__main__":
    args = opts.parse(optidoc)
    data = datautil.getfolds()
    res = [optimize(X,Y,x,y,args) for X,Y,x,y in data]
    print(np.mean(res))
    np.savez_compressed( args.out,res)


