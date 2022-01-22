import os
import json
import threading
import traceback
from functools import wraps
import flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from winhye_common.winhye_logger import logging as logging

logger = logging.getLogger()

__all__ = ["sess", "get_session", "db_session", "create_session"]

# dict for singleton, database URL as key, db engine as value
db_engines = {}
sess = threading.local()

_lock = threading.RLock()


def _acquire_lock():
    if _lock:
        _lock.acquire()


def _release_lock():
    if _lock:
        _lock.release()


def get_session(url: str, timeout: int = 30, **configs):
    """
    Return session based on database URL, maintain singleton for every URL using a dict.

    :param url: str, database URL, example: "dialect+driver://username:password@host:port/database"
    :param timeout: int, session timeout, default is 30(s)
    :param configs: other configs
    :return: sqlalchemy Session
    """
    _acquire_lock()
    if url in db_engines:
        engine = db_engines[url]
    else:
        logger.debug("DB_SESSION CONFIGS[{}]".format(configs))
        engine = create_engine(url, pool_size=10, max_overflow=10, echo=True, pool_timeout=timeout, **configs)
        db_engines[url] = engine
    _release_lock()
    session = sessionmaker(bind=engine)
    return session()


def create_session(url: str, timeout: int = 30):
    """
    Return session based on database URL in thread-local

    :param url: str, database URL, example: "dialect+driver://username:password@host:port/database"
    :param timeout: int, default is 30(s)
    :return: sqlalchemy Session
    """
    return get_session(url, timeout)


def db_session(pg_config: dict = None, mysql_config: dict = None, timeout: int = 30, auto_commit: bool = True):
    """
    Used as decorator, maintaining a sqlalchemy session during the scope. (reserved function root_path for Swagger)
    usage example: @db_session(pg_config=<postgresql config>, mysql_config=<mysql config>)
    P.S. only for Flask framework!

    :param pg_config: dict, postgresql config
    :param mysql_config: dict, mysql config
    :param timeout: int, default is 30(s)
    :param auto_commit: bool, default is True
    :return: decorated function
    """

    def decorator(func):
        func.root_path = os.path.dirname(os.path.abspath(func.__globals__["__file__"]))

        @wraps(func)
        def wrapper(*args, **kwargs):
            sess.pg_sess = None
            sess.mysql_sess = None
            if pg_config is not None:
                pg_url = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
                    pg_config["db_user"], pg_config["db_passwd"],
                    pg_config["db_host"], pg_config["db_port"],
                    pg_config["db_name"]
                )
                logger.debug(pg_url)
                sess.pg_sess = get_session(pg_url, timeout)
                logger.debug("DB_SESSION GET_PG_SESS[{}]".format(sess.pg_sess))
            if mysql_config is not None:
                mysql_url = "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}".format(
                    mysql_config["db_user"], mysql_config["db_passwd"],
                    mysql_config["db_host"], mysql_config["db_port"],
                    mysql_config["db_name"]
                )
                if "pool_recycle" in mysql_config:
                    sess.mysql_sess = get_session(mysql_url, timeout, pool_recycle=int(mysql_config["pool_recycle"]))
                else:
                    sess.mysql_sess = get_session(mysql_url, timeout)
                logger.debug("DB_SESSION GET_MYSQL_SESS[{}]".format(sess.mysql_sess))
            try:
                ret = func(*args, **kwargs)
                if auto_commit is False:
                    logger.debug("auto_commit is False, DB_SESSION directly close...")
                    if sess.pg_sess is not None:
                        logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                        sess.pg_sess.close()
                    if sess.mysql_sess is not None:
                        logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                        sess.mysql_sess.close()
                    return ret
                else:
                    # supported response type: int, dict, flask.Response, tuple[0] in (int, dict, flask.Response)
                    if type(ret) is int:
                        code = ret
                    elif type(ret) is dict:
                        code = ret.get("code")
                    elif type(ret) is flask.Response:
                        code = ret.json.get("code")
                    elif type(ret) is tuple and type(ret[0]) is int:
                        code = ret[0]
                    elif type(ret) is tuple and type(ret[0]) is dict:
                        code = ret[0].get("code")
                    elif type(ret) is tuple and type(ret[0]) is flask.Response:
                        code = ret[0].json.get("code")
                    else:
                        raise Exception("unsupported return type for @db_session: {0}".format(type(ret)))

                    try:
                        if code == 0 or code == 200:
                            logger.info("DB_SESSION commit due to zero code")
                            if sess.pg_sess is not None:
                                logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                                sess.pg_sess.commit()
                            if sess.mysql_sess is not None:
                                logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                                sess.mysql_sess.commit()
                        else:
                            logger.info("DB_SESSION rollback due to non-zero code...")
                            if sess.pg_sess is not None:
                                logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                                sess.pg_sess.rollback()
                            if sess.mysql_sess is not None:
                                logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                                sess.mysql_sess.rollback()
                    except Exception:
                        error_message = "error occurs when {operation} database".format(
                            operation="commit" if code == 0 else "rollback")
                        logger.error(error_message)
                        if sess.pg_sess is not None:
                            logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                            sess.pg_sess.close()
                        if sess.mysql_sess is not None:
                            logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                            sess.mysql_sess.close()
                        return flask.Response(status=500, response=json.dumps({"message": error_message}))

                    logger.debug("database operations finished, DB_SESSION close...")
                    if sess.pg_sess is not None:
                        logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                        sess.pg_sess.close()
                    if sess.mysql_sess is not None:
                        logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                        sess.mysql_sess.close()
                    return ret

            except Exception as e:
                logger.error(e)
                logger.debug(traceback.format_exc())

                if auto_commit is True:
                    logger.debug("session rollback due to exception")
                    try:
                        if sess.pg_sess is not None:
                            logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                            sess.pg_sess.rollback()
                        if sess.mysql_sess is not None:
                            logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                            sess.mysql_sess.rollback()
                    except:
                        error_message = "error occurs when rollback database"
                        logger.error(error_message)
                        if sess.pg_sess is not None:
                            logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                            sess.pg_sess.close()
                        if sess.mysql_sess is not None:
                            logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                            sess.mysql_sess.close()
                        return flask.Response(status=500, response=json.dumps({"message": error_message}))

                if sess.pg_sess is not None:
                    logger.debug("DB_SESSION PG_SESS[{}]".format(sess.pg_sess))
                    sess.pg_sess.close()
                if sess.mysql_sess is not None:
                    logger.debug("DB_SESSION MYSQL_SESS[{}]".format(sess.mysql_sess))
                    sess.mysql_sess.close()
                return flask.Response(status=500)

        return wrapper

    return decorator
