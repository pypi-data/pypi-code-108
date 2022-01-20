import numpy as np 
from statsmodels.distributions.empirical_distribution import ECDF

def Sharpe_rat(risk_returns,safe_asset,Rebalancement_frequency):

        """
        Compute the Sharpe Ratio

        Parameters
        ----------
        risk_returns : np.ndarray
        safe_asset : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, Sharpe Ratio

        """

        Excess_returns = np.mean(risk_returns - safe_asset/Rebalancement_frequency) * Rebalancement_frequency
        strat_std = np.std(risk_returns) * Rebalancement_frequency**.5
        Sharpe_ratio = Excess_returns/strat_std
        return Sharpe_ratio
                          
def Sortino_rat(risk_returns,safe_asset,Rebalancement_frequency):

        """
        Compute the Sortino Ratio

        Parameters
        ----------
        risk_returns : np.ndarray
        safe_asset : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, Sortino Ratio

        """

        Sortino_std = np.std(risk_returns[np.where(risk_returns > 0 )]) * Rebalancement_frequency**.5
        Excess_returns = np.mean(risk_returns- safe_asset / Rebalancement_frequency) * Rebalancement_frequency
        Sortino_ratio = Excess_returns/Sortino_std
        return Sortino_ratio
                          
def Information_rat(risk_returns, benchmark_returns, Rebalancement_frequency):

        """
        Compute the breadth

        Parameters
        ----------
        risk_returns : np.ndarray
        benchmark_returns : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, Information Ratio

        """

        differentials = risk_returns - benchmark_returns 
        volatility = np.std(differentials) * Rebalancement_frequency**.5
        IR = np.mean(differentials) * Rebalancement_frequency / volatility
        return IR
    
def Modigliani_rat(risk_returns, benchmark_returns, safe_asset, Rebalancement_frequency,Sharpe_ratio):

        """
        Compute the Modigliani Ratio 

        Parameters
        ----------
        risk_returns : np.ndarray
        benchmark_returns : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        float64, Modigliani Ratio 

        """

        benchmark_volatility = np.std(benchmark_returns) * Rebalancement_frequency**.5
        m2_ratio = Sharpe_ratio * benchmark_volatility + safe_asset[-1]
        return m2_ratio


def Omega_rat(risk_returns):

        """
        Compute the Omega ratio 

        Parameters
        ----------
        risk_returns : np.ndarray

        Returns
        ----------

        float64, Omega ratio 

        """

        ecdf = ECDF(risk_returns)
        Omega_ratio = (1-ecdf(0))/ecdf(0)
        return Omega_ratio