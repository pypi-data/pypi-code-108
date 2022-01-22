from scipy import sparse
import json
import dill
from biofilm.util.out import report
from biofilm.util.data import getfold


def zehidense(X):
    if sparse.issparse(X):
        return X.todense()
    return X


jdumpfile = lambda thing, filename:  open(filename,'w').write(json.dumps(thing))
dumpfile  = lambda thing, fn: dill.dump(thing,open(fn,'wb'))
loadfile = lambda filename: dill.load(open(filename, 'rb'))


