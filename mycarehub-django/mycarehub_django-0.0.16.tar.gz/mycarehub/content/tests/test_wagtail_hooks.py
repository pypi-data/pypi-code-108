import pytest
from django.core.exceptions import ValidationError
from wagtail.core.models import Site

from mycarehub.content.wagtail_hooks import before_publish_page, get_global_admin_js

pytestmark = pytest.mark.django_db


def test_get_global_admin_js():
    admin_script = get_global_admin_js()
    assert "DOMContentLoaded" in admin_script


def test_before_publish_content_item_audio_video_no_media(
    request_with_user,
    content_item_with_tag_and_category,
):
    page = content_item_with_tag_and_category
    page.item_type = "AUDIO_VIDEO"
    page.save()
    page.refresh_from_db()
    assert page.featured_media.count() == 0
    assert page.item_type == "AUDIO_VIDEO"

    with pytest.raises(ValidationError) as c:
        before_publish_page(request_with_user, page)

    assert (
        "an AUDIO_VIDEO content item must have at least one video "
        "or audio file before publication"
    ) in str(c.value.messages)


def test_before_publish_content_item_pdf_document_no_document(
    request_with_user,
    content_item_with_tag_and_category,
):
    page = content_item_with_tag_and_category
    page.item_type = "PDF_DOCUMENT"
    page.save()
    page.refresh_from_db()
    assert page.documents.count() == 0
    assert page.item_type == "PDF_DOCUMENT"

    with pytest.raises(ValidationError) as c:
        before_publish_page(request_with_user, page)

    assert (
        "a PDF_DOCUMENT content item must have at least one document "
        "attached before publication"
    ) in str(c.value.messages)


def test_before_publish_non_content_item_page(request_with_user):
    site = Site.find_for_request(request_with_user)
    assert site is not None
    root = site.root_page

    # should not raise any exceptions
    before_publish_page(request_with_user, root)


def test_before_publish_content_item_article(
    request_with_user,
    content_item_with_tag_and_category,
):
    # there should be no exception
    before_publish_page(request=request_with_user, page=content_item_with_tag_and_category)
