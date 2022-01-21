import pytest
from django.utils import timezone
from model_bakery import baker
from wagtail.core.models import Page

from mycarehub.content.models import (
    Author,
    ContentItem,
    ContentItemIndexPage,
    ContentItemMediaLink,
)
from mycarehub.content.serializers import MediaSerializedField
from mycarehub.home.models import HomePage

pytestmark = pytest.mark.django_db


def test_media_serialized_field():
    # get the root page
    root = Page.get_first_root_node().specific

    # set up a home page
    home = HomePage(
        title="Home",
        slug="index",
    )
    root.add_child(instance=home)

    # set up a content item index page
    content_item_index = ContentItemIndexPage(
        title="Content Item Index",
        slug="articles",
        intro="content",
    )
    home.add_child(instance=content_item_index)

    # get a hero image
    hero = baker.make("wagtailimages.Image", _create_files=True)

    # set up a content item
    author = baker.make(Author)
    content_item = ContentItem(
        title="An article",
        slug="article-1",
        intro="intro",
        body="body",
        item_type="ARTICLE",
        date=timezone.now().date(),
        author=author,
        hero_image=hero,
    )
    content_item_index.add_child(instance=content_item)

    featured_media = baker.make("wagtailmedia.Media", _create_files=True)
    media = baker.make(
        ContentItemMediaLink,
        page=content_item,
        _create_files=True,
        featured_media=featured_media,
    )
    serializer_field = MediaSerializedField()
    representation = serializer_field.to_representation(content_item.featured_media)

    value = representation[0]
    assert value["url"] == media.featured_media.file.url
    assert value["title"] == media.featured_media.title
    assert value["type"] == media.featured_media.type
    assert value["duration"] == media.featured_media.duration
    assert value["width"] == media.featured_media.width
    assert value["height"] == media.featured_media.height
