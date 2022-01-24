"""AWS MLops package

This package contains the modules for managing your model cycle.
The package works if you have defined a config.py with all properties necessary:
see the documentation on https://aws-mlops.readthedocs.io/en/latest/

It is part of the educational repositories (https://github.com/pandle/materials)
to learn how to write stardard code and common uses of the TDD and CI / CD.

Package contents two main classes: MLOps, the main class, and DataStorage,
the other classes are splitted for each single step of model cycle.

    >>> import aws_mlops
    >>> help(aws_mlops)
    >>> import aws_mlops.mlops as MLOps
    >>> help(MLOps)

# license MIT
# support https://github.com/bilardi/aws-mlops/issues
"""
__version__ = '1.0.0'
__author__ = 'Alessandra Bilardi'
