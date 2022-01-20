from copy import deepcopy
from unittest import TestCase


class RQSDKBackTestTestCase(TestCase):
    base_config = {}

    def __init__(self, methodName='runTest'):
        super(RQSDKBackTestTestCase, self).__init__(methodName)

        test_method = getattr(self, methodName)
        setattr(self, methodName, self._make_test_method(*test_method()))

    @classmethod
    def _make_test_method(cls, config, *funcs):
        def run():
            from rqalpha_plus import run_func
            from rqalpha.utils.dict_func import deep_update
            base_config = deepcopy(cls.base_config)
            deep_update(config, base_config)
            return run_func(config=base_config, **{f.__name__: f for f in funcs})
        return run
