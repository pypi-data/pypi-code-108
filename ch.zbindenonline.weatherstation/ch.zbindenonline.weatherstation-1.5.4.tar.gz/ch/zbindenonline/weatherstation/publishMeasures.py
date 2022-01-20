import datetime
import logging

from ch.zbindenonline.weatherstation.logging import configure_logging
from ch.zbindenonline.weatherstation.measureRepository import MeasureRepository
from ch.zbindenonline.weatherstation.restServiceMeasures import RestServiceMeasures
from .config import *


class Main:
    def __init__(self, service: RestServiceMeasures, repo: MeasureRepository):
        self.service = service
        self.repo = repo

    def run(self) -> None:
        start = datetime.datetime.now()
        try:
            sensors = self.service.get_sensors()
            posted_measures = 0
            for sensor in sensors:
                sensor_id = sensor['id']
                sensor_name = sensor['name']
                last = self.service.get_last_timestamp(sensor_id)
                measures_to_post = self.repo.get_measures_after(sensor_name, last)
                measures_per_sensor = len(measures_to_post)
                if len(measures_to_post) > 0:
                    logging.info('Posting ' + str(measures_per_sensor) + " for sensor '" + sensor['name'] + "'")
                    self.service.post_measures(sensor_id, measures_to_post)
                    posted_measures += measures_per_sensor
            elapsed_time = datetime.datetime.now() - start
            logging.info('Posted ' + str(posted_measures) + ' in ' + str(elapsed_time))
        except Exception as e:
            logging.error("Error occurred: " + str(e))


def main():
    config = read_configuration()
    configure_logging(config.loglevel)
    service = RestServiceMeasures(config.rest.url, config.rest.username, config.rest.password)
    repo = MeasureRepository(config.database)
    Main(service, repo).run()


if __name__ == '__main__':
    main()
