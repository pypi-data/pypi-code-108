import pymongo.monitoring
from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler, \
    interceptor_step_error
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.net.udp_session import UdpSession
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil
import sys, logging

from pprint import pprint, pformat

class WhatapMongoCmdEventListener(pymongo.monitoring.CommandListener):
    def __init__(self):
        pass

    def started(self, event):
        try:
            self.__started(event)
        except Exception as e:
            ctx = TraceContextManager.getLocalContext()
            if ctx:
                logging.debug(e, extra={'id': 'MON22', 'ctx.id':ctx.id}, exc_info=True)
            else:
                logging.debug(e, extra={'id': 'MON22'}, exc_info=True)

    def __started(self, event):
        ctx = TraceContextManager.getLocalContext()
        if not ctx or ctx.db_opening :
            return
        start_time = DateUtil.nowSystem()
        ctx.start_time = start_time
        
        port_or_path = event.database_name
        text = 'mongodb://'
        if hasattr(event, 'connection_id') and len(event.connection_id) == 2:
            text += '{}:{}'.format(*event.connection_id)

        text += '/'
        text += event.database_name
        ctx.active_dbc = text
        ctx.lctx['dbc'] = text

        ctx.active_dbc = 0
        ctx.db_opening = True
        datas = [text]
        ctx.elapsed = 0
        UdpSession.send_packet(PacketTypeEnum.TX_DB_CONN, ctx, datas)
        
        start_time = DateUtil.nowSystem()
        ctx.start_time = start_time
        ctx.active_sqlhash = command

    def succeeded(self, event):
        try:
            self.__succeeded(event)
        except Exception as e:
            ctx = TraceContextManager.getLocalContext()
            if ctx:
                logging.debug(e, extra={'id': 'MON60', 'ctx.id':ctx.id}, exc_info=True)
            else:
                logging.debug(e, extra={'id': 'MON60'}, exc_info=True)

        
    def __succeeded(self, event):
        ctx = TraceContextManager.getLocalContext()
        if not ctx:
            return
        query = 'command: {}, operation_id: {} '.format(event.command_name, event.operation_id)
        if ctx.active_sqlhash:
            query +=' query: {}'.format(ctx.active_sqlhash)

        ctx.db_opening = False
        datas = [ctx.lctx.get('dbc', ''), query]
        ctx.elapsed = int(event.duration_micros / 1000)
        UdpSession.send_packet(PacketTypeEnum.TX_SQL, ctx,
                               datas)

    def failed(self, event):
        try:
            self.__failed(event)
        except Exception as e:
            ctx = TraceContextManager.getLocalContext()
            if ctx:
                logging.debug(e, extra={'id': 'MON85', 'ctx.id':ctx.id}, exc_info=True)
            else:
                logging.debug(e, extra={'id': 'MON85'}, exc_info=True)
    
    def __failed(self, event):
        ctx = TraceContextManager.getLocalContext()
        if not ctx:
            return

        if hasattr(event, 'errtype'):
            ctx.error_step = event.errtype
        if not ctx.error:
            ctx.error = 1

        errors = []
        if hasattr(event, 'errtype'):
            errors.append(event.errtype)
        else:
            errors.append(str())    
        errors.append(str())

        error = 'command: {}, operation_id: {}'.format(event.command_name, event.operation_id)
        if ctx.active_sqlhash:
            error +=' query: {}'.format(ctx.active_sqlhash)
        frame = sys._current_frames().get(ctx.thread.ident)
        if not frame:
            return

        for stack in traceback.extract_stack(frame):
            line = stack[0]
            line_num = stack[1]
            method_name = stack[2]
            
            if line.find('/whatap/trace') > -1 or line.find('/threading.py') > -1:
                continue
            error += '{} ({}:{})\n'.format(method_name,line, line_num)
        
        errors.append(error)
        ctx.elapsed = int(event.duration_micros / 1000)
        UdpSession.send_packet(PacketTypeEnum.TX_ERROR, ctx, errors)

def instrument_mongo_client(module):

    def wrapper_init(fn):
        def trace(*args, **kwargs):
            _kwargs = dict()
            if kwargs:
                _kwargs.update(kwargs)

            event_listeners = [WhatapMongoCmdEventListener()]
            if 'event_listeners' in _kwargs:
                if isinstance(_kwargs['event_listeners'], list):
                    event_listeners += _kwargs['event_listeners']
                else:
                    event_listeners = _kwargs['event_listeners']
            _kwargs['event_listeners'] = event_listeners

            callback = fn(*args, **_kwargs)
            return callback
        
        return trace

    def wrapper_find(fn):
        def trace(*args, **kwargs):
            ctx = TraceContextManager.getLocalContext()
            if ctx:
                if len(args) > 1 and isinstance(args[1], dict):
                    query = pformat(args[1],compact=True)
                    
                    ctx.active_sqlhash = query
            callback = fn(*args, **kwargs)
            return callback
        
        return trace
    
    if hasattr(module, 'version_tuple'):
        (major, minor, buildno) = module.version_tuple
        if major >= 3 and minor >= 11:
            if hasattr(module, 'monitoring'):
                # module.MongoClient.__init__ = wrapper_init(module.MongoClient.__init__)
                module.monitoring.register(WhatapMongoCmdEventListener())
            if hasattr(module, 'collection') and hasattr(module.collection, 'Collection'):
                module.collection.Collection.find = wrapper_find(module.collection.Collection.find)

