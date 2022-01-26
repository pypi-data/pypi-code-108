from django import forms
from edc_form_validators import INVALID_ERROR, FormValidator, FormValidatorMixin
from edc_sites import get_current_country
from edc_utils import age

from mocca_screening.mocca_original_sites import get_mocca_sites_by_country

from ..models import MoccaRegister
from ..stubs import MoccaRegisterFormValidatorStub


class MoccaRegisterFormValidator(FormValidator):
    def clean(self):
        self.validate_mocca_site()
        self.validate_dob_and_age()
        self.validate_best_tel()

    def validate_mocca_site(self):
        mocca_country = get_current_country()
        if self.cleaned_data.get("mocca_site"):
            sites = get_mocca_sites_by_country(country=mocca_country)
            if self.cleaned_data.get("mocca_site").name not in [
                v.name for v in sites.values()
            ]:
                raise forms.ValidationError(
                    {"mocca_site": "Invalid site for selected country"}
                )

    def validate_dob_and_age(self):
        if (
            self.cleaned_data.get("dob")
            and self.instance.report_datetime
            and self.get_age() < 18
        ):
            raise forms.ValidationError({"dob": "Must 18 or older"})

        if self.cleaned_data.get("dob") and not self.cleaned_data.get("birth_year"):
            raise forms.ValidationError({"birth_year": "This field is required"})

        if self.cleaned_data.get("dob") and self.cleaned_data.get("birth_year"):
            if self.cleaned_data.get("dob").year != self.cleaned_data.get("birth_year"):
                raise forms.ValidationError(
                    {"birth_year": "Must match year in date of birth."}
                )
        if (
            self.cleaned_data.get("dob")
            and self.cleaned_data.get("age_in_years")
            and self.get_age() != self.cleaned_data.get("age_in_years")
        ):
            raise forms.ValidationError(
                {
                    "age_in_years": (
                        "Must match years from given date of birth "
                        f"until now (hint: got {self.get_age()})"
                    )
                }
            )

    def get_age(self: MoccaRegisterFormValidatorStub):
        return age(
            born=self.cleaned_data.get("dob"),
            reference_dt=self.instance.report_datetime,
        ).years

    def validate_best_tel(self):

        if self.cleaned_data.get("tel_two") and not self.cleaned_data.get("tel_one"):
            self.raise_validation_error(
                {"tel_one": "This field is required"}, error_code=INVALID_ERROR
            )
        if self.cleaned_data.get("tel_three") and not self.cleaned_data.get("tel_two"):
            self.raise_validation_error(
                {"tel_one": "This field is required"}, error_code=INVALID_ERROR
            )
        condition = (
            self.cleaned_data.get("tel_one")
            or self.cleaned_data.get("tel_two")
            or self.cleaned_data.get("tel_three")
        )
        self.required_if_true(condition, field_required="best_tel")
        if (
            not self.cleaned_data.get("tel_two")
            and self.cleaned_data.get("best_tel")
            and self.cleaned_data.get("best_tel") == "tel_2"
        ):
            self.raise_validation_error(
                {"best_tel": "Invalid selection"}, error_code=INVALID_ERROR
            )
        if (
            not self.cleaned_data.get("tel_three")
            and self.cleaned_data.get("best_tel")
            and self.cleaned_data.get("best_tel") == "tel_3"
        ):
            self.raise_validation_error(
                {"best_tel": "Invalid selection"}, error_code=INVALID_ERROR
            )


class MoccaRegisterForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = MoccaRegisterFormValidator

    screening_identifier = forms.CharField(
        label="Screening identifier",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = MoccaRegister
        fields = "__all__"
