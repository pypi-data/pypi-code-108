from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor, interceptor_error


def instrument(module):
    def wrapper(fn):
        @trace_handler(fn, True)
        def trace(*args, **kwargs):
            request = args[0].request
            
            environ = dict()
            environ['HTTP_HOST'] = request.host
            environ['PATH_INFO'] = request.path
            environ['QUERY_STRING'] = request.query_arguments
            environ['REMOTE_ADDR'] = request.remote_ip
            environ['HTTP_USER_AGENT'] = request.headers.get('User-Agent', '')
            environ['HTTP_REFERER'] = ''
            
            callback = interceptor((fn, environ), *args, **kwargs)
            
            return callback
        
        return trace
    
    module.RequestHandler._execute = wrapper(module.RequestHandler._execute)
    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            
            e = args[1]
            status_code = args[0]._status_code
            errors = [e.__class__.__name__, str(e)]
            interceptor_error(status_code, errors)
            return callback
        
        return trace
    
    module.RequestHandler._handle_request_exception = wrapper(
        module.RequestHandler._handle_request_exception)
