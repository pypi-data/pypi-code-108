from django.utils.functional import cached_property
from oscar.core.loading import get_model
from oscar.apps.dashboard.catalogue.forms import ProductForm

Product = get_model('catalogue', 'Product')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
StockRecord = get_model('partner','StockRecord')
Partner = get_model('partner','Partner')

__all__ = ['AttachedCell', 'AttributeCell', 'PartnerCell']


class CellBase:
    type = None
    enabled = True

    def __init__(self, row, col, obj=None):  # @UnusedVariable
        self.row = row
        self.col = col
        self.name = col.name
        self.code = col.code
        self.product = row.product

    @property
    def data(self):
        raise NotImplementedError()

    @property
    def field(self):
        raise NotImplementedError()

    def save(self, code, value):
        raise NotImplementedError()

    def __repr__(self):
        return 'Cell:{}:{}'.format(self.product.upc, str(self))

    def __str__(self):
        return self.code


class AttachedCell(CellBase):
    type = 'attached'

    @property
    def data(self):
        return getattr(self.product, self.code)

    @property
    def field(self):
        field = Product._meta.get_field(self.code).formfield()
        field.initial = getattr(self.product, self.code)
        return field

    def save(self, code, value):
        if getattr(self.product, code) != value:
            setattr(self.product, code, value)
            self.product.save()


class AttributeCell(CellBase):
    type = 'attribute'

    def __init__(self, obj, *args, **kwargs):
        self.attribute = obj
        super().__init__(*args, **kwargs)

    @property
    def enabled(self):
        attribute_codes = [attribute.code for attribute in
                self.product.product_class.attributes.all()]
        return self.code in attribute_codes

    @property
    def data(self):
        value = self.attribute_values.get(self.code, None)
        if value:
            if self.attribute.type == 'option':
                value = value.option
            elif self.attribute.type == 'multi_option':
                value = ', '.join([x.option for x in value])
        return value

    @property
    def field(self):
        field = ProductForm.FIELD_FACTORIES[self.attribute.type](self.attribute)
        field.initial = self.attribute_values.get(self.code)
        return field

    @cached_property
    def attribute_values(self):
        product_attributes = {}
        for attribute_value in self.product.attribute_values.all():
            attribute_code = attribute_value.attribute.code
            value = attribute_value.value
            product_attributes[attribute_code] = value
        return product_attributes

    def save(self, code, value):
        attribute = self.product.product_class.attributes.get(code=self.code)
        if attribute.type == 'option':
            if value:
                ProductAttributeValue.objects.update_or_create(
                    attribute=attribute,
                    product=self.product,
                    defaults={
                        'value_option': value,
                    },
                )[0]
            else:
                ProductAttributeValue.objects.filter(
                    attribute=attribute,
                    product=self.product,
                ).delete()
        elif attribute.type == 'multi_option':
            if value:
                val = ProductAttributeValue.objects.get_or_create(
                    attribute=attribute,
                    product=self.product,
                )[0]
                val.value_multi_option.set(value)
            else:
                ProductAttributeValue.objects.filter(
                    attribute=attribute,
                    product=self.product,
                ).delete()
        else:
            ProductAttributeValue.objects.filter(
                attribute=attribute, product=self.product
            ).delete()


class PartnerCell(CellBase):
    type = 'partner'

    def __init__(self, obj, *args, **kwargs):
        self.partner = obj
        super().__init__(*args, **kwargs)

    @property
    def data(self):
        return self.stockrecords.get(self.code, None)

    @cached_property
    def stockrecords(self):
        return {stockrecord.partner.code: stockrecord.price
                for stockrecord in self.product.stockrecords.all()}

    @property
    def field(self):
        field = StockRecord._meta.get_field('price').formfield()
        stockrecord = self.stockrecords.get(self.code, None)
        if stockrecord is not None:
            field.initial = stockrecord
        return field

    def save(self, code, value):
        partner = Partner.objects.get(code=code)
        if value is None:
            StockRecord.objects.filter(partner=partner, product=self.product
                                       ).delete()
        StockRecord.objects.update_or_create(
            partner=partner,
            product=self.product,
            defaults={
                'price': value,
            }
        )
