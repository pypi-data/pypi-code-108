"""Module for defining deprecated regression class imports"""
# pylint: skip-file
from deprecated import deprecated
from clease import regression

__all__ = ('LinearRegression', 'Tikhonov', 'Lasso', 'BayesianCompressiveSensing',
           'ConstrainedRidge', 'GAFit', 'GeneralizedRidgeRegression', 'PhysicalRidge',
           'SequentialClusterRidge')

MSG = 'Import {} from clease.regression instead'
DEP_VERSION = '0.10.0'  # Deprecation version


@deprecated(version=DEP_VERSION, reason=MSG.format('LinearRegression'))
class LinearRegression(regression.LinearRegression):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('Tikhonov'))
class Tikhonov(regression.Tikhonov):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('Lasso'))
class Lasso(regression.Lasso):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('BayesianCompressiveSensing'))
class BayesianCompressiveSensing(regression.BayesianCompressiveSensing):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('ConstrainedRidge'))
class ConstrainedRidge(regression.ConstrainedRidge):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('GAFit'))
class GAFit(regression.GAFit):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('GeneralizedRidgeRegression'))
class GeneralizedRidgeRegression(regression.GeneralizedRidgeRegression):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('PhysicalRidge'))
class PhysicalRidge(regression.PhysicalRidge):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('SequentialClusterRidge'))
class SequentialClusterRidge(regression.SequentialClusterRidge):
    pass
