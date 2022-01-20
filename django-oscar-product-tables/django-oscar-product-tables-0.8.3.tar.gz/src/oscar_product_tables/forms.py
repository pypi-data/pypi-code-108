from django import forms
from oscar.core.loading import get_model

ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
AttributeOption = get_model('catalogue', 'AttributeOption')
Partner = get_model('partner','Partner')
StockRecord = get_model('partner','StockRecord')


class ProductFieldForm(forms.Form):
    def __init__(self, cell, request):
        self.url = request.path
        self.code = cell.code
        self.name = cell.name
        #pylint: disable=invalid-name
        auto_id = 'id_%s_' + str(cell.product.id)
        self.id = 'form_' + auto_id % (self.code,)
        if request.method == 'POST':
            super().__init__(request.POST, auto_id=auto_id)
        else:
            super().__init__(auto_id=auto_id)
        self.cell = cell

        self.field = self.get_field()
        self.initialize_fields()
        self.is_valid()

    def get_field(self):
        field = self.cell.field
        field.widget.attrs['class'] = 'form-control'
        return field

    def initialize_fields(self):
        self.fields['productid'] = forms.IntegerField(
            widget=forms.HiddenInput(),
            initial=self.cell.product.id,
        )
        self.fields['code'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=self.cell.code,
        )
        self.fields[self.code] = self.field

    def save(self):
        code = self.cleaned_data['code']
        value = self.cleaned_data[code]
        self.cell.save(code, value)
