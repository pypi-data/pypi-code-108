import argparse
import configparser
import json


class BrokerConfig:
    def __init__(self, outdoor_weather_uid: str, broker: str = 'localhost', qos: int = 1):
        self.broker = broker
        self.outdoor_weather_uid = outdoor_weather_uid
        self.qos = qos


class RestConfig:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password


class PicturesConfig:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, picture_dir: str,
                 picture_url: str, camera_id: str,
                 delete_after_publish: bool):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.picture_dir = picture_dir
        self.picture_url = picture_url
        self.camera_id = camera_id
        self.delete_after_publish = delete_after_publish


class Config:
    def __init__(self, broker: BrokerConfig, rest: RestConfig, pictures: PicturesConfig, loglevel: str = 'INFO',
                 sensors: dict = '{}',
                 database: str = 'dorben.db'):
        self.loglevel = loglevel
        self.sensors = sensors
        self.broker = broker
        self.database = database
        self.rest = rest
        self.pictures = pictures


def read_configuration() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config file", type=str, default='weatherstation.cfg')
    parser.add_argument("-l", "--log", help="level to log", type=str, default="INFO")
    args = parser.parse_args()
    return create_config(args)


def create_config(args) -> Config:
    config = configparser.ConfigParser()
    if len(config.read(args.config)) == 0:
        raise FileNotFoundError('ConfigFile not found', args.config)

    default = config['DEFAULT']
    sensors = json.loads(default.get('sensors'))
    broker_conf = BrokerConfig(default.get('outdoor_weather_uid'), default.get('broker'))
    rest = config['rest']
    rest_conf = RestConfig(rest.get('url'), rest.get('username'), rest.get('password'))
    picture = config['pictures']
    picture_conf = PicturesConfig(picture.get('client_id'), picture.get('client_secret'), picture.get('username'),
                                  picture.get('password'), picture.get('picture_dir'), picture.get('picture_url'),
                                  picture.get('camera_id'),
                                  picture.get('delete_after_publish').lower() == 'true')

    return Config(broker_conf, rest_conf, picture_conf, args.log.upper(), sensors, default.get('database'))
