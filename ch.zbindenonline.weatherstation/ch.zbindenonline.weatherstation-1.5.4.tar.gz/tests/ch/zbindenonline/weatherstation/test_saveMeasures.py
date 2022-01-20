
import os
import shutil
import tempfile
import unittest

from mockito import mock, unstub, when

from ch.zbindenonline.weatherstation.measureRepository import MeasureRepository
from ch.zbindenonline.weatherstation.saveMeasures import Main
from ch.zbindenonline.weatherstation.domain import Measure
from .util import date_time


class SaveMeasuresTest(unittest.TestCase):

    def setUp(self):
        config_sensors = {'87': {'name': 'aussen'}}
        self.test_dir = tempfile.mkdtemp()
        self.repo = MeasureRepository(os.path.join(self.test_dir, 'test.db'), config_sensors)
        self.repo.init()
        self.repo.add_sensor('aussen')

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        unstub()

    def test_saveMeasures(self):
        sensor_service = mock()
        measures = [
            Measure(87, date_time('2021-12-20 16:49:59'), 5.9, 62),
            Measure(87, date_time('2021-12-20 16:50:00'), 6.0, 63),
            Measure(87, date_time('2021-12-20 16:50:01'), 6.1, 64),
            Measure(56, date_time('2021-12-20 16:51:01'), 3.1, 62),
        ]
        when(sensor_service).get_measures().thenReturn(measures)
        main = Main(sensor_service, self.repo)

        main.run()

        persisted = self.repo.get_measures_after('aussen', '2021-12-20 16:50:00')
        self.assertEqual(1, len(persisted))
        self.assertEqual('2021-12-20 16:50:01', persisted[0]['measured_at'])
        self.assertEqual(str(6.1), persisted[0]['temperature'])
        self.assertEqual(str(64.0), persisted[0]['humidity'])


if __name__ == '__main__':
    unittest.main()
