import numpy as np 
from pyinsurance.Metric_Generator.returns_metrics import Cumulative_ret

def Drawdown_function(risk_returns):

        """
        Compute the Drawdown serie 

        Parameters
        ----------
        risk_returns : np.ndarray

        Returns
        ----------

        np.ndarray,Drawdown 

        """

        C = Cumulative_ret(risk_returns)
        Drawdown = ( C / np.maximum.accumulate(C,axis = 0) - 1 ) * 100
        return Drawdown      