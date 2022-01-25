from whatap.trace.mod.application_wsgi import transfer, trace_handler, \
    interceptor_httpc_request


def instrument_requests(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            # set mtid header
            args[1].headers = transfer(args[1].headers)
            
            # set httpc_url
            httpc_url = args[1].url
            callback = interceptor_httpc_request(fn, httpc_url, *args, **kwargs)
            return callback
        
        return trace
    
    module.Session.send = wrapper(module.Session.send)
