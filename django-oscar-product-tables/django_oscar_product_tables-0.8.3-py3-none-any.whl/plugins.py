from django.conf import settings
from oscar.core.loading import get_model
from .col import Col
from .cell import *

Product = get_model('catalogue', 'Product')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
Partner = get_model('partner','Partner')

__all__ = ['FieldsPluginBase', 'AttachedFieldsPlugin', 'AttributeFieldsPlugin',
           'PartnerFieldsPlugin']


class FieldsPluginBase:
    """
    Col need to be classmethods because they are needed before instantiating
    """
    cell_class = None

    def __init__(self, rows):
        self.code = self.cell_class.type
        self.objects = self.get_objects()
        self.cols = [*self.get_cols()]
        self.rows = self.add_cells_to_rows(rows)

    def get_objects(self):
        '''
        :returns: Dict of all objects with an identifier as key
        '''
        return {obj.code: obj for obj in self.get_queryset()}

    def add_cells_to_rows(self, rows):
        for row in rows:
            for col in self.cols:
                obj = self.get_obj(row, col)
                cell = self.cell_class(row=row, col=col, obj=obj)
                row.add_cell(cell)
        return rows

    def get_cols(self):
        raise NotImplementedError('Needs to be overwritten')

    def get_queryset(self):
        return []

    def get_obj(self, row, col):
        """ This fetches the relevant database object """
        return self.objects.get(col.code, None)

    @classmethod
    def product_queryset(cls, qs):
        return qs


class AttachedFieldsPlugin(FieldsPluginBase):
    cell_class = AttachedCell

    def get_cols(self):
        cols = []
        for code in self.get_fieldnames():
            field = Product._meta.get_field(code)
            cols.append(
                Col(field.name, Product._meta.get_field(code).verbose_name))
        return cols

    @classmethod
    def get_fieldnames(cls):
        fieldnames = getattr(settings, 'OSCAR_ATTACHED_PRODUCT_FIELDS', [])
        return ['upc', 'title', *fieldnames]

    @classmethod
    def product_queryset(cls, qs):
        for field in cls.get_fieldnames():
            if Product._meta.get_field(field).is_relation:
                qs = qs.select_related(field)
        return qs


class AttributeFieldsPlugin(FieldsPluginBase):
    cell_class = AttributeCell

    def get_cols(self):
        for obj in self.objects.values():
            yield Col(obj.code, obj.name)

    def get_queryset(self):
        qs = ProductAttribute.objects.distinct('code')
        qs = qs.select_related('option_group')
        qs = qs.prefetch_related('option_group__options')
        return qs

    @classmethod
    def product_queryset(cls, qs):
        qs = qs.select_related('product_class')
        qs = qs.prefetch_related(
            'product_class__attributes',
            'attribute_values',
            'attribute_values__attribute',
            'attribute_values__value_option',
            'stockrecords',
            'stockrecords__partner',
        )
        return qs


class PartnerFieldsPlugin(FieldsPluginBase):
    cell_class = PartnerCell

    def get_cols(self):
        for obj in self.objects.values():
            yield Col(obj.code, obj.name)

    def get_queryset(self):
        return Partner.objects.all()
