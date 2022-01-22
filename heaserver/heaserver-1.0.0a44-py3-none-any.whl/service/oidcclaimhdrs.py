"""
Header constants for the Open ID Connect standard claims, and additional claims specific to HEA, that are set by the
HEA reverse proxy. The standard claim headers are prefixed by OIDC_CLAIM_.

Definitions of the standard claims may be found at
https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims. This document also specifies requirements
for using additional claims, which HEA follows.

The following constants contain the names of the claim headers:
SUB_HEADER: the sub claim.
CLAIM_HEADERS: a tuple containing all of the claim header names.
"""

SUB = 'OIDC_CLAIM_sub'

CLAIM_HEADERS = tuple(SUB, )
