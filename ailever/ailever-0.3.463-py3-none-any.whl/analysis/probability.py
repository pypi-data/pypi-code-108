from ..logging_system import logger
import numpy as np
import pandas as pd
from scipy.stats import bernoulli, binom, nbinom, poisson, geom, hypergeom, expon, norm

class Probability:
    def __init__(self, distribution='poisson'):
        self.distribution = distribution.lower()
    
    def parameter_manual(self):
        distribution = getattr(self, self.distribution)
        logger['analysis'].info("params=dict(trial=_, expected_occurence=_, success_probability=_, life_time=_, mean=_, std=_)")
        return help(distribution)

    def insert_params(self, params:dict):
        self.params = params
        param_keys = self.params.keys()
        if ('trial' in param_keys) and ('expected_occurence' in param_keys):
            self._trial = self.params['trial']
            self._expected_occurence = self.params['expected_occurence']
            self._success_probability = self._expected_occurence/self._trial
        elif ('trial' in param_keys) and ('success_probability' in param_keys):
            self._trial = self.params['trial']
            self._success_probability = self.params['success_probability']
            self._expected_occurence = int(self._trial * self._success_probability)
        elif ('expected_occurence' in param_keys) and ('success_probability' in param_keys):
            self._trial = int(self.params['expected_occurence']/self.params['success_probability'])
            self._success_probability = self.params['success_probability']
            self._expected_occurence = self.params['expected_occurence']
        elif 'success_probability' in param_keys:
            self._success_probability = self.params['success_probability']
            self._expected_occurence = 10
            self._trial =  int(self._expected_occurence/self._success_probability)
        else:
            self._trial = 100
            self._success_probability = 0.1
            self._expected_occurence = 10

        if 'life_time' in param_keys:
            self._life_time = self.params['life_time']
        else:
            self._life_time = self._expected_occurence

        if ('mean' in param_keys) and ('std' in param_keys):
            self._mean = self.params['mean']
            self._std = self.params['std']
        else:
            self._mean = self._expected_occurence
            self._std = self._expected_occurence/10

        self.probability = self.calculate()

    def calculate(self):
        logger['analysis'].info(f"TRIAL[{self._trial}] OCCURENCE[{self._expected_occurence}] PROBABILTY[{self._success_probability}] LIFETIME[{self._life_time}]")
        logger['analysis'].info(" - [EXP_CDF_P][L] less than success occurence")
        logger['analysis'].info(" - [POI_CDF_P][O] less than success occurence")
        logger['analysis'].info(" - [GEO_CDF_P][P] first event occurence")
        logger['analysis'].info(" - [NBI_CDF_P][O,P] ")
        logger['analysis'].info(" - [BIN_CDF_P][T,P] less than success occurence")
        logger['analysis'].info(" - [EXP_CDF_N][L] more than success occurence")
        logger['analysis'].info(" - [POI_CDF_N][O] more than success occurence")
        logger['analysis'].info(" - [GEO_CDF_N][P] ")
        logger['analysis'].info(" - [NBI_CDF_N][O,P] ")
        logger['analysis'].info(" - [BIN_CDF_N][T,P] more than success occurence")
        prob_factor = dict()
        prob_factor['trial'] = self._trial
        prob_factor['success_probability'] = self._success_probability
        prob_factor['expected_occurrence'] = self._expected_occurence
        prob_factor['life_time'] = self._life_time
        prob_factor['mean'] = self._mean
        prob_factor['std'] = self._std

        prob_matrix = pd.DataFrame(data=range(1,prob_factor['trial']+1), columns=['IDX'])
        prob_matrix['GEO'] = prob_matrix.IDX.apply(lambda x: x+1)
        prob_matrix['NBI'] = prob_matrix.IDX.apply(lambda x: x+prob_factor['expected_occurrence'])
        prob_matrix['NOM_CDF_P'] = prob_matrix.IDX.apply(lambda x: norm.cdf(x, loc=prob_factor['mean'], scale=prob_factor['std'])).round(6)
        prob_matrix['EXP_CDF_P'] = prob_matrix.IDX.apply(lambda t: expon.cdf(t, loc=0, scale=prob_factor['life_time'])).round(6)
        prob_matrix['POI_CDF_P'] = prob_matrix.IDX.apply(lambda x: poisson.cdf(x-1, mu=prob_factor['expected_occurrence'])).round(6)
        prob_matrix['GEO_CDF_P'] = prob_matrix.IDX.apply(lambda x: geom.cdf(x-1, p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['NBI_CDF_P'] = prob_matrix.IDX.apply(lambda x: nbinom.cdf(x-1, n=prob_factor['expected_occurrence'], p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['BIN_CDF_P'] = prob_matrix.IDX.apply(lambda x: binom.cdf(x-1, n=prob_factor['trial'], p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['NOM_CDF_N'] = prob_matrix.IDX.apply(lambda x: 1 - norm.cdf(x, loc=prob_factor['mean'], scale=prob_factor['std'])).round(6)
        prob_matrix['EXP_CDF_N'] = prob_matrix.IDX.apply(lambda t: 1 - expon.cdf(t, loc=0, scale=prob_factor['life_time'])).round(6)
        prob_matrix['POI_CDF_N'] = prob_matrix.IDX.apply(lambda x: 1 - poisson.cdf(x-1, mu=prob_factor['expected_occurrence'])).round(6)
        prob_matrix['GEO_CDF_N'] = prob_matrix.IDX.apply(lambda x: 1 - geom.cdf(x-1, p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['NBI_CDF_N'] = prob_matrix.IDX.apply(lambda x: 1 - nbinom.cdf(x-1, n=prob_factor['expected_occurrence'], p=prob_factor['success_probability'],loc=0)).round(6)
        prob_matrix['BIN_CDF_N'] = prob_matrix.IDX.apply(lambda x: 1 - binom.cdf(x-1, n=prob_factor['trial'], p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['NOM_PDF'] = prob_matrix.IDX.apply(lambda x: norm.pdf(x, loc=prob_factor['mean'], scale=prob_factor['std'])).round(6)
        prob_matrix['EXP_PDF'] = prob_matrix.IDX.apply(lambda t: expon.pdf(t, loc=0, scale=prob_factor['life_time'])).round(6)
        prob_matrix['POI_PMF'] = prob_matrix.IDX.apply(lambda x: poisson.pmf(x, mu=prob_factor['expected_occurrence'])).round(6)
        prob_matrix['GEO_PMF'] = prob_matrix.IDX.apply(lambda x: geom.pmf(x, p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['NBI_PMF'] = prob_matrix.IDX.apply(lambda x: nbinom.pmf(x, n=prob_factor['expected_occurrence'], p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix['BIN_PMF'] = prob_matrix.IDX.apply(lambda x: binom.pmf(x, n=prob_factor['trial'], p=prob_factor['success_probability'], loc=0)).round(6)
        prob_matrix = prob_matrix.set_index(['IDX', 'GEO', 'NBI'])
        prob_matrix.plot(figsize=(25,7))
        return prob_matrix
    
    @staticmethod
    def bernoulli():
        #bernoulli.rvs(p, loc=0, size=1, random_state=None)
        #bernoulli.pmf(k, p, loc=0)
        #bernoulli.logpmf(k, p, loc=0)
        #bernoulli.cdf(k, p, loc=0)
        #bernoulli.logcdf(k, p, loc=0)
        #bernoulli.sf(k, p, loc=0)
        #bernoulli.logsf(k, p, loc=0)
        #bernoulli.ppf(q, p, loc=0)
        #bernoulli.isf(q, p, loc=0)
        #bernoulli.stats(p, loc=0, moments=’mv’)
        #bernoulli.entropy(p, loc=0)
        #bernoulli.expect(func, args=(p,), loc=0, lb=None, ub=None, conditional=False)
        #bernoulli.median(p, loc=0)
        #bernoulli.mean(p, loc=0)
        #bernoulli.var(p, loc=0)
        #bernoulli.std(p, loc=0)
        #bernoulli.interval(alpha, p, loc=0)
        pass
    
    @staticmethod
    def binomial():
        #binom.rvs(n, p, loc=0, size=1, random_state=None)
        #binom.pmf(k, n, p, loc=0)
        #binom.logpmf(k, n, p, loc=0)
        #binom.cdf(k, n, p, loc=0)
        #binom.logcdf(k, n, p, loc=0)
        #binom.sf(k, n, p, loc=0)
        #binom.logsf(k, n, p, loc=0)
        #binom.ppf(q, n, p, loc=0)
        #binom.isf(q, n, p, loc=0)
        #binom.stats(n, p, loc=0, moments=’mv’)
        #binom.entropy(n, p, loc=0)
        #binom.expect(func, args=(n, p), loc=0, lb=None, ub=None, conditional=False)
        #binom.median(n, p, loc=0)
        #binom.mean(n, p, loc=0)
        #binom.var(n, p, loc=0)
        #binom.std(n, p, loc=0)
        #binom.interval(alpha, n, p, loc=0)
        pass

    @staticmethod
    def negative_binomial():
        #nbinom.rvs(n, p, loc=0, size=1, random_state=None)
        #nbinom.pmf(k, n, p, loc=0)
        #nbinom.logpmf(k, n, p, loc=0)
        #nbinom.cdf(k, n, p, loc=0)
        #nbinom.logcdf(k, n, p, loc=0)
        #nbinom.sf(k, n, p, loc=0)
        #nbinom.logsf(k, n, p, loc=0)
        #nbinom.ppf(q, n, p, loc=0)
        #nbinom.isf(q, n, p, loc=0)
        #nbinom.stats(n, p, loc=0, moments=’mv’)
        #nbinom.entropy(n, p, loc=0)
        #nbinom.expect(func, args=(n, p), loc=0, lb=None, ub=None, conditional=False)
        #nbinom.median(n, p, loc=0)
        #nbinom.mean(n, p, loc=0)
        #nbinom.var(n, p, loc=0)
        #nbinom.std(n, p, loc=0)
        #nbinom.interval(alpha, n, p, loc=0)
        pass

    @staticmethod
    def hypergeometric():
        #hypergeom.rvs(M, n, N, loc=0, size=1, random_state=None)
        #hypergeom.pmf(k, M, n, N, loc=0)
        #hypergeom.logpmf(k, M, n, N, loc=0)
        #hypergeom.cdf(k, M, n, N, loc=0)
        #hypergeom.logcdf(k, M, n, N, loc=0)
        #hypergeom.sf(k, M, n, N, loc=0)
        #hypergeom.logsf(k, M, n, N, loc=0)
        #hypergeom.ppf(q, M, n, N, loc=0)
        #hypergeom.isf(q, M, n, N, loc=0)
        #hypergeom.stats(M, n, N, loc=0, moments=’mv’)
        #hypergeom.entropy(M, n, N, loc=0)
        #hypergeom.expect(func, args=(M, n, N), loc=0, lb=None, ub=None, conditional=False)
        #hypergeom.median(M, n, N, loc=0)
        #hypergeom.mean(M, n, N, loc=0)
        #hypergeom.var(M, n, N, loc=0)
        #hypergeom.std(M, n, N, loc=0)
        #hypergeom.interval(alpha, M, n, N, loc=0)
        pass

    @staticmethod
    def geometric():
        #geom.rvs(p, loc=0, size=1, random_state=None)
        #geom.pmf(k, p, loc=0)
        #geom.logpmf(k, p, loc=0)
        #geom.cdf(k, p, loc=0)
        #geom.logcdf(k, p, loc=0)
        #geom.sf(k, p, loc=0)
        #geom.logsf(k, p, loc=0)
        #geom.ppf(q, p, loc=0)
        #geom.isf(q, p, loc=0)
        #geom.stats(p, loc=0, moments=’mv’)
        #geom.entropy(p, loc=0)
        #geom.expect(func, args=(p,), loc=0, lb=None, ub=None, conditional=False)
        #geom.median(p, loc=0)
        #geom.mean(p, loc=0)
        #geom.var(p, loc=0)
        #geom.std(p, loc=0)
        #geom.interval(alpha, p, loc=0)
        pass

    @staticmethod
    def poisson(k, mu, loc=0):
        #poisson.rvs(mu, loc=0, size=1, random_state=None)
        #poisson.logpmf(k, mu, loc=0)
        #poisson.cdf(k, mu, loc=0)
        #poisson.logcdf(k, mu, loc=0)
        #poisson.sf(k, mu, loc=0)
        #poisson.logsf(k, mu, loc=0)
        #poisson.ppf(q, mu, loc=0)
        #poisson.isf(q, mu, loc=0)
        #poisson.stats(mu, loc=0, moments=’mv’)
        #poisson.entropy(mu, loc=0)
        #poisson.expect(func, args=(mu,), loc=0, lb=None, ub=None, conditional=False)
        #poisson.median(mu, loc=0)
        #poisson.mean(mu, loc=0)
        #poisson.var(mu, loc=0)
        #poisson.std(mu, loc=0)
        #poisson.interval(alpha, mu, loc=0)
        return poisson.pmf(k, mu, loc=loc)

    @staticmethod
    def exponential():
        #expon.rvs(loc=0, scale=1, size=1, random_state=None)
        #expon.pdf(x, loc=0, scale=1)
        #expon.logpdf(x, loc=0, scale=1)
        #expon.cdf(x, loc=0, scale=1)
        #expon.logcdf(x, loc=0, scale=1)
        #expon.sf(x, loc=0, scale=1)
        #expon.logsf(x, loc=0, scale=1)
        #expon.ppf(q, loc=0, scale=1)
        #expon.isf(q, loc=0, scale=1)
        #expon.moment(n, loc=0, scale=1)
        #expon.stats(loc=0, scale=1, moments=’mv’)
        #expon.entropy(loc=0, scale=1)
        #expon.fit(data)
        #expon.expect(func, args=(), loc=0, scale=1, lb=None, ub=None, conditional=False, **kwds)
        #expon.median(loc=0, scale=1)
        #expon.mean(loc=0, scale=1)
        #expon.var(loc=0, scale=1)
        #expon.std(loc=0, scale=1)
        #expon.interval(alpha, loc=0, scale=1)
        pass

    @staticmethod
    def normal():
        #norm.rvs(loc=0, scale=1, size=1, random_state=None)
        #norm.pdf(x, loc=0, scale=1)
        #norm.logpdf(x, loc=0, scale=1)
        #norm.cdf(x, loc=0, scale=1)
        #norm.logcdf(x, loc=0, scale=1)
        #norm.sf(x, loc=0, scale=1)
        #norm.logsf(x, loc=0, scale=1)
        #norm.ppf(q, loc=0, scale=1)
        #norm.isf(q, loc=0, scale=1)
        #norm.moment(n, loc=0, scale=1)
        #norm.stats(loc=0, scale=1, moments=’mv’)
        #norm.entropy(loc=0, scale=1)
        #norm.fit(data)
        #norm.expect(func, args=(), loc=0, scale=1, lb=None, ub=None, conditional=False, **kwds)
        #norm.median(loc=0, scale=1)
        #norm.mean(loc=0, scale=1)
        #norm.var(loc=0, scale=1)
        #norm.std(loc=0, scale=1)
        #norm.interval(alpha, loc=0, scale=1)
        pass

    def simulate(self, params:dict):
        pass
