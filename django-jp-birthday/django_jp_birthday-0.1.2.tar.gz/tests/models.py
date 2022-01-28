from jp_birthday.models import BirthdayModel


class ModelTest(BirthdayModel):
    class Meta:
        app_label = "jp_birthday"
        ordering = ("pk",)
