#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


def derivative(x_values, y_values, order=1, averaging_window=1):
    """
    Calculate the numerical derivative of data.

    Calculation is done by averaging the left and right derivatives in the
    averaging window, only the outermost data points are calculated with only
    a one-sided derivative. Therefore, the outermost order*averaging_window
    data points suffer from the numerical calculation and might be grossly
    incorrect, especially if noisy data is used.

    Parameters
    ----------
    x_values : ndarray
        The x values. Must be a 1D array of shape (N,).
    y_values : ndarray
        A 2D array containing the y data. Must be of shape (M, N) with M data
        rows to be derived that share the same x data.
    order : int, optional
        Gives the derivative order. Default is 1.
    averaging_window : int, optional
        The data points on each side of each datapoint that are used for
        averaging. The larger the value, the more smoothed is the derivative.
        Default is 1.

    Returns
    -------
    derivative : ndarray
        An ndarray of the shape (M, N) containing the derivative values.

    """
    x_spacing = np.diff(x_values)

    for ii in range(order):
        y_spacing = np.diff(y_values, axis=1)

        left_derivative = y_spacing/x_spacing

        derivative_sum = np.zeros_like(left_derivative)
        for jj in range(2*averaging_window):
            derivative_sum += np.roll(left_derivative, -jj, axis=1)
        derivative_mean = derivative_sum[:, :-2*averaging_window+1]/(2*averaging_window)

        left_vector = left_derivative[:, :2*averaging_window-1]
        right_vector = left_derivative[:, -2*averaging_window+1:].T[::-1].T
        for kk, mm in enumerate([2*rr-1 for rr in range(1, averaging_window+1)]):
            derivative_mean = np.insert(
                derivative_mean, kk, np.sum(left_vector[:, 0:mm], axis=1)/mm,
                axis=1)
            derivative_mean = np.insert(
                derivative_mean, derivative_mean.shape[1]-kk,
                np.sum(right_vector[:, 0:mm], axis=1)/mm, axis=1)

        y_values = derivative_mean

    return derivative_mean
