# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringScanner import StringScanner
from test.io.ScannerFixture import ScannerFixture


class TestStringScanner:
    content = None
    scanner: StringScanner
    fixture: ScannerFixture

    def setup_method(self):
        self.content = "Test String\nLine2\rLine3\r\n\r\nLine5"
        self.scanner = StringScanner(self.content)
        self.fixture = ScannerFixture(self.scanner, self.content)

    def test_read(self):
        self.fixture.test_read()

    def test_unread(self):
        self.fixture.test_unread()

    def test_line_column(self):
        self.fixture.test_line_column(3, ord('s'), 1, 3)
        self.fixture.test_line_column(12, ord('\n'), 2, 0)
        self.fixture.test_line_column(15, ord('n'), 2, 3)
        self.fixture.test_line_column(21, ord('n'), 3, 3)
        self.fixture.test_line_column(26, ord('\r'), 4, 0)
        self.fixture.test_line_column(30, ord('n'), 5, 3)
