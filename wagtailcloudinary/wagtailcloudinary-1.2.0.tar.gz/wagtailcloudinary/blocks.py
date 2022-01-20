from django import forms
from django.forms.models import model_to_dict

from django.utils.functional import cached_property

from wagtail.core.blocks import FieldBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from .fields import str_to_cloudinary_resource, CloudinaryResource


class CloudinaryImageBlock(FieldBlock):
    class Meta:
        icon = "image"

    def __init__(self, required=True, help_text=None, **kwargs):
        self.field_options = {
            "required": required,
            "help_text": help_text,
        }
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        from .widgets import CloudinaryImageChooser

        field_kwargs = dict(
            widget=CloudinaryImageChooser(),
            **self.field_options,
        )
        return forms.CharField(**field_kwargs)

    def get_api_representation(self, value, context=None):
        # Treat "" as None
        if value == "":
            value = None
        if value is not None:
            value = str_to_cloudinary_resource(value).public_id
        return super().get_api_representation(value, context)


class CloudinarySnippetChooserBlock(SnippetChooserBlock):
    """
    Use this snippet chooser block when you have a snippet that contains a
    CloudinaryField AND you must display the details of the snippet in the
    Wagtail API (http://docs.wagtail.io/en/v2.4/advanced_topics/api/).
    """

    def get_api_representation(self, value, context=None):
        snippet_dict = model_to_dict(value)
        for key, value in snippet_dict.items():
            if type(value) is CloudinaryResource:
                snippet_dict[key] = value.public_id
        return snippet_dict
