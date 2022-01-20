"""
A module for computing and transforming sigma points and converting between sigma points and covariance parameters.
"""

import numpy as np
import veroku.factors.gaussian as gauss


def get_sigma_points_array(gaussian_factor):
    """
    Get 2*dim + 1 equals weight sigma points for a Gaussian distribution with the given parameters.

    :param gaussian_factor: The factor
    :return: (numpy array) An array with sigma points as column vectors.
    """
    assert isinstance(gaussian_factor, gauss.Gaussian), "Error: gaussian_factor is not a Gaussian factor."
    cov = gaussian_factor.get_cov()
    mean = gaussian_factor.get_mean()
    chol = np.linalg.cholesky(cov)
    dim = cov.shape[0]
    k = (dim + 0.5) ** 0.5
    sigma_point_array_n = mean - k * chol
    sigma_point_array_p = mean + k * chol
    sigma_points_array = np.concatenate([sigma_point_array_n, mean, sigma_point_array_p], axis=1)
    return sigma_points_array


def sigma_point_array_to_gaussian_params(sigma_point_array):
    """
    Convert a sigma point array to Gaussian covariance parameters.

    :param sigma_point_array: (numpy array) An array where the columns correspond to sigma points.
    :return: The mean (numpy array) and covariance (numpy array) of the sigma points.
    """
    mean = np.expand_dims(np.mean(sigma_point_array, axis=1), axis=1)
    cov = np.cov(sigma_point_array, bias=1)
    return cov, mean


def sigma_points_to_gaussian_params(sigma_points):
    """
    Convert a sigma points to Gaussian covariance parameters.

    :param sigma_points: (list of numpy arrays) An array where the columns correspond to sigma points.
    :return: The mean (numpy array) and covariance (numpy array) of the sigma points.
    """
    sigma_point_array = np.concatenate(sigma_points, axis=1)
    return sigma_point_array_to_gaussian_params(sigma_point_array)


def sigma_points_array_to_joint_params(sigma_points_array, transform, var_names=None):
    """
    Construct joint sigma points using the original sigma points and the transform function, then Calculate the joint
    covariance parameters of the joint sigma points.

    :param sigma_points_array: (numpy array) An array where the columns correspond to sigma points.
    :param transform: (function) The transformation function.
    :param var_names: The variable names of the variables to be transformed.
    :return: The joint mean (numpy array) and joint covariance (numpy array) of the sigma points.
    """
    transformed_sigma_points_array = transform(sigma_points_array, var_names)
    joint_sigma_point_array = np.concatenate([sigma_points_array, transformed_sigma_points_array], axis=0)
    joint_cov, joint_mean = sigma_point_array_to_gaussian_params(joint_sigma_point_array)
    return joint_cov, joint_mean
