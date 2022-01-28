def acf_pacf_fig(x, both=False, lag=30):
        import numpy as np
        from statsmodels.tsa.stattools import acf, pacf
        import matplotlib.pyplot as plt
        if lag<21:
           ticks=range(lag+1)
        else:
           ticks=range(0, lag+1, 5)
        if both==False:
             acf_lag=acf(x, nlags=lag, fft=False)
             plt.vlines(range(lag+1), [0], acf_lag)
             plt.axhline(y=0.0,linewidth=1)
             plt.axhline(y=1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
             plt.axhline(y=-1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
             plt.xticks(ticks=ticks)
             plt.xlabel('Lag')
             plt.ylabel('ACF')
             #plt.show()
        elif both==True:
            acf_lag=acf(x, nlags=lag, fft=False)
            plt.figure()
            plt.subplot(211)
            plt.vlines(range(lag+1), [0], acf_lag)
            plt.axhline(y=0.0,linewidth=1)
            plt.axhline(y=1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
            plt.axhline(y=-1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
            plt.xticks(ticks=ticks)
            plt.ylabel('ACF')
            pacf_lag=pacf(x, nlags=lag, method='ywmle')
            plt.subplot(212)
            plt.vlines(range(lag+1), [0], pacf_lag)
            plt.axhline(y=0.0, linewidth=1)
            plt.axhline(y=1.96/np.sqrt(len(x)), linestyle='--', color='blue', linewidth=1)
            plt.axhline(y=-1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
            plt.xticks(ticks=ticks)
            plt.xlabel('Lag')
            plt.ylabel('PACF')
            #plt.show()
        
         
