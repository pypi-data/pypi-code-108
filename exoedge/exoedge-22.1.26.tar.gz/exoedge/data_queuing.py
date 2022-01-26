import json
import os
import re
import sqlite3
import threading
import time

import six.moves.urllib as urllib
from appdirs import user_data_dir

from exoedge import logger

LOG = logger.getLogger(__name__)

# Murano has payload limit to 64KB
PAYLOAD_MAX_SIZE = 64000

def murano_urlencode(data):
    return urllib.parse.quote_plus(data.encode('utf-8'))


class Queuing(object):
    def __init__(self, host, device_id, device,
                 batch_amount=0,
                 db_max_size=20000000,  # 20 MB
                 db_path=user_data_dir('exoedge', 'exosite'),
                 drop_strategy='oldest',
                 record_rate=1,
                 remove_unused_device=False
                 ):
        self.batch_amount = batch_amount
        self.record_rate = record_rate
        self.dequeue_enabled = False
        self.table_name = 'queue.' + self.product_id(host) + '.' + device_id
        self.db_path = os.path.normpath(db_path)
        self.device = device
        self.device.set_http_timeout(10)
        self.db = DB(self.db_path, self.table_name, db_max_size, drop_strategy)

        if not self.db.is_table_exist():
            self.db.create_table()

        self.is_table_empty = True if self.db.is_table_empty() else False
        if not self.is_table_empty:
            self.enable_dequeue()

        if remove_unused_device:
            self.db.delete_unused_table()

    def enable_dequeue(self):
        self.dequeue_enabled = True
        self.thread = threading.Thread(target=self.dequeue_table)
        self.thread.start()

    def disable_dequeue(self):
        LOG.info('Stoping data queuing...')
        self.dequeue_enabled = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def dequeue_table(self):
        while self.dequeue_enabled:
            records = self.db.read_table(
                auto=(self.batch_amount == 0), amount=self.batch_amount)

            if not len(records):
                self.is_table_empty = True
                self.dequeue_enabled = False
                continue

            try:
                if self.device.outbound_protocol == 'https':
                    self.https(records)
                else:
                    self.mqtt(records)

                self.db.table.delete(start=records[0][0], end=records[-1][0])
            except Exception as err:
                LOG.warn('Consume record failed')

            time.sleep(self.record_rate)

    def https(self, records):
        data = {}
        for row in records:
            data[row[1]] = row[2]
        payloads = {"data_in": data}

        status, result = self.device.tell(payloads=payloads)

        if not status:
            raise Exception('Https recored fail')

    def mqtt(self, records):
        payload = json.dumps(list(map(lambda row: {
            'timestamp': row[1],
            'values': {
                'data_in': row[2]
            }
        }, records)))
        status, result = self.device.tell(payloads=payloads)

        if not status:
            raise Exception('Mqtt not published')

    def product_id(self, host):
        """
            ex:
            host = "mqtt://z4fwqr3fmr0200000.m2.exosite.io/"
            return z4fwqr3fmr0200000
        """

        try:
            return re.search(r"(?<=//)\w+", host).group(0)
        except AttributeError as err:
            LOG.error('Invalid host fomat: {}'.format(err))
            raise

    def tell(self, resource=None, timestamp=None, payload=None):
        """
            resource: device's resource.
            timestamp: time.time()
            payload: json string
        """

        def payload_size_over_limit():
            payload_size = self.db.data_size(payload)
            if payload_size>=PAYLOAD_MAX_SIZE:
                LOG.warn('Tell failed, payload size {} byte and limist is {} byte'.format(payload_size, PAYLOAD_MAX_SIZE))
                return True
            else:
                return False

        if self.is_table_empty:
            status, result = self.device.tell(
                resource=resource,
                timestamp=timestamp,
                payload=payload
            )

            if not status:
                if payload_size_over_limit():
                    return False, 'payload size over limit {}'.format(PAYLOAD_MAX_SIZE)
                res = self.db.insert_record(timestamp, payload)
                if res is not None:
                    return False, 'Insert db fail: {}'.format(res)
                self.is_table_empty = False
                self.enable_dequeue()
                return True, 'Tell failed, putting payload into DB'
            return status, result
        else:
            if payload_size_over_limit():
                return False, 'payload size over limit {}'.format(PAYLOAD_MAX_SIZE)
            res = self.db.insert_record(timestamp, payload)
            if res is not None:
                return False, 'Insert db fail: {}'.format(res)
            return True, 'DB is not empty, putting payload into DB'


