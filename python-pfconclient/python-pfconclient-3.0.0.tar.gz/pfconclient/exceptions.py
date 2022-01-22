"""
Pfcon exceptions module.
"""


class PfconException(Exception): pass


class PfconRequestException(PfconException): pass


class PfconRequestInvalidTokenException(PfconRequestException): pass


class PfconErrorException(PfconException): pass

