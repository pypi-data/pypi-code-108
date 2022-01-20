from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.db.models import CharField
from .utils import str_to_cloudinary_resource, CloudinaryResource
from . import widgets


CloudinaryWidget = widgets.CloudinaryImageChooser  # For backwards compat


class CloudinaryField(CharField):
    description = "CloudinaryField"

    def __init__(self, *args, **kwargs):
        if "max_length" not in kwargs:
            kwargs["max_length"] = 255
        self.type = kwargs.pop("type", "upload")
        self.resource_type = kwargs.pop("resource_type", "image")
        return super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value or isinstance(value, CloudinaryResource):
            return value
        return str_to_cloudinary_resource(value, self.resource_type, self.type)

    def from_db_value(self, value, expression, connection, context):
        if value == "":
            return None
        return self.to_python(value)

    def get_prep_value(self, value):
        if isinstance(value, CloudinaryResource):
            return value.get_prep_value()
        else:
            return value


FORMFIELD_FOR_DBFIELD_DEFAULTS[CloudinaryField] = {
    "widget": CloudinaryWidget,
}
