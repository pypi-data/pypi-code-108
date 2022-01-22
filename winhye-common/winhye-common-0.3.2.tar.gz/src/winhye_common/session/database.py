import threading
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from winhye_common.utils.exception_base import WinhyeException, ExceptionCode
from winhye_common.winhye_logger import logging as logging

__all__ = ['DatabaseClient', 'DBException']
_lock = threading.RLock()
logger = logging.getLogger()


def _acquire_lock():
    if _lock:
        _lock.acquire()


def _release_lock():
    if _lock:
        _lock.release()


class DBException(WinhyeException):
    """DB exception
    """

    def __init__(self, message: str):
        super(DBException, self).__init__(ExceptionCode.DB, message)


class DatabaseClient:
    engines = None
    pool_size = None

    @staticmethod
    def init(pool_size: int = 1):
        """
        Initialize database client

        :param pool_size: int, default value: 1
        """
        if DatabaseClient.engines is not None:
            return
        DatabaseClient.engines = {}
        DatabaseClient.pool_size = pool_size

    @staticmethod
    def get_session(url: str, timeout: int = 30, echo: bool = False, pool_recycle: int = -1, **configs):
        """
        Return database session

        :param pool_recycle:
        :param url: str, database url, format as "dialect+driver://username:password@host:port/database"
        :param timeout: int, default value: 30 seconds
        :param echo: bool, default value: False
        :param configs: other configurations
        :return: SQLAlchemy session
        """
        _acquire_lock()
        if url in DatabaseClient.engines:
            engine = DatabaseClient.engines[url]
        else:
            logger.debug("DatabaseSession create new engine, config: {config}".format(config=configs))
            engine = create_engine(url, pool_size=DatabaseClient.pool_size, echo=echo, pool_timeout=timeout,
                                   pool_recycle=pool_recycle, **configs)
            DatabaseClient.engines[url] = engine
        _release_lock()
        return sessionmaker(bind=engine)()

    def __init__(self, url: str, timeout: int = 30, echo: bool = False, pool_recycle: int = -1, **configs):
        """
        Create database session

        :param url: str, database url, format as "dialect+driver://username:password@host:port/database"
        :param timeout: int, default value: 30 seconds
        :param echo: bool, default value: False
        :param configs: other configurations
        """
        if DatabaseClient.engines is None:
            DatabaseClient.init()
        self.session = DatabaseClient.get_session(url=url, timeout=timeout, echo=echo, pool_recycle=pool_recycle,
                                                  **configs)

    def execute(self, sqls: list):
        """
        Execute several SQLs

        :param sqls: list, sqls to be executed
        """
        try:
            for sql, param_dict in sqls:
                logger.debug("executing param_dict: {param_dict}".format(param_dict=param_dict))
                logger.debug("executing sql: {sql}".format(sql=sql))
                self.session.execute(text(sql), param_dict)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(e)
            raise DBException("cannot update status: {exception}".format(exception=e))

    def get_values(self, sql: str, param_dict: dict) -> list:
        """
        Get values from database

        :param sql: str
        :param param_dict: dict
        :return: list, values
        """
        logger.debug("executing param_dict: {param_dict}".format(param_dict=param_dict))
        logger.debug("executing sql: {sql}".format(sql=sql))
        try:
            result = self.session.execute(text(sql), param_dict)
            rows = result.fetchall()
            return rows
        except Exception as e:
            logger.error(e)
            raise DBException("cannot get values: {exception}".format(exception=e))

    def get_value(self, sql: str, param_dict: dict) -> tuple:
        """
        Get value from database

        :param sql: str
        :param param_dict: dict
        :return: tuple, values
        """
        logger.debug("executing param_dict: {param_dict}".format(param_dict=param_dict))
        logger.debug("executing sql: {sql}".format(sql=sql))
        try:
            result = self.session.execute(text(sql), param_dict)
            row = result.fetchone()
            return row
        except Exception as e:
            logger.error(e)
            raise DBException("cannot get values: {exception}".format(exception=e))

    def close(self):
        """Close database session
        """
        try:
            self.session.close()
        except Exception as e:
            logger.error(e)
            raise DBException("cannot close: {exception}".format(exception=e))


if __name__ == '__main__':
    conn = DatabaseClient(
        "postgresql+psycopg2://xingqiao:Yhth111#@pgm-2zes4j7rsv2xbv789o.pg.rds.aliyuncs.com:1921/winhye_test"
    )
    conn.init(pool_size=1)
    sql = "select robot_id, video_stream from robot_info"
    res = conn.get_values(sql, {})
    logger.info(res)
    conn.close()
