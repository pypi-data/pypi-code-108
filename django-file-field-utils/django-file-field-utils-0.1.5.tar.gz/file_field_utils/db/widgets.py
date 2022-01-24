import logging
import re

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from os import path

from easy_thumbnails.exceptions import InvalidImageFormatError

from file_field_utils.utils import make_absolute_url

logger = logging.getLogger("django-file-field-utils")

from easy_thumbnails.files import get_thumbnailer


class ConfigurableImageWidget(AdminFileWidget):
    """
    use it whit this statement if your admin inherits from ConfigurableWidgetsMixinAdmin
        dbfield_overrides = {'img':{'widget':ConfigurableImageWidget({'width':80,'height':80})}}
    """
    default_width = 60
    default_height = 60
    default_crop = "smart"

    class Media:
        css = {
            'all': ('fhcore/admin/css/admin_form_overrides.css',)
        }

    def __init__(self, attrs=None):
        if attrs is not None:
            for k in ['width', 'height', 'crop']:
                try:
                    setattr(self, k, attrs.pop(k))
                except KeyError:
                    setattr(self, k, None)
        super(ConfigurableImageWidget, self).__init__
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

    def get_width(self):
        return getattr(self, 'width', self.default_width)

    def get_height(self):
        return getattr(self, 'height', self.default_height)

    def get_crop(self):
        return getattr(self, 'crop', self.default_crop)

    def get_image_opts(self):
        return {'size': (self.get_width(), self.get_height()),
                'crop': self.get_crop()}

    def get_image_html(self, value, thumbnail_url):
        help_text = "" if not hasattr(self, "help_text") else self.help_text
        output_html = f'<div class="box img-preview" style="float:left;margin-right:5px;">' \
                        f'<h4 style="text-align:center;color:#fff;background:#9AB8D6;">{_("Preview")}</h4>' \
                            f'<a target="_blank" href="{value.url}">' \
                                f'<img src="{thumbnail_url}" alt="{path.split(value.url)[-1]}" />' \
                            f'</a>' \
                      f'</div>' \
                      f'<div class="help">{help_text}</div>{_("Change:")} '
        return output_html

    def is_svg_image(self, file_path):
        import re
        from urllib.request import urlopen

        SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
        SVG_RE = re.compile(SVG_R, re.DOTALL)

        f = urlopen(f"{make_absolute_url(file_path)}")

        file_contents = f.read().decode('latin_1')  # avoid any conversion exception

        is_svg = SVG_RE.match(file_contents) is not None

        return is_svg

    def render(self, name, value, attrs=None, **kwargs):
        output = []
        if value and hasattr(value, "url"):
            try:
                if not self.is_svg_image(value.url):
                    if hasattr(self, 'thumbnail') and self.thumbnail:
                        thumbnail = self.thumbnail
                    else:
                        realname = re.sub(r'^(\w+)-(\d+)-', '', name)
                        image_preview = getattr(value.instance, realname)
                        opts = self.get_image_opts()
                        thumbnail = get_thumbnailer(image_preview).get_thumbnail(opts)
                    thumbnail_url = thumbnail.url
                else:
                    thumbnail_url = value.url
                output.append(self.get_image_html(value, thumbnail_url))

            except IOError:
                pass
            except InvalidImageFormatError:
                logger.info("File con formato non previsto")
            except Exception as ex:
                raise
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
