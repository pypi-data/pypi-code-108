import uuid
import datetime


def get_run_id():
    return str(uuid.uuid4()).upper()


class get_time(object):
    @staticmethod
    def now():
        return datetime.datetime.now()

    @staticmethod
    def logging_time():
        dt = datetime.datetime.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')
