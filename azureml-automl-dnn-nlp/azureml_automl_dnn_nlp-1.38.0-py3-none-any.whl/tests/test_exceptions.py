import unittest
from azureml.automl.core.shared.exceptions import AutoMLException


class TestExceptions(unittest.TestCase):

    def test_with_create_without_pii(self):
        from azureml.automl.dnn.nlp.common import exceptions
        for i in dir(exceptions):
            if i.endswith('Exception'):
                cl = getattr(exceptions, i)
                if issubclass(cl, AutoMLException):
                    try:
                        raise cl.create_without_pii("blah")
                    except Exception as e:
                        assert e.__class__.__name__ == cl.__name__
                        # All the exceptions must have has_pii = False
                        assert not e.has_pii
                        assert 'blah' in e.pii_free_msg()


if __name__ == "__main__":
    unittest.main()
