from whatap.conf.configure import Configure as conf
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.net.udp_session import UdpSession
from whatap.trace.mod.application_wsgi import interceptor, trace_handler, \
    interceptor_error
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.trace.trace_context import TraceContext
from whatap.util.date_util import DateUtil
from whatap.util.userid_util import UseridUtil as userid_util
import whatap.util.throttle_util as throttle_util
import time

def blocking_handler():
    def handler(func):
        from django.http import HttpResponse
        def wrapper(*args, **kwargs):
            if conf.throttle_enabled and args and len(args) > 2:
                remote_ip = userid_util.getRemoteAddr(args)
                req = args[1]
                path = req['PATH_INFO']
                if throttle_util.isblocking(remote_ip, path):
                    if conf.reject_event_enabled:
                        ctx = TraceContextManager.getLocalContext()
                        if not ctx:
                            ctx = TraceContext()

                        throttle_util.sendrejectevent(ctx, path, remote_ip)
                    if conf.throttle_blocked_forward:
                        response = HttpResponse(status=302)
                        response['Location'] = throttle_blocked_forward
                        return response
                    status = '403 Forbidden'
                    start_response= args[2]
                    start_response(status, [])
                    response = HttpResponse(content=conf.throttle_blocked_message, status=403)
                    return response
            return func(*args, **kwargs)

        return wrapper

    return handler

def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        @blocking_handler()
        def trace(*args, **kwargs):

            callback = interceptor(fn, *args, **kwargs)

            return callback
        
        return trace
    
    module.WSGIHandler.__call__ = wrapper(module.WSGIHandler.__call__)



def instrument_handlers_base(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            request = args[1]
            ctx = TraceContextManager.getLocalContext()
            callback = fn(*args, **kwargs)
            
            if conf.trace_auto_normalize_enabled:
                resolver_match = request.resolver_match
                if resolver_match:
                    
                    path = request.path
                    for key, value in resolver_match.kwargs.items():
                        path = path.replace(resolver_match.kwargs[key],
                                            '{' + key + '}')
                    
                    start_time = DateUtil.nowSystem()
                    ctx.start_time = start_time
                    ctx.service_name = path
                    
                    if hasattr(resolver_match, 'view_name'):
                        type_name = 'View' \
                            if resolver_match._func_path != resolver_match.view_name \
                            else 'Function'
                        desc = '{0}: {1}'.format(type_name,
                                                 resolver_match._func_path)
                        datas = [' ', ' ', desc]
                        ctx.elapsed = DateUtil.nowSystem() - start_time
                        UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx,
                                               datas)

            return callback
        
        return trace

    if hasattr(module.BaseHandler, 'apply_response_fixes'):
        module.BaseHandler.apply_response_fixes = wrapper(
            module.BaseHandler.apply_response_fixes)

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            
            e = args[3]
            status_code = callback.status_code
            errors = [e[0].__name__,
                      e[1].args[1] if len(
                          e[1].args) > 1 \
                          else repr(e[1].args[0])]
            interceptor_error(status_code, errors)
            
            return callback
        
        return trace

    if hasattr(module.BaseHandler, 'handle_uncaught_exception'):
        module.BaseHandler.handle_uncaught_exception = wrapper(
            module.BaseHandler.handle_uncaught_exception)

    def get_response_wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            request = args[1]
            ctx = TraceContextManager.getLocalContext()
            if ctx and conf.trace_user_enabled:
                if not conf.trace_user_using_ip:
                    userid_util.setUserId(request, callback, ctx._rawuserid )

            return callback

        return trace
    module.BaseHandler.get_response = get_response_wrapper(
        module.BaseHandler.get_response)


def instrument_generic_base(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            self = args[0]
            ctx = TraceContextManager.getLocalContext()
            start_time = DateUtil.nowSystem()
            ctx.start_time = start_time
            desc = '{0}.{1}'.format(self.__module__, type(self).__name__)
            datas = [' ', ' ', desc]
            
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)
            
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.View.dispatch = wrapper(module.View.dispatch)




# Django==1.10

def instrument_urls_base(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.reverse = wrapper(module.reverse)


def instrument_handlers_exception(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.convert_exception_to_response.convert_exception_to_response = wrapper(
        module.convert_exception_to_response.convert_exception_to_response)

def instrument_handlers_static(module):
    def get_response_wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)

            ctx = TraceContextManager.getLocalContext()
            if ctx:
                ctx.userid = 0

            return callback

        return trace

    module.StaticFilesHandler.get_response = get_response_wrapper(
        module.StaticFilesHandler.get_response)

