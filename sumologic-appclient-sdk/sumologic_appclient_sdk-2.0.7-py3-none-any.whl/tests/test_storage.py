# -*- coding: future_fstrings -*-
import os
import sys
import unittest
import pdb
import functools
import traceback



if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from tests.base import ParametrizedTestCase, CustomTextTestRunner


def debug_on(*exceptions):
    if not exceptions:
        exceptions = (AssertionError, )
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions:
                info = sys.exc_info()
                traceback.print_exception(*info)
                pdb.post_mortem(info[2])
        return wrapper
    return decorator

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.common.logger import get_logger

logger = get_logger(__name__, force_create=True, ENABLE_LOGFILE=False)

class TestingStorage(ParametrizedTestCase):

    ENV_WITH_NO_LOCK_IMPLEMENTATION = ['azure', "gcp"]
    ENV_NOT_ACCEPTING_FLOAT_KEYS = ["aws", "gcp"]
    ENV_WITH_SAME_KEY_TYPES_CONSTRAINT = ["aws", "onprem"]
    ENV_WITH_NO_THREAD_LEVEL_LOCKING = ['onprem']

    @classmethod
    def get_store(cls, store_type, key_type):

        if store_type =="aws":
            aws_cli = ProviderFactory.get_provider("aws", region_name="us-east-1")
            store = aws_cli.get_storage("keyvalue", name='testdb', key_type=key_type, force_create=True, logger=logger)
        elif store_type == "gcp":
            gcp_cli = ProviderFactory.get_provider("gcp")
            store = gcp_cli.get_storage("keyvalue", name='testdb', force_create=True, logger=logger)
        elif store_type == "azure":
            azure_cli = ProviderFactory.get_provider("azure")
            store = azure_cli.get_storage("keyvalue", name='kvstore', force_create=True, logger=logger)
        else:
            op_cli = ProviderFactory.get_provider("onprem")
            store = op_cli.get_storage("keyvalue", name='testdb', force_create=True, db_dir="~/sumo", logger=logger)

        return store

    def setUp(self):
        super(ParametrizedTestCase, self).setUp()

        key_type = "S"
        if self._testMethodName.startswith("test_int_keys"):
            key_type = "N"
        self.store =  self.get_store(self.param, key_type)

    def tearDown(self):
        self.store.destroy()

    def test_string_values(self):
        key = "abckey"
        value = b"abvvalue" if sys.version_info > (3,0) else "abvvalue"
        self.run_crud_tests(key, value)
        self.run_lock_tests(key, value, exclude_env=self.ENV_WITH_NO_LOCK_IMPLEMENTATION)

    # @debug_on()
    def test_object_values(self):
        key = "abckey"
        value = {"name": "John", "age": 31, "city": ["New York", "Detroit", {"a": 40}], "hobbies": {"cricket": True, "football": False}}
        self.run_crud_tests(key, value)
        self.run_lock_tests(key, value, exclude_env=self.ENV_WITH_NO_LOCK_IMPLEMENTATION)

    def test_float_keys(self):
        # testing precision and floating values
        key = 1234567890123.12345
        value = {"value": 1234567890123.12345}
        self.run_crud_tests(key, value, exclude_env=self.ENV_NOT_ACCEPTING_FLOAT_KEYS)
        self.run_lock_tests(key, value, exclude_env=self.ENV_WITH_NO_LOCK_IMPLEMENTATION)

    # def test_decimal_keys(self):
    #     key = decimal.Decimal('1234567890123.12345678901234567890')
    #     value = {"value": decimal.Decimal('1234567890123.12345678901234567890')}
    #     self.run_crud_tests(key, value, exclude_env=["onprem", "azure"])

    # @debug_on()
    def test_int_keys(self):
        key = 1
        value = {"msg": {"value": [{"morning": "Good morning"}, {"night": "Good night"}]}}
        self.run_crud_tests(key, value)
        self.run_lock_tests(key, value, exclude_env=self.ENV_WITH_NO_LOCK_IMPLEMENTATION)

    def test_keys_with_different_types(self):
        key = "abckey"
        value = {"name": "John"}
        key2 = 1
        self.run_crud_tests(key, value)
        self.run_crud_tests(key2, value, exclude_env=self.ENV_WITH_SAME_KEY_TYPES_CONSTRAINT)
        self.run_lock_tests(key, value, exclude_env=self.ENV_WITH_NO_LOCK_IMPLEMENTATION)

    def run_crud_tests(self, key, value, exclude_env=None):
        exclude_env = exclude_env or []
        if self.param not in exclude_env:
            self.store.set(key, value)
            self.assertTrue(self.store.get(key) == value, f'''GetValue: {self.store.get(key)}  Value {value} not same''')
            self.assertTrue(self.store.has_key(key) == True, f'''{key} not Found''')
            self.store.delete(key)
            self.assertTrue(self.store.has_key(key) == False, f'''{key} not Deleted''')

    def run_lock_tests(self, key, value, exclude_env=None):
        exclude_env = exclude_env or []
        if self.param not in exclude_env:
            self.assertTrue(self.store.acquire_lock(key) == True, f'''{key} not Locked''')
            self.assertTrue(self.store.acquire_lock(key) == (True if self.store.env in self.ENV_WITH_NO_THREAD_LEVEL_LOCKING else False), f''' {key} Another thread or process should fail to acquire lock on same key ''')
            self.assertTrue(self.store.release_lock(key) == True, f'''{key} not Released''')
            self.assertTrue(self.store.release_lock(key) == False, f'''{key} must return false on re releasing key''')
            # lock_key = self.store._get_lock_key(key)
            # self.assertTrue(self.store.has_key(lock_key) == False, f'''{lock_key} Lock key not deleted''')
            self.assertTrue(self.store.release_lock("unknownkey2") == False, f''' Releasing lock on unknown key should not fail''')

def run_test():

    suite = unittest.TestSuite()
    result = None
    has_warnings = has_failures = False
    try:
        testloader = unittest.TestLoader()
        test_names = testloader.getTestCaseNames(TestingStorage)
        for deployment_name in ["aws", "gcp", "azure", "onprem"]:
            for test_name in test_names:
                suite.addTest(TestingStorage(deployment_name, test_name))

        result = CustomTextTestRunner().run(suite)
    except BaseException as e:
        logger.error("Error in run_test: %s\n%s" % (e, traceback.format_exc()))
    finally:
        if not result:
            has_failures = True  # must have failed on initialization
            logger.debug("Results - Failed to initialize")
        else:
            has_failures = not result.wasSuccessful()
            has_warnings = len(result.warnings) > 0

    logger.info("%s\n" % ("="*130))

    return has_failures, has_warnings



if __name__ == "__main__":
    run_test()