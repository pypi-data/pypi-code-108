import os
import shutil
import sqlite3
import unittest
import tempfile

from ch.zbindenonline.weatherstation.domain import Measure
from ch.zbindenonline.weatherstation.measureRepository import MeasureRepository
from .util import date_time


def insert_test_data(database):
    conn = sqlite3.connect(database)
    with conn:
        conn.execute("INSERT INTO sensor(id, name) values(1, 'sensor_1')")
        conn.execute(
            "INSERT INTO measure(id, created_at, temperature, humidity, sensor) values(1, '2021-12-20 12:55:00', '20.1', '65.1', 1)")
        conn.execute(
            "INSERT INTO measure(id, created_at, temperature, humidity, sensor) values(2, '2021-12-20 12:56:00', '20.2', '65.2', 1)")
        conn.execute(
            "INSERT INTO measure(id, created_at, temperature, humidity, sensor) values(3, '2021-12-20 12:57:00', '20.3', '65.3', 1)")
        conn.execute("INSERT INTO sensor(id, name) values(2, 'sensor_2')")
        conn.execute(
            "INSERT INTO measure(id, created_at, temperature, humidity, sensor) values(4, '2021-12-20 12:56:00', '21.1', '66.1', 2)")


class MeasureRepositoryShould(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save(self):
        database = os.path.join(self.test_dir, 'testSave.db')
        repo = MeasureRepository(database)
        repo.init()
        conn = sqlite3.connect(database)
        with conn:
            conn.execute("INSERT INTO sensor(id, name) values(1, 'sensor_1')")
            conn.execute(
                "INSERT INTO measure(id, created_at, temperature, humidity, sensor) values(1, '2022-01-18 12:00:00', '0', '0', 1)")

        result = repo.save(Measure(1, date_time('2022-01-18 11:59:59'), 0, 0))
        self.assertEqual(False, result, msg='Measure before last measurement')

        result = repo.save(Measure(1, date_time('2022-01-18 12:00:59'), 0, 0))
        self.assertEqual(False, result, msg='Measure too short after last measurement')

        result = repo.save(Measure(1, date_time('2022-01-18 12:01:00'), 0, 0))
        self.assertEqual(True, result)

    def test_get_measures_after(self):
        database = os.path.join(self.test_dir, 'test.db')
        repo = MeasureRepository(database)
        repo.init()
        insert_test_data(database)

        result = repo.get_measures_after('sensor_1', '2021-12-20 12:55:00')

        self.assertEqual(2, len(result))


if __name__ == '__main__':
    unittest.main()
