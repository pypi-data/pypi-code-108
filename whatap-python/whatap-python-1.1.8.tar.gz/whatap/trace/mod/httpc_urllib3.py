from whatap.trace.mod.application_wsgi import transfer, interceptor_httpc_request, \
    trace_handler, interceptor_sock_connect


def instrument_urllib3(module):
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
    if hasattr(module, 'RequestMethods'):
        module.RequestMethods.request = wrapper(module.RequestMethods.request)
    