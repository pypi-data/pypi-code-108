from django import forms
from edc_appointment.constants import NEW_APPT
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import raise_if_clinical_review_does_not_exist
from edc_form_validators.form_validator import FormValidator

from mocca_consent.models import SubjectConsent

from ..models import NextAppointment, SubjectVisit


class NextAppointmentValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        self.date_not_before(
            "report_datetime",
            "appt_date",
            convert_to_date=True,
        )
        appointment = self.cleaned_data.get("subject_visit").appointment
        appt_date = self.cleaned_data.get("appt_date")
        # TODO: confirm next appointment date logic for routine appointment
        if appointment.next:
            msg = None
            if (
                appointment.next.appt_status != NEW_APPT
                and appt_date != appointment.next.appt_datetime.date()
            ):
                msg = f"Invalid. Expected {appointment.next.appt_datetime.date()}"
            elif appointment.next.next:
                if appt_date and appointment.next.next.appt_datetime.date():
                    if appt_date > appointment.next.next.appt_datetime.date():
                        msg = (
                            "Invalid. Cannot be after "
                            f"{appointment.next.next.appt_datetime.date()} "
                        )
            if msg:
                raise forms.ValidationError({"appt_date": f"{msg}"})

    @property
    def clinic_type(self):
        return SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier
        ).clinic_type


class NextAppointmentForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = NextAppointmentValidator

    def __init__(self, *args, **kwargs):
        try:
            appt_date = SubjectVisit.objects.get(
                id=kwargs.get("initial").get("subject_visit")
            ).appointment.next.appt_datetime
        except AttributeError:
            pass
        else:
            kwargs["initial"].update(appt_date=appt_date)
        super().__init__(*args, **kwargs)

    class Meta:
        model = NextAppointment
        fields = "__all__"
