from unittest import TestCase
import datetime

from wrgl.isoformat import fromisoformat

class FromISOFormatTestCase(TestCase):
    def test_parse(self):
        self.assertEqual(
            fromisoformat('2021-11-17T01:22:53Z'),
            datetime.datetime(2021, 11, 17, 1, 22, 53, tzinfo=datetime.timezone.utc)
        )
        self.assertEqual(
            fromisoformat('2021-11-17T01:22:53+07:00'),
            datetime.datetime(2021, 11, 17, 1, 22, 53, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
        )