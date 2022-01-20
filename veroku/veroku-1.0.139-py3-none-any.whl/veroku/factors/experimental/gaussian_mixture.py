"""
A module for instantiating and performing operations on multivariate Gaussian mixture distributions.
"""

# pylint: disable=cyclic-import
# pylint: disable=protected-access

# Standard imports
import cmath

# Third-party imports
import numpy as np
import numdifftools as nd
from matplotlib import pyplot as plt
from scipy.optimize import minimize
from scipy import special

# Local imports
from veroku.factors._factor import Factor
from veroku.factors import _factor_utils
import veroku.factors.gaussian as gauss
from veroku._constants import DEFAULT_FACTOR_RTOL, DEFAULT_FACTOR_ATOL

# TODO: confirm that the different GaussianMixture divide methods have sufficient stability and accuracy in their
#  approximations.
# TODO: Add tests for the divide methods.
# TODO: move to factors (non-experimental) once the divide methods have been checked and tested properly.


class GaussianMixture(Factor):
    """
    A Class for instantiating and performing operations on multivariate Gaussian mixture functions.
    """

    def __init__(self, factors, cancel_method=0):
        """
        A GaussianMixture constructor.

        :param factors: a list of Gaussian type objects with the same dimensionality.
        :type factors: Gaussian list
        :param cancel_method: The method of performing approximate division.
                              This is only applicable if the factor is a Gaussian mixture with more than one component.
                              0: moment match denominator to single Gaussian and divide
                              1: approximate modes of quotient as Gaussians
                              2: Use complex moment matching on inverse mixture sets (s_im) and approximate the inverse
                                 of each s_im as a Gaussian
        :type cancel_method: int
        """
        assert factors, "Error: empty list passed to constructor."
        self.cancel_method = cancel_method
        self.components = [gaussian.copy() for gaussian in factors]
        self.num_components = len(factors)

        var_names0 = factors[0].var_names

        for component in self.components:
            if var_names0 != component.var_names:
                raise ValueError("inconsistent var_names in list of Gaussians.")
        super().__init__(var_names=var_names0)

    @classmethod
    def from_sklearn_gmm(cls, gmm, var_names):
        """
        Extract the Gaussian mixture parameters from a learned sklearn Gaussian Mixture Model and
        construct an equivalent Gaussian mixture object.

        :param gmm: The Gaussian mixture model
        :type gmm: sklearn.mixture._bayesian_mixture.BayesianGaussianMixture
        :param var_names: The feature/variable names.
        :type var_names: str list
        :return: The Gaussian mixture.
        """
        gaussian_components = []
        for mean, cov, weight in zip(gmm.means_, gmm.covariances_, gmm.weights_):
            gaussian = gauss.Gaussian(var_names=var_names,
                                      mean=mean,
                                      cov=cov,
                                      log_weight=np.log(weight))
            gaussian_components.append(gaussian)
        return cls(gaussian_components)

    def equals(self, factor, rtol=DEFAULT_FACTOR_RTOL, atol=DEFAULT_FACTOR_ATOL):
        """
        Check if this factor is the same as another factor.

        :param factor: The factor to compare with.
        :type factor: GaussianMixture
        :param float rtol: The absolute tolerance parameter (see numpy Notes for allclose function).
        :param float atol: The absolute tolerance parameter (see numpy Notes for allclose function).
        :return: Result of equals comparison between self and gaussian
        rtype: bool
        """
        # TODO: consider adding type error here rather
        if not isinstance(factor, GaussianMixture):
            raise TypeError(f"factor must be of GaussianMixture type but has type {type(factor)}")
        if factor.num_components != self.num_components:
            return False
        for i in range(self.num_components):
            found_corresponding_factor = False
            for j in range(i, self.num_components):
                if self.get_component(i).equals(factor.get_component(j)):
                    found_corresponding_factor = True
            if not found_corresponding_factor:
                return False
        return True

    def get_component(self, index):
        """
        Get the Gaussian component at an index.

        :param index: The index of teh component to return.
        :type index: int
        :return: The component at the given index.
        :rtype: Gaussian
        """
        return self.components[index]

    def copy(self):
        """
        Make a copy of this Gaussian mixture.

        :return: The copied GaussianMixture.
        :rtype: GaussianMixture
        """
        component_copies = []
        for comp in self.components:
            component_copies.append(comp.copy())
        return GaussianMixture(component_copies)

    def multiply(self, factor):
        """
        Multiply this GaussianMixture with another factor.

        :param factor: The factor to multiply with.
        :type factor: Gaussian or Gaussian Mixture
        :return: The factor product.
        :rtype: GaussianMixture
        """
        new_components = []
        if isinstance(factor, gauss.Gaussian):
            for comp in self.components:
                new_components.append(comp.multiply(factor))
        elif isinstance(factor, GaussianMixture):
            for comp_ai in self.components:
                for comp_bi in factor.components:
                    new_components.append(comp_ai.multiply(comp_bi))
        else:
            raise TypeError("unsupported factor type.")
        return GaussianMixture(new_components)

    def divide(self, factor):
        """
        Divide this GaussianMixture by another factor.

        :param factor: The factor divide by.
        :type factor: Gaussian or Gaussian Mixture
        :return: The resulting factor quotient (approximate in the case of where both the numerator and denominator are
        GaussianMixtures with more than one component).
        :rtype: GaussianMixture
        """
        if isinstance(factor, gauss.Gaussian):
            single_gaussian = factor
        elif isinstance(factor, GaussianMixture):
            if factor.num_components == 1:
                single_gaussian = factor.get_component(index=0)
            else:
                if self.cancel_method == 0:
                    single_gaussian = factor.moment_match_to_single_gaussian()
                if self.cancel_method == 1:
                    return GaussianMixture._gm_division_m1(self, factor)
                if self.cancel_method == 2:
                    return GaussianMixture._gm_division_m2(self, factor)
        else:
            raise TypeError("unsupported factor type.")
        new_components = []
        for comp in self.components:
            new_components.append(comp.divide(single_gaussian))
        return GaussianMixture(new_components)

    def reduce(self, vrs, values):
        """
        Observe a subset of the variables in the scope of this Gaussian mixture and return the resulting factor.

        :param vrs: the names of the observed variable (list)
        :type vrs: str list
        :param values: the values of the observed variables (list or vector-like object)
        :type values: vector-like
        :return: the observation reduced factor.
        :rtype: GaussianMixture
        """
        new_components = []
        for comp in self.components:
            new_components.append(comp.reduce(vrs, values))
        return GaussianMixture(new_components)

    def marginalize(self, vrs, keep=True):
        """
        Integrate out variables from this Gaussian mixture.

        :param vrs: A subset of variables in the factor's scope.
        :type vrs: str list
        :param keep: Whether to keep or sum out vrs.
        :type keep: bool
        :return: the resulting marginal factor.
        :rtype: GaussianMixture
        """
        new_components = []
        for comp in self.components:
            new_components.append(comp.marginalize(vrs, keep))
        return GaussianMixture(new_components)

    def distance_from_vacuous(self):
        """
        NOTE: Not Implemented yet.
        Get the Kullback-Leibler (KL) divergence between the message factor and a vacuous (uniform) version of it.

        :return: The KL-divergence
        """
        raise NotImplementedError('This function has not been implemented yet.')

    def kl_divergence(self, factor):
        """
        NOTE: Not Implemented yet.
        Get the KL-divergence D_KL(self || factor) between a normalized version of this factor and another factor.

        :param factor: The other factor
        :type factor: GaussianMixture
        :return: The Kullback-Leibler divergence
        :rtype: float
        """
        raise NotImplementedError('This function has not been implemented yet.')

    def log_potential(self, x_val, vrs=None):
        """
        Get the log of the value of the Gaussian mixture potential at X.

        :param x_val: The point to evaluate the GaussianMixture at.
        :type x_val: vector-like
        :return: log of the value of the GaussianMixture potential at x.
        :rtype: float
        """
        log_potentials = []
        for comp in self.components:
            log_potentials.append(comp.log_potential(x_val=x_val, vrs=vrs))
        total_log_potx = special.logsumexp(log_potentials)
        return total_log_potx

    def potential(self, x_val):
        """
        Get the value of the Gaussian mixture potential at x_val.

        :param x_val: The point to evaluate the GaussianMixture at.
        :type x_val: vector-like
        :return: log of the value of the GaussianMixture potential at x_val.
        :rtype: float
        """
        total_potx = 0.0
        for comp in self.components:
            total_potx += comp.potential(x_val)
        return total_potx

    def _get_means(self):
        """
        Get the means of the Gaussian components.

        :return: the mean vectors
        """
        means = []
        for comp in self.components:
            means.append(comp.get_mean())
        return means

    def _get_covs(self):
        """
        Get the covariance matrices of the Gaussian components.

        :return: the covariance matrices
        :rtype: np.ndarray list
        """
        covs = []
        for comp in self.components:
            covs.append(comp.get_cov())
        return covs

    def _get_log_weights(self):
        """
        Get the log weights of the Gaussian mixture components.

        :return: the log weights
        :rtype: float
        """
        log_weights = []
        for comp in self.components:
            log_weights.append(comp.get_log_weight())
        return log_weights

    def _get_weights(self):
        """
        Get the weights of the Gaussian mixture components.

        :return: the log weights
        :rtype: float list
        """
        weights = []
        for comp in self.components:
            weights.append(comp.get_weight())
        return weights

    def get_log_weight(self):
        """
        Get the total log weight of the Gaussian mixture.

        :return: The log weight
        :rtype: float
        """
        return special.logsumexp(self._get_log_weights())

    def normalize(self):
        """
        Normalize the factor.

        :return: The normalized factor.
        :rtype: GaussianMixture
        """
        unnormalized_log_weight = self.get_log_weight()
        new_components = []
        for comp in self.components:
            comp_copy = comp.copy()
            comp_copy._add_log_weight(-1.0 * unnormalized_log_weight)
            new_components.append(comp_copy)
        return GaussianMixture(new_components)

    @property
    def is_vacuous(self):
        """
        Check if a Gaussian mixture distribution contains no information. This is the case when the K matrices of all
        components are zero matrices.

        :return: The result of the check.
        :rtype: Bool
        """
        # TODO: see how this is used. Should this be true if there is one vacuous component? Or only if all components
        #  are vacuous? Maybe make a contains vacuous function as well.
        for comp in self.components:
            if not comp._is_vacuous:
                return False
        return True

    def sample(self, num_samples):
        """
        Sample from this Gaussian mixture

        :param num_samples: The number of sample to draw.
        :type num_samples: int
        :return: The samples
        :rtype: float list
        """
        weights = self._get_weights()
        component_choice_samples = np.random.choice(
            range(len(weights)), size=num_samples, p=weights / np.sum(weights)
        )
        samples = []
        for comp_index in component_choice_samples:
            samples.append(self.components[comp_index].sample(1)[0])
        return np.array(samples)

    def _get_sensible_xlim(self):
        """
        Helper function for plot function to get the x limits that contain the majority of the Gaussian mass.

        :return: The x limits.
        :rtype: float list
        """
        x_lower_candidates = []
        x_upper_candidates = []
        for comp in self.components:
            stddev = np.sqrt(comp.get_cov()[0, 0])
            x_lower_candidates.append(comp.get_mean()[0, 0] - 3 * stddev)
            x_upper_candidates.append(comp.get_mean()[0, 0] + 3 * stddev)
        x_lower = min(x_lower_candidates)
        x_upper = max(x_upper_candidates)
        return [x_lower, x_upper]

    def plot(self, log=False, xlim=None, ylim=None, show_individual_components=False):
        """
        Plot the Gaussian mixture potential function (only for 1d and 2d functions).

        :param log: if this is True, the log-potential will be plotted
        :type log: bool
        :param xlim: the x limits to plot the function over (optional)
        :type xlim: 2 element float list
        :param ylim: the y limits to plot the function over (optional and only used in 2d case)
        :type ylim: 2 element float list
        """
        if self.dim == 1:
            if xlim is None:
                xlim = self._get_sensible_xlim()
            if xlim is not None:
                x_lower = xlim[0]
                x_upper = xlim[1]
            num_points = 200
            x_series = np.linspace(x_lower, x_upper, num_points)
            total_potx = np.zeros(num_points)
            for comp in self.components:
                if log:
                    potx = np.array([comp.log_potential(xi) for xi in x_series])
                else:
                    potx = np.array([comp.potential(xi) for xi in x_series])
                if show_individual_components:
                    plt.plot(x_series, potx)
                total_potx += potx
            plt.plot(x_series, total_potx)
        elif self.dim == 2:
            self._plot_2d(log=log, xlim=xlim, ylim=ylim)
        else:
            raise NotImplementedError("Plotting not implemented for dim!=1.")

    def show(self):
        """
        Print the parameters of the Gaussian mixture distribution
        """
        for i, comp in enumerate(self.components):
            print("component ", i, "/", len(self.components))
            comp.show()

    def moment_match_to_single_gaussian(self):
        """
        Calculate the mean and covariance of the Gaussian mixture and return a Gaussian with these parameters as an
        approximation of the Gaussian Mixture.

        :return: The Gaussian approximation.
        :rtype: Gaussian
        """
        new_mean = np.zeros([self.dim, 1])
        log_weights = []
        for comp in self.components:
            weight_mean = comp.get_weight() * comp.get_mean()
            new_mean += weight_mean
            log_weights.append(comp.get_log_weight())
        log_sum_weights = special.logsumexp(log_weights)
        sum_weights = np.exp(log_sum_weights)
        new_mean = new_mean / sum_weights
        new_cov = np.zeros([self.dim, self.dim])
        for comp in self.components:
            udud_t = comp.get_weight() * (comp.get_mean() - new_mean).dot(
                (comp.get_mean() - new_mean).transpose()
            )
            new_cov += comp.get_weight() * comp.get_cov() + udud_t
        new_cov = new_cov / sum_weights
        return gauss.Gaussian(
            cov=new_cov, mean=new_mean, log_weight=log_sum_weights, var_names=self.components[0].var_names
        )

    def argmax(self):
        """
        Find the input vector that maximises the potential function of the Gaussian mixture.

        :return: The argmax assignment.
        :rtype: numpy.ndarray
        """
        global_maximum_potential = -float("inf")
        global_argmax = None
        success = False

        def neg_gmm_log_pot(x_val):
            return -1.0 * self.log_potential(x_val)

        for comp in self.components:
            res = minimize(neg_gmm_log_pot, x0=comp.get_mean(), method="BFGS", options={"disp": False})
            x_local_max = res.x
            if res.success:
                success = True
                local_maximum_potential = self.potential(x_local_max)
                if local_maximum_potential > global_maximum_potential:
                    global_maximum_potential = local_maximum_potential
                    global_argmax = x_local_max
        if not success:
            raise Exception("could not find optimum")
        return global_argmax

    def _argmin(self):
        """
        Find the input vector that minimises the potential function of the Gaussian mixture with negative definite
        precision matrices.

        :return: The point where the function has a global minimum.
        :rtype: np.ndarray
        """
        global_minimum_potential = float("inf")
        global_argmin = None
        success = False

        def gmm_pot(x_vals):
            return self.potential(x_vals)

        for comp in self.components:
            res = minimize(gmm_pot, x0=comp.get_mean(), method="BFGS", options={"disp": False})
            x_local_min = res.x
            if res.success:
                success = True
                local_minimum_potential = self.potential(x_local_min)
                if local_minimum_potential < global_minimum_potential:
                    global_minimum_potential = local_minimum_potential
                    global_argmin = x_local_min
        if not success:
            raise Exception("could not find optimum")
        return global_argmin

    def _moment_match_complex_gaussian(self):
        """
        Calculate the mean and covariance of the Gaussian mixture and return a Gaussian
        with these parameters a Gaussian approximation of the Gaussian Mixture.

        :return: The Gaussian approximation.
        :rtype: Gaussian
        """
        # TODO: check if the normal moment matching function can be replaced with this one.
        new_mean = np.zeros([self.dim, 1]).astype(complex)
        weights = []
        for comp in self.components:
            c_weight = comp._get_complex_weight()
            c_mean = np.linalg.inv(comp.get_prec()).dot(comp.get_h()).astype(complex)
            new_mean += c_weight * c_mean
            weights.append(c_weight)
        sum_weights = sum(weights)
        new_mean = new_mean / sum_weights
        new_cov = np.zeros([self.dim, self.dim]).astype(complex)
        for comp in self.components:
            c_weight = comp._get_complex_weight()
            c_mean = np.linalg.inv(comp.get_prec()).dot(comp.get_h()).astype(complex)
            udud_t = c_weight * (c_mean - new_mean).dot((c_mean - new_mean).transpose())
            c_cov = np.linalg.inv(comp.get_prec()).astype(complex)
            new_cov += c_weight * c_cov + udud_t
        new_cov = new_cov / sum_weights

        new_log_weight = np.log(sum_weights)

        new_prec, new_h_vec, new_g = GaussianMixture._complex_cov_form_to_real_canform(
            new_cov, new_mean, new_log_weight
        )
        return gauss.Gaussian(prec=new_prec, h_vec=new_h_vec, g_val=new_g, var_names=self.components[0].var_names)

    @staticmethod
    def _complex_cov_form_to_real_canform(cov, mean, log_weight):
        """
        A helper function for _moment_match_complex_gaussian.

        :param cov: the (possibly complex) covariance matrix
        :param mean: the (possibly complex) covariance matrix
        :param log_weight: the (possibly complex) log weight
        :return: the real parts of the converted canonical parameters (prec, h_vec, g_val)
        """
        prec = np.linalg.inv(cov)
        h_vec = prec.dot(mean)
        ut_k_u = ((mean.transpose()).dot(prec)).dot(mean)
        log_det_term = cmath.log(np.linalg.det(2.0 * np.pi * cov))
        g_val = abs(log_weight - 0.5 * ut_k_u - 0.5 * log_det_term)
        return prec.real, h_vec.real, g_val.real

    @staticmethod
    def _get_inverse_gaussians(gaussian_mixture_a, gaussian_mixture_b):
        """
        A helper function for _gm_division_m1. Returns the inverse components.

        :param gaussian_mixture_a: The numerator mixture
        :param gaussian_mixture_b: The denominator mixture
        :return: The inverse Gaussian components and the mode locations of the quotient:
                 gaussian_mixture_a/gaussian_mixture_b

        Example:
            if gaussian_mixture_a = Ga1 + Ga2
            and gaussian_mixture_b = Gb1 + Gb2
            Then return Gb1/Ga1 + Gb1/Ga2 + Gb2/Ga1 + Gb2/Ga2
        """
        minimum_locations = []
        for g_a in gaussian_mixture_a.components:
            inverse_components = []
            inverse_gaussian_mixtures = []
            for g_b in gaussian_mixture_b.components:
                inverse_components.append(g_b.divide(g_a))
            inverse_gaussian_mixture = GaussianMixture(inverse_components)
            inverse_gaussian_mixtures.append(inverse_gaussian_mixture)

            minimum_loc = inverse_gaussian_mixture._argmin()
            minimum_locations.append(minimum_loc)

        def neg_gm_log_quotient_potential(x_val):
            """
            Get the negative of the log value of the Gaussian mixture quotient (gma/gmb)
            """
            potential = -1.0 * (gaussian_mixture_a.log_potential(x_val) - gaussian_mixture_b.log_potential(x_val))
            return potential

        mode_locations = []
        for minimum_loc in minimum_locations:
            res = minimize(
                neg_gm_log_quotient_potential, x0=minimum_loc, method="BFGS", options={"disp": False}
            )
            x_local_min = res.x
            if res.success:
                mode_locations.append(x_local_min)
        unique_mode_locations = _factor_utils.remove_duplicate_values(mode_locations, tol=1e-3)
        return inverse_gaussian_mixtures, unique_mode_locations

    @staticmethod
    def _gm_division_m1(gaussian_mixture_a, gaussian_mixture_b):
        """
        Method 1 for approximating the quotient (gma/gmb) of two Gaussian mixtures as a Gaussian mixture.
        This is an implementation of the method described in 'A Probabilistic Graphical Model Approach to Multiple
        Object Tracking' (section 8.2) The Gaussian mixture quotient is optimised from a set of starting points in order
        to find modes. Laplaces method is then used at these modes to approximate the mode as a Gaussian. The quotient
        is then approximated as a sum of these Gaussians.

        :param GaussianMixture gma: The numerator factor
        :param GaussianMixture gmb: The denominator factor
        :returns: an approximation of the quotient function as a Gaussian mixture
        :rtype: GaussianMixture
        """

        resulting_gaussian_components = []
        inverse_gaussian_mixtures, unique_mode_locations = GaussianMixture._get_inverse_gaussians(
            gaussian_mixture_a, gaussian_mixture_b
        )
        inv_gm = GaussianMixture(inverse_gaussian_mixtures)

        for mode_location in unique_mode_locations:
            prec_i = nd.Hessian(inv_gm.log_potential)(mode_location)
            mean_i = _factor_utils.make_column_vector(mode_location)
            h_i = prec_i.dot(mean_i)

            ut_k_u = ((mean_i.transpose()).dot(prec_i)).dot(mean_i)
            log_weight_i = -0.5 * np.log(np.linalg.det(prec_i / (2.0 * np.pi))) * inv_gm.log_potential(mean_i)
            g_i = log_weight_i - 0.5 * ut_k_u + 0.5 * np.log(np.linalg.det(prec_i / (2.0 * np.pi)))

            component = gauss.Gaussian(prec=prec_i, h_vec=h_i, g_val=g_i, var_names=gaussian_mixture_a.components[0].var_names)
            resulting_gaussian_components.append(component)
        return GaussianMixture(resulting_gaussian_components)

    @staticmethod
    def _gm_division_m2(gma, gmb):
        """
        Method 2 for approximating the quotient (gma/gmb) of two Gaussian mixtures as a Gaussian mixture.
        This function does applies the moment matching equations to sets of negative definite mixtures (using
        _moment_match_complex_gaussian). For each of these mixtures, a single negative definite 'Gaussian' (h(x)) is then
        obtained. This function is then inverted (g(x) = 1/h(x)), resulting in a positive definite Gaussian function.
        The Gaussian mixture quotient (gma/gmb) is then approximated as the sum of the g(x) functions.

        This method is can be much faster than _gm_division_m1 (~10 times [tested on for one dimensional functions]),
        but also results a Gaussian mixture with the same number of components as gma. Whereas _gm_division_m2 should
        have the same number of components as the modes of the quotient function.

        :param GaussianMixture gma: The numerator factor
        :param GaussianMixture gmb: The denominator factor
        :returns: An approximation of the quotient function as a Gaussian mixture
        :rtype: GaussianMixture
        """
        # TODO: add check for dimensions that are not devided by
        #       - the variances in these will not change (if this makes sense)

        inverse_gaussian_mixtures = []
        resulting_gaussian_components = []
        count = 0
        for gaussian_a in gma.components:
            inverse_components = []
            for gaussian_b in gmb.components:
                conditional = gaussian_b.divide(gaussian_a)
                inverse_components.append(conditional)
            inverse_gaussian_mixture = GaussianMixture(inverse_components)
            inverse_gaussian_mixtures.append(inverse_gaussian_mixture)
            inverse_gaussian_approx = inverse_gaussian_mixture._moment_match_complex_gaussian()
            if _factor_utils.is_pos_def(inverse_gaussian_approx.prec):
                count += 1
                # raise ValueError(' precision is negative definite.')
                print("Warning: precision is negative definite.")
            gaussian_approx = inverse_gaussian_approx._invert()
            resulting_gaussian_components.append(gaussian_approx)
        print("num pos def = ", count, "/", len(gma.components))
        resulting_gm = GaussianMixture(resulting_gaussian_components)
        return resulting_gm

    def _get_limits_for_2d_plot(self):
        """
        Get x and y limits which includes most of the Gaussian mixture's mass, by considering
        the mean and variance of each Gaussian component.
        """
        x_lower_candidates = []
        x_upper_candidates = []
        y_lower_candidates = []
        y_upper_candidates = []
        for comp in self.components:
            stddev_x = np.sqrt(comp.get_cov()[0, 0])
            stddev_y = np.sqrt(comp.get_cov()[1, 1])
            mean_x = comp.get_mean()[0, 0]
            mean_y = comp.get_mean()[1, 0]
            x_lower_candidates.append(mean_x - 3.0 * stddev_x)
            x_upper_candidates.append(mean_x + 3.0 * stddev_x)
            y_lower_candidates.append(mean_y - 3.0 * stddev_y)
            y_upper_candidates.append(mean_y + 3.0 * stddev_y)
        x_lower = min(x_lower_candidates)
        x_upper = max(x_upper_candidates)
        y_lower = min(y_lower_candidates)
        y_upper = max(y_upper_candidates)
        return [x_lower, x_upper], [y_lower, y_upper]

    def _plot_2d(self, log, xlim, ylim):
        """
        Plot a 2d Gaussian mixture potential function

        :param log: if this is True, the log-potential will be plotted
        :param xlim: the x limits to plot the function over (optional)
        :param ylim: the y limits to plot the function over (optional)
        """
        if xlim is None and ylim is None:
            xlim, ylim = self._get_limits_for_2d_plot()
        elif xlim is not None and ylim is not None:
            pass
        else:
            print("Warning: partial limits received. Generating limits automatically.")
            xlim, ylim = self._get_limits_for_2d_plot()

        xlabel = self.var_names[0]
        ylabel = self.var_names[1]

        if not log:
            _factor_utils.plot_2d(func=self.potential, xlim=xlim, ylim=ylim, xlabel=xlabel, ylabel=ylabel)
        else:
            _factor_utils.plot_2d(func=self.log_potential, xlim=xlim, ylim=ylim, xlabel=xlabel, ylabel=ylabel)
