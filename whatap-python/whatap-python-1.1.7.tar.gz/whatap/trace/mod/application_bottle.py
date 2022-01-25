from whatap.trace.mod.application_wsgi import interceptor, trace_handler, \
    interceptor_error


def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            callback = interceptor(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.Bottle.__call__ = wrapper(module.Bottle.__call__)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            if len(args) > 3:
                e = args[3]
                status_code = args[1]
            else:
                e = args[0]
                status_code = e._status_code
            
            errors = [e.__class__.__name__, str(e)]
            interceptor_error(status_code, errors)
            return callback
        
        return trace
    
    module.HTTPError.__init__ = wrapper(module.HTTPError.__init__)
