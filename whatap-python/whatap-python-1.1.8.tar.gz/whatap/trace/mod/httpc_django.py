from whatap.trace.mod.application_wsgi import transfer, trace_handler, \
    interceptor_httpc_request


def instrument_revproxy_views(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            callback = fn(*args, **kwargs)
            
            # set mtid header
            callback = transfer(callback)
            return callback
        return trace
    
    module.ProxyView.get_proxy_request_headers = wrapper(module.ProxyView.get_proxy_request_headers)

    
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            # set httpc_url
            httpc_url = args[0].upstream
            callback = interceptor_httpc_request(fn, httpc_url, *args, **kwargs)
            return callback

        return trace
    
    module.ProxyView.dispatch = wrapper(module.ProxyView.dispatch)

