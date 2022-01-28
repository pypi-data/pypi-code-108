# -*- coding: utf-8 -*-
r"""
Mode following technique for two dimensional functions.
"""
import numpy as np
from pathlib import Path
from typing import Callable, Tuple, List, Union

import pandas as pd


class CModeFollowing2D:
    r"""

    """

    def __init__(self, f: Callable, initial: np.ndarray, mf_steps: int = 100, mf_steplength: float = 0.1,
                 h: float = 0.00001) -> None:
        r"""
        Initialize mode follower.

        Args:
            f(Callable): The energy function describing the surface

            initial(np.ndarray): 2D point (will be automatically projected on the surface). For this configuration the
            hessian will be diagonalized).

            h(float): finite element for hessian approximations

            mf_steps(int): number of iterations following one mode

            mf_steplength(float): scaling factor for the displacement along the eigenvector
        """
        self._initial = initial
        self._f = self._function_wrapper(f=f)
        self._h = h
        self._mfsteplength = mf_steplength
        self._mfsteps = mf_steps
        # identify the eigenvectors and eigenvalues for the initial state
        self._eigenvalues_initial, self._eigenvectors_initial = self.diagonalize_hessian(self._initial)
        print(f'The given initial state has the eigenvalues: {self._eigenvalues_initial} \n The given intial state'
              f'has the eigenvectors: {self._eigenvectors_initial}.')

    @property
    def eigenvalues_initial(self) -> np.ndarray:
        r"""
        Returns:
            the eigenvalues of the initial point
        """
        return self._eigenvalues_initial

    @property
    def eigenvectors_initial(self) -> np.ndarray:
        r"""
        Returns:
            the eigenvectors of the intial point
        """
        return self._eigenvectors_initial

    @staticmethod
    def _function_wrapper(f: Callable) -> Callable:
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
            return f(x, y)

        return wrapper

    def __call__(self, mode_index: int = 0, i_write_out: bool = False, gralog: int = 1,
                 write_out: Union[Path, None] = None) -> Tuple[List[np.ndarray],List[float],List[np.ndarray]]:
        r"""

        Args:
            mode_index(int): index of the mode to follow
            i_write_output(bool): boolean whether an output is written to a file
            gralog(int): frequency for output writing
            write_out(Path): Path for potential output file

        Returns:
            a list of the points (2D ndarrays), the eigenvalues and the eigenvectors calculated for the mode following
            for the selected mode
        """
        if write_out is None:
            write_out = Path.cwd() / f'mf_{mode_index}.dat'
        if mode_index not in [0, 1]:
            raise ValueError("This is a 2D problem. There are only 2 evecs. Please enter 0 or 1.")

        evec = self._eigenvectors_initial[mode_index]
        eval = self._eigenvalues_initial[mode_index]
        current_point = self._initial
        write_dict = {'iteration': [0], 'current_point': [current_point], 'eigenvalue': [eval],
                          'eigenvector': [evec]}

        for step in range(self._mfsteps):
            displaced_point = self._displace_structure(current_point, evec, self._mfsteplength)
            new_evals, new_evecs = self.diagonalize_hessian(displaced_point)
            new_index, evec = self._modetracker(evec, new_evecs)
            if np.mod(step, gralog) == 0:
                write_dict['iteration'].append(step)
                write_dict['current_point'].append(displaced_point)
                write_dict['eigenvalue'].append(new_evals[new_index])
                write_dict['eigenvector'].append(evec)
                df = pd.DataFrame(write_dict)
                df.to_json(write_out)
            current_point = displaced_point
        if i_write_out:
            df = pd.DataFrame(write_dict)
            df.to_json(write_out)
        return write_dict['current_point'], write_dict['eigenvalue'], write_dict['eigenvector']


    def _modetracker(self, current_eigenvector: np.ndarray, new_eigenvectors: np.ndarray) -> Tuple[int, np.ndarray]:
        r"""
        Chooses the eigenvector from the new eigenvector set which gives the highest normalized inner product with the
        previous eigenvector.

        Args:
            current_eigenvector(np.ndarray): the current eigenvector

        Returns:
            the best choice for the eigenvector to stay on the same mode and the index of the eigenvalue to which the
            new eigenvector belongs to
        @todo: something seems not to work here! (For the sp it always detects the same mode)
        """
        best_quality = 0  # the closer to 1 the better
        chosen_evec = None
        index_chosen_evec = None
        for (idx, evec) in enumerate(new_eigenvectors):
            quality = np.dot(evec, current_eigenvector) / (np.linalg.norm(evec) * np.linalg.norm(current_eigenvector))

            if abs(quality) >= best_quality:
                if quality<=0:
                    chosen_evec = -1 *evec
                else:
                    chosen_evec = evec
                index_chosen_evec = idx
        return index_chosen_evec, chosen_evec

    @staticmethod
    def _displace_structure(point: np.ndarray, displacement: np.ndarray, steplength: float = 0.1) -> np.ndarray:
        r"""
        Displaces a 2D point along a 2D vectors according to a steplength

        Args:
            point: point for displacement (usually the current step of the modefollowing
            displacement: displacementvector (2D) (usually the current eigenvector
            steplength: scale the step

        Returns:
            the displaced point
        """
        return point + displacement * steplength

    def diagonalize_hessian(self, point: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Diagonalize the hessian of the energy landscape for a given point.

        Args:
            point: 2D point for which the hessian will be diagonalized

        Returns:
            the eigenvalues and eigenvectors
        """
        hess = self._hessian(point, self._h)
        # calculate eigenvalues and normalized eigenvectors:
        return np.linalg.eigh(hess)

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
