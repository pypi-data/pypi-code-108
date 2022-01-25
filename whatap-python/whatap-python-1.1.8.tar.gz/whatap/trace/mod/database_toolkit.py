from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.net.udp_session import UdpSession
from whatap.trace.mod.application_wsgi import trace_handler, interceptor_db_execute, interceptor_step_error, sendDebugProfile
from whatap.util.date_util import DateUtil
from whatap.trace.trace_context_manager import TraceContextManager
from functools import wraps

def instrument_sqlalchemy(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            ctx = TraceContextManager.getLocalContext()
            
            start_time = DateUtil.nowSystem()
            ctx.start_time = start_time
            
            text = args[0].bind.url.__to_string__().replace('***', '')
            ctx.lctx['dbc'] = text
            
            datas = [' ', ' ', 'DB SESSION INFO: ' + text]
            ctx.elapsed = DateUtil.nowSystem() - start_time
            UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)
            
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    module.Session.get_bind = wrapper(module.Session.get_bind)

def addQuote(arg_dict):
    quoted_dict = dict()

    for k, v in arg_dict.items():
        if isinstance(v, str):
            quoted_dict[k] = "'" + v.replace("'", "\\'") + "'"
        else:
            quoted_dict[k] = v

    return quoted_dict

def instrument_sqlalchemy_engine(module):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            # print('instrument_sqlalchemy_engine step -1')
            ctx = TraceContextManager.getLocalContext()
            # print('instrument_sqlalchemy_engine CTX:', ctx)
            cursor = args[1]
            query = None
            if len(args) > 3 and type(args[3]) == dict and args[3]:
                try:
                    query = args[2] % addQuote(args[3])
                except Exception as e:
                    pass
            # print('instrument_sqlalchemy_engine 2:', query)
            try:
                if not query:
                    query = args[2].decode()
            except Exception as e:
                query = str(args[2])
            # print('instrument_sqlalchemy_engine 3:', query)
            if not query or ctx.active_sqlhash:
                return fn(*args, **kwargs)

            start_time = DateUtil.nowSystem()
            ctx.start_time = start_time
            ctx.active_sqlhash = query
            # print('instrument_sqlalchemy_engine 4')
            try:
                callback = fn(*args, **kwargs)
                # print('instrument_sqlalchemy_engine 5')
                return callback
            except Exception as e:
                interceptor_step_error(e)
            finally:
                # print('instrument_sqlalchemy_engine 6')
                ctx = TraceContextManager.getLocalContext()
                if ctx:
                    datas = [ctx.lctx.get('dbc', ''), query]
                    ctx.elapsed = DateUtil.nowSystem() - start_time
                    # print('instrument_sqlalchemy_engine 6.1', datas)
                    UdpSession.send_packet(PacketTypeEnum.TX_SQL, ctx,
                                           datas)
                    # print('instrument_sqlalchemy_engine 7')
                    if hasattr(cursor, 'rowcount'):
                        count = cursor.rowcount
                        # print('instrument_sqlalchemy_engine 8')
                        if count > -1:
                            desc = '{0}: {1}'.format('Fetch count', count)
                            datas = [' ', ' ', desc]
                            ctx.elapsed = 0
                            UdpSession.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)
                    ctx.active_sqlhash = 0

                # print('instrument_sqlalchemy_engine 9')

        return trace

    # print('database_toolkit.instrument_sqlalchemy_engine step -1')
    if hasattr(module, 'DefaultDialect') and hasattr(module.DefaultDialect, 'do_execute'):
        # print('database_toolkit.instrument_sqlalchemy_engine step -2')
        module.DefaultDialect.do_execute = wrapper(module.DefaultDialect.do_execute)
        module.DefaultDialect.do_executemany = wrapper(module.DefaultDialect.do_executemany)
        module.DefaultDialect.do_execute_no_params = wrapper(module.DefaultDialect.do_execute_no_params)
        # print('database_toolkit.instrument_sqlalchemy_engine step -3')

class _urlbase(object):
    def __init__(self, url):
        self.url = url

class connect(_urlbase):
    def __call__(self,*args, **kwargs):
        TraceContextManager.addDBPoolIdle(self.url)
        # import os
        # print("connect for ",self.url, os.getpid())
        
class checkin(_urlbase):
    def __call__(self,*args, **kwargs):
        TraceContextManager.addDBPoolIdle(self.url, isCheckIn=True)
        #print("checkin for ",self.url)
        
class checkout(_urlbase):
    def __call__(self,*args, **kwargs):
        TraceContextManager.addDBPoolActive(self.url)
        #print("checkout for ",self.url)

class reset(_urlbase):
    def __call__(self,*args, **kwargs):
        #print("reset for ",self.url)
        pass

class invalidate(_urlbase):
    def __call__(self,*args, **kwargs):
        #print("invalidate for ",self.url)
        TraceContextManager.removeDBPoolIdle(self.url)

class close(_urlbase):
    def __call__(self,*args, **kwargs):
        TraceContextManager.removeDBPoolIdle(self.url)
        
class detach(_urlbase):
    def __call__(self,*args, **kwargs):
        TraceContextManager.removeDBPoolIdle(self.url)

class close_detached(_urlbase):
    def __call__(self,*args, **kwargs):
        #print("close_detached for ",self.url)
        pass


def instrument_sqlalchemy_engine_basic(module):
    def wrapper(fn):
        @wraps(fn)
        def trace(*args, **kwargs):
            engine = fn(*args, **kwargs)
            if len(args) > 0:
                url = str(args[0])
                try:
                    import sqlalchemy.engine.event as event
                    
                    event.listen(engine, "connect", connect(url))
                    event.listen(engine, "checkin", checkin(url))
                    event.listen(engine, "checkout", checkout(url))
                    event.listen(engine, "close", close(url))
                except Exception as e:
                    pass
                try:
                    import sqlalchemy.event.api as event
                    
                    event.listen(engine, "connect", connect(url))
                    event.listen(engine, "checkin", checkin(url))
                    event.listen(engine, "checkout", checkout(url))
                    
                    #event.listen(engine, "reset", reset(url))
                    #event.listen(engine, "invalidate", invalidate(url))
                    event.listen(engine, "close", close(url))
                    #event.listen(engine, "detach", detach(url))
                    #event.listen(engine, "close_detached", close_detached(url))

                except Exception as e:
                    pass
            return engine
        
        return trace
    if hasattr(module, "create_engine"):
        module.create_engine = wrapper(module.create_engine)
