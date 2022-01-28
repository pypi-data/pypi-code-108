# -*- coding: utf-8 -*-
r"""
Newton minimization technique for two dimensional functions
"""
import numpy as np
from pathlib import Path
from typing import Callable


class CNewton2D:
    r"""
    Newton minimization technique for 2 dimensional configuration spaces
    """

    def __init__(self, f: Callable, initial: np.ndarray, iterations: int = 20,
                 modification_technique: str = 'nondiagonal_trivial', h: float = 0.00001) -> None:
        r"""
        Initialize newtons method

        Args:
            f(Callable): Callable for energy landscape

            initial(np.ndarray): start point for the calculation

            iterations(int): number of steps

            modification_technique(str): decider string for modification technique of the hessian in non convex regions

            h(float): finite element for hessian approximations
        """
        if len(initial) != 2:
            raise ValueError('Start point has to be 2 dimensional')
        self._initial = initial
        self._f = self._function_wrapper(f=f)
        self._iterations = iterations
        self._modification_technique = modification_technique
        self._h = h

    def _function_wrapper(self, f: Callable) -> Callable:
        r"""
        This wrapper changes the input structure of the callable to be in line with the visualization interface. The
        visualization interface uses a function which takes f(x,y) while the methods in this class need a callable with
        the parameter f(r(x,y)). This wrapper provides this functionality.
        Args:
            f: takes a callable with the functionality f(x,y)

        Returns: a function with f(r).
        """
        def wrapper(r: np.ndarray) -> np.ndarray:
            if len(np.shape(r)) == 1:
                x = r[0]
                y = r[1]
            else:
                x = r[:, 0]
                y = r[:, 1]
            return f(x,y)
        return wrapper

    def __call__(self, i_write_output: bool = False, gralog: int = 1,
                 write_out: Path = Path.cwd() / 'newton.dat') -> np.ndarray:
        r"""
        Calls newtons method

        Args:
            i_write_output(bool): boolean whether an output is written to a file
            gralog(int): frequency for output writing
            write_out(Path): Path for potential output file
        Returns:
            Sequence of point passed by in the minimization. Obtain the minimum through [-1,:]
        """
        points = []
        currentpoint = self._initial
        points.append(currentpoint)
        if i_write_output:
            with open(str(write_out), 'w') as f:
                f.write(f'iter  pointx  pointy  step  forcex  forcey\n')
        for k in range(self._iterations):
            # ensure that hessian is positive definite
            if self._modification_technique == 'nondiagonal_trivial':
                Bk = self._mod_nondiag_trivial(point=currentpoint, delta=1)
            elif self._modification_technique == 'diagonal_trivial':
                Bk = self._mod_diag_trivial(point=currentpoint, delta=1)
            elif self._modification_technique == 'cholesky':
                Bk = self._mod_cholesky(point=currentpoint)
            else:
                raise NotImplementedError('Modification method not implemented!')
            # calculate energy gradient:
            grad = self._gradient(point=currentpoint, h=self._h)
            print('flag0')
            pk = np.linalg.solve(Bk, -1 * grad)
            print('flag1')
            alpha_k = self._choose_steplength(point=currentpoint, step=pk, grad=grad)
            # displace current point
            if np.mod(k, gralog) == 0:
                if i_write_output:
                    with open(str(write_out), 'a') as f:
                        f.write(f'{k}  {currentpoint[0]}  {currentpoint[1]}  {alpha_k}  {pk[0]}  {pk[1]}\n')
                print(f"iteration Newton: {k},point: {currentpoint} , force: {pk * alpha_k}")
            # convergence criterium:
            currentpoint_new = currentpoint + alpha_k * pk
            print('flag2')
            if np.linalg.norm(currentpoint_new - currentpoint) <= 1e-6:
                break
            currentpoint = currentpoint_new
            points.append(currentpoint_new)
        return np.asarray(points)

    def _choose_steplength(self, point: np.ndarray, step: np.ndarray, grad: np.ndarray, reducefactor: float = 0.6,
                           c1: float = 1e-4, startalpha: float = 1) -> float:
        r"""
        Backtracking algorithm with sufficient decrease condition

        Args:
            point(np.ndarray): current point

            step(np.ndarray): current direction of the line search

            grad(np.ndarray): current gradient

            reducefactor(float): reduce factor for alpha. Has to be in interval (0,1)

            c1(float): condition number for sufficient decrease condition. Is usually very small

            startalpha(float): biggest value of alpha which is gradually reduced if condition is not satisfied. For
            Newtons method is should be 1.

        Returns:
            the step length
        """
        alpha = startalpha
        alpha = 1.0
        #while self._f(point + alpha * step) >= (self._f(point) + c1 * alpha * np.dot(grad, step)):
        #    alpha = reducefactor * alpha
        #    print(alpha)
        return alpha

    def _mod_nondiag_trivial(self, point: np.ndarray, delta: float = 1) -> np.ndarray:
        r"""
        Nondiagonal modification technique for delivering a positive definite approx of the hessian.

        Args:
            point(np.ndarray): current point

            delta(float): limit for pos. def. If delta = 1 the negative eigenvalues are mirrored around 1. Another
            option is to set delta larger than machine precision u. E.g. delta= sqrt(u) which is around 10^-8. This
            can leed to really large steps (artificial for Newtons methods).

        Returns:
            positive definite modification of hessian
        """
        # first calculate eigenvalues
        hess = self._hessian(point=point, h=self._h)
        # spectral decomposition the eigenvecs are represented by Q (the columns are the eigenvectors)
        eigenvals, eigenvecs = np.linalg.eigh(hess)
        # build tau_i
        tau = np.array([0.0 if eigenval >= delta else delta - eigenval for eigenval in eigenvals])
        # return modifcated hessian
        return eigenvecs.dot(np.diag(eigenvals + tau)).dot(eigenvecs.T)

    def _mod_diag_trivial(self, point: np.ndarray, delta: float = 1.0) -> np.ndarray:
        r"""
        Diagonal modification technique for delivering a positive definite approx of the hessian.

        Args:
            point(np.ndarray): current point

            delta(float): limit for pos. def. If delta = 1 the negative eigenvalues are mirrored around 1. Another
            option is to set delta larger than machine precision u. E.g. delta= sqrt(u) which is around 10^-8. This
            can leed to really large steps (artificial for Newtons methods).

        Returns:
            positive definite modification of hessian
        """
        # first calculate eigenvalues
        hess = self._hessian(point=point, h=self._h)
        # spectral decomposition the eigenvecs are represented by Q (the columns are the eigenvectors)
        eigenvals, eigenvecs = np.linalg.eigh(hess)
        tau = max(0.0, delta - eigenvals[0])
        return hess + tau * np.identity(2)

    def _mod_cholesky(self, point: np.ndarray, beta: float = 1e-3, iterations: int = 100):
        r"""
        Cholesky with added multiple of identity

        Args:
            point(np.ndarray): current point

            beta(float): heuristic parameter typical value 1e-3

            iterations(int): iterations needed to obtain positive definite matrix

        Returns:
            positive definite approximation of hessian
        """
        # first calculate hessian
        hess = self._hessian(point=point, h=self._h)
        # dimension of problem
        n = hess.shape[0]
        if min([hess[aii][aii] for aii in range(n)]) > 0:
            tau_0 = 0
        else:
            tau_0 = -1 * min([hess[aii][aii] for aii in range(n)]) + beta
        tau_k = tau_0
        for k in range(iterations):
            A = hess + tau_k * np.identity(n)
            try:
                L = np.linalg.cholesky(A)
                return L.dot(L.T)
            except np.linalg.LinAlgError:
                tau_k = max(tau_k * 2, beta)
                continue

    def _hessian(self, point: np.ndarray, h: float) -> np.ndarray:
        r"""
        Calculate the hessian for a given point with finite elements

        Args:
            point(np.ndarray): Point for which the hessian is evaluated.
            h(float): finite element

        Returns:
            numpy array of hessian: [[dfdxdx, dfdxdy],[dfdydx, dfdydy]]
        """
        hess = np.zeros(shape=(2, 2))
        # diagonal terms
        hess[0, 0] = (self._f(point + 2 * h * np.array([1, 0])) - 2 * self._f(point + h * np.array([1, 0])) + self._f(
            point)) / h ** 2
        hess[1, 1] = (self._f(point + 2 * h * np.array([0, 1])) - 2 * self._f(point + h * np.array([0, 1])) + self._f(
            point)) / h ** 2
        hess[0, 1] = (self._f(point + h * np.array([1, 1])) - self._f(point + h * np.array([1, 0])) - self._f(
            point + h * np.array([0, 1])) + self._f(point)) / h ** 2
        hess[1, 0] = hess[0, 1]
        return hess

    def _gradient(self, point: np.ndarray, h: float) -> np.ndarray:
        r"""
        Calculate the energy gradient

        Args:
            point(np.ndarray): Point for which the gradient is evaluated.
            h(float): finite element

        Return:
             1d numpy array with length 2: [dfdx,dfdy]
        """
        dfdx = (self._f(point + h * np.array([1, 0])) - self._f(point)) / h
        dfdy = (self._f(point + h * np.array([0, 1])) - self._f(point)) / h
        return np.array([dfdx, dfdy])
