import os

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


def get_available_svg_image_extensions():
    try:
        from PIL import Image
    except ImportError:
        return []
    else:
        Image.init()
        list_exstentions = [ext.lower()[1:] for ext in Image.EXTENSION.keys()]
        list_exstentions.append("svg")
        return list_exstentions


def validate_svg(f):
    try:
        import xml.etree.cElementTree as et

        # Find "start" word in file and get "tag" from there
        f.seek(0)
        tag = None
        try:
            for event, el in et.iterparse(f, ("start",)):
                tag = el.tag
                break
        except et.ParseError:
            pass

        # Check that this "tag" is correct
        if tag != "{http://www.w3.org/2000/svg}svg":
            raise ValidationError("Uploaded file is not an image or SVG file.")

        # Do not forget to "reset" file
        f.seek(0)

        return f
    except ImportError:
        raise ValidationError(
            "validate_svg requires xml package to work, please install it"
        )


@deconstructible
class UploadPath(object):
    """
    big_snapshot = models.ImageField(_('Big Snapshot'), upload_to=UploadPath('big_snapshot'), blank=True)
    """

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __call__(self, instance, filename):
        return self.get_upload_path(instance, filename)

    def get_upload_path(self, instance, filename):
        return os.path.join(
            "uploads",
            instance._meta.app_label.lower(),
            instance.__class__.__name__.lower(),
            self.attr_name.lower(),
            os.path.basename(filename),
        )


@deconstructible
class UploadPathWithID(UploadPath):
    def get_upload_path(self, instance, filename):
        return os.path.join(
            "uploads",
            instance._meta.app_label.lower(),
            instance.__class__.__name__.lower(),
            self.attr_name.lower(),
            str(instance.id),
            os.path.basename(filename),
        )
