import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_tag_filter_found_tags(
    content_item_with_tag_and_category,
    request_with_user,
    client,
):
    assert content_item_with_tag_and_category is not None
    assert content_item_with_tag_and_category.tags.count() == 1
    assert content_item_with_tag_and_category.tags.filter(name="a-valid-tag").count() == 1

    client.force_login(request_with_user.user)
    url = (
        reverse("wagtailapi:pages:listing")
        + "?type=content.ContentItem&fields=*&order=-first_published_at&tag=a-valid-tag"
    )
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["meta"]["total_count"] == 1


def test_tag_filter_absent_tags(
    content_item_with_tag_and_category,
    request_with_user,
    client,
):
    assert content_item_with_tag_and_category is not None
    assert content_item_with_tag_and_category.tags.count() == 1
    assert content_item_with_tag_and_category.tags.filter(name="not-a-valid-tag").count() == 0

    client.force_login(request_with_user.user)
    url = (
        reverse("wagtailapi:pages:listing")
        + "?type=content.ContentItem&fields=*&order=-first_published_at&tag=not-a-valid-tag"
    )
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["meta"]["total_count"] == 0


def test_category_filter_found_categories(
    content_item_with_tag_and_category,
    request_with_user,
    client,
):
    assert content_item_with_tag_and_category is not None
    assert content_item_with_tag_and_category.categories.count() == 1
    assert content_item_with_tag_and_category.categories.filter(id=999_999).count() == 1

    client.force_login(request_with_user.user)
    url = (
        reverse("wagtailapi:pages:listing")
        + "?type=content.ContentItem&fields=*&order=-first_published_at&category=999999"
    )
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["meta"]["total_count"] == 1


def test_category_filter_absent_categories(
    content_item_with_tag_and_category,
    request_with_user,
    client,
):
    assert content_item_with_tag_and_category is not None
    assert content_item_with_tag_and_category.categories.count() == 1
    assert content_item_with_tag_and_category.categories.filter(id=999_999).count() == 1

    client.force_login(request_with_user.user)
    url = (
        reverse("wagtailapi:pages:listing")
        + "?type=content.ContentItem&fields=*&order=-first_published_at&category=87654321"
    )
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["meta"]["total_count"] == 0


def test_category_get_all_categories(
    content_item_with_tag_and_category,
    request_with_user,
    client,
):
    assert content_item_with_tag_and_category is not None
    assert content_item_with_tag_and_category.categories.count() == 1
    assert content_item_with_tag_and_category.categories.filter().count() == 1

    client.force_login(request_with_user.user)
    url = (
        reverse("wagtailapi:pages:listing")
        + "?type=content.ContentItem&fields=*&order=-first_published_at"
    )
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["meta"]["total_count"] == 1
