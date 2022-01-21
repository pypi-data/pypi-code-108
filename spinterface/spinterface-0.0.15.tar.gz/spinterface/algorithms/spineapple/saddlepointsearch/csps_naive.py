# -*- coding: utf-8 -*-

# @todo:ADAPT THIS TO THE NEW STRUCTURE
r"""
Naive implementation of the saddle point search for 2d (x,y).
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Callable


class CSPS_2D_naive:
    r"""
    Class for naive implementation of SPS
    """

    def __init__(self, f: Callable, initial: np.ndarray, iterations: int = 1000, ds: float = 0.001,
                 h: float = 0.00001) -> None:
        r"""
        Initialize SPS

        Args:
            f(Callable): Callable for energy landscape

            initial(np.ndarray): start point for the calculation

            iterations(int): number of eigenvector displacements

            ds(float): step width along eigenvector

            h(float): finite element

        """
        if len(initial) != 2:
            raise ValueError('Start point has to be 2 dimensional')
        self._initial = initial
        self._f = f
        self._iterations = iterations
        self._ds = ds
        self._h = h

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

    def __call__(self, gralog: int, write_out: Path = Path.cwd() / 'sps.dat'):
        r"""
        Call the SPS

        Args:
            gralog(int): frequency of output writing
        """
        current_point = self._initial
        with open(str(write_out), 'w') as f:
            f.write(f'iter  pointx  pointy  eval1  eval2  evec1x  evec1y  evec2x  evec2y  forcex  forcey\n')
        for iter in range(self._iterations):
            hess = self._hessian(current_point, self._h)
            # calculate eigenvalues and normalized eigenvectors:
            eigenvals, eigenvecs = np.linalg.eigh(hess)
            # eigenvalues and eigenvectors are returned in ascending order. Chose minimum:
            eigenval = eigenvals[0]
            eigenvec = eigenvecs[:, 0]
            # calculate negative gradient
            neg_grad = -1 * self._gradient(current_point, self._h)
            force = neg_grad - 2 * (np.dot(neg_grad, eigenvec)) * eigenvec
            # do step (eventually scale with eigenvalue?)
            current_point = current_point + force * self._ds
            if np.mod(iter, gralog) == 0:
                with open(str(write_out), 'a') as f:
                    f.write(
                        f'{iter}  {current_point[0]}  {current_point[1]}  {eigenvals[0]}  {eigenvals[1]}  {eigenvecs[0, 0]}  {eigenvecs[1, 0]}  {eigenvecs[0, 1]}  {eigenvecs[1, 1]}  {force[0]}  {force[1]}\n')
                print(f"iteration GNEB: {iter},point: {current_point} , force: {force}")
