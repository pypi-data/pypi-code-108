#
# Quantum Machine Learning
# Copyright (C) 2018 Hongxiang Chen - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Written by Hongxiang Chen <h.chen.17@ucl.ac.uk>, 2018.
#

import copy
import math

import numpy as np


class LearningRateScheduler:
    def __init__(self):
        pass

    def get_lr(self, sgd) -> float:
        raise NotImplementedError


class DecayByKSteps(LearningRateScheduler):
    def __init__(self, k, decay):
        self.k = k
        self.decay = decay
        super(DecayByKSteps, self).__init__()

    def get_lr(self, sgd):
        if sgd.step_count != 0 and sgd.step_count % self.k == 0:
            return sgd.lr_cur * self.decay
        else:
            return sgd.lr_cur


class InverseTimeDecay(LearningRateScheduler):
    def __init__(self, decay_rate, decay_steps):
        """
        Learning rate calculated as:
            learning_rate / (1 + decay_rate * global_step / decay_step)
        :param decay_rate:
        """
        super(InverseTimeDecay, self).__init__()
        self.decay_rate = decay_rate
        self.decay_steps = decay_steps

    def get_lr(self, sgd):
        return sgd.learning_rate / (1 + self.decay_rate * sgd.step_count / self.decay_steps)


class GradientBasedOptimiser:
    def __init__(
            self,
            initial_lr=1.0,
    ):
        self._ini_lr = copy.copy(initial_lr)  # for __copy__
        self._lr = initial_lr
        self.lr_cur = self.learning_rate
        self.step_count = 0
        self.x_cur = None
        self.g_cur = None

    @property
    def learning_rate(self):
        return self._lr

    @learning_rate.setter
    def learning_rate(self, new):
        self._lr = new

    def compute_gradient(self, grad, variable):
        """Compute the gradient for this optimiser.

        Besides computing gradients for the variable, this function may also modifies the variables (as in some accelerated
        gradient methods).
        iteration/step.
        :return: (gradient, variables)
        """
        return grad(variable), variable

    def apply_update(self, gradient_calculated, variable):
        """Apply the calculated gradient to update internal variables, and return the variable for the next step.
        """
        self.step_count += 1
        return variable

    def get_name(self):
        return 'GradientBasedOptimiser'

    def __copy__(self):
        """Create a new optimiser with the same parameter, but without initial internal state"""
        return GradientBasedOptimiser(initial_lr=self._ini_lr)


class SGD(GradientBasedOptimiser):
    # minics the implementation found in Tensorflow:
    # https://www.tensorflow.org/api_docs/python/tf/train/AdamOptimizer
    def __init__(
            self,
            learning_rate=0.001,
            lr_scheduler: LearningRateScheduler = None,
            momentum=None,
            # use_nesterov = False, # todo Add this
    ):
        """
        :param learning_rate:
        :param lr_scheduler:  The decay func which accepts the current lr rate, and
        :param momentum: If not None, will absorb previous momentum (gradient) multiplied by this factor
        in calculation of gradient.
        lr: float >= 0. Learning rate.
        """
        super(SGD, self).__init__(initial_lr=learning_rate)
        self.lr_scheduler = lr_scheduler
        self.momentum = momentum if momentum is not None else 0
        self.momentums_cur = None

    def minimise(self, maxiter, theta_0, grad, log_func, log_freq, ):
        self.x_cur = theta_0
        while self.step_count < maxiter:
            gradient_calculated, variable = self.compute_gradient(grad=grad, variable=self.x_cur)
            self.apply_update(gradient_calculated=gradient_calculated, variable=variable)
            if (self.step_count == 1) or (self.step_count % log_freq == 0):
                log_func(self)
        log_func(self)

    def compute_gradient(self, grad, variable):
        return super(SGD, self).compute_gradient(grad=grad, variable=variable)

    def apply_update(self, gradient_calculated, variable):
        self.step_count += 1
        if self.momentums_cur is None:
            self.momentums_cur = np.zeros_like(self.x_cur)
        self.x_cur = variable
        self.g_cur = gradient_calculated
        self.lr_cur = self.learning_rate if self.lr_scheduler is None else self.lr_scheduler.get_lr(self)
        if self.momentum == 0:
            self.x_cur -= self.lr_cur * self.g_cur
        else:
            self.momentums_cur = self.momentum * self.momentums_cur - self.lr_cur * self.g_cur
            self.x_cur += self.momentums_cur
        return self.x_cur

    def __str__(self):
        if self.momentum == 0:
            return 'SGD'
        else:
            return 'SGD_momentum'

    def get_name(self):
        return str(self)

    def __copy__(self):
        return SGD(learning_rate=self._ini_lr, lr_scheduler=self.lr_scheduler,
                   momentum=self.momentum)


