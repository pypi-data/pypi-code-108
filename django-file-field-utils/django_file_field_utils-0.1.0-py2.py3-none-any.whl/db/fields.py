from django.db import models

from file_field_utils.db.forms import SVGAndImageFieldForm


class SVGAndImageField(models.ImageField):
    def formfield(self, **kwargs):
        defaults = {'form_class': SVGAndImageFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)
