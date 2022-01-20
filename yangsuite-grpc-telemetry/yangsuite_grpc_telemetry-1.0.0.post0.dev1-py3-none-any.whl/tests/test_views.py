# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Testing of Django view functions for yangsuite-grpc-telemetry."""
from django_webtest import WebTest
from django.contrib.auth.models import User
try:
    # Django 2.x
    from django.urls import reverse
except ImportError:
    # Django 1.x
    from django.core.urlresolvers import reverse


class TestRenderMainPage(WebTest):
    """Tests for the render_main_page view function."""

    def setUp(self):
        """Function that will be automatically called before each test."""
        # Create a fake user account
        User.objects.create_user('user', 'user@localhost', 'ordinaryuser')
        # Get the URL this view is invoked from
        self.url = reverse('grpctelemetry:main')

    def test_login_required(self):
        """If not logged in, YANG Suite should redirect to login page."""
        # Send a GET request with no associated login
        response = self.app.get(self.url)
        # We should be redirected to the login page
        self.assertRedirects(response, "/accounts/login/?next=" + self.url)

    def test_success(self):
        """If logged in, the page should be rendered successfully."""
        # Send a GET request logged in as 'user'
        response = self.app.get(self.url, user='user')
        # Should get a success response rendering the main page template
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "ysgrpctelemetry/grpctelemetry.html")
