""" test data

   isort:skip_file
"""

import unittest

class ImportsTest(unittest.TestCase):

    def test_import_uploader(self):
        from ciocore import uploader
        self.assertTrue(True)

    def test_import_downloader(self):
        from ciocore import downloader
        self.assertTrue(True)


    def test_import_worker(self):
        from ciocore import worker
        self.assertTrue(True)

    def test_client_db(self):
        from ciocore import client_db
        self.assertTrue(True)

