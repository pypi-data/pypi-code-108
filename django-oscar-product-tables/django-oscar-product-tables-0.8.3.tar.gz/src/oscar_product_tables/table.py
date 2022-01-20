from oscar_product_tables.plugins import *
from oscar.core.loading import get_model
from .row import Row

Product = get_model('catalogue', 'Product')


class Table:
    fixed_cell_count = 2
    all_plugin_classes = [
        AttachedFieldsPlugin,
        AttributeFieldsPlugin,
        PartnerFieldsPlugin,
    ]

    def __init__(self, plugin_classes=None, product=None):
        plugin_classes = plugin_classes or self.all_plugin_classes
        self.products = self.get_queryset(plugin_classes, product)
        self.rows = [Row(product) for product in self.products]
        self.plugins = [cls(self.rows) for cls in plugin_classes]
        self.cols = [*self.get_cols()]

    def get_cols(self):
        for plugin in self.plugins:
            for col in plugin.cols:
                yield col

    def get_queryset(self, plugin_classes, product=None):
        qs = Product.objects.browsable_dashboard()
        if product:
            qs = qs.filter(id=product.id)
        for cls in plugin_classes:
            qs = cls.product_queryset(qs)
        qs = qs.order_by('title')
        return qs

    def get_field(self, product, code):
        for row in self.rows:
            if row.product == product:
                break
        for cell in row.cells:
            if cell.code == code:
                return cell
