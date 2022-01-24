import extools
from extools.test import ExTestCase

try:
    from accpac import *
except ImportError:
    pass

ORDER_HEADER_VIEWID = "OE0520"
ORDER_DETAIL_VIEWID = "OE0500"
DEFAULT_ORDNUMBER = "ORD000000000001"

AR_CUSTOMER_VIEWID = "AR0024"
AR_CUSTOMER_COUNT = 27
AR_CUSTOMER_FIRST = "1100"
AR_CUSTOMER_LAST = "WEBCUST"

class ExToolsTestCase(ExTestCase):
    """Test the functions in :py:mod:`extools` module."""

    def test_lines_in(self):
        """Verify that all_lines_in iterates in the right order and the correct
        number of times."""
        customers = []

        view = openView(AR_CUSTOMER_VIEWID)
        for line in extools.lines_in(view):
            customers.append(line.get("IDCUST"))

        self.assert_equal(len(customers), AR_CUSTOMER_COUNT)
        self.assert_equal(customers[0], AR_CUSTOMER_FIRST)
        self.assert_equal(customers[-1], AR_CUSTOMER_LAST)

    def test_lines_in_view(self):
        """Verify that all_lines_in_view iterates in the right order and the
        correct number of times."""
        customers = []

        for line in extools.lines_in_view(AR_CUSTOMER_VIEWID):
            customers.append(line.get("IDCUST"))

        self.assert_equal(len(customers), AR_CUSTOMER_COUNT)
        self.assert_equal(customers[0], AR_CUSTOMER_FIRST)
        self.assert_equal(customers[-1], AR_CUSTOMER_LAST)

    def test_open_and_fetch_row(self):
        """Verify that open_and_fetch_row opens and seeks correctly."""
        view = extools.open_and_fetch_row(ORDER_HEADER_VIEWID)
        self.assert_equal(view.get("ORDNUMBER"), DEFAULT_ORDNUMBER)

def main(*args, **kwargs):
    """This main hook is picked up by ExTestRunner for automatic execution."""
    ext = ExToolsTestCase()
    ext.run()
