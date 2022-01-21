import pytest
from wagtail.core.models import Page

from mycarehub.home.models import HomePage

pytestmark = pytest.mark.django_db


def test_home_page_context(request_with_user):
    root = Page.get_first_root_node().specific
    assert root is not None

    home = HomePage(
        title="Home",
        slug="index",
    )
    root.add_child(instance=home)

    context = home.get_context(request_with_user)
    assert context is not None
    assert "items" in context
    assert context["items"] is not None
