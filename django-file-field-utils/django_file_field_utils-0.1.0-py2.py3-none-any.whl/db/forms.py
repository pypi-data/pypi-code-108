from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django import forms

from file_field_utils.db.utils.backend import get_available_svg_image_extensions, validate_svg


validate_svg_image_file_extension = FileExtensionValidator(
    allowed_extensions=get_available_svg_image_extensions(),
)


class SVGAndImageFieldForm(forms.ImageField):
    default_validators = [validate_svg_image_file_extension]

    def to_python(self, data):
        try:
            f = super().to_python(data)
        except ValidationError:
            return validate_svg(data)

        return f
