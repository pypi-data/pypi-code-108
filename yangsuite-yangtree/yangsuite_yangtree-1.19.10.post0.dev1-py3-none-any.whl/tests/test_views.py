# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Testing of Django view functions for yangsuite-yangtree."""
import os

import unittest2 as unittest

from django_webtest import WebTest

try:
    # Django 2.x
    from django.urls import reverse
except ImportError:
    # Django 1.x
    from django.core.urlresolvers import reverse

from django.utils.http import urlquote

from yangsuite.paths import set_base_path
from ysyangtree import YSContext
from ysyangtree.views import rfc_section_text


class LoginRequiredTest(object):
    """Mixin adding an authentication test step."""

    def test_login_required(self):
        """If not logged in, YANG Suite should redirect to login page."""
        # Send a GET request with no associated login
        response = self.app.get(self.url)
        # We should be redirected to the login page
        self.assertRedirects(response,
                             "/accounts/login/?next=" + urlquote(self.url))


class TestExplorePage(WebTest, LoginRequiredTest):
    """Test the main 'explore' yangtree view page."""

    url = reverse('yangtree:explore')

    def setUp(self):
        """Per-test automatic setup."""
        set_base_path(base_dir)

    def test_success(self):
        """If logged in, the page should be rendered successfully."""
        response = self.app.get(self.url, user='test')
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'ysyangtree/yangtree.html')


class TestGetRFC(WebTest, LoginRequiredTest):
    """Test the get_rfc yangtree view."""
    csrf_checks = False

    url = reverse('yangtree:getrfc')

    def setUp(self):
        """Per-test automatic setup."""
        set_base_path(base_dir)

    def test_get_no_nodetype(self):
        """Request missing 'nodetype' parameter."""
        response = self.app.post(self.url, user='test')
        self.assertEqual(200, response.status_code)
        data = response.json
        self.assertEqual('module', data.get('content'))

    def test_get_unknown(self):
        """Request RFC section that doesn't exist."""
        response = self.app.post(self.url, user='test',
                                 params={'nodetype': 'unknown'})
        self.assertEqual(200, response.status_code)
        data = response.json
        self.assertEqual('No additional information known',
                         data.get('content'))
        self.assertEqual('', data.get('reference'))

    def test_success(self):
        """Basic success case."""
        response = self.app.post(self.url, user='test',
                                 params={'nodetype': 'output'})
        self.assertEqual(200, response.status_code)
        data = response.json
        self.assertIn('The output Statement', data.get('content'))
        self.assertEqual('https://tools.ietf.org/html/rfc6020#section-7.13.3',
                         data.get('reference'))

        # Requesting same content a second time will hit the cache
        # TODO verify that the cache isn't re-populated unnecessarily
        response = self.app.post(self.url, user='test',
                                 params={'nodetype': 'output'})
        self.assertEqual(200, response.status_code)
        data = response.json
        self.assertIn('The output Statement', data.get('content'))
        self.assertEqual('https://tools.ietf.org/html/rfc6020#section-7.13.3',
                         data.get('reference'))


class TestRFCSectionText(unittest.TestCase):
    """Exercise rfc_section_text() beyond what can be done through the view."""

    def test_invalid_start(self):
        """Test an invalid starting section."""
        self.assertEqual("", rfc_section_text("25.99.1"))

    def test_invalid_end(self):
        """Test a valid start with an invalid explicit end."""
        # Section 9.12.1 is only about four lines long, but since
        # we specified an end that is never found, the returned text
        # continues until the end of the document in this case
        self.assertGreater(len(rfc_section_text('9.12.1', '8.0').split("\n")),
                           200)


