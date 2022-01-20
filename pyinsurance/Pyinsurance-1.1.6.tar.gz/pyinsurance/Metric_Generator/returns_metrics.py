import numpy as np 

def cagr(risk_returns,Rebalancement_frequency):

        """
        Compute the Compound Annual Growth Rate (CAGR)

        Parameters
        ----------
        risk_returns : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, CAGR

        """

        Value_earned = Cumulative_ret(risk_returns)[-1]
        N = risk_returns.size / Rebalancement_frequency
        cagr = Value_earned ** (1/N) - 1 
        return cagr
    
def Cumulative_ret(risk_returns):

        """
        Compute the Cumulative return across time 

        Parameters
        ----------
        risk_returns : np.ndarray

        Returns
        ----------

        np.ndarray, CAGR

        """

        return np.cumprod(1 + risk_returns)