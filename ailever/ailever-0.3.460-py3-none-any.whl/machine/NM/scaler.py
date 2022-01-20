def standard(X):
    X = (X - X.mean(axis=0))/X.std(ddof=1)
    return X

def minmax(X):
    X = (X-X.min(axis=0))/(X.max(axis=0) - X.min(axis=0))
    return X
