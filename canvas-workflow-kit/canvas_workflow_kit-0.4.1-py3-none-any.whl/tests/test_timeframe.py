from .base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe
import arrow


class TimeFrameTest(SDKBaseTest):

    def setUp(self):
        super().setUp()

    def test___init__(self):
        # correct extremities
        start = arrow.get('1999-06-10', 'YYYY-MM-DD')
        end = arrow.get('2109-06-10', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)
        self.assertEqual(start, tested.start)
        self.assertEqual(end, tested.end)
        # incorrect extremities
        end = arrow.get('1999-06-10', 'YYYY-MM-DD')
        start = arrow.get('2109-06-10', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)
        self.assertEqual(start, tested.start)
        self.assertEqual(end, tested.end)

    def test___str__(self):
        # correct extremities
        start = arrow.get('1999-06-10', 'YYYY-MM-DD')
        end = arrow.get('2109-06-10', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)
        result = str(tested)
        self.assertEqual(
            '<Timeframe start=1999-06-10T00:00:00+00:00, end=2109-06-10T00:00:00+00:00>', result)
        # incorrect extremities
        end = arrow.get('1999-06-10', 'YYYY-MM-DD')
        start = arrow.get('2109-06-10', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)
        result = str(tested)
        self.assertEqual(
            '<Timeframe start=2109-06-10T00:00:00+00:00, end=1999-06-10T00:00:00+00:00>', result)

    def test_cycle(self):
        start = arrow.get('1999-06-10', 'YYYY-MM-DD')
        end = arrow.get('1999-06-20', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)
        self.assertEqual(10, tested.duration)

        start = arrow.get('1999-06-10', 'YYYY-MM-DD')
        end = arrow.get('2001-06-20', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)
        self.assertEqual(365 + 366 + 10, tested.duration)

    def test_increased_by(self):
        start = arrow.get('2018-10-31', 'YYYY-MM-DD')
        end = arrow.get('2018-11-01', 'YYYY-MM-DD')
        tested = Timeframe(start=start, end=end)

        result = tested.increased_by(years=-2)
        self.assertEqual('2016-10-31', result.start.format('YYYY-MM-DD'))
        self.assertEqual('2018-11-01', result.end.format('YYYY-MM-DD'))

        result = tested.increased_by(months=-2)
        self.assertEqual('2018-08-31', result.start.format('YYYY-MM-DD'))
        self.assertEqual('2018-11-01', result.end.format('YYYY-MM-DD'))

        result = tested.increased_by(days=-2)
        self.assertEqual('2018-10-29', result.start.format('YYYY-MM-DD'))
        self.assertEqual('2018-11-01', result.end.format('YYYY-MM-DD'))

        result = tested.increased_by(years=2)
        self.assertEqual('2018-10-31', result.start.format('YYYY-MM-DD'))
        self.assertEqual('2020-11-01', result.end.format('YYYY-MM-DD'))

        result = tested.increased_by(months=2)
        self.assertEqual('2018-10-31', result.start.format('YYYY-MM-DD'))
        self.assertEqual('2019-01-01', result.end.format('YYYY-MM-DD'))

        result = tested.increased_by(days=2)
        self.assertEqual('2018-10-31', result.start.format('YYYY-MM-DD'))
        self.assertEqual('2018-11-03', result.end.format('YYYY-MM-DD'))