class Adagrad(GradientBasedOptimiser):
    def get_name(self):
        return 'Adagrad'

    def __init__(self, learning_rate=0.01, epsilon=1e-6, moving_average_decay=None):
        """

        :param learning_rate:
        :param epsilon: The small value inside the square root of the denominator of the
        adjusted learning rate.
        :param moving_average_decay: If `None` will collect an equal weighted historical gradicent.
        If a `float` \in [0,1], will collect an exponential moving average of historical gradient by
        historical_grad = m.a.f. * historical_grad + (1-m.a.f.) * current_grad ** 2

        Note: Should be called RMSProp when using moving avg decay
        """
        # the parameter for this estimator
        super(Adagrad, self).__init__(initial_lr=learning_rate)
        self.historical_grad = None
        self.epsilon = epsilon
        if moving_average_decay is not None:
            if moving_average_decay > 1 or moving_average_decay < 0:
                raise ValueError(moving_average_decay)
        self.moving_avg_decay = moving_average_decay

    def _accumulate_historical_gradient(self):
        if self.moving_avg_decay is None:
            self.historical_grad += np.square(self.g_cur)
        else:
            self.historical_grad = self.moving_avg_decay * self.historical_grad + \
                                   (1 - self.moving_avg_decay) * np.square(self.g_cur)

    def minimise(self, maxiter, theta_0, grad, log_func, log_freq):
        self.x_cur = theta_0
        while self.step_count < maxiter:
            gradient_calculated, variable = self.compute_gradient(grad=grad, variable=self.x_cur)
            self.apply_update(gradient_calculated=gradient_calculated, variable=variable)
            if (self.step_count == 1) or (self.step_count % log_freq == 0):
                log_func(self)
        log_func(self)

    def compute_gradient(self, grad, variable):
        return super(Adagrad, self).compute_gradient(grad=grad, variable=variable)

    def apply_update(self, gradient_calculated, variable):
        self.step_count += 1
        if self.historical_grad is None:
            self.historical_grad = np.zeros_like(variable)
        self.x_cur = variable
        self.g_cur = gradient_calculated
        self._accumulate_historical_gradient()
        self.lr_cur = self.learning_rate / np.sqrt(self.historical_grad + self.epsilon)
        self.x_cur -= (self.lr_cur * self.g_cur)
        return self.x_cur

    def __copy__(self):
        return Adagrad(learning_rate=self._ini_lr, epsilon=self.epsilon,
                       moving_average_decay=self.moving_avg_decay)