class Table(object):
    def __init__(self, query_db, name):
        self.name = name
        self.query_db = query_db

    def read(self, limit=1, startId=0):
        res = self.query_db(
            """
                SELECT * FROM '{}' WHERE id >= {} LIMIT {}
            """.format(self.name, startId, limit),
            one=False
        )
        return res

    def insert(self, time, value):
        res = self.query_db(
            """
                INSERT INTO '{}' VALUES (null, '{}', '{}')
            """.format(self.name, time, value)
        )
        return res

    def delete(self, start=0, end=99999999):
        res = self.query_db(
            """
               DELETE FROM '{}' WHERE id between {} and {}
            """.format(self.name, start, end)
        )
        return res

    def drop_oldest_records(self, drop_range_seconds=600):
        """
           Check all of table to delete the oldest 10 mins data, except the last 10 mins data.
        """
        table = self.the_oldest_record_table()
        if not table:
            return False

        oldest_time = table[1]

        if oldest_time + drop_range_seconds > time.time():
            return False

        res = self.query_db(
            """
                DELETE FROM '{}'
                WHERE timestamp <= '{}'
            """.format(table[0], oldest_time + drop_range_seconds)
        )
        return res

    def the_oldest_record_table(self):
        """
            return ex: ('queue.abcdcdkk2ls00000.device', 1.0)
        """
        oldest_table_time = 9999999999
        table = ()

        for table_name in self.all_table_name():
            timestamp = self.query_db(
                """
                    SELECT timestamp FROM '{}' ORDER BY timestamp ASC limit 1
                """.format(table_name)
            )
            if timestamp and timestamp < oldest_table_time:
                oldest_table_time = timestamp
                table = (table_name, oldest_table_time)

        return table

    def all_table_name(self):
        """
           return ex: ['queue.abcdcdkk2ls00000.device', 'queue.abcdcdkk2ls00000.device2']
        """
        res = self.query_db(
            """
                SELECT name FROM sqlite_master where name LIKE 'queue.%'
            """, one=False
        )
        return [i[0] for i in res]

    def delete_table(self, table_name):
        res = self.query_db(
            """
                DROP TABLE IF EXISTS '{}'
            """.format(table_name), one=False
        )

        return res


class DB(Table):
    def __init__(self, db_path, table_name, db_max_size, drop_strategy):
        self.table = Table(self.query_db, table_name)

        if not os.path.isdir(db_path):
            os.makedirs(db_path)
        self.path = os.path.join(db_path, 'exoedge.db')
        self.table_name = table_name
        self.db_max_size = db_max_size
        self.drop_strategy = drop_strategy
        self.is_vacuumed = True

    def insert_record(self, time, value):
        real_size = os.stat(self.path).st_size

        if real_size >= self.db_max_size:
            LOG.warn('DB current size is {} byte, max size is {} byte'.format(
                real_size, self.db_max_size))
            self.is_vacuumed = False

            if self.drop_strategy == 'oldest':
                # The drop size may small then insert size so may over size limitation little bit.
                self.drop_oldest_records()
                return None
            elif self.drop_strategy == 'latest':
                return None
            else:
                return 'Drop strategy not supported'

        return self.table.insert(time, value)

    def delete_unused_table(self):
        for table_name in self.table.all_table_name():
            if table_name != self.table_name:
                self.table.delete_table(table_name)

        return True

    def read_table(self, auto=True, amount=0):
        """
            vacuum DB when DB from full to empty.
        """
        res = self.limit_data_size(auto, amount)

        if not len(res) and not self.is_vacuumed:
            LOG.info('Doing DB vacuum')
            self.vacuum()
            self.is_vacuumed = True
        return res

    def query_db(self, query, values=None, one=True):
        """
            Method for all queries to the database.

            query: an SQL statement string
            values: a tuple of query values for
                    statements like SELECT, UPDATE, etc.
                    number of values in tuple should match
                    number of '?' in query
            one: default behavior for query return value
                 is to call and return query.fetchone().
                 if one=False, return query.fetchall().
        """

        LOG.debug("Executing query: {!r}, {}, one = {}"
                  .format(query, values, one))
        result = None

        with sqlite3.connect(self.path) as conn:
            # if db not exist, will auto created
            cursor = conn.cursor()
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            conn.commit()
            result = cursor.fetchone() if one else cursor.fetchall()
            if result and one:
                result = result[0]
        LOG.debug("db result = {0}".format(result))
        return result

    def create_table(self):
        self.query_db(
            """
                CREATE TABLE '{}' (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    data TEXT
                )
            """.format(self.table_name)
        )
        LOG.info('Table {} created'.format(self.table_name))

    def is_table_empty(self):
        res = self.query_db(
            """
                SELECT * FROM '{}'
            """.format(self.table_name)
        )
        return False if res else True

    def is_table_exist(self):
        """
         res example: u'z4fwqr3fmr0200000.j1939'
        """

        res = self.query_db(
            """
                SELECT name FROM sqlite_master WHERE type='table' AND name='{}';
            """.format(self.table_name)
        )
        return True if res else False

    def vacuum(self):
        res = self.query_db("VACUUM")
        return res

    def limit_data_size(self, auto=True, amount=0):
        """
            When send data Murano Resources, the maximum size is 64K
            auto: True - auto retrieve data which close to 64K, ignore amount parameter
                  False - retrieve data by given amount and deduct to 64K
        """
        # byte
        size_limit = PAYLOAD_MAX_SIZE
        size = 0

        if auto:
            records = []
            start_id = 0

            while True:
                data = self.table.read(startId=start_id, limit=1)
                if not data:
                    break
                size += self.data_size('{timestamp:.7f}={generateddata}&'.format(timestamp=data[0][1], generateddata=data[0][2]))
                if size > size_limit:
                    break
                records.append(data[0])
                start_id = data[0][0]+1
        else:
            records = self.table.read(amount)

            for index, record in enumerate(records):
                size += self.data_size('{timestamp:.7f}={generateddata}&'.format(timestamp=record[1], generateddata=record[2]))
                if size > size_limit:
                    return records[:index]

        return records

    def data_size(self, data):
        return len(murano_urlencode(data))
