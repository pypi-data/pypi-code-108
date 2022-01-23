import numpy as np
import pandas as pd
from .deltas import Delta, LightDelta, DeltaResampling, DeltaBayHess
from functools import partial
from copy import deepcopy
from time import time


class MICE:
    """
    Class for MICE estimator objects

    Parameters
    ----------
    grad : callable
        Gradient function, input must be (dim_var, (sample_size, dim_random)),
        output must be (sample_size, dim_var)
    sampler : callable or list
        A function with argument sample_size that returns a sample of size
        (sample_size, dim_random) or a list of size (sample_size, dim_random)
    eps : float, default=1.0
        The admissible relative error in grad estimate
    dropping : bool, default=True
        If True, checks whether to drop previous iteration
    restart : bool default=True
        If True, checks whether to restart hierarchy every iteration
    clip_type : {'full', 'all'}, default='full'

        * 'full': Checks, for each level l, if clipping at l is advantageous

        * 'all': (only for the finite case) Clips only when sample_size equals
        the total data size

    min_batch : int, default=10
        Minimum sample_size
    restart_factor : int default=10
        Increase factor of sample sizes for restarting
    max_cost : float, default=1000
        Maximum number of gradient evaluations before halting execution
    tol : float, default=0
        Tolerance on the norm of the gradient estimate. If it gets smaller
        than 'tol' than MICE halts execution
    drop_param : float, default=0.5
        Parameter to stimulate dropping
    restart_param : float, default=0
        Parameter to stimulate restarting
    max_hierarchy_size : int, default=1000
        Maximum length of hierarchy, restarts when reached
    mice_type : {'resampling', 'light', 'naive'}, default='resampling'

        * 'resampling': Uses resampling to estimate gradient norm and also
        uses Welford's algorithm to estimate variance

        * 'light': Uses Welford's algorithm to estimate variances, thus
        reducing memory and processing overhead

        * 'naive': Keeps all gradient evaluations on memory

    verbose : bool, default=False
        Prints information on screen
    aggr_cost : float, default=0.1
        Quantifies the overhead of MICE per hierarchy length in terms of
        gradient evaluations. Larger values of 'aggr_cost' discourage
        longer hierarchies.
    re_part : int, default=5
        (resampling) Sets the number of partitions
    re_percentile : float, default=0.05
        (resampling) Percentile of gradient norms used as estimate
    re_tot_cost : float, default=0.2
        (resampling) fraction of total cost to be used for resampling
    re_min_n : int, default=5
        (resampling) minimum resampling size
    re_max_samp : int, default=1000
        (resampling) Maximum resampling size
    big_batch : bool, default=False
        For the finite case, forces restart sample size to be data size
    adpt : bool, default=True
        Adaptivity measuring time from gradient evaluations and MICE overhead
        to compute 'aggr_cost' and resampling cost


    Methods
    -------

    __call__(x)
        Calls the method 'evaluate' with given input.

    aggr_deltas()
        Aggregates the data in each Delta object to compute MICE estimate.

    evaluate(x)
        Evaluates MICE at 'x'.

    get_log()
        Returns the log with information from each iteration.
    """

    def __init__(self,
                 grad,
                 sampler,
                 eps=1.0,
                 dropping=True,
                 restart=True,
                 clip_type='full',
                 min_batch=10,
                 restart_factor=10,
                 max_cost=1000,
                 tol=0.,
                 drop_param=0.5,
                 restart_param=0,
                 max_hierarchy_size=1000,
                 mice_type='resampling',
                 verbose=False,
                 aggr_cost=0.1,
                 re_part=5,
                 re_percentile=0.05,
                 re_tot_cost=0.2,
                 re_min_n=5,
                 re_max_samp=1000,
                 big_batch=False,
                 adpt=True):
        self.grad = partial(self._check_grad, func=grad)
        self.sampler = sampler
        self.eps = eps
        self.m_min = min_batch
        self.m_restart_min = restart_factor * min_batch
        self.max_cost = max_cost
        self.dropping = dropping
        self.drop_param = drop_param
        self.restart = restart
        self.restart_param = restart_param
        if not (isinstance(sampler, list) or callable(sampler)):
            raise Exception("'sampler' must be either a list or a callable")
        self.finite = isinstance(sampler, list)
        self.sum = partial(np.sum, axis=0)
        self.aggr = partial(np.mean, axis=0)
        self.inner = np.dot
        self.norm = np.linalg.norm
        self.var = lambda x: np.sum(np.var(x, axis=0, ddof=1))
        self.max_hierarchy_size = max_hierarchy_size
        self.tol = tol
        self.verbose = verbose
        if verbose:
            self.print = print
        else:
            self.print = lambda x: None
        self.deltas = []
        self.dim = None
        self.counter = 0
        self._log_dict = {'event': None, 'num_grads': None, 'vl': None,
                         'bias_rel_err': None, 'grad_norm': None,
                         'iteration': None}
        self.log_list = [self._log_dict.copy()]
        self.k = 0
        self.times = {
            'gradients': 0.,
            'aggregation': 0.,
            'resampling': 0.,
            'clipping': 0.,
            'mice': 0.
        }
        self.aggregations = 0
        self.aggr_cost = aggr_cost
        self.adpt = adpt
        self.terminate = False
        self.force_restart = False
        self.mice_type = mice_type
        if self.mice_type == 'naive':
            self.delta_class = Delta
        elif self.mice_type == 'light':
            self.delta_class = LightDelta
        elif self.mice_type == 'resampling':
            self.delta_class = partial(DeltaResampling, re_part=re_part,
                                       m_min=min_batch)
        elif self.mice_type == 'bayesian hessian':
            self.delta_class = partial(DeltaBayHess, re_part=re_part,
                                       m_min=min_batch)
        if self.mice_type in ['resampling', 'bayesian hessian']:
            self.resamples = 0
            self.err_tol = 1e-6
            self.re_part = re_part
            self.re_percentile = re_percentile
            self.re_max_samp = re_max_samp
            self.re_tot_cost = re_tot_cost
            self.re_cost = 1.
            self.re_min_n = re_min_n
            self.define_tol = self._define_tol_norm_resampling
            self.norm_estim = None
        else:
            self.err_tol = .0
            self.define_tol = self._define_tol_norm
        if self.finite:
            self.data_size = len(sampler)
            self.m_restart_min = np.minimum(self.m_restart_min, self.data_size)
            self.create_delta = self._create_delta_finite
            if big_batch:
                self.get_opt_ml = self._get_opt_ml_finite_bigbatch
            else:
                self.get_opt_ml = self._get_opt_ml_finite
            self.print(f'Finite case: size{self.data_size}')
        else:
            self.create_delta = self._create_delta_continuous
            self.get_opt_ml = self._get_opt_ml_continuous
            self.print('Continuous case')
        if clip_type == 'full':
            self.check_clipping = self._check_clipping_full
        elif clip_type == 'all':
            self.check_clipping = self._check_clipping_all
        elif clip_type is None:
            self.check_clipping = lambda opt_ml: opt_ml

    def __call__(self, x):
        """
        Calls method 'evaluate' with argument 'x'

        Parameters
        ----------
        x: array_like
            Where to evaluate the MICE estimator.

        Returns
        -------
        estimate: array_like
            Gradient estimated at 'x'.

        """
        return self.evaluate(x)

    def __getattr__(self, item):
        if item == 'sample_sizes':
            return [delta.m for delta in self.deltas]
        elif item == 'v_l':
            return [delta.v_l for delta in self.deltas]
        # elif item == 'log':
        #     return pd.DataFrame(self.log_list)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no "
                                 f"attribute '{item}'")

    def get_log(self):
        """
        Returns a Pandas DataFrame with the log of MICE evaluations per
        iteration. The columns are:

        * event : a string with 'start', 'MICE', 'restart', 'dropped', or 'end'

        * num_grads : the number of gradient evaluations

        * vl : the contribution of the last Delta to the statistical error

        * bias_rel_err : the relative expected square norm of the bias

        * grad_norm : MICE's estimate norm

        * iteration : the iteration number

        Returns
        -------
        log : Pandas DataFrame
            A dataframe containing the history of the MICE evaluations.
        """
        return pd.DataFrame(self.log_list)

    def _check_grad(self, x, thetas, func):
        t0 = time()
        out = np.asarray(func(x, thetas))
        self.times['gradients'] += time() - t0
        if np.shape(out) != (len(thetas), self.dim):
            raise Exception('Gradient function does not return array of '
                            'appropriate size, (sample_size, dim_var)')
        return out

    def evaluate(self, x):
        """
        Estimates the gradient at 'x' using MICE

        Parameters
        ----------
        x : array_like
            Where to evaluate the MICE estimator.

        Returns
        ----------
        estimate : array_like
            Gradient estimated at 'x'
        """
        t0 = time()
        self.print('Evaluating MICE')
        if len(self.deltas) == 0:
            if hasattr(x, '__len__'):
                self.dim = len(x)
            else:
                self.dim = 1
                x = np.reshape(x, self.dim)
            self.deltas.append(self.create_delta(x, c=1))
            self.deltas[0].m_min = self.m_restart_min
            # self.log_list.append(['start'])
            self.log_list[0]['event'] = 'start'
        else:
            x = np.reshape(x, self.dim)
            self.deltas.append(self.create_delta(
                x, c=2, x_l1=self.deltas[-1].x_l))
            # self.log_list.append(['MICE'])
            self.log_list.append(self._log_dict.copy())
            self.log_list[-1]['event'] = 'MICE'
        if self._check_max_cost(extra_eval=self.m_min*self.deltas[-1].c):
            return np.full(self.dim, np.nan)
        for delta in self.deltas:
            delta.m_prev = delta.m
        self.deltas[-1].update_delta(self, self.deltas[-1].m_min)
        self.err_tol = self.define_tol()
        opt_ml = self.get_opt_ml(self.deltas)
        if self.dropping and len(self.deltas) > 2:
            opt_ml = self._check_dropping(opt_ml)
        if len(self.deltas) > 1 and self.restart:
            opt_ml = self._check_restart(opt_ml)
        opt_ml = self.check_clipping(opt_ml)
        while not self._check_samp_sizes(opt_ml):
            for delta, m_opt in zip(self.deltas, opt_ml):
                if self.finite:
                    m_min = np.minimum(delta.m_min, self.data_size - delta.m)
                else:
                    m_min = delta.m_min
                m_to_sample = np.minimum(m_opt - delta.m, delta.m)
                if m_to_sample > 0:
                    m_to_sample = np.maximum(m_to_sample, m_min)
                if self._check_max_cost(extra_eval=m_to_sample*delta.c):
                    return np.full(self.dim, np.nan)
                delta.update_delta(self, delta.m + m_to_sample)
            self.err_tol = self.define_tol()
            opt_ml = self.get_opt_ml(self.deltas)
        df_estim = self.aggr_deltas()
        # print(f'{bias=}, {bias_rel_err=}')
        # self.log_list[-1] += [self.counter, self.deltas[-1].v_l, bias_rel_err,
        #                  self.norm(df_estim), len(self.deltas)]
        self._update_log()
        self.times['mice'] += time() - t0
        self._check_tol(df_estim)
        self.k += 1
        return df_estim

    def _update_log(self):
        bias = self._compute_bias()
        f_estim = self.aggr_deltas()
        bias_rel_err = np.sqrt(bias) / self.norm(f_estim)

        self.log_list[-1]['num_grads'] = self.counter
        self.log_list[-1]['vl'] = self.deltas[-1].v_l
        self.log_list[-1]['bias_rel_err'] = bias_rel_err
        self.log_list[-1]['grad_norm'] = self.norm(f_estim)
        self.log_list[-1]['hier_length'] = len(self.deltas)
        self.log_list[-1]['iteration'] = len(self.log_list)

    def _compute_bias(self):
        """
        Computes an approximation of the expectation of the square mean of the
        bias

        Returns
        -------
        bias: float
        """
        bias = 0
        for delta in self.deltas[:-1]:
            bias += delta.m_prev / delta.m ** 2 * delta.v_l
        return bias

    def _check_clipping_full(self, opt_ml):
        if self.finite:
            t0 = time()
            m_is_datasize = np.where(opt_ml == self.data_size)[0]
            if len(m_is_datasize) and m_is_datasize.max() > 0:
                lvl_clip = m_is_datasize.max()
                ml = np.array(self.sample_sizes)
                cost = np.maximum(opt_ml - ml, 0).sum() + \
                    self.aggr_cost * len(ml)
                deltas_clip = self.deltas[lvl_clip:]
                opt_ml_clip = self.get_opt_ml(deltas_clip)
                cost_clip = (np.maximum(opt_ml_clip - ml[lvl_clip:], 0).sum()
                             + self.aggr_cost * len(opt_ml_clip))
                if cost_clip <= cost:
                    self.print(f'Clipping at l:{lvl_clip}'
                               f'clip cost:{cost_clip}, '
                               f'continuing cost: {cost}')
                    self.deltas = deltas_clip
                    self.deltas[0] = self.deltas[0].restart(self)
                    opt_ml = opt_ml_clip
            self.times['clipping'] += time() - t0
        return opt_ml

    def _check_clipping_all(self, opt_ml):
        t0 = time()
        ml = np.array(self.sample_sizes)
        cost = np.maximum(opt_ml - ml, 0).sum() + self.aggr_cost * len(ml)
        cost_clip = []
        opt_ml_clip = []
        for i in range(len(self.deltas)):
            deltas_clip = self.deltas[i:]
            opt_ml_clip.append(self.get_opt_ml(deltas_clip))
            cost_clip.append(np.maximum(opt_ml_clip[-1] - ml[i:], 0).sum()
                             + self.aggr_cost * len(opt_ml_clip[-1]))
        if np.min(cost_clip) < cost:
            i = np.argmin(cost_clip)
            self.deltas = self.deltas[i:]
            self.deltas[0] = self.deltas[0].restart(self)
            opt_ml = opt_ml_clip[i]
            self.print(f'Clipping at l:{i}, '
                       f'clip cost:{cost_clip[i]}, '
                       f'continuing cost: {cost}')
        self.times['clipping'] += time() - t0
        return opt_ml

    def _check_restart(self, opt_ml):
        """
        Check whether or not it is advantageous to restart the hierarchy.

        Parameters
        ----------
        opt_ml : array_like
            NumPy array containing the optimal sample size for each level of
            the current hierarchy.

        Returns
        -------
        opt_ml : array_like
            The optimal sample size after checking restart, i.e., if restart
            is done this method returns a singleton array.
        """
        ml = self.sample_sizes
        mice_cost = np.maximum(0, np.ceil(opt_ml - ml)).sum() \
            + self.aggr_cost * len(opt_ml)
        new_delta = self.deltas[-1].restart(self)
        opt_ml_restart = self.get_opt_ml([new_delta])
        opt_ml_restart = np.maximum(opt_ml_restart, self.m_restart_min)
        restart_cost = np.maximum(0, opt_ml_restart - ml[-1]) + self.aggr_cost
        if (restart_cost < mice_cost * (1 + self.restart_param)
                or len(self.deltas) > self.max_hierarchy_size
                or self.force_restart):
            self.force_restart = False
            # self.log_list[-1] = ['restart']
            self.log_list[-1]['event'] = 'restart'
            self.print(
                f'restart: Yes, Cost to continue:{mice_cost}, '
                f'restart cost:{restart_cost}')
            self.deltas = [new_delta]
            return np.array(opt_ml_restart)
        else:
            self.print(
                f'restart: No, Cost to continue:{mice_cost}, '
                f'restart cost:{restart_cost}')
            return opt_ml

    def _check_dropping(self, opt_ml):
        """
        Check whether or not it is advantageous to drop the last iteration
        out of the hierarchy.

        Parameters
        ----------
        opt_ml : array_like
            NumPy array containing the optimal sample size for each level of
            the current hierarchy.

        Returns
        -------
        opt_ml : array_like
            The optimal sample size after checking dropping.
        """
        ml = self.sample_sizes
        mice_cost = np.maximum(0, np.ceil(opt_ml - ml)).sum() \
            + self.aggr_cost * len(opt_ml)
        delta_drop = self.create_delta(
            self.deltas[-1].x_l, c=2, x_l1=self.deltas[-3].x_l)
        delta_drop.update_delta(self, self.m_min)
        opt_ml_drop = self.get_opt_ml(self.deltas[:-2] + [delta_drop])
        drop_cost = np.maximum(0, np.ceil(
            opt_ml_drop - (ml[:-2] + [ml[-1]]))).sum() \
            + self.aggr_cost * len(opt_ml_drop)
        if drop_cost <= mice_cost * (1 + self.drop_param):
            # self.log_list[-2][0] = 'dropped'
            self.log_list[-2]['event'] = 'dropped'
            self.print(
                f'Drop: Yes, Cost to continue:{mice_cost}, '
                f'dropping cost:{drop_cost}')
            self.deltas = self.deltas[:-2] + [delta_drop]
            return opt_ml_drop
        else:
            self.print(
                f'Drop: No, Cost to continue:{mice_cost}, '
                f'dropping cost:{drop_cost}')
            return opt_ml

    def _create_delta_continuous(self, x, c=2, x_l1=None):
        delta_sampler = deepcopy(self.sampler)
        return self.delta_class(x=x, sampler=delta_sampler, c=c, x_l1=x_l1)

    def _create_delta_finite(self, x, c=2, x_l1=None):
        start = np.random.randint(self.data_size)
        sample_idx = _sample_generator(start, self.data_size)
        delta_sampler = partial(_sampler_finite,
                                sample_iterator=sample_idx,
                                sample=self.sampler)
        return self.delta_class(x=x, sampler=delta_sampler, c=c, x_l1=x_l1)

    def _check_max_cost(self, extra_eval=0):
        """
        Check if the maximum cost will be violated if 'extra_vals' are sampled.

        Parameters
        ----------
        extra_eval : int
            Number of evaluations required to be sampled in current iteration.

        Returns
        -------
        violation : bool
            Whether or not the new evaluations will exceed the maximum cost.
        """
        if self.counter + extra_eval > self.max_cost:
            self.print(f'The cost exceeded the maximum of {self.max_cost}')
            self.terminate = True
            self.log_list[-1]['event'] = 'end'
            self.log_list[-1]['num_grads'] = self.counter
            self.log_list[-1]['vl'] = None
            self.log_list[-1]['bias_rel_err'] = None
            self.log_list[-1]['grad_norm'] = None
            self.log_list[-1]['hier_length'] = None
            self.log_list[-1]['iteration'] = None
            return True
        else:
            return False

    def _check_tol(self, df_estim):
        if self.norm(df_estim) < self.tol:
            self.print(f'The norm of the gradient {self.norm(df_estim)}'
                       f'is less than {self.tol}')
            self.terminate = True
            self.log_list[-1]['event'] = 'end'

    def _check_samp_sizes(self, opt_ml):
        """
        Check if current sample sizes are larger than 'opt_ml' for all levels.

        Parameters
        ----------
        opt_ml : array_like
            Optimal sample sizes for each level in the hierarchy.

        Returns
        -------


        """
        return all(opt_ml <= self.sample_sizes)

    def aggr_deltas(self):
        """
        Sums all the levels in the hierarchy to compute the MICE estimate.

        Returns
        -------
        estimate: array_like
            Estimate from MICE
        """
        t0 = time()
        estimate = self.sum([delta.f_delta_av for delta in self.deltas])
        self.times['aggregation'] += time() - t0
        self.aggregations += len(self.deltas)
        if self.adpt:
            self.aggr_cost = (
                    (self.times['aggregation'] / self.aggregations)
                    / (self.times['gradients'] / self.counter))
        return estimate

    def _define_tol_norm(self):
        f_estim = self.aggr_deltas()
        return self.eps * self.norm(f_estim)

    def _define_tol_norm_resampling(self):
        t0 = time()
        ml = self.sample_sizes
        opt_ml = self.get_opt_ml(self.deltas)
        cost = np.maximum(opt_ml - ml, 0).sum()
        if self.adpt:
            re_samp = (int(self.re_tot_cost * cost
                           / (self.re_cost * len(self.deltas))))
        else:
            re_samp = self.re_max_samp
        re_samp = np.min([re_samp, self.re_max_samp,
                          (2 * self.re_part) ** len(self.deltas)])
        n = np.max([re_samp, self.re_min_n])
        samples = np.random.randint(self.re_part,
                                    size=(int(n), len(self.deltas)))

        estims = np.vstack(self.deltas[0].f_deltas[samples[:, 0]])
        for delta, samples_ in zip(self.deltas[1:], samples[:, 1:].T):
            estims += delta.f_deltas[samples_]
        norms = np.linalg.norm(estims, axis=1)
        norms = np.append(norms, self.norm(self.aggr_deltas()))

        self.times['resampling'] += time() - t0
        self.resamples += n
        self.re_cost = ((self.times['resampling'] / self.resamples)
                        / (self.times['gradients'] / self.counter))
        norms = np.sort(norms)
        self.norm_estim = norms[int(np.floor((n + 1) * self.re_percentile))]
        return self.eps * self.norm_estim

    def _get_opt_ml_finite(self, deltas):
        ds = self.data_size

        vl, ml, cl = [deltas[0].v_batch], [deltas[0].m], [1]
        m_min = [self.m_restart_min]
        for delta in deltas[1:]:
            vl.append(delta.v_l)
            ml.append(delta.m)
            cl.append(delta.c)
            m_min.append(self.m_min)

        vl = np.array(vl)
        ml = np.array(ml)
        cl = np.array(cl)

        opt_ml = np.array(m_min).astype('int')
        ells = ml < ds

        while np.sum([vl / opt_ml * (1 - opt_ml / ds)]) > self.err_tol ** 2:
            aux1 = self.err_tol ** 2 + 1 / (self.data_size - 1) * np.sum(
                vl[ells])
            aux2 = np.sum(np.sqrt(np.multiply(vl[ells], cl[ells]))) \
                * self.data_size / (self.data_size - 1)
            opt_ml[ells] = np.ceil(np.divide(vl[ells], cl[ells]) ** 0.5 * aux2
                                   / aux1).astype('int')
            opt_ml = np.minimum(opt_ml, self.data_size)
            opt_ml = np.maximum(opt_ml, ml)
            opt_ml = np.maximum(opt_ml, m_min)
            ells = opt_ml < ds
        return opt_ml

    def _get_opt_ml_finite_bigbatch(self, deltas):
        if len(deltas) == 1:
            return np.array([self.data_size])
        else:
            ds = self.data_size
            vl, ml, cl = [deltas[0].v_batch], [deltas[0].m], [1]
            for delta in deltas[1:]:
                vl.append(delta.v_l)
                ml.append(delta.m)
                cl.append(delta.c)

            vl = np.array(vl)
            ml = np.array(ml)
            cl = np.array(cl)

            opt_ml = np.asarray(ml)
            ells = opt_ml < ds

            while np.sum(
                    [vl / opt_ml * (1 - opt_ml / ds)]) > self.err_tol ** 2:
                aux1 = self.err_tol ** 2 \
                       + 1 / (self.data_size - 1) * np.sum(vl[ells])
                aux2 = np.sum(np.sqrt(np.multiply(vl[ells], cl[ells]))) \
                    * self.data_size / (self.data_size - 1)
                opt_ml[ells] = np.ceil(np.divide(vl[ells], cl[ells]) ** 0.5
                                       * aux2 / aux1).astype('int')
                opt_ml = np.minimum(opt_ml, self.data_size)
                ells = opt_ml < ds
        return opt_ml

    def _get_opt_ml_continuous(self, deltas):
        vl, ml, cl = [deltas[0].v_batch], [deltas[0].m], [1]
        m_min = [self.m_restart_min]
        for delta in deltas[1:]:
            vl.append(delta.v_l)
            ml.append(delta.m)
            cl.append(delta.c)
            m_min.append(self.m_min)
        constant = np.sum(np.sqrt(np.multiply(vl, cl)))
        opt_ml = np.ceil(self.err_tol ** (-2)
                         * np.divide(vl, cl) ** 0.5 * constant).astype('int')
        opt_ml = np.maximum(opt_ml, m_min)
        self.print(f'Optimal Ml: {opt_ml}')
        return opt_ml


def _sample_generator(start, datasize):
    i = start
    while True:
        if i == datasize - 1:
            i = 0
            yield i
        else:
            i += 1
            yield i


def _sampler_finite(n, sample_iterator, sample):
    return [sample[sample_idx] for i, sample_idx in zip(range(n),
                                                        sample_iterator)]
