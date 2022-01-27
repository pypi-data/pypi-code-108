# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

try:
    from trytond.modules.carrier_api_ups.tests.test_carrier_api_ups import (
        suite)
except ImportError:
    from .test_carrier_api_ups import suite

__all__ = ['suite']
