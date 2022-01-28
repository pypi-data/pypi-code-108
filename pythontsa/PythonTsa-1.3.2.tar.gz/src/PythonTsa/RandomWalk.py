def RandomWalk_with_drift(drift, nsample, scale=1, distrvs=None, burnin=0):

        """
        Simulate data from a random walk with a drift
        
        Parameters
        drift : float
             the drift of the random walk
        nsample : int
        the size of sample
        scale : float
        The standard deviation of noise.
        distrvs : function, random number generator
        A function that generates the random numbers, and takes ``size``
        as argument. The default is np.random.standard_normal.
        burnin : int
        Number of observation at the beginning of the sample to drop.
        Used to reduce dependence on initial values.
        """

        import numpy as np
        import pandas as pd
        distrvs = np.random.standard_normal if distrvs is None else distrvs
        newsize = nsample
        newsize += burnin
        eta = scale * distrvs(size=newsize)
        eta = pd.Series(eta)
        mysample = np.zeros(newsize)
        mysample = pd.Series(mysample, dtype='float64')
        for t in range(1, newsize):
           mysample.iloc[t]=drift+mysample.iloc[t-1]+eta.iloc[t]
        fslice = slice(burnin, None, None)
        myrw= mysample[fslice]
        myrw.index=range(len(myrw))

        return myrw
                
        
