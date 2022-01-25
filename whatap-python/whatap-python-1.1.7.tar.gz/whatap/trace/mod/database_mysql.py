from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_db_con, interceptor_db_execute, interceptor_db_close


def instrument_MySQLdb(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            db_type = 'mysql'
            callback = interceptor_db_con(fn, db_type, *args, **kwargs)
            return callback
        
        return trace
    if hasattr(module, "connect"):
        module.connect = wrapper(module.connect)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback
        
        return trace
    
    if hasattr(module, "connection") and hasattr(module.connection, "close"):
        get_dict(module.connection)['close'] = wrapper(
            module.connection.close)


def instrument_MySQLdb_cursors(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_execute(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.BaseCursor.execute = wrapper(module.BaseCursor.execute)
    if hasattr(module.BaseCursor,'callproc'):
        module.BaseCursor.callproc= wrapper(module.BaseCursor.callproc)

def instrument_pymysql(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            db_type = 'mysql'
            callback = interceptor_db_con(fn, db_type, *args, **kwargs)
            return callback
        
        return trace
    
    module.connect = wrapper(module.connect)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_close(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.connections.Connection.close = wrapper(
        module.connections.Connection.close)

def instrument_pymysql_cursors(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_db_execute(fn, *args, **kwargs)
            return callback

        return trace

    module.Cursor.execute = wrapper(module.Cursor.execute)