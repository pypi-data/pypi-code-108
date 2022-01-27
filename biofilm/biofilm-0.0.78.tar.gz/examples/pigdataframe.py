
from numpy.random import Generator, PCG64
import dirtyopts
import pandas
from scipy.sparse import load_npz
import numpy as np

doc = '''
--pigdatasubsample int -1         # new arg to subsample
--randinit int -1                 # use biofilms randinit
--pigblacklist str no asser no genome kernel
--fabikernel bool False
'''

def read(filename):
    args = dirtyopts.parse(doc)
    p = pandas.read_pickle(filename)
    names = p.pop("NAME")

    if args.pigblacklist == 'genome':
        rm = np.where(p['GENOMEOVERLAP'] == 1)[0]
        p.drop(rm, inplace = True)
    elif args.pigblacklist == 'kernel':
        rm = np.where(p['KERNELNEIGH'] > .7)[0]
        p.drop(rm, inplace=True)
    if p.isnull().values.any():
        print(f"THERE ARE NANS")
    p.reset_index(inplace=True)

    if args.pigdatasubsample > 0:
        nid = np.where(p['CLASS'] == 0)[0].ravel()
        rg = Generator(PCG64(args.randinit))
        nid = rg.permuted(nid)
        nid = nid[args.pigdatasubsample:]
        p.drop(nid,inplace=True, axis = 0)

    # separate y and X
    y = p.pop("CLASS").to_numpy()

    if args.fabikernel:
        if args.pigdatasubsample> 0:
            print(f" you can not subsample the fabi stack yet .. exiting")
            exit()

        #return load_npz("/home/ubuntu/repos/biofilm/biofilm/VECTORS.npz"), y
        return load_npz("/home/ubuntu/repos/WEINBERG/SMALLVECS.npz"), y , list(range(2**16)), names

    p.pop("GENOMEOVERLAP")
    p.pop("KERNELNEIGH")
    X = p.to_numpy()
    # now we load subsample and so on
    features = p.columns[1:]
    return X[:,1:],y,features,names  # somehow dataframes attach an index so we jump one


if __name__ == "__main__":
    read("../biofilm/pigdataframe.pkl")