class AdamMinimizer(GradientBasedOptimiser):
    def __init__(self, learning_rate=0.001,
                 beta1=0.9,
                 beta2=0.999,
                 epsilon=1e-08,
                 ):
        # mimics the implementation found in Tensorflow:
        # https://www.tensorflow.org/api_docs/python/tf/train/AdamOptimizer
        super(AdamMinimizer, self).__init__(initial_lr=learning_rate)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m_t = None
        self.v_t = None

    def minimise(self, maxiter, theta_0, grad, log_func, log_freq):
        self.x_cur = theta_0

        while self.step_count < maxiter:
            grad_calculated, variable = self.compute_gradient(grad=grad, variable=self.x_cur)
            self.apply_update(gradient_calculated=grad_calculated, variable=variable)
            if (self.step_count == 1) or (self.step_count % log_freq == 0):
                log_func(self)
        log_func(self)

    def compute_gradient(self, grad, variable):
        return super(AdamMinimizer, self).compute_gradient(grad=grad, variable=variable)

    def apply_update(self, gradient_calculated, variable):
        self.step_count += 1
        self.g_cur = gradient_calculated
        self.x_cur = variable
        if self.m_t is None:
            self.m_t = np.zeros(shape=len(self.x_cur))  # (Initialize 1st moment vector)
            self.v_t = np.zeros(shape=len(self.x_cur))  # (Initialize 2nd moment vector)

        lr_t = self.learning_rate * (math.sqrt(1 - self.beta2 ** self.step_count) / (1 - self.beta1 ** self.step_count))

        self.m_t = self.beta1 * self.m_t + (1 - self.beta1) * self.g_cur
        self.v_t = self.beta2 * self.v_t + (1 - self.beta2) * (self.g_cur ** 2)
        self.lr_cur = lr_t * self.m_t / (np.sqrt(self.v_t) + self.epsilon)
        self.x_cur -= self.lr_cur
        return self.x_cur

    def __str__(self):
        return 'Adam'

    def get_name(self):
        return str(self)

    def __copy__(self):
        return AdamMinimizer(learning_rate=self._ini_lr, beta1=self.beta1, beta2=self.beta2, epsilon=self.epsilon)


class RProp(GradientBasedOptimiser):
    """Implement the simple RProp algorithm.

    Ref:
        http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.52.4576&rep=rep1&type=pdf
        https://www.researchgate.net/publication/2765136_RPROP_-_A_Fast_Adaptive_Learning_Algorithm
        An good read related is: http://arxiv.org/abs/1509.04612v2
    Notes
    ------
    This algorithm uses a value delta which acts in a similar way as learning rate. Therefore,
    all learning_rate is set to this delta.
    """

    def __init__(self, d0=1.0, eta_p=1.2, eta_m=0.5, dmin=1e-6, dmax=50.0):
        """
        Parameters
        ----------
        d0 : float
            The initial moving rate. It is not critical (according to the paper) since it will
            be adapted by this algorithm.
        """
        if eta_p <= 1:
            raise ValueError('eta_plus must bigger than 1:' + str(eta_p))
        if eta_m <= 0 or eta_m >= 1:
            raise ValueError('eta_minus must be in range (0,1):' + str(eta_m))
        if not (0 <= dmin <= d0 <= dmax):
            raise ValueError('Invalid delta (dmin,d0,dmax)=({0},{1},{2})'.format(
                str(dmin), str(d0), str(dmax)
            ))
        d0 = float(d0)
        super(RProp, self).__init__(initial_lr=d0)
        self.prev_grad = None
        self.prev_variable_change = None
        self.eta_plus = float(eta_p)
        self.eta_minus = float(eta_m)
        self.delta_min = float(dmin)
        self.delta_max = float(dmax)

        # self.restart_patience = 50
        # self.record_

    def apply_update(self, gradient_calculated, variable):
        self.g_cur = gradient_calculated  # to be used in __copy__

        variable = super(RProp, self).apply_update(
            gradient_calculated=gradient_calculated, variable=variable)
        # This is an vertorised version of the original algorithm
        if self.prev_grad is None:
            # Initial update
            self.learning_rate = np.full(shape=variable.shape, fill_value=self.learning_rate)
            self.prev_grad = gradient_calculated
            grad_sign = np.sign(gradient_calculated)
            variable -= self.learning_rate * grad_sign
        else:
            tmp = np.sign(gradient_calculated * self.prev_grad)
            self.learning_rate[tmp > 0] *= self.eta_plus
            self.learning_rate[tmp < 0] *= self.eta_minus

            # constraint it into with min and max
            if self.delta_min > 0:
                self.learning_rate = np.maximum(self.learning_rate, self.delta_min)
            self.learning_rate = np.minimum(self.learning_rate, self.delta_max)

            # iRprop-
            gradient_calculated[tmp < 0] = 0

            grad_sign = np.sign(gradient_calculated)
            variable -= self.learning_rate * grad_sign

            # update prev_grad for next iteration
            self.prev_grad = gradient_calculated
        return variable

    def __copy__(self):
        ret = RProp(d0=self._ini_lr, eta_p=self.eta_plus, eta_m=self.eta_minus, dmin=self.delta_min,
                    dmax=self.delta_max)
        ret.learning_rate = np.random.rand(len(self.g_cur)) * self._ini_lr
        return ret


