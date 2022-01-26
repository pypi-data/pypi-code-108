from django import forms

from ..models import DailyClosingLog


class DailyClosingLogForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        attended = cleaned_data.get("attended")
        approached = cleaned_data.get("approached")
        agreed_to_screen = cleaned_data.get("agreed_to_screen")
        if attended is not None and approached is not None:
            if approached > attended:
                raise forms.ValidationError(
                    {
                        "approached": (
                            "Invalid. Number approached cannot be greater "
                            "than number attended"
                        )
                    }
                )
        if approached is not None and agreed_to_screen is not None:
            if agreed_to_screen > approached:
                raise forms.ValidationError(
                    {
                        "agreed_to_screen": (
                            "Invalid. Number who agreed to be screened cannot "
                            "be greater than number approached"
                        )
                    }
                )
        return cleaned_data

    class Meta:
        model = DailyClosingLog
        fields = "__all__"
