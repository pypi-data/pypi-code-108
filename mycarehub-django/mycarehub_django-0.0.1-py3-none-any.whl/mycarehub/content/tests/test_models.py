import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_bakery import baker
from wagtail.core.models import Page

from mycarehub.content.models import (
    Author,
    ContentItem,
    ContentItemCategory,
    ContentItemIndexPage,
    ContentItemTagIndexPage,
)
from mycarehub.home.models import HomePage

pytestmark = pytest.mark.django_db


def test_author_str():
    author = baker.make(Author, name="Mwandishi")
    assert str(author) == "Mwandishi"


def test_content_item_category_str():
    content_item_category = baker.make(ContentItemCategory, name="kategori")
    assert str(content_item_category) == "kategori"


def test_content_item_tag_index_page_get_context(request_with_user):
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

    # make a tag index page
    content_item_tag_index = ContentItemTagIndexPage(
        title="Tags",
        slug="tags",
    )
    root.add_child(instance=content_item_tag_index)
    context = content_item_tag_index.get_context(request_with_user)
    assert context is not None
    assert "tagged_items" in context
    assert context["tagged_items"].count() == 1

    content_item_index_context = content_item_index.get_context(request_with_user)
    assert content_item_index_context is not None
    assert "content_items" in content_item_index_context
    assert content_item_index_context["content_items"].count() >= 1


def test_content_item_properties(request_with_user):
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

    assert content_item.author_name == author.name
    assert content_item.author_avatar_url == ""
    assert content_item.category_details == []
    assert content_item.tag_names == []

    # add categories
    icon = baker.make("wagtailimages.Image", _create_files=True)
    cat = baker.make(ContentItemCategory, icon=icon)
    content_item.categories.add(cat)
    assert content_item.category_details == [
        {
            "category_id": cat.id,
            "category_name": cat.name,
            "category_icon": cat.icon.file.url,
        }
    ]


def test_content_item_validate_article_hero_image(request_with_user):
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
    )

    with pytest.raises(ValidationError) as c:
        content_item_index.add_child(instance=content_item)

    assert "an article must have a hero image" in str(c.value.messages)
