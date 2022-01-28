from django import forms
from django.utils.translation import gettext_lazy as _

from .models import VimeoLink


class VimeoUrlForm(forms.Form):

    video_id = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop("submission")

        vimeo = getattr(self.submission, "vimeo_link", None)
        if vimeo:
            initial = kwargs.get("initial", dict())
            initial["video_id"] = f"https://vimeo.com/{vimeo.video_id}"
            kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        self.fields["video_id"].label = self.submission.title

    def clean_video_id(self):
        data = self.cleaned_data["video_id"]
        if "vimeo.com" not in data:
            raise forms.ValidationError(_("Please provide a Vimeo URL!"))
        parts = [v for v in data.split("/") if v]
        return parts[-1]

    def save(self):
        video_id = self.cleaned_data.get("video_id")
        if video_id:
            VimeoLink.objects.update_or_create(
                submission=self.submission, defaults={"video_id": video_id}
            )
        else:
            VimeoLink.objects.filter(submission=self.submission).delete()

    class Meta:
        model = VimeoLink
        fields = ("video_id",)
