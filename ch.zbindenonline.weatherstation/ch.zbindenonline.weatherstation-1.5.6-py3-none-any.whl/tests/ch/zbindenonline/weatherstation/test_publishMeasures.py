import shutil
import tempfile
import unittest

from mockito import when, mock, verify, verifyZeroInteractions, verifyNoUnwantedInteractions, unstub

from ch.zbindenonline.weatherstation.publishMeasures import Main


class PublishMeasuresTest(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        unstub()

    def test_main_with_no_sensors(self):
        service = mock()
        repo = mock()
        when(service).get_sensors().thenReturn([])
        main = Main(service, repo)

        main.run()

        verifyZeroInteractions(repo)

    def test_main_with_no_measures(self):
        service = mock()
        repo = mock()
        when(service).get_sensors().thenReturn([{"id": "1", "name": "aussen"}])
        when(service).get_last_timestamp('1').thenReturn('2021-12-20 11:43')
        when(repo).get_measures_after('aussen', '2021-12-20 11:43').thenReturn([])
        main = Main(service, repo)

        main.run()

        verifyNoUnwantedInteractions(repo)
        verifyNoUnwantedInteractions(service)

    def test_main_with_one_measure(self):
        service = mock()
        repo = mock()
        when(service).get_sensors().thenReturn([{"id": "2", "name": "innen"}])
        when(service).get_last_timestamp('2').thenReturn('2021-12-20 11:48')
        when(repo).get_measures_after('innen', '2021-12-20 11:48').thenReturn(
            [{"measured_at": "2021-12-20 11:49", "temperature": "23", "humidity": "62"}])
        main = Main(service, repo)

        main.run()

        verify(service).post_measures('2', [{"measured_at": "2021-12-20 11:49", "temperature": "23", "humidity": "62"}])
        verifyNoUnwantedInteractions(repo)
        verifyNoUnwantedInteractions(service)

    def test_main_with_sensors_and_measures(self):
        service = mock()
        repo = mock()
        when(service).get_sensors().thenReturn([{"id": "2", "name": "innen"}, {"id": "3", "name": "kueche"}])
        when(service).get_last_timestamp('2').thenReturn('2021-12-20 11:48')
        when(repo).get_measures_after('innen', '2021-12-20 11:48').thenReturn(
            [{"measured_at": "2021-12-20 11:49", "temperature": "23", "humidity": "62"}])
        when(service).get_last_timestamp('3').thenReturn('2021-12-20 12:00')
        when(repo).get_measures_after('kueche', '2021-12-20 12:00').thenReturn(
            [{"measured_at": "2021-12-20 12:05", "temperature": "21.4", "humidity": "57.3"},
             {"measured_at": "2021-12-20 12:10", "temperature": "21.6", "humidity": "55.2"}])
        main = Main(service, repo)

        main.run()

        verify(service).post_measures('2', [{"measured_at": "2021-12-20 11:49", "temperature": "23", "humidity": "62"}])
        verify(service).post_measures('3', [
            {"measured_at": "2021-12-20 12:05", "temperature": "21.4", "humidity": "57.3"},
            {"measured_at": "2021-12-20 12:10", "temperature": "21.6", "humidity": "55.2"}
        ])
        verifyNoUnwantedInteractions(repo)
        verifyNoUnwantedInteractions(service)


if __name__ == '__main__':
    unittest.main()
