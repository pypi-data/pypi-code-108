import statsmodels.api as sm

def jensen_alpha_beta(risk_returns ,benchmark_returns,Rebalancement_frequency):

        """
        Compute the Beta and alpha of the investment under the CAPM 

        Parameters
        ----------
        risk_returns : np.ndarray
        benchmark_returns : np.ndarray
        Rebalancement_frequency : np.float64

        Returns
        ----------

        np.float64,Beta,np.float64,Alpha  

        """


        benchmark_returns = sm.add_constant(benchmark_returns)
        model = sm.OLS(risk_returns,benchmark_returns).fit()
        alpha,beta = model.params[0] * Rebalancement_frequency , model.params[1]
        return beta,alpha