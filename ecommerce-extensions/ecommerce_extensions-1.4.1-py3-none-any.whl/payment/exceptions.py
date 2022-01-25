""" Module for custom exceptions. """
from oscar.apps.payment.exceptions import GatewayError


class InvalidEdnxDecision(GatewayError):
    """The decision returned by ednx was not recognized."""


class TransactionPending(Exception):
    """Exception for when a payment status is pending"""
