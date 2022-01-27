import logging

import elasticsearch

from .settings import ERROR_LOGGER
from texta_elastic.exceptions import NotFoundError, ElasticsearchError


def elastic_connection(func):
    """
    Decorator for wrapping Elasticsearch functions that are used in views,
    to return a properly formatted error message during connection issues
    instead of the typical HTTP 500 one.
    """


    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except elasticsearch.exceptions.NotFoundError as e:
            logging.getLogger(ERROR_LOGGER).error(e.info)
            raise NotFoundError(e.info)

        except elasticsearch.exceptions.AuthorizationException as e:
            logging.getLogger(ERROR_LOGGER).warning(e.info)
            error = [error["reason"] for error in e.info["error"]["root_cause"]]
            raise error

        except elasticsearch.exceptions.AuthenticationException as e:
            logging.getLogger(ERROR_LOGGER).warning(e.info)
            raise ElasticsearchError(e.info)

        except elasticsearch.exceptions.TransportError as e:
            logging.getLogger(ERROR_LOGGER).exception(e.info)
            raise ElasticsearchError(e.error)

        except elasticsearch.exceptions.ConnectionTimeout as e:
            logging.getLogger(ERROR_LOGGER).error(e.info)
            raise ElasticsearchError(e.info)


    return func_wrapper
