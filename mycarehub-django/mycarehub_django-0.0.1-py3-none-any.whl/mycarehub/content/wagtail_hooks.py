from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from wagtail.core import hooks

from .models import ContentItem


@hooks.register("insert_global_admin_js")
def get_global_admin_js():
    return mark_safe(
        r"""
    <script>
    window.addEventListener('DOMContentLoaded', function () {
        document.addEventListener('wagtail:images-upload', function(event) {
            var newTitle = (event.detail.data.title || '').replace(/[^a-zA-Z0-9\s-]/g, "");
            event.detail.data.title = newTitle;
        });

        document.addEventListener('wagtail:documents-upload', function(event) {
            var extension = (event.detail.filename.match(/\.([^.]*?)(?=\?|#|$)/) || [''])[1];
            var newTitle = '(' + extension.toUpperCase() + ') ' + (event.detail.data.title || '');
            event.detail.data.title = newTitle;
        });
    });
    </script>
    """
    )


@hooks.register("before_publish_page")
def before_publish_page(request, page):
    """
    Audio_Video type pages must have media linked before publishing.

    Document type pages must have documents linked before publishing.
    """

    if page.specific_class == ContentItem:

        if page.item_type == "AUDIO_VIDEO" and page.featured_media.count() == 0:
            msg = (
                "an AUDIO_VIDEO content item must have at least one video "
                "or audio file before publication"
            )
            raise ValidationError(msg)

        if page.item_type == "PDF_DOCUMENT" and page.documents.count() == 0:
            msg = (
                "a PDF_DOCUMENT content item must have at least one document "
                "attached before publication"
            )
            raise ValidationError(msg)
