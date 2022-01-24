from datetime import datetime
from contextlib import contextmanager
from extools.errors import ExToolsError
from extools.message import ExMessages

class ExTestError(ExToolsError):
    """Raised by failed test cases."""
    pass

def asserts(method):
    def wrapper(self, *args, **kw):
        self.results[self._current_test]['assertions'] += 1
        return method(self, *args, **kw)
    return wrapper

class ExTestCase():
    """A self running test case class for Extender scripts.

    ExTestCase can be used to test code in the Extender environment.
    Test cases will run with access to the current company.  Write your tests
    against the sample data in SAMINC, setup anything else you need on the fly,
    to make it easy to build a repeatable test environment.

    :param log_level: level of the built-in logger.
    :type log_level: int

    To create your own tests:

    1. subclass ExTestCase
    2. define the ``.setup()`` and ``.teardown`` methods
    3. create as many methods starting with ``test_`` as you'd like
    4. run your test suite by creating an instance and calling ``.run()``

    Run all the tests in a project using the included ExTestRunner module.

    Let's say you want to test your set order decription custom function,
    which sets the order decription to the customer number.

    .. code-block:: python

        from extools.view import exview

        def set_description_to_customer_number(ordnumber):
            '''Set the order description to the customer number.

            :param ordnumber: the order number to update.
            :type ordnumber: str
            :rtype: None
            :raises: ExViewError
            '''
            with exview("OE0500", seek_to={"ORDNUMBER": ordnumber}) as exv:
                exv.update(DESC=exv.get("CUSTOMER"))

    Using the :py:meth:`extools.view.exview` context manager makes opening,
    closing, and seeking the view easy.  To test it, we will need a record in
    the SAMINC database that we can change the Description on.  The first,
    ORD000000000001, seems to fit the bill.

    .. code-block:: python

        from extools.test import ExTestCase
        from mymodule import set_description_to_customer_number

        class MyTest(ExTestCase):

            # Make the order to work on a constant
            ORDER_NUMBER = "ORD000000000001"
            ORDER_VIEW = "OE0500"

            def setup(self):
                # Make sure the field isn't already set to the customer number
                with exview(ORDER_VIEW, seek_to={"ORDNUMBER": ORDER_NUMBER}) as exv:
                    if exv.get("DESC") == exv.get("CUSTOMER"):
                        exv.update(DESC="Description")

            # The test method must start with ``test_`` to be auto-detected.
            def test_set_description_to_customer_number(self):
                # Use the built-in assertions to check the pre-
                with exview(ORDER_VIEW, seek_to={"ORDNUMBER": ORDER_NUMBER}) as exv:
                    self.assertTrue(not exv.get("CUSTOMER") == exv.get("DESC"))

                set_description_to_customer_number(ORDER_NUMBER)

                #and post conditions
                with exview(ORDER_VIEW, seek_to={"ORDNUMBER": ORDER_NUMBER}) as exv:
                    self.assertTrue(exv.get("CUSTOMER") == exv.get("DESC"))

        def main():
            # To run your tests, instantiate the class and run it!
            mt = MyTest()
            mt.run()
        """

    # Try to set rotating indexes to avoid stepping on yourself.
    INDEX_MAX = 99
    _index = 9


    def __init__(self, log_level=ExMessages.INFO):
        self.name = self.__class__.__name__
        self.exm = ExMessages(self.name, log_level)
        self.index = self.generate_index()

        # { 'test_name': { 'result': True/False, 'assertions': 0 }, ... }
        self.results = {}
        self._current_test = None

    def generate_index(self):
        """Get the next available view index and increment the counter."""
        # Avoid the first 10.
        self._index = (self._index + 1) % self.INDEX_MAX
        if self._index < 10:
            self._index = 10
        return self._index

    @asserts
    def assert_true(self, obj):
        """Assert that something is truthy."""
        if not obj:
            raise ExTestError("{} is not true".format(obj))

    @asserts
    def assert_equal(self, obj1, obj2):
        """Assert that two things are equal."""
        if obj1 != obj2:
            raise ExTestError("'{}' ({}) is not equal to '{}' ({})".format(
                obj1, type(obj1), obj2, type(obj2)))

    @asserts
    @contextmanager
    def assert_raises(self, exception):
        """Assert that a particular block raises a specific exception.

        .. code-block:: python

            import mything
            from mything.errors import MyAwesomeError
            ...
            class MyThingTestCase(ExTestCase):
                ...
                def test_my_thing():
                    ...
                    with self.assertRaises(MyAwesomeError):
                        my_thing.do_the_awesome_stuff()
        """
        try:
            yield
        except exception:
            return True
        except Exception as e:
            raise ExTestError("{} not raised".format(exception), trigger_exc=e)
        else:
            raise ExTestError("{} not raised".format(exception))

    def run(self, with_transaction=True):
        """Run all the tests in the class and provide a report."""
        passed = []
        failed = []
        try:
            self.setup_class()
            for meth in dir(self):
                if meth.startswith('test_'):
                    self.exm.debug("Running {}".format(meth))
                    self._current_test = meth
                    self.results[meth] = { 'result': False, 'assertions': 0 }
                    try:
                        self.setup()
                        # with self._db_transaction():
                        r = getattr(self, meth)()
                        self.results[meth]['result'] = True
                        self.results[meth]['return'] = r
                        passed.append(meth)
                    except Exception as e:
                        failed.append(meth)
                        self.exm.error("{} failed: {}".format(meth, e),
                                        exc_info=True)
                    finally:
                        self.teardown()
        finally:
            self.teardown_class()
        self.exm.info("Failing tests ({}):\n{}\nPassing Tests({}):\n{}".format(
            len(failed), ", ".join(failed), len(passed), ", ".join(passed)))

        s = ""
        for (test, data) in self.results.items():
            s += "{} ({} assertions): {}\n".format(test,
                                                   data['assertions'],
                                                   data["result"], )
        self.exm.info(s)

    def _db_transaction(self, transaction_name=None):
        """This won't work because the transaction happens on a per-connection basis.

        And I can't get to the connection pool, deep in the bowels of sage."""
        if not transaction_name:
            transaction_name = datetime.now().strftime(
                    "%Y%m%d%H%M%S-{}".format(__name__))
        try:
            with exsql() as exs:
                exs.query("BEGIN TRANSACTION {}".format(transaction_name))
                yield exs
        finally:
            try:
                exs.query("ROLLBACK TRANSACTION {}".format(transaction_name))
            except:
                self.exm.error("Failed to rollback {}. Database state may "
                               "be inconsistent.".format(transaction_name))

            try:
                exs.close()
            except:
                pass # Do something useful

    def setup(self):
        """Steps that are run before every test."""
        pass

    def teardown(self):
        """Steps that are run after every test."""
        pass

    def setup_class(self):
        """Steps that are run once before the test suite starts."""
        pass

    def teardown_class(self):
        """Steps that are run once after the test suite ends."""
        pass
