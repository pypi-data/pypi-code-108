from django.utils.translation import gettext_lazy as _
from oscar.core.application import OscarConfig


class ProductTablesConfig(OscarConfig):

    name = 'oscar_product_tables'
    verbose_name = _('Product tables')
    namespace = 'oscar_product_tables'