class ExplorativeRProp(RProp):

    def __init__(self, d0, eta_p, eta_m, dmin, dmax, remember_g_eps):
        super(ExplorativeRProp, self).__init__(d0=d0, eta_p=eta_p, eta_m=eta_m, dmin=dmin, dmax=dmax)
        if remember_g_eps <= 0: raise ValueError(remember_g_eps)
        self.remembered = {
            'g': None,
            'variable_update_delat': None,
            'eps': remember_g_eps,
        }
        self._notify_apply_g_to_remember_vari_update = False
        raise NotImplementedError('work in progress')

    def compute_gradient(self, grad, variable):
        g = grad(variable)
        if np.average(g) >= self.remembered['eps']:
            self.remembered['g'] = np.copy(g)
            self._notify_apply_g_to_remember_vari_update = True
        return g, variable

    def apply_update(self, gradient_calculated, variable):
        variable = super(ExplorativeRProp, self).apply_update(
            gradient_calculated=gradient_calculated, variable=variable)
        if self._notify_apply_g_to_remember_vari_update:
            self.remembered['variable_update_delat'] = np.copy(self.learning_rate)
            self._notify_apply_g_to_remember_vari_update = False
        return variable

    def escape_minimal_with_memorised_step(self, variable):
        """Will do the variable update using the step and gradient remembered before.
        If the memory is empty, will just return the variable unaltered.
        """
        if self.remembered['g'] is not None:
            variable -= self.remembered['variable_update_delat'] * np.sign(self.remembered['g'])
            return variable
        else:
            return variable


def get_opt_by_name(name, *args, **kwargs):
    dikt = {SGD.__name__: SGD,
            Adagrad.__name__: Adagrad,
            AdamMinimizer.__name__: AdamMinimizer,
            RProp.__name__: RProp,
            ExplorativeRProp.__name__: ExplorativeRProp,
            }
    return dikt[name](*args, **kwargs)


