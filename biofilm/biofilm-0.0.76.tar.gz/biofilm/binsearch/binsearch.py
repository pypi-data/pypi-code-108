import numpy as np
import structout as so
from sklearn.metrics import  f1_score
from sklearn.model_selection import RandomizedSearchCV as RSCV
from pprint import pprint
import copy
from lmz import *
import scipy
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import StratifiedShuffleSplit as SSSplit
from scipy.stats.mstats import pearsonr
import biofilm.binsearch.limit as limit

class binsearch(RSCV):
    def fit(self, X, y=None, *, groups=None, **fit_params):
        assert self.n_iter >=25, "n_iter should be at least 25"
        # we want to change theese:
        self.binlog = 0,{}
        self.param_distributions = self.binsearch(X,y)
        #pparm(self.param_distributions)
        super().fit(X,y,groups=groups,**fit_params)

    def binsearch(self,x,y, estipoints = 20):
        nuparams = copy.deepcopy(self.param_distributions)
        for i in range(2):
            r = self.halfsearch_cool(x,y, nuparams, estipoints)
            nuparams = self.limitparams(r,nuparams, thresh = .15)
            self.n_iter -= int(estipoints/2)
        return nuparams

    def halfsearch(self,X,Y, params, niter):
        f1,f2  =next(StratifiedKFold(n_splits=2 , shuffle=True).split(X,Y))
        a,b,c,d = X[f1],Y[f1],X[f2],Y[f2]
        niter= int(niter/2)
        # Randomized search on hyper parameters
        searcher = RSCV(self.estimator,
                    params,
                    n_iter=niter,
                    scoring=self.scoring,
                    n_jobs=self.n_jobs,
                    cv=self.cv,
                    refit=False,
                    random_state=None,
                    error_score=np.nan,
                    return_train_score=True)
        r = searcher.fit(a,b).cv_results_
        s = searcher.fit(c,d).cv_results_
        li = lambda di: Zip(di['mean_test_score'], di['params'])
        return  li(r)+li(s)

    def halfsearch_cool(self,X,Y, params, niter):
        train_size  = (self.cv-1)/(self.cv*2)
        test_size= (1-train_size)/2
        splitter = SSSplit(self.cv, train_size=train_size)
        # Randomized search on hyper parameters
        searcher = RSCV(self.estimator,
                    params,
                    n_iter=niter,
                    scoring=self.scoring,
                    n_jobs=self.n_jobs,
                    cv=splitter,
                    refit=False,
                    random_state=None,
                    error_score=np.nan,
                    return_train_score=True)
        r=searcher.fit(X,Y).cv_results_
        li = lambda di: Zip(di['mean_test_score'], di['params'])
        return  li(r)


    def limitparams(self,best,curparams, thresh):
        allparams = self.param_distributions
        best.sort(reverse=True, key=lambda x:x[0])
        nuparams={}
        for k,v in curparams.items():
            nuparams[k]= limit.limit([ (score,di[k]) for score, di in best ] ,curparams[k],k, allparams[k], thresh)
        return nuparams


def pparm(params):
    print ("^"*80)
    for k,v in params.items():
        if isinstance(v,list):
            if  not all( [x == v[0] for x in v]  ):
                print(k, v if isinstance(v,list) else (v.args))
        else:
            print(k, v if isinstance(v,list) else (v.args))
    pprint(params)

