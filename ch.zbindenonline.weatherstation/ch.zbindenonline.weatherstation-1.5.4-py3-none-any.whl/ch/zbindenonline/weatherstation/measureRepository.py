import datetime
import logging
import os
import sqlite3
from datetime import timedelta
from sqlite3.dbapi2 import Connection
from typing import List

from ch.zbindenonline.weatherstation.domain import Measure


class MeasureRepository:
    def __init__(self, database: str, config_sensors: dict = {}):
        self.database = database
        self.config_sensors = config_sensors

    def get_measures_after(self, sensor_name: str, last: str) -> List[Measure]:
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT m.created_at, m.temperature, m.humidity from measure m join sensor s on s.id=m.sensor "
                "where s.name=? and m.created_at >= datetime(?, '+1 second')",
                (sensor_name, last))
            records = cur.fetchall()
            measures_data = []
            for record in records:
                data = {'measured_at': record[0], 'temperature': str(record[1]),
                        'humidity': str(record[2])}
                measures_data.append(data)
            return measures_data

    def init(self) -> None:
        if os.path.isfile(self.database):
            logging.debug('Database ' + self.database + 'does exist already')
            return

        logging.debug('Initialize database ' + self.database)
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS sensor (
                    id INTEGER PRIMARY KEY,
                                       name TEXT NOT NULL
                    )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS measure (
                 id INTEGER PRIMARY KEY,
                 created_at TIMESTAMP NOT NULL,
                 temperature real NOT NULL,
                 humidity real NOT NULL,
                 sensor INTEGER NOT NULL REFERENCES sensor(id)
                )''')

    def save(self, measure: Measure) -> bool:
        logging.info('Save to database')
        conn = sqlite3.connect(self.database)
        with conn:
            sensors_map = dict(map(reversed, conn.execute('select id, name from sensor')))
            logging.info(sensors_map)
            conf_name = self.__get_conf_name(measure.sensor_id)
            sens = sensors_map.get(conf_name)
            if sens is None:
                logging.debug('insert sensor into database')
                cur = conn.cursor()
                cur.execute('INSERT OR IGNORE INTO sensor(name) values(?)', (conf_name,))
                sens = cur.lastrowid
                logging.debug('Inserted sensor %s with name %s', sens, conf_name)
            last_measure = self.__get_last_measure(conn, measure.sensor_id)
            if self.__need_to_persist(last_measure, measure):
                cur = conn.cursor()
                cur.execute('INSERT INTO measure(created_at, temperature, humidity, sensor) values(?, ?, ?, ?)',
                            (measure.measured_at, measure.temperature, measure.humidity, sens))
                return cur.rowcount > 0
            return False

    def __need_to_persist(self, last_measure: datetime, new_measure: Measure) -> bool:
        need_to_persist = new_measure.measured_at >= (last_measure + + timedelta(minutes=1))
        if not need_to_persist:
            logging.info('Measure ' + str(new_measure) + ' will not be persisted, las_measure was at ' + str(last_measure))
        return need_to_persist

    def __get_last_measure(self, conn: Connection, sensor_id: int) -> datetime:
        cur = conn.cursor()
        cur.execute(
            "SELECT MAX(m.created_at) from measure m where m.sensor=?", (str(sensor_id),)
        )
        result = cur.fetchone()
        if len(result) > 0 and result[0] is not None:
            return datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        return datetime.datetime(1970, 1, 1)

    def __get_conf_name(self, sensor_id: int) -> str | None:
        config = self.config_sensors.get(str(sensor_id))
        if config:
            return config['name']
        return None

    def add_sensor(self, name: str) -> None:
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT OR IGNORE INTO sensor(name) values(?)', (name,))
