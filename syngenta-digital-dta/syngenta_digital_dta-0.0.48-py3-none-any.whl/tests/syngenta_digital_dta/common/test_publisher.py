import unittest
import warnings

from syngenta_digital_dta.common import publisher


class PublisherTest(unittest.TestCase):

    def setUp(self, *args, **keywargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None
        self.mock_sns_arn = 'arn:aws:sns:us-east-2:111111111111:unittest-mock-sns-topic'

    def test_publish_basic(self):
        publisher.publish(
            arn=self.mock_sns_arn,
            data={'key': 'value'},
            model_schema='unit-test',
            model_identifier='unit_test_id',
            region='us-east-2',
            operation='create'
        )
