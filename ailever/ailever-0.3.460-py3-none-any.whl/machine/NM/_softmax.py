import numpy as np

def softmax(X):
    return np.exp(X)/np.exp(X).sum()
