import numpy as np 
import pandas as pd 
import warnings
from pyinsurance.Metric_Generator.ratios import Sharpe_rat , Sortino_rat , Omega_rat, Modigliani_rat,Information_rat
from pyinsurance.Metric_Generator.returns_metrics import cagr , Cumulative_ret
from pyinsurance.Metric_Generator.Probabilistic_Sharpe_Ratio import probabilistic_sharpe_ratio
from pyinsurance.Metric_Generator.Standard_dev import stdeviation
from pyinsurance.Value_at_risk.Value_at_risk import VaR
from pyinsurance.ts.TIPP_Model import TIPP
from pyinsurance.ts.Drawdown import Drawdown_function
from pyinsurance.Regressions.OLS_Basic import jensen_alpha_beta
warnings.filterwarnings('ignore')

class tipp_model:
    
    def __init__(self,risk_returns,safe_asset,lock_in\
                ,Min_risk_part,Capital_reinjection_rate,Initial_funds\
                ,floor_percent,multiplier , Benchmark_returns\
                ,Rebalancement_frequency = 252,theta = 0.01,Horizon = 1) -> None : 
        
        self.Runner(risk_returns,safe_asset,lock_in,\
                 Min_risk_part,Capital_reinjection_rate,Initial_funds\
                ,floor_percent,multiplier,Rebalancement_frequency)
        
        self.Benchmark_returns = Benchmark_returns.values.reshape(-1)[1:]
            
        
        self.Sharpe_ratio = Sharpe_rat(self.return_mtx , self.safe_asset_mtx ,\
                                            Rebalancement_frequency)
        
        self.Sortino_ratio = Sortino_rat(self.return_mtx , self.safe_asset_mtx ,\
                                              Rebalancement_frequency)
        
        self.Breadth = Information_rat(self.return_mtx, self.Benchmark_returns,\
                                             Rebalancement_frequency)
        
        self.PSR = probabilistic_sharpe_ratio(self.return_mtx, self.Benchmark_returns,\
                                              self.safe_asset_mtx,Rebalancement_frequency,\
                                              self.Sharpe_ratio)
        
        self.standard_deviation = stdeviation(self.return_mtx,Rebalancement_frequency)
        
        self.Cumulative_returns = Cumulative_ret(self.return_mtx)
        
        self.Omega_ratio = Omega_rat(self.return_mtx)
        
        self.CAGR = cagr(self.return_mtx,Rebalancement_frequency)
        
        self.Drawdown = Drawdown_function(self.return_mtx)
        
        self.Value_at_risk , self.Conditional_Value_at_risk = VaR(self.return_mtx, theta , Horizon)
        
        self.Modigliani_ratio = Modigliani_rat(self.return_mtx, self.Benchmark_returns,\
                                                self.safe_asset_mtx, Rebalancement_frequency\
                                                ,self.Sharpe_ratio)
            
        self.Beta , self.Alpha = jensen_alpha_beta(self.return_mtx , self.Benchmark_returns\
                                                        , Rebalancement_frequency )
        
    def Runner(self,risk_returns : np.ndarray ,safe_asset : np.ndarray ,lock_in : np.float64,\
                 Min_risk_part : np.float64 ,Capital_reinjection_rate : np.float64 ,Initial_funds : np.float64\
                ,floor_percent : np.float64,multiplier : np.float64 ,Rebalancement_frequency : np.float64):

        """
        Runs the TIPP class

        Parameters
        ----------
        risk_returns : np.ndarray
        safe_asset : np.ndarray
        lock_in : np.float64
        Min_risk_part : np.float64
        Capital_reinjection_rate : np.float64
        Initial_funds : np.float64
        floor_percent : np.float64
        multiplier : np.float64
        Rebalancement_frequency : np.float64

        Returns
        ----------

        Fund : np.ndarray , containing the cumulative fund Matrix
        floor : np.ndarray , containing the evolution of the floor level
        risk_returns_mtx : np.ndarray , containing the return of the original investment
        safe_asset_mtx : np.ndarray , containing the interest rates 
        return_mtx : np.ndarray , containing the return of the investment using a TIPP portfolio  
        """
        
        self.Fund , self.floor ,self.capital_reinjection,self.Reference_capital,\
        self.risk_returns_mtx , self.safe_asset_mtx , self.return_mtx  = TIPP(risk_returns,safe_asset,lock_in,\
                 Min_risk_part,Capital_reinjection_rate,Initial_funds\
                ,floor_percent,multiplier,Rebalancement_frequency).tipp
        pass 


