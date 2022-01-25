from whatap.trace.mod.application_wsgi import transfer, trace_handler, \
    interceptor_httpc_request, interceptor_sock_connect

request_injection_processed = False
def instrument_httplib(module):
    global request_injection_processed
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            # set mtid header
            kwargs['headers'] = transfer(kwargs.get('headers', {}))
            newargs = []
            for arg in args:
                if arg and isinstance(arg, dict) and 'host' in [x.lower() for x in arg.keys()]:
                    arg = transfer(arg)
                newargs.append(arg)
            # set httpc_url
            httpc_url = args[2]
            if hasattr(args[0], 'host'):
                httpc_url = getattr(args[0], 'host') + httpc_url
            callback = interceptor_httpc_request(fn, httpc_url, *newargs, **kwargs)
            return callback
        
        return trace
    if not request_injection_processed:
        module.HTTPConnection.request = wrapper(module.HTTPConnection.request)
        request_injection_processed = True

    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_sock_connect(fn, *args, **kwargs)
            return callback
        
        return trace
    module.HTTPConnection.connect = wrapper(module.HTTPConnection.connect)

def instrument_httplib2(module):
    global request_injection_processed
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            # set mtid header
            kwargs['headers'] = transfer(kwargs.get('headers', {}))
            newargs = []
            for arg in args:
                if arg and isinstance(arg, dict) and 'host' in [x.lower() for x in arg.keys()]:
                    arg = transfer(arg)
                newargs.append(arg)
            # set httpc_url
            httpc_url = args[2]
            if hasattr(args[0], 'host'):
                httpc_url = getattr(args[0], 'host') + httpc_url
            callback = interceptor_httpc_request(fn, httpc_url, *newargs, **kwargs)
        
        return trace
    if not request_injection_processed:
        module.Http.request = wrapper(module.Http.request)
        request_injection_processed = True
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = interceptor_sock_connect(fn, *args, **kwargs)
            return callback
        return trace

    module.HTTPConnectionWithTimeout.connect = wrapper(module.HTTPConnectionWithTimeout.connect)
    module.HTTPSConnectionWithTimeout.connect = wrapper(module.HTTPSConnectionWithTimeout.connect)