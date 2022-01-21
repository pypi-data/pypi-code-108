#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

class Hyperplane():
    """
    Hyperplane object defined as :math:`a.x + r \geq 0`.
    """

    def __init__(self,
                 a=None,
                 r=None,
                 zero=10**-7,
                 verbose = 0):
        self.a = a
        self.r = r
        self.zero = zero
        self.verbose = verbose

    def set_by_points(self, A):
        """
        Set the hyperplane by points.

        Parameters
        ----------
        A : array-like of shape (n_samples, n_features)
            The points which define the hyperplane. Each row is a point.
            For `$d$` dimension, ``A`` should be of shape `$(d,d)$`.

        Returns
        -------
        self

        """
        if A.shape[0] != A.shape[1]:
            raise (ValueError('Unexpected A value. For a d dimension problem, it should be of shape (d,d).'))

        self.A = A
        try:
            self.a = np.linalg.solve(A, np.ones(A.shape[0]))
        except:
            if self.verbose > -1:
                print('Warning : epsilon-perturbation added to solve the system.')
            self.a = np.linalg.solve(A + (np.random.random(A.shape) * 2 - 1) * self.zero,
                                     np.ones(A.shape[0]))
            # self.a = np.linalg.lstsq(A, np.ones(A.shape[0]))[0]
            
        self.r = - np.dot(self.a, A[0])

        return (self)

    def distance(self, X, p=2):
        """
        Computes the distance to the hyperplane according to the formula :math:`d(x,p) = \\frac{x \centerdot a + r}{\| a \|_2^2}\| a \|_p`

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The points to compute the distance to the hyperplane.

        Returns
        -------
        dist : array-like of shape (n_samples,).
            The computed distances.
        
        """
        dist = np.abs(np.dot(X, self.a) + self.r) / np.linalg.norm(self.a, ord=2)**2 * np.linalg.norm(self.a, ord=p)

        return (dist)

    def set_positive_side(self, p):
        """
        Set the positive side.

        Parameters
        ----------
        p : array-like of shape (n_features,)
            A single point considered in the positive side.

        Raises
        ------
        
            ValueError : If p belongs to the hyperplane.

        Returns
        -------
        self

        """
        norm_p = np.dot(p[None, :], self.a) + self.r

        if norm_p == 0:
            raise (ValueError("P should not belongs to the hyperplane."))

        if norm_p < 0:
            self.a *= -1
            self.r *= -1
        
        return(self)

    def side(self, X):
        """
        Get the side boolean vector.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The points to get the side boolean.

        Returns
        -------
        s : array-like of shape (n_samples,)
            The boolean array indicating the side of each points. If True, the 
            element is considered to belong to the positive side.
        """
        g = np.dot(X, self.a) + self.r + self.zero
                
        return (g >= 0)
    
    def affine_transform(self, translation, scale, inplace=False):
        """
        Affine transformation of the hyperplane.

        Parameters
        ----------
        translation : array-like of shape (n_features,)
            The translation vector.
        scale : float or array-like of shape (n_features,)
            The scaling factor.
        inplace : bool, default=False
            If True, inplace translation and self returns. The default is False.

        Returns
        -------
        self or Hyperplane.

        """
        if scale is float:
            scale = np.ones(self.a.size) * scale
        
        t_a = np.zeros_like(self.a)
        for j in range(self.a.size):
            if ~np.isclose(self.a[j],0):
                t_a[j] = self.a[j] / scale[j]
                
        t_r = self.r - np.dot(self.a, translation)
        
        if inplace:
            self.a = t_a
            self.r = t_r
            return(self)
        else:
            return(Hyperplane(a = t_a, r = t_r))
    
    def compute_n_solutions(self):
        """
        Computes n solutions of a.x + b = 0

        Returns
        -------
        sol : array-like of shape (n_features, n_features)
            The solutions (among an infinity of others).
        """
        sol = []
        list_j = []
        for j in range(self.a.size):
            if ~np.isclose(self.a[j], 0):
                s = np.zeros_like(self.a)
                s[j] = -self.r / self.a[j]
                sol.append(s)
                list_j.append(j)
        
        list_j_bar = np.delete(np.arange(self.a.size), list_j)
        
        complete_sol = np.zeros((len(self.a), len(self.a)))
        complete_sol[list_j,:] = np.array(sol)
        
        for j in range(self.a.size):
            if j not in list_j:
                complete_sol[j,:] = sol[0]
                complete_sol[list_j_bar, j] = 1 
        
        return(complete_sol)
