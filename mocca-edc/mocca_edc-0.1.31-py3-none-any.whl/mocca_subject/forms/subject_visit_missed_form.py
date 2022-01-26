from django.forms import ModelForm
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_visit_tracking.form_validators import VisitMissedFormValidator

from ..models import SubjectVisitMissed


class SubjectVisitMissedForm(CrfModelFormMixin, ModelForm):

    form_validator_cls = VisitMissedFormValidator

    class Meta:
        model = SubjectVisitMissed
        fields = "__all__"
