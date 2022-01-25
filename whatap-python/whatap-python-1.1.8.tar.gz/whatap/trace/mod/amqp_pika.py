from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error, start_interceptor, end_interceptor
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil

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
    text += parseConnection(args[0].connection.params)
    text += '?exchage='
    text += kwargs['exchange']
    text += '&routing='
    text += kwargs['routing_key']
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text

    ctx.active_dbc = 0
    ctx.db_opening = True
    ctx.elapsed = DateUtil.nowSystem() - start_time
    datas = [' ', ' ', 'MQ SESSION INFO: ' + text]
    UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

def instrument_pika(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = intercept_publish(fn, *args, **kwargs)
            return callback
        
        return trace

    if hasattr(module, 'Channel') and hasattr(module.Channel, 'basic_publish'):
        module.Channel.basic_publish = wrapper(module.Channel.basic_publish)


