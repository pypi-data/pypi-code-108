import inspect
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.net.udp_session import UdpSession
from whatap.trace import get_dict
from whatap.trace.mod.application_wsgi import trace_handler
from whatap.util.date_util import DateUtil
from whatap.trace.trace_context_manager import TraceContextManager

from whatap import logging


def instrument_plugin(module_dict):
    def wrapper(fn):
        @trace_handler(fn)
        def trace(*args, **kwargs):
            module_name = fn.__module__
            def_name = fn.__name__
            class_name = args[0].__class__.__name__ if len(args) and hasattr(
                args[0], def_name) else None
            
            if class_name:
                text = '{}:{}.{}'.format(module_name, class_name, def_name)
            else:
                text = '{}:{}'.format(module_name, def_name)
            
            ctx = TraceContextManager.getLocalContext()
            start_time = DateUtil.nowSystem()
            ctx.start_time = start_time
            try:
                callback = fn(*args, **kwargs)
                return callback
            except Exception as e:
                logging.debug(e, extra={'id': 'hook_method_patterns PARSING ERROR'})
            finally:
                datas = [text, '']
                ctx.elapsed = DateUtil.nowSystem() - start_time
                UdpSession.send_packet(PacketTypeEnum.TX_METHOD, ctx, datas)
        
        return trace
    
    try:
        for class_def in module_dict['class_defs']:
            class_def_list = class_def.split('.')  # exception
            
            m_list = []
            t_list = []
            module = module_dict['module']
            if len(class_def_list) == 2:
                if class_def_list[0] == '*':
                    for attr in dir(module):
                        if not attr.startswith('__') \
                                and not attr.endswith('__') \
                                and inspect.isclass(getattr(module, attr)) \
                                and not isinstance(getattr(module, attr), type(module)) \
                                and module.__name__ == getattr(module, attr).__module__ :
                            m_list.append(getattr(module, attr))
                else:
                    m_list = [getattr(module, class_def_list[0])]
                    
                target = class_def_list[1]
            else:
                m_list = [module]
                target = class_def_list[0]
                
            for m in m_list:
                if target == '*':
                    for attr in dir(m):
                        if not attr.startswith('__') \
                                and not attr.endswith('__') \
                                and hasattr(m, attr) \
                                and inspect.isfunction(getattr(m, attr)):
                            t_list.append(attr)
                else:
                    t_list.append(target)
                
                for t in t_list:
                    if hasattr(m, t):
                        try:
                            setattr(m, t, wrapper(getattr(m, t)))
                        except Exception as e:
                            get_dict(m)[t] = wrapper(getattr(m, t))
    except Exception as e:
        logging.debug(e, extra={'id': 'hook_method_patterns PARSING ERROR'})
        
