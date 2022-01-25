"""
Tests for the extra html.
"""
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from path import Path
from testfixtures import LogCapture

from ecommerce_extensions.tenant.extra_html import process_html
from ecommerce_extensions.tenant.extra_options import ERROR_MESSAGE, check_attributes_required


class TestsProcessExtraHtml(TestCase):
    """ Tests for extra html"""

    def test_returned_process_html(self):
        """
        Test process_html function returns a dictionary with all the valid html
        in the correct order.
        """
        path = Path("/test")
        tenantoptions = {
            "html": {
                ".*/test": [
                    {
                        "content": "<h1>Hola Mundo START!</h1>"
                    },
                    {
                        "location": "body_end",
                        "content": "<h1>Hola Mundo END!</h1>"
                    },
                ]
            }
        }
        test_html = {
            "body_start": "<h1>Hola Mundo START!</h1>",
            "body_end": "<h1>Hola Mundo END!</h1>"
        }

        html_returns = process_html(path, tenantoptions)

        self.assertEqual(test_html, html_returns)

    def test_returned_(self):
        """
        Test process_html function returns only the html that have a valid configuration.
        """
        path = Path("/test")
        tenantoptions = {
            "html": {
                ".*/test": [
                    {
                        "conten": "<h1>Hola Mundo END!</h1>"
                    },
                ]
            }
        }

        html_returns = process_html(path, tenantoptions)

        self.assertEqual({}, html_returns)

    def test_returned_path_html(self):
        """
        Test process_html function returns only the html that match the current request path.
        """
        path = Path("/test")
        tenantoptions = {
            "html": {
                ".*/dashboard": [
                    {
                        "location": "bodyend",
                        "content": "<h1>Hola Mundo END!</h1>"
                    },
                ]
            }
        }

        html_returns = process_html(path, tenantoptions)

        self.assertEqual({}, html_returns)

    def test_check_attributes_required_fails_silently(self):
        """
        Test check_attributes_required function logs error when a html has a missing/incorrect attribute.
        """
        values = {}
        attributes = ['content']
        log_message = "{prefix} {error_message}".format(prefix="HTML", error_message=ERROR_MESSAGE) % attributes

        with LogCapture() as log:
            check_attributes_required(
                values,
                attributes,
                "HTML"
            )
            log.check(("ecommerce_extensions.tenant.extra_options",
                       "ERROR",
                       log_message))
