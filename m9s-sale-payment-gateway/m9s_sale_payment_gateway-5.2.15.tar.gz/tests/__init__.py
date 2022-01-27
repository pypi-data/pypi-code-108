# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

try:
    from trytond.modules.sale_payment_gateway.tests.test_sale_payment_gateway import (
        create_sale, suite)
except ImportError:
    from .test_sale_payment_gateway import create_sale, suite

__all__ = ['suite', 'create_sale']
