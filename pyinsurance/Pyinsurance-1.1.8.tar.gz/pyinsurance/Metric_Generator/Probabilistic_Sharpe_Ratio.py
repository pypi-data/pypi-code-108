import scipy  
import numpy as np 
from pyinsurance.Metric_Generator.ratios import Sharpe_rat


def estimated_sharpe_ratio_stdev(risk_returns,safe_asset,Rebalancement_frequency,Sharpe_Ratio):

        """
        Compute the standard deviation of the sharpe ratio across time

        Parameters
        ----------
        risk_returns : np.ndarray
        safe_asset : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, Sharpe ratio Standard deviation
        """

        N = risk_returns.size
        sk = scipy.stats.skey(risk_returns)
        kurt = scipy.stats.kurtosis(risk_returns)
        Sharpe_std = np.sqrt((1 + (0.5 * Sharpe_Ratio ** 2) - (sk * Sharpe_Ratio)\
                              + (((kurt - 3) / 4) * Sharpe_Ratio ** 2)) / (N - 1)) * Rebalancement_frequency
        return Sharpe_std
def probabilistic_sharpe_ratio(risk_returns, benchmark_returns,safe_asset,Rebalancement_frequency,Sharpe_Ratio):
        """
        Compute the Probabilistic Sharpe ratio 

        Parameters
        ----------
        risk_returns : np.ndarray
        benchmark_returns : np.ndarray
        safe_asset : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------
        float64, PSR
        """

        Sharpe_std = estimated_sharpe_ratio_stdev(risk_returns,safe_asset,Rebalancement_frequency,Sharpe_Ratio)
        sharpe_ratio_benchmark = Sharpe_rat(benchmark_returns,safe_asset,Rebalancement_frequency)
        probabilistic_SR = scipy.stats.norm.cdf((Sharpe_Ratio - sharpe_ratio_benchmark) / Sharpe_std)
        return probabilistic_SR