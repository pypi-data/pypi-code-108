def Tacf_pacf_fig(ar, ma, both=False, fig=True, lag=20):
     from statsmodels.tsa.arima_process import ArmaProcess
     acf=ArmaProcess(ar,ma).acf(lags=lag+1)
     pacf=ArmaProcess(ar,ma).pacf(lags=lag+1)
     if fig==True:
        import numpy as np
        import matplotlib.pyplot as plt
        if lag<31:
           ticks=range(lag+1)
        else:
           ticks=range(0, lag+1, 5)
        if both==False:
             plt.vlines(range(lag+1), [0], acf, linewidth=1.5)
             plt.axhline(y=0.0,linewidth=1)
             plt.xticks(ticks=ticks)
             plt.xlabel('Lag')
             plt.ylabel('True ACF')
             plt.show()
        elif both==True:
            plt.figure()
            plt.subplot(211)
            plt.vlines(range(lag+1), [0], acf, linewidth=1.5)
            plt.axhline(y=0.0,linewidth=1)
            plt.xticks(ticks=ticks)
            plt.ylabel('True ACF')
            plt.subplot(212)
            plt.vlines(range(lag+1), [0], pacf, linewidth=1.5)
            plt.axhline(y=0.0, linewidth=1)
            plt.xticks(ticks=ticks)
            plt.xlabel('Lag')
            plt.ylabel('True PACF')
            plt.show()
     elif fig==False:
           return  acf, pacf 
        

