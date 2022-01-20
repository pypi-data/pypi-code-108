import numpy as np 
from arch import arch_model
from scipy.stats import t
 
def VaR(return_matrix, theta,Horizon): #500 datas needed 

        """
        Compute the Value-at-Risk and Conditional Value-at-Risk

        Parameters
        ----------
        risk_returns : np.ndarray
        theta : np.float64
        Horizon : np.int16

        Returns
        ----------

        np.ndarray,np.ndarray   VaR , CVaR

        """
        
        am     = arch_model(return_matrix * 100 , vol='Garch'\
                         , p=1 , o=1 , q=1,mean='AR', lags=1,dist='StudentsT')
        res    = am.fit(update_freq=1,disp='off')
        forecasts = res.forecast(horizon=Horizon)
        z      = (return_matrix - forecasts.mean.iloc[-1,0])/res.conditional_volatility
        z      = z[~np.isnan(z)] #Remove NaNs
        z_up   = - np.sort(z)
        params = t.fit(z_up)
        alpha  = params[0]
        q_99_t = np.sqrt((alpha-2)/alpha)*t.ppf(1-theta,alpha)
        VaR    = - (forecasts.mean.iloc[-1,0] + \
                 np.sqrt((forecasts.variance.iloc[-1,0]))*q_99_t)
        CVaR     = - (t.pdf(t.ppf(1-theta,alpha),alpha)/theta) * ( alpha+t.ppf(1-theta,alpha)**2)\
                /(alpha-1) * np.sqrt(forecasts.variance.iloc[-1,0]) - forecasts.mean.iloc[-1,0]
                
        return VaR,CVaR