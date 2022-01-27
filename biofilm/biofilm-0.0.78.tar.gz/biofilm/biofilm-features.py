from lmz import Map,Zip,Filter,Grouper,Range,Transpose
import dirtyopts as opts
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score
import structout as so
from biofilm import util
from biofilm.algo import feature_inspection
from biofilm.algo.feature_selection import *
from sklearn.ensemble import RandomForestClassifier
featdoc='''
# options for feature selection:
--method str svm  svm all corr variance logistic relaxedlasso  VarianceInflation aggloclust forest
--out str numpycompressdumpgoeshere
--plot bool False
--n_jobs int 1

--svmparamrange float+ -3 2 5
--penalty str l1
--varthresh float 1

--showtop int 0
'''


##########################3
#  ZE ENDO
########################


def main():
    args = opts.parse(featdoc)
    XYxy, feat, inst  = util.getfold()

    #ftclust.ft(XYxy[0],XYxy[1], feat) #TODO something to inspect features?? ftclust does that but only when cout low..

    res  = eval(args.method)(*XYxy, args)

    performancetest(*XYxy,res[0])
    so.lprint(np.sort(res[1]))
    #import pprint;pprint.pprint(res)

    def np_bool_select(numpi, bools):
        return np.array([x for x,y in zip(numpi,bools) if y  ])

    np.savez_compressed(args.out, *res, np_bool_select(feat,res[0]))

    bestft = [(score,name) for good,score,name in zip(res[0],res[1],feat) if good]
    bestft.sort(reverse=True)
    for scor, name in bestft[:args.showtop]:
        print(f"{name}: {scor}")


if __name__ == "__main__":
    main()


