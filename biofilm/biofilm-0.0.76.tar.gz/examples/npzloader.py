
def read(filename): 
    import numpy as np
    d = np.load(filename,allow_pickle=True) 
    X,y = [d[f'arr_{x}'] for x in range(2)]
    return X,y
