import numpy as np
from pyctp import saftvrmie
import scipy.linalg as lin
from scipy.constants import Boltzmann, Avogadro
from scipy.integrate import quad
from pykingas.KineticGas import cpp_KineticGas
import warnings

FLT_EPS = 1e-12

def check_valid_composition(x):
    if abs(sum(x) - 1) > FLT_EPS:
        warnings.warn('Mole fractions do not sum to unity, sum(x) = '+str(sum(x)))

class KineticGas:

    default_N = 7

    def __init__(self, comps, mole_weights=None, sigma=None, eps_div_k=None):
        '''
        :param comps (str): Comma-separated list of components, following Thermopack-convention
        :param BH (bool) : Use Barker-Henderson diameters?

        Default parameters are equal to default parameters for saft-vr-mie (saftvrmie_parameters.f90)
        If parameters are explicitly supplied, these will be used instead of defaults
        :param mole_weights : (1D array) Molar weights [g/mol]
        :param sigma : (1D array) hard-sphere diameters [m]
        :param eps_div_k : (1D array) epsilon parameter / Boltzmann constant [-]
        '''
        self.T = None
        self.particle_density = None
        self.mole_fracs = None
        self.computed_d_points = {} # dict of state points in which (d_1, d0, d1) have already been computed
        self.computed_a_points = {}  # dict of state points in which (a_1, a1) have already been computed

        self.eos = saftvrmie.saftvrmie() # Only used as interface to mie-parameter database
        self.eos.init(comps)

        complist = comps.split(',')
        if mole_weights is None:
            mole_weights = np.array([self.eos.compmoleweight(self.eos.getcompindex(comp)) for comp in complist])
        self.mole_weights = np.array(mole_weights) * 1e-3 / Avogadro
        self.m0 = np.sum(self.mole_weights)
        self.M = self.mole_weights/self.m0
        self.M1, self.M2 = self.M

        if eps_div_k is None:
            eps_div_k = [self.eos.get_pure_fluid_param(i)[2] for i in range(1, len(complist) + 1)]
        self.epsilon_ij = self.get_epsilon_matrix(eps_div_k)
        self.epsilon = np.diag(self.epsilon_ij)

        if sigma is None:
            sigma = np.array([self.eos.get_pure_fluid_param(i)[1] for i in range(1, len(complist) + 1)])
        self.sigma_ij = self.get_sigma_matrix(sigma, BH=False)
        self.sigma = np.diag(self.sigma_ij)

        self.cpp_kingas = cpp_KineticGas(self.mole_weights, self.sigma_ij)


    def get_A_matrix(self, T, mole_fracs, N=default_N):
        check_valid_composition(mole_fracs)
        return self.cpp_kingas.get_A_matrix(T, mole_fracs, N)

    def get_reduced_A_matrix(self, T, mole_fracs, N=default_N):
        check_valid_composition(mole_fracs)
        return self.cpp_kingas.get_reduced_A_matrix(T, mole_fracs, N)

    def compute_d_vector(self, T, particle_density, mole_fracs, N=default_N, BH=False):
        check_valid_composition(mole_fracs)
        if (T, particle_density, tuple(mole_fracs), N, BH) in self.computed_d_points.keys():
            return self.computed_d_points[(T, particle_density, tuple(mole_fracs), N, BH)]

        if BH:
            sigmaij = self.get_sigma_matrix(self.sigma, BH=BH, T=T)
            cpp_kingas = cpp_KineticGas(self.mole_weights, sigmaij)

        else:
            cpp_kingas = self.cpp_kingas

        A = cpp_kingas.get_A_matrix(T, mole_fracs, N)

        delta = cpp_kingas.get_delta_vector(T, particle_density, N)
        d = lin.solve(A, delta)
        d_1, d0, d1 = d[N - 1], d[N], d[N + 1]

        self.computed_d_points[(T, particle_density, tuple(mole_fracs), N, BH)] = (d_1, d0, d1)
        return (d_1, d0, d1)

    def compute_a_vector(self, T, particle_density, mole_fracs, N=default_N, BH=False):
        check_valid_composition(mole_fracs)
        if (T, particle_density, tuple(mole_fracs), N, BH) in self.computed_a_points.keys():
            return self.computed_a_points[(T, particle_density, tuple(mole_fracs), N, BH)]

        if BH:
            sigmaij = self.get_sigma_matrix(self.sigma, BH=BH, T=T)
            cpp_kingas = cpp_KineticGas(self.mole_weights, sigmaij)
        else:
            cpp_kingas = self.cpp_kingas

        A = cpp_kingas.get_reduced_A_matrix(T, mole_fracs, N)
        alpha = cpp_kingas.get_alpha_vector(T, particle_density, mole_fracs, N)
        a = lin.solve(A, alpha)
        a_1, a1 = a[N - 1], a[N]

        self.computed_a_points[(T, particle_density, tuple(mole_fracs), N, BH)] = (a_1, a1)
        return a_1, a1

    def alpha_T0(self, T, Vm, x, N=default_N, BH=False):
        '''
        Compute the thermal diffusion factor
        :param T: Temperature [K]
        :param Vm: Molar volume [m3/mol]
        :param x: Molar composition [-]
        :param N: Order of Enskog approximation [-]
        :param BH: Use Barker-Henderson diameters?
        :return: (ndarray) Thermal diffusion factors [-]
        '''

        check_valid_composition(x)
        particle_density = Avogadro / Vm
        d_1, d0, d1 = self.compute_d_vector(T, particle_density, x, N=N, BH=BH)
        kT = - (5 / (2 * d0)) * ((x[0] * d1 / np.sqrt(self.M[0])) + (x[1] * d_1 / np.sqrt(self.M[1])))
        kT_vec = np.array([kT, -kT])
        return kT_vec * ((1 / np.array(x)) + (1 / (1 - np.array(x))) )

    def interdiffusion(self, T, Vm, x, N=default_N, BH=False):
        '''
        Compute the interdiffusion coefficient
        :param T: Temperature [K]
        :param Vm: Molar volume [m3/mol]
        :param x: Molar composition [-]
        :param N: Order of Enskog approximation [-]
        :param BH: Use Barker-Henderson diameters?
        :return: (float) Interdiffusion coefficient [m^{-2}s^{-1}]
        '''
        check_valid_composition(x)
        particle_density = Avogadro / Vm
        _, d0, _ = self.compute_d_vector(T, particle_density, x, N=N, BH=BH)

        return 0.5 * np.product(x) * np.sqrt(2 * Boltzmann * T / self.m0) * d0

    def thermal_diffusion(self, T, Vm, x, N=default_N, BH=False):
        '''
        Compute the thermal diffusion ratios
        :param T: Temperature [K]
        :param Vm: Molar volume [m3/mol]
        :param x: Molar composition [-]
        :param N: Order of Enskog approximation [-]
        :param BH: Use Barker-Henderson diameters?
        :return: (ndarray) Thermal diffusion ratios [-]
        '''
        check_valid_composition(x)
        particle_density = Avogadro / Vm
        d_1, _, d1 = self.compute_d_vector(T, particle_density, x, N=N, BH=BH)
        return - (5 / 4) * np.product(x) * np.sqrt(2 * Boltzmann * T / self.m0) \
               * ((x[0] * d1 / np.sqrt(self.M1)) + (x[1] * d_1 / np.sqrt(self.M2)))

    def thermal_conductivity(self, T, Vm, x, N=default_N, BH=False):
        '''
        Compute the Thermal conductivity
        :param T: Temperature [K]
        :param Vm: Molar volume [m3/mol]
        :param x: Molar composition [-]
        :param N: Order of Enskog approximation [-]
        :param BH: Use Barker-Henderson diameters?
        :return: (float) Thermal conductivity [W m^{-2} K^{-1}]
        '''
        check_valid_composition(x)
        particle_density = Avogadro / Vm
        a_1, a1 = self.compute_a_vector(T, particle_density, x, N=N, BH=BH)
        return - (5 / 4) * Boltzmann * particle_density * np.sqrt(2 * Boltzmann * T / self.m0) \
               * ((x[0] * a1 / np.sqrt(self.M1)) + (x[1] * a_1 / np.sqrt(self.M2)))

    def get_epsilon_matrix(self, eps_div_k):
        epsilon = np.array(eps_div_k) * Boltzmann
        return np.sqrt(epsilon * np.vstack(epsilon))

    def get_sigma_matrix(self, sigma, BH=False, T=None):
        '''
        Get Barker-Henderson diameters for each pair of particles.
        Using Lorentz-Berthleot rules for combining Mie-parameters for each pair of particles

        :param sigma: (1D array) hard sphere diameters [m]
        :return: N x N matrix of hard sphere diameters, where sigma_ij = 0.5 * (sigma_i + sigma_j),
                such that the diagonal is the radius of each component, and off-diagonals are the average diameter of
                component i and j.
        '''

        sigma_ij = 0.5 * np.sum(np.meshgrid(sigma, np.vstack(sigma)), axis=0)

        if BH:
            return np.array([[quad(self.BH_integrand, 0, sigma_ij[i, j], args=(sigma_ij[i, j], self.epsilon_ij[i, j], T))[0]
                              for i in range(len(sigma_ij))]
                             for j in range(len(sigma_ij))])
        else:
            return sigma_ij

    def BH_integrand(self, r, sigma, epsilon, T):
        lambda_r = 12
        lambda_a = 6
        return 1 - np.exp(-self.u_Mie(r, sigma, epsilon, lambda_r, lambda_a) / (T * Boltzmann))

    def u_Mie(self, r, sigma, epsilon, lambda_r, lambda_a):
        C = lambda_r / (lambda_r - lambda_a) * (lambda_r / lambda_a) ** (lambda_a / (lambda_r - lambda_a))
        return C * epsilon * ((sigma / r) ** lambda_r - (sigma / r) ** lambda_a)

def test():
    comps = 'AR,HE'
    kingas = KineticGas(comps)

    T = 300
    x = [0.7, 0.3]
    Vm = 24e-3

    alpha_T0 = kingas.alpha_T0(T, Vm, x)
    D12 = kingas.interdiffusion(T, Vm, x)
    DT = kingas.thermal_diffusion(T, Vm, x)
    thermal_cond = kingas.thermal_conductivity(T, Vm, x)

    kingas.alpha_T0(T, Vm, x, BH=True)
    kingas.interdiffusion(T, Vm, x, BH=True)
    kingas.thermal_diffusion(T, Vm, x, BH=True)
    kingas.thermal_conductivity(T, Vm, x, BH=True)

    if any(abs(alpha_T0 - kingas.alpha_T0(T, Vm, x)) > FLT_EPS):
        return 1
    if abs(D12 - kingas.interdiffusion(T, Vm, x)) > FLT_EPS:
        return 2
    if abs(DT - kingas.thermal_diffusion(T, Vm, x)) > FLT_EPS:
        return 3
    if abs(thermal_cond - kingas.thermal_conductivity(T, Vm, x)) > FLT_EPS:
        return 4

    return 0
