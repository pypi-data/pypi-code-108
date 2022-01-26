from django import forms
from django.utils.translation import gettext_lazy as _
from apps.offer.models import ConditionalOffer
from ..models import Newsletter


class MessageGeneratorForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields['price'] = forms.BooleanField(
            label=_('Preis'),
            required=False,
            initial=True,
        )
        self.fields['newsletter'] = forms.ChoiceField(
            label=_('Newsletter'),
            choices = Newsletter.objects.values_list('id', 'title'),
            required=True,
        )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['newsletter'] = Newsletter.objects.get(
            pk=cleaned_data['newsletter']
        )
        cleaned_data['offer'] = ConditionalOffer.objects.get(
                pk=self.request.POST['offer_pk']
            )
        return cleaned_data
