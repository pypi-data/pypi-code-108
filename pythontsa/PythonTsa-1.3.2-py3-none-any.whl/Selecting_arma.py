def choose_arma(x, max_p, max_q, ctrl=1.05):
     import numpy as np
     import pandas as pd
     import statsmodels.api as sm
     from statsmodels.tsa.arima_model import ARMA
     import warnings

     AIC_table = pd.DataFrame(np.zeros((max_p+1, max_q+1), dtype=float))
     BIC_table = pd.DataFrame(np.zeros((max_p+1, max_q+1), dtype=float))
     HQIC_table = pd.DataFrame(np.zeros((max_p+1, max_q+1), dtype=float))
     
     warnings.simplefilter('ignore')

     for p in range(max_p+1):
          for q in range(max_q+1):
              if p == 0 and q == 0:
                  continue
              arma_mod=ARMA(x, order=(p, q))
              try:
                   res = arma_mod.fit(method='mle')
                   if p>0 and q>0:
                        mARroot=min(abs(res.arroots))
                        mMAroot=min(abs(res.maroots))
                        if mARroot>ctrl and mMAroot>ctrl:
                           AIC_table.iloc[p, q] = round(res.aic, 2)
                           BIC_table.iloc[p, q] = round(res.bic, 2)
                           HQIC_table.iloc[p, q] = round(res.hqic, 2)
                        else:
                           AIC_table.iloc[p, q] = np.nan
                           BIC_table.iloc[p, q] = np.nan
                           HQIC_table.iloc[p, q] = np.nan
                   elif p==0 and q>0:
                         mMAroot=min(abs(res.maroots))
                         if mMAroot>ctrl:
                            AIC_table.iloc[p, q] = round(res.aic, 2)
                            BIC_table.iloc[p, q] = round(res.bic, 2)
                            HQIC_table.iloc[p, q] = round(res.hqic, 2)
                         else:
                            AIC_table.iloc[p, q] = np.nan
                            BIC_table.iloc[p, q] = np.nan
                            HQIC_table.iloc[p, q] = np.nan
                   elif p>0 and q==0:
                         mARroot=min(abs(res.arroots))
                         if mARroot>ctrl:
                            AIC_table.iloc[p, q] = round(res.aic, 2)
                            BIC_table.iloc[p, q] = round(res.bic, 2)
                            HQIC_table.iloc[p, q] = round(res.hqic, 2)
                         else:
                            AIC_table.iloc[p, q] = np.nan
                            BIC_table.iloc[p, q] = np.nan
                            HQIC_table.iloc[p, q] = np.nan
              except:
                   AIC_table.iloc[p, q] = np.nan
                   BIC_table.iloc[p, q] = np.nan
                   HQIC_table.iloc[p, q] = np.nan
     AIC_table.iloc[0, 0] = np.nan
     BIC_table.iloc[0, 0] = np.nan
     HQIC_table.iloc[0, 0] = np.nan
     AIC_colmin = pd.DataFrame.min(AIC_table)
     BIC_colmin = pd.DataFrame.min(BIC_table)
     HQIC_colmin = pd.DataFrame.min(HQIC_table)
     AIC_min=pd.Series.min(AIC_colmin)
     BIC_min=pd.Series.min(BIC_colmin)
     HQIC_min=pd.Series.min(HQIC_colmin)
     place =np.where(AIC_table==AIC_min)
     placeB =np.where(BIC_table==BIC_min)
     placeH =np.where(HQIC_table==HQIC_min)
     print("AIC: ",  "\n", AIC_table)
     print("AIC minimum is", AIC_min)
     print("(p, q)=", place)
     print("BIC: ",  "\n", BIC_table)
     print("BIC minimum is", BIC_min) 
     print("(p, q)=", placeB)
     print("HQIC: ",  "\n", HQIC_table)
     print("HQIC minimum is", HQIC_min) 
     print("(p, q)=", placeH)

