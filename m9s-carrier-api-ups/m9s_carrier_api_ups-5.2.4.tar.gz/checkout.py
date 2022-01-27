# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.modules.nereid_checkout.checkout import (
    not_empty_cart, sale_has_non_guest_party)
from trytond.pool import PoolMeta

from nereid import route
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('nereid_webshop')


class Checkout(metaclass=PoolMeta):
    __name__ = 'nereid.checkout'

    @classmethod
    @route('/checkout/delivery-method', methods=['GET', 'POST'],
        readonly=False)
    @not_empty_cart
    @sale_has_non_guest_party
    def delivery_method(cls):
        '''
        Get requests have to be read/write because the wizard writes on
        creation to the database.
        '''
        return super().delivery_method()
