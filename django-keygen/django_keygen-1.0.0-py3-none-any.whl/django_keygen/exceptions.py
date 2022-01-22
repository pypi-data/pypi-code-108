"""Custom warning classes for the parent application."""


class SecurityWarning(Warning):
    """Warning related to usage of insecure settings"""


class SecurityException(Exception):
    """Error related to usage of insecure settings"""