base_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestGetTree(WebTest, LoginRequiredTest):
    """Test the get_tree yangtree view."""
    csrf_checks = False

    url = reverse('yangtree:gettree')

    def setUp(self):
        """Per-test automatic setup."""
        set_base_path(base_dir)

    def test_negative_missing_names(self):
        """Negative test - omitted 'names' parameter."""
        response = self.app.post(self.url, user='test', expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('400 No model name(s) specified', response.status)

    def test_negative_malformed_yangset(self):
        """Negative test - invalid 'yangset' parameter."""
        response = self.app.post(self.url, user='test',
                                 params={'names[]': ['ietf-interfaces'],
                                         'yangset': 'foobar'},
                                 expect_errors=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual('400 Invalid yangset string', response.status)

    def test_negative_no_such_yangset(self):
        """Negative test - nonexistent yangset."""
        response = self.app.post(self.url, user='test',
                                 params={'names[]': ['ietf-interfaces'],
                                         'yangset': 'test+foobar'},
                                 expect_errors=True)
        self.assertEqual(404, response.status_code)
        self.assertEqual('404 No such yangset', response.status)

    def test_success(self):
        """Basic success test."""
        response = self.app.post(self.url, user='test',
                                 params={'names[]': ['ietf-interfaces'],
                                         'yangset': 'test+testyangset'})
        try:
            self.assertEqual(200, response.status_code)
            data = response.json
            self.assertEqual(['data', 'included_nodetypes'],
                             sorted(data.keys()))

            # Context is done loading at this point
            get_response = self.app.get(self.url, user='test',
                                        params={'yangset': 'test+testyangset'})
            self.assertEqual(200, get_response.status_code)
            data = get_response.json
            self.assertEqual(data['value'], data['max'])

            # Requesting same models again will use cached context/ParseYang
            response = self.app.post(self.url, user='test',
                                     params={'names[]': ['ietf-interfaces'],
                                             'yangset': 'test+testyangset'})
            self.assertEqual(200, response.status_code)
            data = response.json
            self.assertEqual(['data', 'included_nodetypes'],
                             sorted(data.keys()))
            self.assertEqual(1, len(YSContext._instances))
        finally:
            YSContext.discard_instance('test+testyangset')

    def test_success_name(self):
        """Success with legacy 'name' parameter."""
        response = self.app.post(self.url, user='test',
                                 params={'name': 'ietf-interfaces',
                                         'yangset': 'test+testyangset'})
        try:
            self.assertEqual(200, response.status_code)
            data = response.json
            self.assertEqual(['data', 'included_nodetypes'],
                             sorted(data.keys()))

        finally:
            YSContext.discard_instance('test+testyangset')

    def test_success_name_special(self):
        """Success with special yangset name parameter."""
        response = self.app.post(self.url, user='test',
                                 params={'name': 'ietf-interfaces',
                                         'yangset': 'test+Test.yangset'})
        try:
            self.assertEqual(200, response.status_code)
            data = response.json
            self.assertEqual(['data', 'included_nodetypes'],
                             sorted(data.keys()))

        finally:
            YSContext.discard_instance('test+test-yangset')

    def test_success_yangset_change(self):
        """Ensure cache is cleared when yangset is changed but module is not.

        See issue #110.
        """
        response = self.app.post(self.url, user='test',
                                 params={'names[]': ['ietf-inet-types'],
                                         'yangset': 'test+oldtypes'})
        try:
            self.assertEqual(200, response.status_code)
            data = response.json
            # We have loaded ietf-inet-types@2010-09-24
            self.assertEqual('2010-09-24', data['data'][0]['data']['revision'])
        finally:
            YSContext.discard_instance('test+oldtypes')

        # Now request the same module from a different yangset
        response = self.app.post(self.url, user='test',
                                 params={'names[]': ['ietf-inet-types'],
                                         'yangset': 'test+testyangset'})
        try:
            self.assertEqual(200, response.status_code)
            data = response.json
            # We have now loaded ietf-inet-types@2013-07-15
            self.assertEqual('2013-07-15', data['data'][0]['data']['revision'])
        finally:
            YSContext.discard_instance('test+testyangset')
