from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import sys


class BasePreprocessor(object):
    def __init__(self, params, params_keys):
        if type(self) is BasePreprocessor:
            raise NotImplementedError

        actual_keys = set(params.keys())
        expected_keys = set(params_keys)
        if not actual_keys.issubset(expected_keys):
            raise ValueError('Unknown parameters {}.'.format(list(actual_keys - expected_keys)))

        self._is_fitted = False
        # self._internal_state_keys = ['_is_fitted'] + internal_state_keys

        # for n in self._internal_state_keys:
        #     value = None
        #     if internal_state is not None and n in internal_state:
        #         value = internal_state[n]
        #     setattr(self, n, value)

    def fit(self, df):
        self._is_fitted = True

    def transform(self, df):
        if not self._is_fitted:
            raise ValueError

    def fit_transform(self, df):
        self.fit(df)
        return self.transform(df)

    # def internal_state(self):
    #     return {n: getattr(self, n) for n in self._internal_state_keys}

    # def serialize(self):
    #     return self._dump(vars(self))

    # def deserialize(self, serialized_data):
    #     vars(self).update(self._load(serialized_data))

    # @staticmethod
    # def _dump(data):
    #     return json.dumps(data)

    # @staticmethod
    # def _load(serialized_data):
    #     return json.loads(serialized_data)
