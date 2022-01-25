from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil
import numbers

def intercept_send_command(fn, instance, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if ctx.db_opening :
        return fn(instance, *args, **kwargs)
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    port_or_path = getattr(instance, 'port', getattr(instance, 'path', None))
    text = 'redis://'
    text += getattr(instance, 'host','localhost')
    text += ':{}'.format(port_or_path)
    text += '/'
    text += str(getattr(instance, 'db', 0))
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text

    ctx.active_dbc = 0
    ctx.db_opening = True
    datas = [text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    UdpSession.send_packet(PacketTypeEnum.TX_DB_CONN, ctx, datas)
    query = " ".join([ str(arg)[:20] for arg in args])
    if ctx.active_sqlhash:
        return fn(*args, **kwargs)

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    ctx.active_sqlhash = query

    try:
        callback = fn(instance, *args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        ctx.db_opening = False
        datas = [ctx.lctx.get('dbc', ''), query]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        UdpSession.send_packet(PacketTypeEnum.TX_SQL, ctx,
                               datas)


def interceptor_read_response(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return fn(*args, **kwargs)
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    callback = None
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        if callback:
            count = -1
            if isinstance(callback, int):
                count = callback
            elif isinstance(callback, list):
                count = len(callback)

            if count > -1:
                msg = '{0}: {1}'.format('Fetch bytes', count)
                datas = [ msg,' ', ' ']
                ctx.elapsed = 0
                UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

        ctx.active_sqlhash = 0

def instrument_redis_connection(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = intercept_send_command(fn, args[0], *args[1:], **kwargs)
            return callback
        
        return trace

    if hasattr(module, 'Connection') and hasattr(module.Connection, 'send_command'):
        module.Connection.send_command = wrapper(module.Connection.send_command)

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_read_response(fn, *args, **kwargs)
            return callback

        return trace

    if hasattr(module, 'Connection') and hasattr(module.Connection, 'read_response'):
        module.Connection.read_response= wrapper(module.Connection.read_response)

