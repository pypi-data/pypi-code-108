from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error, start_interceptor, end_interceptor
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil

def intercept_worker(fn, *args, **kwargs):
    ctx = TraceContext()
    worker_ctx = args[1]
    ctx.service_name = worker_ctx.call_id_stack
    start_interceptor(ctx)

    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        end_interceptor()

def instrument_nameko_spawn_worker(module):
    def wrapper(fn):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            callback = intercept_worker(fn, *args, **kwargs)
            return callback

        return trace

    if hasattr(module, 'ServiceContainer') and hasattr(module.ServiceContainer, '_run_worker'):
        from eventlet.corolocal import local
        TraceContextManager.local = local()
        module.ServiceContainer._run_worker = wrapper(module.ServiceContainer._run_worker)

