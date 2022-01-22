import numpy as np
import dirtyopts
import structout as so
from sklearn.metrics import  f1_score
import pprint
from biofilm import util
from autosklearn.experimental.askl2 import AutoSklearn2Classifier as ASK2
from autosklearn.classification import AutoSklearnClassifier as ASK1
import autosklearn.metrics

optidoc='''
--method str any  'extra_trees', 'passive_aggressive', 'random_forest', 'sgd', 'gradient_boosting', 'mlp'
--out str jsongoeshere
--n_jobs int 1
--time int 3600
--randinit int 1337  # should be the same as the one in data.py
--preprocess bool False
#--metric str f1 assert f1 auc   TODO
'''

def optimize(X,Y,x,y, args):

    if args.method == 'any':
        estis =  ['extra_trees', 'passive_aggressive', 'random_forest', 'sgd', 'gradient_boosting', 'mlp']
    else:
        estis = [args.method]


    #include_estimators = estis,
    #include_preprocessors = ["no_preprocessing"] if not args.preprocess else None,
    include = {}
    if not args.preprocess:
            include['feature_preprocessor'] =  ["no_preprocessing"]
            #include['data_preprocessor']     =  ['NoPreprocessing']

    estim = ASK1(
            n_jobs = args.n_jobs,
            ensemble_size = 1,
            include = include,
            memory_limit = int(240000/30),
            time_left_for_this_task = args.time,
            metric = autosklearn.metrics.f1,
            max_models_on_disc = 1
            )
    estim.fit(X,Y)
    #import code
    #code.interact(local=dict(globals(), **locals()))
    # there is only 1 model in the end -> 0, we dont care about its weight -> 1 (this is the model)
    #print(f" asdasdasd{estim.get_models_with_weights()}")
    # models with weights is a list of model in the ensemble: [(weight_1, model_1), …, (weight_n, model_n)]
    #pipeline = estim.get_models_with_weights()[0][1]
    #print('estim',estim.get_params(deep=True))
    #print('estimator:',estimator.get_params(deep=True))

    return estim




def main():
    args = dirtyopts.parse(optidoc)
    data, fea, ins = util.getfold()
    model = optimize(*data,args)
    scorehistory =  np.nan_to_num(\
            model.performance_over_time_['single_best_optimization_score'].to_numpy(),nan=0.0)
    util.report(model, args.out, additionaloutput=\
            {'scorehistory': scorehistory , 'performancelog': model.performance_over_time_})
    so.lprint(scorehistory)
    if data[0].shape[1] < 100:
        print("SELECTED FEATURES: ", end='')
        pipeline = model.get_models_with_weights()[0][1]
        if type(pipeline.steps[2][1].choice.preprocessor) == str:
            print("all")
        else:
            print('\n',pipeline.steps[2][1].choice.preprocessor.get_support())


if __name__ == "__main__":
    main()

