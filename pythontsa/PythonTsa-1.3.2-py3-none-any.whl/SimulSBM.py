def simulSBM(n=3000, seed=137, fig=True):
        import numpy as np
        import pandas as pd
        from numpy.random import normal
        import matplotlib.pyplot as plt
        np.random.seed(seed)
        a=normal(size=n)
        x=np.cumsum(a)/np.sqrt(n)
        w=pd.Series(np.arange(n+1), dtype='float')
        t=pd.Series(np.arange(n+1), dtype='float')
        w[0]=0.0
        t[0]=0.0
        for j in range(1, n+1):
            w[j]=x[j-1]
            t[j]=j/n
        w.index=t 
        if fig==True: 	
           w.plot()
           plt.xlabel('Time $t$')
           plt.ylabel('Standard Brownian Motion')
           plt.show()
        
        return w
