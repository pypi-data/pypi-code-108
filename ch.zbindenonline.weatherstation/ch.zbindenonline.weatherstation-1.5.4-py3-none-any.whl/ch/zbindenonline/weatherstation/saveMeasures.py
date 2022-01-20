from ch.zbindenonline.weatherstation.logging import configure_logging
from ch.zbindenonline.weatherstation.measureRepository import MeasureRepository
from ch.zbindenonline.weatherstation.sensorService import SensorService
from .config import *


class Main:
    def __init__(self, sensor_service: SensorService, repo: MeasureRepository):
        self.sensor_service = sensor_service
        self.repo = repo

    def run(self) -> None:
        measures = self.sensor_service.get_measures()
        for measure in measures:
            self.repo.save(measure)


def main():
    config = read_configuration()
    configure_logging(config.loglevel)
    sensor_service = SensorService(config.broker.outdoor_weather_uid)
    repo = MeasureRepository(config.database, config.sensors)
    Main(sensor_service, repo).run()


if __name__ == '__main__':
    main()
