from django.db import models

from jnt_django_toolbox.forms.fields import EnumChoiceField


class EnumField(models.TextField):
    """
    Wrapper around django choices.

    Allow better using of django 3 choices.
    """

    def __init__(self, enum, *args, **kwargs):
        """Initializer."""
        self.enum = enum
        kwargs["choices"] = enum.choices

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Deconstruct field for clone."""
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum"] = self.enum

        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """Build form field."""
        kwargs["choices_form_class"] = EnumChoiceField
        form_field = super().formfield(**kwargs)
        form_field.enum = self.enum

        return form_field
