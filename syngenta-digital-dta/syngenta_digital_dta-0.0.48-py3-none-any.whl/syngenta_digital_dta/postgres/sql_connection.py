import typing

from syngenta_digital_dta.postgres.sql_connector import SQLConnector


def sql_connection(func: typing.Callable) -> typing.Callable:
    __connections = {}

    def decorator(obj: typing.Union["PostgresAdapter", "RedshiftAdapter"]):

        # reuse the existing connection if it isn't closed
        if __connections.get(obj.endpoint) and __connections[obj.endpoint].connection and not __connections[obj.endpoint].connection.closed:
            return func(obj, __connections[obj.endpoint])

        __connections[obj.endpoint] = SQLConnector(obj)
        return func(obj, __connections[obj.endpoint])

    return decorator
