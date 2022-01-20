import numpy as np 

def stdeviation(risk_returns,Rebalancement_frequency):

        """
        Compute the standard deviation of the investment  

        Parameters
        ----------
        risk_returns : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, standard deviation 

        """

        stdev = np.std(risk_returns) * Rebalancement_frequency**.5
        return stdev