from whatap.trace.mod.application_wsgi import interceptor, trace_handler, \
    interceptor_error


def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            callback = interceptor(fn, *args, **kwargs)
            return callback
        
        return trace
    
    module.Flask.wsgi_app = wrapper(module.Flask.wsgi_app)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            if not callback:
                e = args[1]
                errors = [e.__class__.__name__]
                if hasattr(args[1], 'code'):
                    status_code = e.code
                    errors.append(e.description)
                else:
                    status_code = 500
                    errors.append(e.args[0])
                
                interceptor_error(status_code, errors)
            
            return callback
        
        return trace
    if hasattr(module.Flask, '_find_error_handler'):
        module.Flask._find_error_handler = wrapper(
            module.Flask._find_error_handler)
