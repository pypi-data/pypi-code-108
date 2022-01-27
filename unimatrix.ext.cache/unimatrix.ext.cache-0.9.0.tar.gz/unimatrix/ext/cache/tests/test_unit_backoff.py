# pylint: skip-file
import unittest

from ..exceptions import Backoff


class BackoffTestCase(unittest.TestCase):

    def test_http_headers_contain_retry_after(self):
        exc = Backoff(60)
        self.assertIn('Retry-After', exc.http_headers)
        self.assertEqual(exc.http_headers['Retry-After'], '60')
        
