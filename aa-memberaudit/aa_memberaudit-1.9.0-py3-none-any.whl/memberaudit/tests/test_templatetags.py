from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..templatetags.memberaudit import navactive_2


class TestNavactive2(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_simple_return_active_when_matches(self):
        request = self.factory.get(reverse("memberaudit:add_character"))
        result = navactive_2(request, "memberaudit:add_character")
        self.assertEqual(result, "active")

    def test_simple_return_empty_when_no_match(self):
        request = self.factory.get(reverse("memberaudit:add_character"))
        result = navactive_2(request, "memberaudit:reports")
        self.assertEqual(result, "")

    def test_complex_return_active_when_matches(self):
        request = self.factory.get(reverse("memberaudit:character_viewer", args=[2]))
        result = navactive_2(request, "memberaudit:character_viewer", 2)
        self.assertEqual(result, "active")
