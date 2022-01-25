from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil
import traceback

def intercept_connect(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        text = None

        if kwargs:
            text = 'smtp://'
            text += kwargs.get('host')
            text += ':'
            text += str(kwargs.get('port', 0))
        elif args and len(args) > 2:
            text = 'smtplilb.SMTP.connect('
            text += args[1]
            text += ','
            text += str(args[2])
            text += ')'
        if text:
            payloads = [text, '']
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.TX_METHOD, ctx, payloads)

def intercept_method(method, fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        payloads = [method, '']
        ctx.elapsed = DateUtil.nowSystem() - start_time
        UdpSession.send_packet(PacketTypeEnum.TX_METHOD, ctx, payloads)

def instrument_smtp(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = intercept_connect(fn, *args, **kwargs)
            return callback

        return trace

    if hasattr(module, 'SMTP') and hasattr(module.SMTP, 'connect'):
        module.SMTP.connect= wrapper(module.SMTP.connect)

    def wrapper(fn, method):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = intercept_method(method, fn, *args, **kwargs)
            return callback

        return trace

    for method in ['sendmail',]:
        if hasattr(module, 'SMTP') and hasattr(module.SMTP, method):
            setattr(module.SMTP, method, wrapper(getattr(module.SMTP, method), 'smtplib.SMTP.{}'.format(method)))
