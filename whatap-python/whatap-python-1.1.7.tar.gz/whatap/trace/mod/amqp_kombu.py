from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error, start_interceptor, end_interceptor
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil

def parseCallbackName(args):
    if args:
        receiver = args[0]
        callbackspan = []

        if len(args) > 2:
            message = args[2]
            if hasattr(message, 'delivery_info'):
                if 'exchange' in message.delivery_info:
                    callbackspan.append(message.delivery_info['exchange'])
                if 'routing_key' in message.delivery_info:
                    callbackspan.append(message.delivery_info['routing_key'])

        if not callbackspan:
            callback = receiver.callbacks[0]
            if isinstance(callback, partial):
                callback = callback.func

            if hasattr(callback, '__qualname__'):
                callbackspan.append(callback.__qualname__)
            else:
                if hasattr(callback, '__module__'):
                    callbackspan.append(callback.__module__)
                if hasattr(callback, '__self__'):
                    callbackspan.append(callback.__self__.__class__.__name__)
                if hasattr(callback, '__name__'):
                    callbackspan.append(callback.__name__)

        return '.'.join(callbackspan)
    return ''

def intercept_receive(fn, *args, **kwargs):
    ctx = TraceContext()
    ctx.service_name = parseCallbackName(args)
    start_interceptor(ctx)

    try:
        callback = fn(*args, **kwargs)
        ctx = TraceContextManager.getLocalContext()
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        if ctx:
            end_interceptor(ctx=ctx)

def parseConnection(conn):
    connstr = ''
    if conn.host:
        connstr += conn.host
    if conn.virtual_host:
        connstr += "/" + conn.virtual_host
    return connstr

def intercept_publish(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    text = 'rabbitmq://'
    text += parseConnection(args[0].channel.connection)
    text += '?exchage='
    text += args[10]
    text += '&routing='
    text += args[7]
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text

    ctx.active_dbc = 0
    ctx.db_opening = True
    ctx.elapsed = DateUtil.nowSystem() - start_time

    datas = [' ', ' ', 'MQ SESSION INFO: ' + text]
    UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)


    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    try:
        callback = fn( *args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        ctx.db_opening = False

def instrument_kombu(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = intercept_publish(fn, *args, **kwargs)
            return callback
        
        return trace

    if hasattr(module, 'Producer') and hasattr(module.Producer, '_publish'):
        module.Producer._publish = wrapper(module.Producer._publish)

    def wrapper(fn):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            callback = intercept_receive(fn, *args, **kwargs)
            return callback

        return trace

    if hasattr(module, 'Consumer') and hasattr(module.Consumer, 'receive'):
        module.Consumer.receive = wrapper(module.Consumer.receive)

