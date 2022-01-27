import numpy as np
import dirtyopts
import structout as so
from sklearn.metrics import  f1_score
import pprint
from biofilm import util
from autosklearn.experimental.askl2 import AutoSklearn2Classifier as ASK2
from autosklearn.classification import AutoSklearnClassifier as ASK1
import autosklearn.metrics
from sklearn.datasets import make_classification


'''
we just want a quick test:
    lets generate a classification task via sklearn and run the thing for 1 min
'''

estim = ASK1( n_jobs = 3,
            ensemble_size = 1,
            time_left_for_this_task = 30,
            metric = autosklearn.metrics.f1,
            max_models_on_disc = 1)

X,Y = make_classification()
estim.fit(X,Y)

scorehistory =  np.nan_to_num(\
            estim.performance_over_time_['single_best_optimization_score'].to_numpy(),nan=0.0)
so.lprint(scorehistory)