if __name__ == '__main__':
    loss = lambda x: np.sum(np.abs(x))


    def grad(x):
        x = list(x)
        g = []
        for x_i in x:
            if x_i > 0:
                g.append(1)
            elif x_i < 0:
                g.append(-1)
            else:
                g.append(0)
        return np.array(g)


    def log_func(sgd: SGD):
        print('x:' + repr(sgd.x_cur))
        print('lr:' + repr(sgd.lr_cur))


    def test_sgd():
        print('Expectiong non-convegence due to limited steps:')
        sgd = SGD(
            learning_rate=1, lr_scheduler=None
        )
        sgd.minimise(
            maxiter=10,
            theta_0=[20, 5],
            grad=grad,
            log_func=log_func, log_freq=1,
        )
        del sgd
        print('Expect oscillate due to constant lr:')
        sgd = SGD(
            learning_rate=1, lr_scheduler=None
        )
        sgd.minimise(
            maxiter=10,
            theta_0=[1.1, 3],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del sgd
        print('\n\nExpect success decay(exp decay)\n')
        sgd = SGD(
            learning_rate=1, lr_scheduler=DecayByKSteps(k=10, decay=0.9),
        )
        sgd.minimise(
            maxiter=500,
            theta_0=[15.0, -30.0],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del sgd
        print('\n\nExpect success decay (inverse time)\n')
        sgd = SGD(
            learning_rate=1, lr_scheduler=InverseTimeDecay(
                decay_rate=1,
                decay_steps=40,
            )
        )
        sgd.minimise(
            maxiter=400,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del sgd


    # test_sgd()
    def test_sgd_m():
        print('\n\nExpect oscialltion (due to accumulated momentum)\n')
        sgd = SGD(
            learning_rate=1, lr_scheduler=None,
            momentum=1,
        )
        sgd.minimise(
            maxiter=100,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del sgd
        print('\n\nExpect oscialltion (due to accumulated momentum)\n')
        sgd = SGD(
            learning_rate=1, lr_scheduler=None,
            momentum=2,
        )
        sgd.minimise(
            maxiter=100,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del sgd


    test_sgd_m()


    def test_adagrad():
        print('\n\nExpect quick decay of lr due to adagrad\n')
        adagrad = Adagrad(
            learning_rate=1,
        )
        adagrad.minimise(
            maxiter=200,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del adagrad
        print('\n\nExpect better optimisation result due to no so quick decay of lr\n')
        adagrad = Adagrad(
            learning_rate=1,
            moving_average_decay=0.8,
        )
        adagrad.minimise(
            maxiter=50,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )
        del adagrad


    # test_adagrad()

    def test_adam():
        class OldAdamMinimizer:
            # mimics the implementation found in Tensorflow:
            # https://www.tensorflow.org/api_docs/python/tf/train/AdamOptimizer
            def __init__(self, learning_rate=0.001,
                         beta1=0.9,
                         beta2=0.999,
                         epsilon=1e-08,
                         ):
                self.learning_rate = learning_rate
                self.beta1 = beta1
                self.beta2 = beta2
                self.epsilon = epsilon
                self.x_cur = None
                self.g_cur = None
                self.step_count = None
                self.lr_cur = None

            def minimise(self, maxiter, theta_0, grad, log_func, log_freq, action_before_compute_grad=None):
                self.x_cur = theta_0
                self.m_t = np.zeros(shape=len(self.x_cur))  # (Initialize initial 1st moment vector)
                self.v_t = np.zeros(shape=len(self.x_cur))  # (Initialize initial 2nd moment vector)
                self.step_count = 0
                while self.step_count < maxiter:
                    self.step_count += 1
                    if action_before_compute_grad is not None:
                        action_before_compute_grad(self)
                    self.g_cur = grad(self.x_cur)
                    lr_t = self.learning_rate * math.sqrt(1 - self.beta2 ** self.step_count) / (
                            1 - self.beta1 ** self.step_count)

                    self.m_t = self.beta1 * self.m_t + (1 - self.beta1) * self.g_cur
                    self.v_t = self.beta2 * self.v_t + (1 - self.beta2) * (self.g_cur ** 2)
                    self.lr_cur = lr_t * self.m_t / (np.sqrt(self.v_t) + self.epsilon)
                    self.x_cur = self.x_cur - self.lr_cur
                    if (self.step_count == 1) or (self.step_count % log_freq == 0):
                        log_func(self)
                log_func(self)

        old = OldAdamMinimizer(learning_rate=1)
        new = AdamMinimizer(learning_rate=1)
        print('\nOld Adam:')
        old.minimise(
            maxiter=30,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )
        print('\n\nNew Adam:')
        new.minimise(
            maxiter=30,
            theta_0=[15, -30],
            grad=grad, log_func=log_func, log_freq=1,
        )


    # test_adam()

    def use_scipy_to_find_the_minimum():
        from scipy.optimize import minimize
        # use conjugate gradient to find the minimum and see if it is correct
        res = minimize(fun=loss, x0=np.array([15, -30], dtype=float), method='Nelder-Mead')
        print(res)


    # use_scipy_to_find_the_minimum()

    def test_rprop():
        print('\n\nHow about rprop?:\n')
        rp = RProp()
        rp.x_cur = np.array([15, -30], np.float)
        log_freq = 1
        maxiter = 200
        while rp.step_count < maxiter:
            gradient_calculated, variable = rp.compute_gradient(grad=grad, variable=rp.x_cur)
            rp.apply_update(gradient_calculated=gradient_calculated, variable=variable)
            if (rp.step_count == 1) or (rp.step_count % log_freq == 0):
                log_func(rp)
        log_func(rp)
        del rp
    # test_rprop()
