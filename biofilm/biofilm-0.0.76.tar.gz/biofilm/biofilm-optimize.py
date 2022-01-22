import dirtyopts as opts
import json
import biofilm.util.data as datautil
import numpy as np
import structout as so
from hpsklearn import HyperoptEstimator
from hyperopt import tpe
from sklearn.metrics import  f1_score
import pprint

optidoc='''
--method str any_classifier  svc knn random_forest extra_trees ada_boost gradient_boosting sgd
--out str jsongoeshere
'''

from hpsklearn.components import *
#pip install git+https://github.com/hyperopt/hyperopt-sklearn 
def optimize(X,Y,x,y, args):
    estim = HyperoptEstimator(
            classifier=eval(args.method)('myguy'),
            algo=tpe.suggest,
            max_evals = 30,
            trial_timeout  = 120, 
            #loss_fn = lambda a,b: (1 - f1_score(a,b)),
            preprocessing=[],
            ex_preprocs=[]
            )
    estim.fit(X,Y)

    score = f1_score(y,estim.predict(x) )
    parm = str(estim.best_model()['learner'])
    res = {'score': score, "param":parm}
    pprint.pprint(res)
    return res

jdumpfile = lambda thing, filename:  open(filename,'w').write(json.dumps(thing))

def main():
    args = opts.parse(optidoc)
    data = datautil.getfold()
    res = optimize(*data,args)
    jdumpfile(res,args.out)

if __name__ == "__main__":
    main()



