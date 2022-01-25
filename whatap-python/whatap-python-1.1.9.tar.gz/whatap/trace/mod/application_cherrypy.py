from whatap.trace.mod.application_wsgi import interceptor, trace_handler, \
    interceptor_error


def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            callback = interceptor(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.Application.__call__ = wrapper(module.Application.__call__)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            
            e = args[0]
            status_code = e.code
            errors = [e.reason, e._message]
            interceptor_error(status_code, errors)
            return callback
        
        return trace
    
    module.HTTPError.set_response = wrapper(module.HTTPError.set_response)
