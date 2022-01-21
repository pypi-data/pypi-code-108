import pytest
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from taggit.models import Tag
from wagtail.core.models import Page, Site

from mycarehub.content.models import Author, ContentItem, ContentItemCategory, ContentItemIndexPage
from mycarehub.home.models import HomePage
from mycarehub.users.models import User
from mycarehub.users.tests.factories import UserFactory

fake = Faker()


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def test_email_backend(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def user_with_all_permissions(user) -> User:
    all_perms = Permission.objects.all()
    for perm in all_perms:
        user.user_permissions.add(perm)
    user.save()
    return user


@pytest.fixture
def group_with_all_permissions() -> Group:
    group = baker.make(Group)
    all_perms = Permission.objects.all()
    for perm in all_perms:
        group.permissions.add(perm)

    group.save()
    return group


@pytest.fixture
def user_with_group(user, group_with_all_permissions) -> User:
    user.groups.add(group_with_all_permissions)
    user.save()
    return user


@pytest.fixture
def request_with_user(rf, django_user_model, user_with_all_permissions):
    url = settings.ADMIN_URL + "/common/organisation/add/"
    request = rf.get(url)
    request.user = user_with_all_permissions
    return request


@pytest.fixture
def content_item_with_tag_and_category(request_with_user):
    # get the root page
    site = Site.find_for_request(request_with_user)
    assert site is not None
    root = site.root_page
    assert root is not None

    # set up a home page
    home = HomePage(
        title="Home",
        slug="index",
    )
    root.add_child(instance=home)
    root.save_revision().publish()

    # set up a content item index page
    content_item_index = ContentItemIndexPage(
        title="Content Item Index",
        slug="articles",
        intro="content",
    )
    home.add_child(instance=content_item_index)
    home.save_revision().publish()

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
    content_item_index.save_revision().publish()

    # add a category
    icon = baker.make("wagtailimages.Image", _create_files=True)
    cat = baker.make(ContentItemCategory, id=999_999, name="a valid category", icon=icon)
    content_item.categories.add(cat)
    content_item.save()
    assert ContentItem.objects.filter(categories__id=cat.pk).count() == 1

    # add a tag
    tag = baker.make(Tag, name="a-valid-tag")  # expect slug a-valid-tag
    content_item.tags.add(tag)
    content_item.save()
    assert ContentItem.objects.filter(tags__name="a-valid-tag").count() == 1

    # sanity checks
    assert (
        Page.objects.all().public().live().count() >= 4
    )  # root, home, content index, content item
    assert ContentItem.objects.all().public().live().count() == 1

    # return the initialized content item
    content_item.save_revision().publish()
    return content_item


def gen_rich_text_field():
    return fake.text()  # pragma: nocover


baker.generators.add("wagtail.core.fields.RichTextField", gen_rich_text_field)
