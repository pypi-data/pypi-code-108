import dirtyopts
import biofilm.util.out as out
import dill
from biofilm.util import data as datautil
from ubergauss.tools import loadfile, dumpfile
optidoc='''
--out str modeldilldump
--model str inputmodel
'''


def fit(X,Y,x,y, args):
    model = loadfile(args.model)['estimator']

    #ASK = AutoSklearnClassifier(per_run_time_limit=360,memory_limit=30000)
    #ASK.fit_pipeline(X=X, y=Y,config=model.config)
    #breakpoint()
    #if "_preprocessor" in model.__dict__:
    #    print("look me up! a90s8d70as")
    #    X = model._preprocessor.transform(X)
    model.refit(X,Y)
    #print(model.config)
    #pipeline = ASK.get_models_with_weights()[0][1]
    return model

def main():
    args = dirtyopts.parse(optidoc)
    data, fea, ins = datautil.getfold()
    estim = fit(*data,args)

    if data[2].shape[0]==0:
        print('there is no test set so we just dump the model')
        dumpfile( estim ,args.out+'.model')
    else:
        out.report(estim, args.out)

if __name__ == "__main__":
    main()

