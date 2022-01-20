from django.utils.http import urlquote


class LoginRequiredTest(object):
    """Mixin adding an authentication test step."""

    def test_login_required(self):
        """If not logged in, YANG Suite should redirect to login page."""
        # Send a GET request with no associated login
        response = self.app.get(self.url)
        # We should be redirected to the login page
        self.assertRedirects(response,
                             "/accounts/login/?next=" + urlquote(self.url))


class TargetRepoRequiredTest(object):
    """Mixin adding standard tests for views that require a target repo."""

    def test_negative_no_repository(self):
        """The repository parameter is mandatory."""
        response = self.app.post(self.url, user='test',
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 No repository specified", response.status)

    def test_negative_invalid_repository(self):
        """Error handling if the repository parameter is malformed."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'foo'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual("400 Invalid repository parameter", response.status)

    def test_negative_not_your_repository(self):
        """Non-superuser can't modify someone else's repository."""
        response = self.app.post(self.url, user='badfiles',
                                 params={'repository': 'test+testrepo'},
                                 expect_errors=True)
        self.assertEqual(403, response.status_code)
        self.assertEqual("403 Only superusers may modify the contents of "
                         "another user's repository", response.status)

    def test_negative_nonexistent_repository(self):
        """The repository must exist."""
        response = self.app.post(self.url, user='test',
                                 params={'repository': 'test+nosuchrepo'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual("404 No such repository", response.status)
