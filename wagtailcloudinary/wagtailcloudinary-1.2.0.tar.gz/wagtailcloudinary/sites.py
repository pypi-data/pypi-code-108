import cloudinary
import cloudinary.api
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

try:
    # Django 2
    from django.contrib.staticfiles.templatetags.staticfiles import static
except ModuleNotFoundError:
    # Django 3
    from django.templatetags.static import static
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from wagtail.core import hooks
from wagtail.admin.modal_workflow import render_modal_workflow


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("wagtailcloudinary/css/main.css")
    )


@hooks.register("insert_global_admin_js")
def global_admin_js():
    html = []
    scripts = [
        static("wagtailcloudinary/js/csrf-token.js"),
        static("wagtailadmin/js/vendor/jquery.iframe-transport.js"),
        static("wagtailadmin/js/vendor/jquery.fileupload.js"),
    ]
    for item in scripts:
        html.append('<script src="{}"></script>'.format(item))
    return format_html("".join(html))


def staff_nocache(view):
    return staff_member_required(never_cache(view))


class CloudinarySite:
    def __init__(self, name="cloudinary"):
        self.name = name
        w, h = getattr(settings, "WAGTAILCLOUDINARY_ADMIN_IMAGE_SIZE", (165, 165))
        self.admin_image_version = "w_{},h_{},c_fill".format(w, h)
        config = cloudinary.config()
        self.base_url = "https://res.cloudinary.com/{name}/".format(
            name=config.cloud_name
        )

    def get_urls(self):
        from django.conf.urls import url

        urlpatterns = [
            url(r"^browse/$", staff_nocache(self.browse), name="browse"),
            url(r"^select/(.*)$", staff_nocache(self.select), name="select"),
            url(r"^update/(.*)$", staff_nocache(self.update), name="update"),
            url(r"^upload/$", staff_nocache(self.upload), name="upload"),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), "wagtailcloudinary"

    def browse(self, request):
        params = {"max_results": 40, "tags": True}
        if "next" in request.GET:
            params["next_cursor"] = request.GET["next"]
        tag = request.GET.get("tag", None)
        if tag:
            context = cloudinary.api.resources_by_tag(tag, **params)
        else:
            context = cloudinary.api.resources(**params)
        context["admin_image_version"] = self.admin_image_version
        if "next" in request.GET or "tag" in request.GET:
            template_name = "wagtailcloudinary/include/browse_ajax.html"
            html = render_to_string(template_name, context)
            return JsonResponse(
                {
                    "html": html,
                    "next": context.get("next_cursor", None),
                    "tag": tag,
                }
            )
        else:
            # We don't support load more on tags.
            tags = cloudinary.api.tags(max_results=60)
            context["tags"] = tags.get("tags", None)
            template_name = "wagtailcloudinary/browse.html"
            js_data = {
                "step": "chooser",
                "error_label": "Server Error",
                "error_message": "Error",
            }
            return render_modal_workflow(
                request, template_name, None, context, json_data=js_data
            )  # js_template='wagtailcloudinary/browse.js', json_data=context)

    def upload(self, request):
        response = {"images": []}
        for image in request.FILES.getlist("images[]"):
            options = {}
            data = {
                "image": cloudinary.uploader.upload(image, **options),
                "admin_image_version": self.admin_image_version,
            }
            data.update(
                {
                    "html": render_to_string(
                        "wagtailcloudinary/include/browse_item.html", data
                    )
                }
            )
            response["images"].append(data)
        return JsonResponse(response)

    def select(self, request, path):
        slugs = path.split("/")
        slugs.insert(2, self.admin_image_version)
        return render_modal_workflow(
            request,
            None,
            None,
            json_data={
                "step": "select",
                "image_json": path,
            },
        )

    def update(self, request, public_id):
        data = {"error": True}
        if request.method == "POST":
            tags = request.POST.get("tags", None)
            image = cloudinary.api.update(public_id, tags=tags)
            data["html"] = render_to_string(
                "wagtailcloudinary/include/browse_item.html",
                {
                    "image": image,
                    "admin_image_version": self.admin_image_version,
                },
            )
            data["error"] = False
        return JsonResponse(data)


site = CloudinarySite()
