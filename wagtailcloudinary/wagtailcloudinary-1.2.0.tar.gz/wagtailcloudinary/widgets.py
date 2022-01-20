from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import AdminChooser
from wagtail.core.telepath import register
from wagtail.core.widget_adapters import WidgetAdapter
import json


class CloudinaryImageChooser(AdminChooser):
    choose_one_text = _("Choose an image")
    choose_another_text = _("Change image")
    link_to_chosen_text = _("Edit this image")
    show_edit_link = False

    def get_value_data(self, value):
        if value is None:
            return None
        w, h = getattr(settings, "WAGTAILCLOUDINARY_ADMIN_IMAGE_SIZE", (165, 165))
        data = {
            "id": value,
            "preview": {
                "url": value,
                "width": w,
                "height": h,
                "transforms": "w_{},h_{},c_fill".format(w, h),
            },
        }
        return data

    def render_html(self, name, value_data, attrs):
        value_data = value_data or {}
        original_field_html = super().render_html(name, value_data.get("id"), attrs)
        return render_to_string(
            "wagtailcloudinary/include/input.html",
            {
                "widget": self,
                "original_field_html": original_field_html,
                "attrs": attrs,
                "value": bool(
                    value_data
                ),  # only used by chooser.html to identify blank values
                "preview": value_data.get("preview", {}),
            },
        )

    def render_js_init(self, id_, name, value_data):
        return "createCloudinaryChooser({0});".format(json.dumps(id_))

    @property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailcloudinary/js/cloudinary-chooser.js"),
            ]
        )


class CloudinaryChooserAdapter(WidgetAdapter):
    js_constructor = "wagtailcloudinary.widgets.CloudinaryImageChooser"

    def js_args(self, widget):
        return [
            widget.render_html("__NAME__", None, attrs={"id": "__ID__"}),
            widget.id_for_label("__ID__"),
        ]

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailcloudinary/js/cloudinary-chooser-telepath.js"),
            ]
        )


register(CloudinaryChooserAdapter(), CloudinaryImageChooser)
